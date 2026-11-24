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
