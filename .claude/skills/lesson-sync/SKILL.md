---
name: lesson-sync
description: Sync one fast.ai course lesson with today's stack. Finds the official sources, picks the most recently updated one as baseline, runs it headless, classifies and fixes discrepancies, documents them in docs/course-compat.md, and scaffolds the owner's empty lesson folder. Use when the user runs /lesson-sync <part> <lesson> or asks to start a new lesson.
argument-hint: <part> <lesson>   (e.g. 1 1)
---

# lesson-sync

Arguments: `$ARGUMENTS` = `<part> <lesson>`. Lesson ID = `P<part>-L<NN>` (e.g. `P1-L01`).
All root CLAUDE.md rules apply. This skill is compat plumbing. It never writes lesson
solutions and never commits. Delegate bulky reading (web pages, notebook diffs) to subagents
and keep only their summaries. Run all commands as `micromamba run -n fastai-course ...`.

## 0. Preflight
- `python scripts/check_env.py`. If anything FAILs, stop and report.
- Read `journal/progress.md`. Run `python scripts/fetch_upstream.py list --lesson <ID>`. If the
  lesson already has entries, this is a **re-sync**: only redo steps whose sources changed.

## 1. Find the official sources and choose the baseline
1. Lesson page: `https://course.fast.ai/Lessons/lesson<N>.html`. Ask a web-fetch subagent for
   the lesson title and every Kaggle notebook, GitHub notebook and book chapter it links.
2. Candidates:
   - Kaggle notebooks linked from the page: `kind=kaggle`, ref `owner/slug`.
   - Their copies in fastai/course22: find the matching file by title with
     `gh api repos/fastai/course22/contents --jq '.[].name'`. Numbering differs from lessons.
   - The fastbook chapter (`NN_name.ipynb`, not `clean/`).
3. Record and download each one:
   `python scripts/fetch_upstream.py add --lesson <ID> --kind <github|kaggle> --ref <ref> [--path <file>]`
   This stores the version (SHA or Kaggle version), the last-updated date, and the local copy.
4. **Baseline** = among copies of the *same* lesson notebook (Kaggle vs course22), the one with the
   most recent `updated` date. Mark it with `fetch_upstream.py set-baseline ...`.
   - The fastbook chapter is a separate track. Record it, but do not execute it unless the owner
     asks. Lesson notebooks are what the course runs.
   - Small secondary notebooks with no ML code (e.g. "Jupyter Notebook 101") are recorded, not run.
5. **Source disagreement.** Compare the code cells of the copies:
   `scripts/nb_cells.py <nb> --code-only --cells all` on each, with a diff done in a subagent or
   with difflib. Each material difference (imports, pinned packages, API calls, data source) is a
   `source-mismatch` entry.
6. If Kaggle is unavailable (no credentials), continue with the freshest accessible copy. Log an
   `open` source-mismatch ("Kaggle version unknown") and tell the owner.

## 2. Fetch
`add` already downloaded the files. Confirm with `fetch_upstream.py list --lesson <ID>`: every row must read `[ok]`.

## 3. Baseline run
`python scripts/run_notebook.py <baseline.ipynb> --label baseline --cell-timeout 900 --total-timeout 3600`
(use `run_in_background` for anything longer than ~2 min; wait for the notification).
- Read only the printed summary or `report.md`. Never Read `executed.ipynb` whole; use
  `nb_cells.py <run>/executed.ipynb --cells N --outputs` for specific cells.
- `!pip` lines are skipped automatically. A missing package is an `env` discrepancy: announce,
  install, pin it in environment.yml.
- If the run stops early, also try `--continue-on-error` to see what else breaks downstream. Treat
  those later errors as provisional.

## 4. Classify each finding
| Type | Meaning |
|---|---|
| api-break | code fails because a library API changed or was removed |
| deprecation | code runs but warns that an API will break |
| external-service | a web service changed, is rate-limited or gone (search APIs, HF Hub, …) |
| data-access | dataset URL, Kaggle competition rules, or credentials needed |
| env | our local setup differs from Kaggle: VRAM, paths, `/kaggle/input`, OS, missing package |
| result-drift | runs, but metrics or outputs differ materially from the upstream outputs |
| source-mismatch | official sources disagree with each other |

Ignore noise: one-off network blips (retry once before logging), and warnings from code that
isn't the lesson's (e.g. inside a library's own import), unless the owner will see them.

## 5. Minimal fix, verify, document
1. One minimal fix per discrepancy, in this order of preference: env (install or pin) > change the
   import or API call > change parameters (VRAM) > replace the data source.
2. Put code fixes in `docs/compat-patches/<ID>.toml` (format in `scripts/run_notebook.py`
   docstring; `id` = the compat entry's short name). Each `old` must match exactly once.
3. Re-run: `run_notebook.py <baseline> --patch docs/compat-patches/<ID>.toml --label patched`.
   Iterate until it reaches `ok`, or the remaining issue cannot be fixed (status `open`).
4. **VRAM (6 GB):** on CUDA OOM, or if peak reserved > 5.5 GB, reduce batch size, use
   `.to_fp16()`, or add gradient accumulation. Pick the least invasive option and log it as `env`.
5. **result-drift:** compare metric values from the patched run with the outputs stored in the
   upstream notebook (`nb_cells.py <upstream> --cells <i> --outputs`). Report the numbers; flag
   drift only if it is beyond run-to-run noise.
6. Document in `docs/course-compat.md`: one summary row, plus a detail entry in exactly this format:
   ```
   ### [P1-L01] duckduckgo_search → ddgs
   - Source: <URL> @ <SHA or version, date>
   - Type: external-service
   - Symptom: RatelimitException on DDGS().images(...)
   - Cause: ...
   - Fix: ... (patch id in docs/compat-patches/P1-L01.toml)
   - Verified: re-run on <date>, result ...
   - Status: resolved | workaround | open
   ```
   `resolved` requires that the patched run executed the affected cell successfully, quoting the
   run date and the observed result. Quote upstream code minimally (an import or a call), never prose.
7. Record the baseline choice (sources, dates, why) in a short paragraph under the lesson's
   heading in course-compat.md.

## 6. Scaffold the owner's lesson folder
```
python scripts/scaffold_lesson.py --part <P> --lesson <N> --slug <kebab-title> --title "<Lesson title>" \
  --link "Lesson page=<url>" --link "Kaggle: <name>=<url>" --link "course22=<url>" \
  --link "fastbook ch. <k>=<url>" --link "Questionnaire solutions=<forum url>"
```
- Slug: short kebab-case version of the course.fast.ai lesson title.
- Optional `--section` headings: the lesson's main steps, phrased in your own short words, not
  upstream prose. The scaffold has no code. Never overwrite existing files (the script refuses).

## 7. Wrap up
- Update `journal/progress.md` (lesson row, open issues, next step) and append to
  `journal/<YYYY-MM-DD>.md`.
- Report to the owner: sources table (baseline marked, versions, dates), discrepancy table
  (type, status), run summary (duration, peak VRAM), open items, and the owner's next step
  (which notebook to open, which chapter to read).
- Propose one concise commit message for the changed files (manifest, compat docs, patches,
  scaffold), with no AI attribution (root CLAUDE.md). **Do not commit.**

## Known pitfalls (update after every run)
- The Kaggle notebook version needs Kaggle credentials (docs/setup.md). The kaggle package prints
  an auth banner when they are missing; `fetch_upstream.py` then exits with a clear message.
- The GitHub API path for `resolve` uses `gh`. Without it, unauthenticated requests are limited to
  60 per hour.
