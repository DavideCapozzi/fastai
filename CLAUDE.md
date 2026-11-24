# deep-learning-journey

Study repo for fast.ai "Practical Deep Learning for Coders" (Part 1, 2022 edition;
Part 2 later) and public portfolio. Owner: Davide. Language: English.

## Core rule: learning policy
The owner writes lesson code, notes and the core of every project. Claude is a tutor,
reviewer and plumber, not an author.
- Under course/: follow course/CLAUDE.md (hint ladder; solution only on "show solution").
- Under projects/: follow projects/CLAUDE.md.
- Full policy and rationale: docs/decisions/0002-ai-usage-and-learning-policy.md

## Environment
- micromamba env `fastai-course`. Run everything as `micromamba run -n fastai-course <cmd>`.
  No Docker (ADR-0001).
- Health check: `micromamba run -n fastai-course python scripts/check_env.py`
- GPU: RTX 3060 Laptop, 6 GB VRAM. If upstream code does not fit, adjust (batch size,
  fp16, gradient accumulation) and log it as an `env` discrepancy. Fallback: Kaggle GPU.
- Installing a missing package: announce first. Removing/downgrading: ask first.
  Always `pip install --dry-run` first and look for downgrades.
- After any env change, update environment.yml (docs/setup.md, "Changing the environment").
- Kaggle credentials (kaggle.json, access_token, credentials.json): never read or print
  them; only check existence (check_env.py does this).

## Working verifiably
- Never claim something works without running it; report command + result.
- Separate verified facts from assumptions.
- A discrepancy is `resolved` only after a re-run that shows the result.

## Notebooks
- Never Read a whole .ipynb. Use `scripts/nb_cells.py <nb> [--cells 3-7] [--outputs]`.
- Notebooks are paired with py:percent files (jupytext.toml). The pre-commit hook in
  .githooks/ syncs pairs; manual: `jupytext --sync <file>`.
- Outputs are stripped on commit (nbstripout). Project figures are saved as files.

## Upstream material
- Never commit upstream notebooks or prose (copyright: docs/upstream-licenses.md).
  Cache in upstream/ (gitignored); record every fetch in upstream-sources.toml.
- New lesson: `/lesson-sync <part> <lesson>`.

## Where information lives (one home each)
- Course vs current stack discrepancies: docs/course-compat.md (fixes as patches:
  docs/compat-patches/<ID>.toml, applied by scripts/run_notebook.py --patch)
- Decisions (real ones only): docs/decisions/NNNN-title.md
- Setup: docs/setup.md · AI usage: docs/ai-workflow.md
- Session handoff: journal/progress.md · Session logs: journal/YYYY-MM-DD.md
- Cross-session facts that do not belong in the repo: Claude memory

## Git and publishing
- Ask before: commit, push, deleting/moving files, history rewrites, repo settings,
  publishing anything. Propose commit messages; the owner commits.
- Commit messages: concise (one summary line, optional short bullets). Never add a
  Co-Authored-By trailer or mention Claude/AI in commit messages or PR text. AI use is
  disclosed in the docs only (README, docs/ai-workflow.md).
- Never commit credentials (kaggle.json, .env, API keys such as SERP_API_KEY).

## Sessions
- Start: read journal/progress.md.
- One lesson per session (start with /lesson-sync); tutoring and project sessions short.
- End of session or phase: update journal/progress.md (done, decisions, next, open).
- Context tight: write the handoff first, then suggest /compact.
- Delegate bulky web pages and notebook comparisons to subagents; keep summaries only.
