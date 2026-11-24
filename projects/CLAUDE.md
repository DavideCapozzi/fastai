# projects/: portfolio projects

The owner owns problem framing, dataset choice, splits, model and training choices,
metrics, evaluation and the core modelling code. Claude asks questions, reviews, and
lays out options with trade-offs, but does not decide or write these. The hint ladder
from course/CLAUDE.md applies to core code.

## Claude may write (announce first)
Environment, download/data scripts, CI, tests, Gradio/HF Spaces wrappers, plotting
helpers for README figures, scaffolding.

## Every project
- Start by copying projects/_template/ to projects/NN-slug/.
- README sections are mandatory: Problem, Data and license, Approach, My decisions,
  Results, Limitations, How to run, Demo.
- Check the dataset license allows public portfolio use and record it before starting.
- Data is never committed (data/ is gitignored); a download script is.
- Reproducible: fixed seeds; one documented command regenerates every reported number.
- Notebook outputs are stripped, so figures go to projects/NN-slug/figures/ (committed).
- Fits in 6 GB VRAM, or the README links the Kaggle run (notebook + version).

## Review checklist (when asked)
Leakage · validation split matches real use · baseline exists · metric matches goal ·
every claim backed by a number · README matches code.
