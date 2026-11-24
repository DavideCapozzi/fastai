"""Resolve, record and download upstream course material into upstream/ (gitignored).

The manifest is upstream-sources.toml (committed). Each [[source]] is one file at one version.

    python scripts/fetch_upstream.py resolve github fastai/course22 00-is-it-a-bird-....ipynb
    python scripts/fetch_upstream.py resolve kaggle jhoward/is-it-a-bird-creating-a-model-from-your-own-data
    python scripts/fetch_upstream.py add --lesson P1-L01 --kind github --ref fastai/course22 --path 00-....ipynb
    python scripts/fetch_upstream.py add --lesson P1-L01 --kind kaggle --ref jhoward/is-it-a-bird-...
    python scripts/fetch_upstream.py set-baseline --lesson P1-L01 --kind kaggle --ref jhoward/is-it-a-bird-...
    python scripts/fetch_upstream.py fetch [--lesson P1-L01]     # download entries missing locally
    python scripts/fetch_upstream.py list [--lesson P1-L01]

`resolve` and `add` always look up the latest version upstream. `add` replaces an older entry
for the same (lesson, kind, ref, path). Kaggle needs credentials (docs/setup.md); this script
never reads the credential files itself, the kaggle package does.
"""

from __future__ import annotations

import argparse
import contextlib
import datetime as dt
import io
import json
import subprocess
import sys
import tomllib
import urllib.parse
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
UPSTREAM = REPO / "upstream"
HEADER = """\
# Upstream course material, fetched into upstream/ (gitignored, never committed).
# Maintained by scripts/fetch_upstream.py and the /lesson-sync skill.
# One [[source]] per (lesson, file, version). `baseline = true` marks the most recently
# updated official source for the lesson; the choice is explained in docs/course-compat.md.
# version: full commit SHA (github) or notebook version number (kaggle).
# updated: date of the last upstream change to this file. fetched: date downloaded.
"""
FIELDS = ["lesson", "kind", "ref", "path", "version", "updated", "fetched", "baseline", "url"]


# ---------------------------------------------------------------- manifest I/O
def load(manifest: Path) -> list[dict]:
    if not manifest.exists():
        return []
    return tomllib.loads(manifest.read_text()).get("source", [])


def toml_value(v) -> str:
    if isinstance(v, bool):
        return "true" if v else "false"
    return json.dumps(str(v))  # JSON string escaping is valid TOML basic-string escaping


def save(manifest: Path, sources: list[dict]) -> None:
    sources = sorted(sources, key=lambda s: (s["lesson"], not s.get("baseline", False), s["kind"], s["ref"]))
    out = [HEADER.rstrip()]
    for s in sources:
        out.append("\n[[source]]")
        for k in FIELDS:
            if k in s and s[k] != "":
                out.append(f"{k:8} = {toml_value(s[k])}")
    manifest.write_text("\n".join(out) + "\n")


def local_path(s: dict) -> Path:
    if s["kind"] == "github":
        return UPSTREAM / "github" / s["ref"] / s["version"][:10] / s["path"]
    return UPSTREAM / "kaggle" / s["ref"] / f"v{s['version']}.ipynb"


# ---------------------------------------------------------------- github
def gh_latest(ref: str, path: str) -> dict:
    q = f"repos/{ref}/commits?path={urllib.parse.quote(path)}&per_page=1"
    try:
        raw = subprocess.run(["gh", "api", q], check=True, capture_output=True, text=True).stdout
    except (FileNotFoundError, subprocess.CalledProcessError):
        with urllib.request.urlopen(f"https://api.github.com/{q}", timeout=30) as r:
            raw = r.read().decode()
    commits = json.loads(raw)
    if not commits:
        raise SystemExit(f"no commits found for {ref}:{path} (wrong path?)")
    c = commits[0]
    return {
        "version": c["sha"],
        "updated": c["commit"]["committer"]["date"][:10],
        "url": f"https://github.com/{ref}/blob/{c['sha']}/{path}",
        "message": c["commit"]["message"].splitlines()[0],
    }


def gh_download(s: dict, dest: Path) -> None:
    url = f"https://raw.githubusercontent.com/{s['ref']}/{s['version']}/{urllib.parse.quote(s['path'])}"
    with urllib.request.urlopen(url, timeout=60) as r:
        data = r.read()
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(data)


# ---------------------------------------------------------------- kaggle
def kaggle_get(ref: str, version: str | None = None):
    owner, slug = ref.split("/", 1)
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            from kaggle.api.kaggle_api_extended import KaggleApi
        from kagglesdk.kernels.types.kernels_api_service import ApiGetKernelRequest

        api = KaggleApi()
        api.authenticate()
    except BaseException as e:  # kaggle raises SystemExit/OSError without credentials
        raise SystemExit(
            f"Kaggle API unavailable ({type(e).__name__}: {e}). Credentials missing? See docs/setup.md."
        ) from None
    with api.build_kaggle_client() as k:
        req = ApiGetKernelRequest()
        req.user_name, req.kernel_slug = owner, slug
        if version:
            req.version_label = f"v{version}"
        return k.kernels.kernels_api_client.get_kernel(req)


def kaggle_latest(ref: str) -> dict:
    resp = kaggle_get(ref)
    md = resp.metadata
    return {
        "version": str(md.current_version_number),
        "updated": md.last_run_time.strftime("%Y-%m-%d") if md.last_run_time else "",
        "url": f"https://www.kaggle.com/code/{ref}",
        "message": md.title,
    }


def kaggle_download(s: dict, dest: Path) -> None:
    resp = kaggle_get(s["ref"], s["version"])
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(resp.blob.source)


# ---------------------------------------------------------------- commands
def latest(kind: str, ref: str, path: str) -> dict:
    return gh_latest(ref, path) if kind == "github" else kaggle_latest(ref)


def download(s: dict) -> Path:
    dest = local_path(s)
    if not dest.exists():
        (gh_download if s["kind"] == "github" else kaggle_download)(s, dest)
    return dest


def same(s: dict, a) -> bool:
    return (s["lesson"], s["kind"], s["ref"], s.get("path", "")) == (a.lesson, a.kind, a.ref, a.path or "")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--manifest", type=Path, default=REPO / "upstream-sources.toml")
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("resolve")
    r.add_argument("kind", choices=["github", "kaggle"])
    r.add_argument("ref")
    r.add_argument("path", nargs="?", default="")
    for name in ("add", "set-baseline"):
        p = sub.add_parser(name)
        p.add_argument("--lesson", required=True, help="e.g. P1-L01")
        p.add_argument("--kind", required=True, choices=["github", "kaggle"])
        p.add_argument("--ref", required=True, help="owner/repo or owner/kernel-slug")
        p.add_argument("--path", default="", help="file path inside the repo (github only)")
        if name == "add":
            p.add_argument("--baseline", action="store_true")
    for name in ("fetch", "list"):
        sub.add_parser(name).add_argument("--lesson")
    a = ap.parse_args()

    if a.cmd == "resolve":
        print(json.dumps(latest(a.kind, a.ref, a.path), indent=2))
        return 0

    sources = load(a.manifest)

    if a.cmd == "add":
        info = latest(a.kind, a.ref, a.path)
        entry = {"lesson": a.lesson, "kind": a.kind, "ref": a.ref, "path": a.path,
                 "version": info["version"], "updated": info["updated"],
                 "fetched": dt.date.today().isoformat(), "baseline": a.baseline, "url": info["url"]}
        old = [s for s in sources if same(s, a)]
        if old and old[0]["version"] == entry["version"]:
            entry["fetched"] = old[0].get("fetched", entry["fetched"])
            entry["baseline"] = a.baseline or old[0].get("baseline", False)
        sources = [s for s in sources if not same(s, a)] + [entry]
        if a.baseline:
            for s in sources:
                if s["lesson"] == a.lesson and s is not entry:
                    s["baseline"] = False
        dest = download(entry)
        save(a.manifest, sources)
        print(f"{a.lesson} {a.kind}:{a.ref} {a.path} @ {entry['version'][:10]} "
              f"(updated {entry['updated']}) -> {dest.relative_to(REPO)}")
        return 0

    if a.cmd == "set-baseline":
        hit = [s for s in sources if same(s, a)]
        if not hit:
            raise SystemExit("no such entry; run `add` first")
        for s in sources:
            if s["lesson"] == a.lesson:
                s["baseline"] = s is hit[0]
        save(a.manifest, sources)
        print(f"baseline for {a.lesson}: {a.kind}:{a.ref} {a.path}")
        return 0

    chosen = [s for s in sources if not a.lesson or s["lesson"] == a.lesson]
    for s in chosen:
        dest = download(s) if a.cmd == "fetch" else local_path(s)
        flag = "*" if s.get("baseline") else " "
        state = "ok" if dest.exists() else "missing"
        print(f"{flag} {s['lesson']} {s['kind']:6} {s['ref']} {s.get('path', '')} "
              f"@ {s['version'][:10]} updated {s['updated']} [{state}] {dest.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
