"""Environment health check for the fast.ai course repo.

Run from the terminal:
    micromamba run -n fastai-course python scripts/check_env.py [--offline]
or from VS Code ("Run Python File" with the fastai-course interpreter).

Checks: GPU and VRAM, package versions against environment.yml pins, imports used by
the lessons, the graphviz binary, DDGS image-search reachability, presence of Kaggle and
SerpAPI credentials (existence only: credential files are never opened), and the repo's
notebook tooling (nbstripout filter, jupytext config).

Exit code: 0 if no check FAILed (WARNs allowed), 1 otherwise.
"""

from __future__ import annotations

import argparse
import importlib
import importlib.metadata as md
import os
import re
import shutil
import stat
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
RESULTS: list[tuple[str, str, str]] = []  # (status, check, detail)

# Modules the course imports (lesson numbers in comments). Import failures are FAILs.
IMPORTS = [
    "fastai.vision.all",      # L1-2, 8
    "fastai.text.all",        # L4 (ULMFiT path)
    "fastai.tabular.all",     # L5-6
    "fastai.collab",          # L7
    "timm",                   # L3, road-to-the-top
    "transformers",           # L4
    "datasets",               # L4
    "sentencepiece",          # L4 (deberta tokenizer)
    "ddgs",                   # L1-2 image search
    "fastdownload",           # L1
    "gradio",                 # L2 deployment
    "fastkaggle",             # road-to-the-top
    "kaggle",                 # data access
    "fastbook",               # book chapters
    "sklearn", "sympy", "plotly", "seaborn",
    "dtreeviz", "treeinterpreter", "waterfall_chart", "graphviz",
]


def record(status: str, check: str, detail: str = "") -> None:
    RESULTS.append((status, check, detail))
    print(f"[{status:4}] {check}{': ' + detail if detail else ''}", flush=True)


def section(title: str) -> None:
    print(f"\n== {title}", flush=True)


def check_python() -> None:
    section("Python")
    env = os.environ.get("CONDA_DEFAULT_ENV") or Path(sys.prefix).name
    ok = Path(sys.prefix).name == "fastai-course"
    record("OK" if ok else "WARN", "interpreter", f"{sys.version.split()[0]} in env '{env}' ({sys.prefix})")


def check_gpu() -> None:
    section("GPU")
    try:
        import torch
    except Exception as e:  # noqa: BLE001
        record("FAIL", "torch import", repr(e))
        return
    record("OK", "torch", f"{torch.__version__}, CUDA build {torch.version.cuda}")
    if not torch.cuda.is_available():
        record("FAIL", "CUDA available", "False (check `nvidia-smi` and the Windows NVIDIA driver)")
        return
    props = torch.cuda.get_device_properties(0)
    free, total = torch.cuda.mem_get_info(0)
    record("OK", "device", f"{props.name}, {total / 2**30:.1f} GB total, {free / 2**30:.1f} GB free")
    try:
        x = torch.randn(2048, 2048, device="cuda", dtype=torch.float16)
        t0 = time.perf_counter()
        (x @ x).sum().item()
        record("OK", "fp16 matmul on GPU", f"{(time.perf_counter() - t0) * 1000:.0f} ms")
    except Exception as e:  # noqa: BLE001
        record("FAIL", "fp16 matmul on GPU", repr(e))


def pinned_versions() -> dict[str, str]:
    """Parse `name==version` pins from environment.yml (no YAML dependency needed)."""
    pins = {}
    env_file = REPO / "environment.yml"
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            m = re.match(r"\s*-\s*([A-Za-z0-9_.\-]+)==([^\s#]+)", line)
            if m:
                pins[m.group(1)] = m.group(2)
    return pins


def norm(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


def check_versions() -> None:
    section("Package versions vs environment.yml")
    pins = pinned_versions()
    if not pins:
        record("WARN", "environment.yml", "no pins found")
        return
    drift = []
    for name, want in pins.items():
        try:
            have = md.version(name)
        except md.PackageNotFoundError:
            drift.append(f"{name} missing (want {want})")
            continue
        if norm(have) != norm(want):
            drift.append(f"{name} {have} (pinned {want})")
    if drift:
        record("WARN", f"{len(drift)} of {len(pins)} pins differ", "; ".join(drift))
    else:
        record("OK", "all pins match", f"{len(pins)} packages")
    try:
        md.version("fastbook")
    except md.PackageNotFoundError:
        record("WARN", "fastbook", "not installed: pip install --no-deps fastbook==0.0.29")


def check_imports() -> None:
    section("Imports")
    import contextlib
    import io
    import warnings

    failed = []
    for mod in IMPORTS:
        try:
            # `import kaggle` prints an auth banner when no credentials exist: silence it.
            with warnings.catch_warnings(), contextlib.redirect_stdout(io.StringIO()), \
                    contextlib.redirect_stderr(io.StringIO()):
                warnings.simplefilter("ignore")
                importlib.import_module(mod)
        except Exception as e:  # noqa: BLE001
            failed.append(f"{mod} ({type(e).__name__}: {str(e)[:120]})")
    if failed:
        for f in failed:
            record("FAIL", "import", f)
    else:
        record("OK", "all imports", f"{len(IMPORTS)} modules")
    dot = shutil.which("dot")
    record("OK" if dot else "WARN", "graphviz `dot` binary", dot or "missing (micromamba install -c conda-forge graphviz)")


def check_ddgs(offline: bool) -> None:
    section("Image search (DDGS)")
    if offline:
        record("SKIP", "DDGS reachability", "--offline")
        return
    try:
        from ddgs import DDGS

        t0 = time.perf_counter()
        res = DDGS(timeout=15).images("bird photos", max_results=30)
        urls = [r.get("image") for r in res if r.get("image")]
        dt = time.perf_counter() - t0
        if len(urls) >= 10:
            record("OK", "DDGS().images", f"{len(urls)} URLs in {dt:.1f}s")
        else:
            record("WARN", "DDGS().images", f"only {len(urls)}/30 URLs in {dt:.1f}s (rate limit?)")
    except Exception as e:  # noqa: BLE001
        record("WARN", "DDGS().images", f"{type(e).__name__}: {str(e)[:160]}")


def describe_file(p: Path) -> str:
    """Existence and permissions only. Never opens the file."""
    mode = stat.S_IMODE(p.stat().st_mode)
    note = "" if mode & 0o077 == 0 else " (too open: run chmod 600)"
    return f"{p} exists, mode {mode:o}{note}"


def check_credentials() -> None:
    section("Credentials (presence only; files are never read)")
    home = Path.home()
    legacy_dir = home / ".kaggle"
    xdg = Path(os.environ.get("XDG_CONFIG_HOME") or home / ".config") / "kaggle"
    # kaggle 2.x reads kaggle.json from ~/.kaggle if that dir exists, else from $XDG_CONFIG_HOME/kaggle.
    json_dir = Path(os.environ["KAGGLE_CONFIG_DIR"]) if os.environ.get("KAGGLE_CONFIG_DIR") else (
        legacy_dir if legacy_dir.exists() else xdg
    )
    found = []
    # kaggle.json (legacy key), access_token (API token), credentials.json (`kaggle auth login`)
    for p in {json_dir / "kaggle.json", home / ".kaggle" / "access_token", home / ".kaggle" / "credentials.json"}:
        if p.is_file():
            found.append(describe_file(p))
    for var in ("KAGGLE_API_TOKEN", "KAGGLE_USERNAME", "KAGGLE_KEY"):
        if os.environ.get(var):
            found.append(f"${var} is set")
    stray = xdg / "kaggle.json"
    if legacy_dir.exists() and stray.is_file() and json_dir != xdg:
        record("WARN", "kaggle.json ignored", f"{stray} is shadowed because {legacy_dir} exists")
    if found:
        for f in found:
            record("OK", "Kaggle", f)
    else:
        record("WARN", "Kaggle", f"no credentials: place kaggle.json in {json_dir} (chmod 600)")
    record("OK" if os.environ.get("SERP_API_KEY") else "INFO", "SERP_API_KEY",
           "set" if os.environ.get("SERP_API_KEY") else "not set (only needed for the fastbook ch. 2 SerpAPI path)")


def check_repo_tooling() -> None:
    section("Repo notebook tooling")

    def git(*args: str) -> str:
        r = subprocess.run(["git", "-C", str(REPO), *args], capture_output=True, text=True)
        return r.stdout.strip()

    clean = git("config", "--get", "filter.nbstripout.clean")
    attrs = (REPO / ".gitattributes").read_text() if (REPO / ".gitattributes").exists() else ""
    ok = bool(clean) and "filter=nbstripout" in attrs
    record("OK" if ok else "WARN", "nbstripout git filter",
           "installed" if ok else "missing: nbstripout --install --attributes .gitattributes")
    jt = REPO / "jupytext.toml"
    record("OK" if jt.exists() else "WARN", "jupytext pairing", str(jt.name) if jt.exists() else "jupytext.toml missing")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--offline", action="store_true", help="skip network checks")
    args = ap.parse_args()

    check_python()
    check_gpu()
    check_versions()
    check_imports()
    check_ddgs(args.offline)
    check_credentials()
    check_repo_tooling()

    counts = {s: sum(1 for r in RESULTS if r[0] == s) for s in ("OK", "WARN", "FAIL")}
    print(f"\nSummary: {counts['OK']} OK, {counts['WARN']} WARN, {counts['FAIL']} FAIL")
    return 1 if counts["FAIL"] else 0


if __name__ == "__main__":
    sys.exit(main())
