# Course compatibility notes

Where the official fast.ai course code (Part 1, 2022 edition) and today's stack disagree,
and what I changed to make it run. Stack: see [environment.yml](../environment.yml).
Upstream sources and versions: [upstream-sources.toml](../upstream-sources.toml).

For each lesson, the baseline is whichever official source was **updated most recently**
(the Kaggle notebook linked from course.fast.ai, fastai/course22, or fastai/fastbook). When
these sources disagree, that disagreement is logged as a `source-mismatch`.

**Types:** `api-break` · `deprecation` · `external-service` · `data-access` · `env` ·
`result-drift` · `source-mismatch`
**Status:** `resolved` (fix verified by a re-run) · `workaround` (runs, with a caveat) · `open`

## Summary

| ID | Lesson | Type | Discrepancy | Status |
|---|---|---|---|---|
| [ENV] | all | env | [fastbook pins ipywidgets<8](#env-fastbook-ipywidgets-pin) | workaround |
| [P1-L01] | 1 | external-service | [duckduckgo_search → ddgs](#p1-l01-duckduckgo_search--ddgs) | resolved |
| [P1-L01] | 1 | external-service | [ddgs returns ~35 images per query](#p1-l01-ddgs-returns-35-images-per-query) | workaround |
| [P1-L01] | 1 | deprecation | [matplotlib `__array__` copy warning](#p1-l01-matplotlib-__array__-copy-warning) | workaround |
| [P1-L01] | 1 | source-mismatch | [Kaggle v10 vs course22 copy](#p1-l01-kaggle-v10-vs-course22-copy) | workaround |

## Details

### [ENV] fastbook ipywidgets pin
- Source: PyPI `fastbook==0.0.29` (requirement `ipywidgets<8`), checked 2026-11-23
- Type: env
- Symptom: `pip install fastbook` would downgrade ipywidgets 8.1.8 → 7.8.5 (and
  jupyterlab_widgets 3 → 1), which breaks widgets in JupyterLab 4 / VS Code.
- Cause: an old upper bound in fastbook's metadata; fastai itself works with ipywidgets 8.
- Fix: `pip install --no-deps fastbook==0.0.29` (its other requirements are already pinned in
  environment.yml). `pip check` still reports the pin; this is expected.
- Verified: 2026-11-23, `import fastbook` OK under ipywidgets 8.1.8 (scripts/check_env.py).
  Widget behaviour (`ImageClassifierCleaner`, lesson 2) not yet exercised.
- Status: workaround

## Lesson 1: Getting started (P1-L01)

Baseline: Kaggle `jhoward/is-it-a-bird-creating-a-model-from-your-own-data` v10 (updated
2026-11-21), newer than the course22 copy (`2303905`, 2024-10-08). Secondary, recorded but not
run: Kaggle `jupyter-notebook-101` v3, course22 `01-jupyter-notebook-101` (2023-02-06), fastbook
`01_intro.ipynb` (2024-06-08). Patches: [P1-L01.toml](compat-patches/P1-L01.toml). The Kaggle
copy has no stored outputs, so result comparison uses the course22 outputs.

### [P1-L01] duckduckgo_search → ddgs
- Source: Kaggle jhoward/is-it-a-bird-creating-a-model-from-your-own-data @ v10, 2026-11-21
- Type: external-service
- Symptom: `RatelimitException: https://duckduckgo.com/?q=bird+photos 202 Ratelimit` in the
  first `search_images` call; `RuntimeWarning` that `duckduckgo_search` was renamed to `ddgs`.
- Cause: the old package is renamed and its endpoint is rate-limited.
- Fix: `from duckduckgo_search import DDGS` → `from ddgs import DDGS` (patch `P1-L01-ddgs`).
- Verified: re-run on 2026-11-24 (run `patched`), all 11 code cells ran, 41 s.
- Status: resolved

### [P1-L01] ddgs returns ~35 images per query
- Source: same notebook, cell `search_images(..., max_images=200)`
- Type: external-service
- Symptom: after the rename fix only 35 images per class (70 total, 14 validation); the model
  ends at error_rate 0.214 after `fine_tune(3)`, versus 0.000 in the course22 stored output.
- Cause: ddgs caps image results at about 35 per query regardless of `max_results`.
- Fix: download the union of four query variants (`photo`, `photos`, `picture`, `image`) per
  class (patch `P1-L01-ddgs-cap`). This changes the data-gathering cell, so the dataset is
  similar to upstream's but not identical.
- Verified: re-run on 2026-11-24 (run `patched2`), 134 forest + 139 bird images, 0 failed
  files, error_rate 0.000 after 3 epochs (valid_loss 0.000086), prediction "bird", p=1.0000;
  course22 stored: error_rate 0.000, valid_loss 0.0080. Peak VRAM reserved 954 MB. 117 s.
- Status: workaround

### [P1-L01] matplotlib `__array__` copy warning
- Source: same notebook, `dls.show_batch(max_n=6)`
- Type: deprecation
- Symptom: `DeprecationWarning: __array__ implementation doesn't accept a copy keyword`.
- Cause: a numpy 2 / matplotlib interaction inside the libraries, not in lesson code.
- Fix: none needed; the cell runs and the figure renders.
- Verified: re-run on 2026-11-24 (runs `patched`, `patched2`), cell completes.
- Status: workaround

### [P1-L01] Kaggle v10 vs course22 copy
- Source: Kaggle v10 (2026-11-21) vs fastai/course22 @ 2303905 (2024-10-08)
- Type: source-mismatch
- Symptom: the code cells differ: the install line (`duckduckgo_search>=6.2` pinned on Kaggle,
  unpinned in course22); search queries (`{o} photo` vs `{o} sun photo` / `{o} shade photo`);
  pause between searches (5 s vs 10 s); `.dataloaders(path, bs=32)` vs `.dataloaders(path)`.
- Cause: the Kaggle copy was updated after the GitHub copy.
- Fix: use the Kaggle copy as baseline (most recent).
- Verified: code-cell diff on 2026-11-24 and the baseline run above.
- Status: workaround
