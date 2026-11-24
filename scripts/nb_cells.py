"""Print notebook cells without flooding the terminal (or an agent's context) with base64.

Usage:
    python scripts/nb_cells.py NB.ipynb                 # index: one line per cell
    python scripts/nb_cells.py NB.ipynb --cells 3-7,12  # full source of selected cells
    python scripts/nb_cells.py NB.ipynb --cells 5 --outputs   # + text outputs, images as sizes
    python scripts/nb_cells.py NB.ipynb --code-only --cells all
"""

from __future__ import annotations

import argparse
import sys

import nbformat

MAX_OUT = 2000  # characters of text output per cell


def parse_range(spec: str, n: int) -> list[int]:
    if spec == "all":
        return list(range(n))
    idx: list[int] = []
    for part in spec.split(","):
        if "-" in part:
            a, b = part.split("-")
            idx.extend(range(int(a), int(b) + 1))
        else:
            idx.append(int(part))
    return [i for i in idx if 0 <= i < n]


def render_output(o: dict) -> str:
    kind = o.get("output_type")
    if kind == "stream":
        return "".join(o.get("text", ""))
    if kind == "error":
        return f"{o.get('ename')}: {o.get('evalue')}"
    parts = []
    for mime, val in o.get("data", {}).items():
        if mime == "text/plain":
            parts.append(val if isinstance(val, str) else "".join(val))
        else:
            parts.append(f"[{mime}, {len(str(val)) // 1024} KB]")
    return "\n".join(parts)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("notebook")
    ap.add_argument("--cells", help="e.g. 3-7,12 or all; omit for a one-line index")
    ap.add_argument("--outputs", action="store_true", help="show text outputs (truncated)")
    ap.add_argument("--code-only", action="store_true")
    a = ap.parse_args()

    nb = nbformat.read(a.notebook, as_version=4)
    cells = nb.cells
    if not a.cells:
        print(f"{a.notebook}: {len(cells)} cells, kernel={nb.metadata.get('kernelspec', {}).get('name')}")
        for i, c in enumerate(cells):
            if a.code_only and c.cell_type != "code":
                continue
            lines = c.source.strip().splitlines()
            first = lines[0][:100] if lines else ""
            more = f" (+{len(lines) - 1} lines)" if len(lines) > 1 else ""
            nout = len(c.get("outputs", []))
            print(f"[{i:3}] {c.cell_type[:4]} {first}{more}{f'  <{nout} out>' if nout else ''}")
        return 0

    for i in parse_range(a.cells, len(cells)):
        c = cells[i]
        if a.code_only and c.cell_type != "code":
            continue
        print(f"--- [{i}] {c.cell_type}")
        print(c.source)
        if a.outputs and c.cell_type == "code":
            for o in c.get("outputs", []):
                txt = render_output(o)
                print(f">>> {txt[:MAX_OUT]}{' …[truncated]' if len(txt) > MAX_OUT else ''}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
