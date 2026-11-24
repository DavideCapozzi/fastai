"""Execute a notebook headless in the current env and report what broke.

    python scripts/run_notebook.py NB.ipynb [--patch docs/compat-patches/P1-L01.toml]
        [--label baseline] [--cell-timeout 900] [--total-timeout 3600] [--continue-on-error]

What it does, on a copy (the source notebook is never modified):
  1. Replaces `!pip` / `%pip` / `!conda` lines with `pass  # skipped`, so upstream install cells cannot
     change the env. They are listed in the report.
  2. Applies patches from a TOML file (minimal fixes, each tied to a course-compat entry):
         [[patch]]
         id   = "P1-L01-ddgs"       # course-compat entry this patch implements
         cell = 7                   # optional: restrict the match to one cell
         old  = "from duckduckgo_search import DDGS"
         new  = "from ddgs import DDGS"
     Every `old` must match exactly once in its scope, otherwise nothing runs (exit 3).
  3. Runs every code cell with nbclient. The kernel cwd is the run directory, so downloads land
     there. It stops at the first error unless --continue-on-error.
  4. Collects per-cell errors, warnings (stderr lines that look like warnings), duration, and
     peak CUDA memory (torch.cuda.max_memory_allocated/reserved).

Output in --out-dir (default upstream/runs/<notebook-stem>/<timestamp>-<label>/):
  executed.ipynb, report.json, report.md. A short summary is printed.
Exit code: 0 all cells ran, 1 a cell failed, 2 total timeout, 3 bad patch.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
import time
import tomllib
from pathlib import Path

import nbformat
from nbclient import NotebookClient

REPO = Path(__file__).resolve().parents[1]
INSTALL_RE = re.compile(r"^(\s*)([!%](?:pip|conda|mamba)\b.*)$", re.M)
WARN_RE = re.compile(r"(\w*Warning\b.*|\bwarn(?:ing)?:.*)", re.I)

SETUP = """\
# [run_notebook] setup cell (not part of the upstream notebook)
import os, sys, warnings
warnings.simplefilter("default")
os.environ.setdefault("PYTHONWARNINGS", "default")
try:
    import torch
    if torch.cuda.is_available():
        torch.cuda.reset_peak_memory_stats()
except Exception:
    pass
print("__RUN_NOTEBOOK_PY__", sys.executable)
"""

PROBE = """\
# [run_notebook] probe cell
import json, sys
_r = {}
if "torch" in sys.modules:
    import torch
    if torch.cuda.is_available():
        _r = {"max_allocated_mb": round(torch.cuda.max_memory_allocated() / 2**20),
              "max_reserved_mb": round(torch.cuda.max_memory_reserved() / 2**20),
              "device": torch.cuda.get_device_name(0)}
print("__RUN_NOTEBOOK_VRAM__", json.dumps(_r))
"""


def strip_installs(nb) -> list[dict]:
    skipped = []
    for i, c in enumerate(nb.cells):
        if c.cell_type != "code":
            continue
        for m in INSTALL_RE.finditer(c.source):
            skipped.append({"cell": i, "line": m.group(2).strip()})
        c.source = INSTALL_RE.sub(r"\1pass  # [run_notebook] skipped: \2", c.source)
    return skipped


def apply_patches(nb, patch_file: Path) -> list[dict]:
    patches = tomllib.loads(patch_file.read_text()).get("patch", [])
    applied = []
    for p in patches:
        scope = [p["cell"]] if "cell" in p else range(len(nb.cells))
        hits = [(i, nb.cells[i].source.count(p["old"])) for i in scope if i < len(nb.cells)]
        total = sum(n for _, n in hits)
        if total != 1:
            print(f"patch {p.get('id')}: `old` matched {total} times (need exactly 1)", file=sys.stderr)
            sys.exit(3)
        i = next(i for i, n in hits if n)
        nb.cells[i].source = nb.cells[i].source.replace(p["old"], p["new"])
        applied.append({"id": p.get("id", "?"), "cell": i})
    return applied


def text_of(outputs) -> str:
    parts = []
    for o in outputs:
        if o.get("output_type") == "stream":
            parts.append(o.get("text", ""))
        elif "data" in o and "text/plain" in o["data"]:
            parts.append(o["data"]["text/plain"])
    return "".join(parts)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("notebook", type=Path)
    ap.add_argument("--patch", type=Path)
    ap.add_argument("--label", default="baseline")
    ap.add_argument("--out-dir", type=Path)
    ap.add_argument("--cell-timeout", type=int, default=900)
    ap.add_argument("--total-timeout", type=int, default=3600)
    ap.add_argument("--continue-on-error", action="store_true")
    ap.add_argument("--kernel", default="python3")
    a = ap.parse_args()

    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    out = a.out_dir or REPO / "upstream" / "runs" / a.notebook.stem / f"{stamp}-{a.label}"
    out.mkdir(parents=True, exist_ok=True)

    nb = nbformat.read(a.notebook, as_version=4)
    skipped = strip_installs(nb)
    applied = apply_patches(nb, a.patch) if a.patch else []
    n_code = sum(1 for c in nb.cells if c.cell_type == "code" and c.source.strip())
    nb.cells.insert(0, nbformat.v4.new_code_cell(SETUP))
    off = 1  # cell indices in the report refer to the ORIGINAL notebook

    client = NotebookClient(nb, timeout=a.cell_timeout, kernel_name=a.kernel, allow_errors=True,
                            resources={"metadata": {"path": str(out)}})
    cells, warnings_seen, status, kernel_py, vram = [], {}, "ok", None, {}
    t_start = time.perf_counter()
    with client.setup_kernel():
        for idx in range(len(nb.cells)):
            cell = nb.cells[idx]
            if cell.cell_type != "code" or not cell.source.strip():
                continue
            if time.perf_counter() - t_start > a.total_timeout:
                status = "total-timeout"
                break
            t0 = time.perf_counter()
            try:
                client.execute_cell(cell, idx)
            except Exception as e:  # cell timeout or kernel death
                cell.outputs.append(nbformat.v4.new_output("error", ename=type(e).__name__,
                                                           evalue=str(e)[:500], traceback=[]))
            secs = round(time.perf_counter() - t0, 1)
            txt = text_of(cell.outputs)
            if idx == 0:
                m = re.search(r"__RUN_NOTEBOOK_PY__ (\S+)", txt)
                kernel_py = m.group(1) if m else None
                continue
            orig = idx - off
            for line in txt.splitlines():
                if line[:1].isspace():  # the warnings module echoes the source line indented
                    continue
                w = WARN_RE.search(line)
                if w and "[run_notebook]" not in line:
                    key = w.group(1).strip()[:200]
                    warnings_seen.setdefault(key, orig)
            errs = [o for o in cell.outputs if o.get("output_type") == "error"]
            rec = {"cell": orig, "seconds": secs, "first_line": cell.source.strip().splitlines()[0][:100]}
            if errs:
                e = errs[0]
                tb = [re.sub(r"\x1b\[[0-9;]*m", "", t) for t in e.get("traceback", [])]
                rec["error"] = {"ename": e.get("ename"), "evalue": str(e.get("evalue"))[:500],
                                "traceback_tail": "\n".join(tb[-3:])[-1500:]}
                if "OutOfMemory" in str(e.get("ename")) or "out of memory" in str(e.get("evalue")):
                    rec["error"]["hint"] = "CUDA OOM: candidate `env` discrepancy (bs / fp16 / grad accumulation)"
            cells.append(rec)
            if errs and not a.continue_on_error:
                status = "error"
                break
        probe = nbformat.v4.new_code_cell(PROBE)
        nb.cells.append(probe)
        try:
            client.execute_cell(probe, len(nb.cells) - 1)
            m = re.search(r"__RUN_NOTEBOOK_VRAM__ (.*)", text_of(probe.outputs))
            vram = json.loads(m.group(1)) if m else {}
        except Exception:  # noqa: BLE001
            pass
    if status == "ok" and any("error" in c for c in cells):
        status = "error"

    nbformat.write(nb, out / "executed.ipynb")
    report = {
        "notebook": str(a.notebook), "label": a.label, "status": status,
        "started": stamp, "seconds": round(time.perf_counter() - t_start, 1),
        "kernel_python": kernel_py, "code_cells": n_code, "cells_run": len(cells),
        "skipped_installs": skipped, "patches_applied": applied, "peak_vram": vram,
        "errors": [c for c in cells if "error" in c],
        "warnings": [{"cell": c, "text": w} for w, c in warnings_seen.items()],
        "cells": cells,
    }
    (out / "report.json").write_text(json.dumps(report, indent=2))

    md = [f"# Run report: {a.notebook.name} ({a.label})", "",
          f"- Status: **{status}**, {report['seconds']} s, {len(cells)}/{n_code} code cells run",
          f"- Kernel: `{kernel_py}`", f"- Peak VRAM: {vram or 'n/a'}",
          f"- Skipped installs: {[s['line'] for s in skipped] or 'none'}",
          f"- Patches: {[p['id'] for p in applied] or 'none'}", "", "## Errors"]
    md += [f"- cell {e['cell']} `{e['first_line']}`: **{e['error']['ename']}**: {e['error']['evalue'][:300]}"
           for e in report["errors"]] or ["none"]
    md += ["", "## Warnings (first occurrence)"]
    md += [f"- cell {w['cell']}: {w['text']}" for w in report["warnings"]] or ["none"]
    (out / "report.md").write_text("\n".join(md) + "\n")
    print("\n".join(md))
    print(f"\nRun dir: {out}")
    return {"ok": 0, "error": 1, "total-timeout": 2}[status]


if __name__ == "__main__":
    sys.exit(main())
