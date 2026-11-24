"""Create an empty lesson folder for the owner: notebook (headings + links, no code), notes.md.

    python scripts/scaffold_lesson.py --part 1 --lesson 1 --slug getting-started \
        --title "Getting started" \
        --link "Lesson page=https://course.fast.ai/Lessons/lesson1.html" \
        --link "Kaggle notebook=https://www.kaggle.com/code/..." \
        [--section "Collect data" --section "Train" ...]

Never overwrites existing files. The paired .py is created by `jupytext --sync`.
Headings are generic or given via --section in my own words; no upstream prose is copied.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

import nbformat

REPO = Path(__file__).resolve().parents[1]
DEFAULT_SECTIONS = ["Setup", "Data", "Model and training", "Results and interpretation",
                    "Using the model", "My experiments", "Open questions"]

NOTES = """\
# Lesson {n}: {title}: my notes

> Written by me, in my own words. The agent only flags misconceptions (see ADR-0002).

## Key ideas


## How I would explain it to someone else


## What surprised me / what I got wrong at first


## Questionnaire
<!-- fastbook chapter questionnaire: questions I could not answer first time -->


## Course compatibility issues I hit
<!-- link entries in docs/course-compat.md, e.g. [P1-L{n:02d}] ... -->


## Mini-project ideas

"""


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--part", type=int, required=True)
    ap.add_argument("--lesson", type=int, required=True)
    ap.add_argument("--slug", required=True)
    ap.add_argument("--title", required=True)
    ap.add_argument("--link", action="append", default=[], help="'Label=URL', repeatable")
    ap.add_argument("--section", action="append", help="heading, repeatable (default: generic set)")
    a = ap.parse_args()

    name = f"{a.lesson:02d}-{a.slug}"
    d = REPO / "course" / f"part{a.part}" / name
    d.mkdir(parents=True, exist_ok=True)
    nb_path, notes_path = d / f"{name}.ipynb", d / "notes.md"
    lid = f"P{a.part}-L{a.lesson:02d}"
    created = []

    if not nb_path.exists():
        links = "\n".join(f"- [{lbl}]({url})" for lbl, url in (x.split("=", 1) for x in a.link))
        intro = (
            f"# Lesson {a.lesson}: {a.title}\n\n"
            "My own notebook for this lesson: every code cell is written by me unless it starts with "
            "`# solution shown by agent` ([learning policy](../../../docs/decisions/0002-ai-usage-and-learning-policy.md)).\n\n"
            f"**Sources**\n{links}\n\n"
            f"**Compatibility notes:** entries tagged `[{lid}]` in "
            "[docs/course-compat.md](../../../docs/course-compat.md)."
        )
        nb = nbformat.v4.new_notebook()
        nb.metadata["kernelspec"] = {"name": "python3", "display_name": "Python 3 (ipykernel)", "language": "python"}
        nb.cells = [nbformat.v4.new_markdown_cell(intro)]
        for i, s in enumerate(a.section or DEFAULT_SECTIONS, 1):
            nb.cells += [nbformat.v4.new_markdown_cell(f"## {i}. {s}"), nbformat.v4.new_code_cell("")]
        nbformat.write(nb, nb_path)
        created.append(nb_path)
        subprocess.run([sys.executable, "-m", "jupytext", "--sync", "--quiet", str(nb_path)], check=True)
        created.append(nb_path.with_suffix(".py"))
    if not notes_path.exists():
        notes_path.write_text(NOTES.format(n=a.lesson, title=a.title))
        created.append(notes_path)

    for p in created:
        print("created", p.relative_to(REPO))
    if not created:
        print("nothing to do: all files exist in", d.relative_to(REPO))
    return 0


if __name__ == "__main__":
    sys.exit(main())
