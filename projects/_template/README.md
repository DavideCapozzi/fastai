# <Project title>

<!-- One sentence: what it does and for whom. Then a headline result, e.g.
"Classifies X with 94.1% accuracy (baseline: 71.3%)". Fill this in last. -->

> Built after fast.ai Part 1, lesson <N> ([course notes](../../course/part1/)).
> Modelling, data and evaluation decisions and the core code are mine; see
> [How I use AI](../../docs/ai-workflow.md).

## Problem
<!-- What question does this answer? Who would use it? What does a wrong prediction cost? -->

## Data and license
<!-- Source + link, size, label distribution, collection date.
License and whether it allows public portfolio use (checked on <date>).
How to download: `python scripts/download_data.py` (data/ is never committed). -->

## Approach
<!-- Pipeline in 3–6 bullets: preprocessing, split, model, training, evaluation. -->

## My decisions
<!-- The interesting part for a reader. For each: decision, alternatives considered, why, and
whether the evidence supported it. E.g. "Split by patient rather than by image, because...". -->

| Decision | Alternatives | Why | Outcome |
|---|---|---|---|
| | | | |

## Results
<!-- Metric chosen and why. Baseline vs final model on the held-out set. Figures from
figures/ (notebook outputs are stripped). Every number reproducible with one command. -->

| Model | <metric> | Notes |
|---|---|---|
| Baseline | | |
| Final | | |

## Limitations
<!-- Where it fails (show examples), data biases, what I would do with more time or data. -->

## How to run
```bash
micromamba env create -f ../../environment.yml   # once
micromamba run -n fastai-course python scripts/download_data.py
micromamba run -n fastai-course python scripts/train.py --seed 42   # or: open notebooks/
```
<!-- Hardware: RTX 3060 Laptop 6 GB, <time>. Or: Kaggle notebook <link> version <N>. -->

## Demo
<!-- Link to Hugging Face Space / Gradio app + a screenshot or GIF. -->
