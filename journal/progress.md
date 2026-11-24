# Progress (session handoff)

Read this first when resuming. Updated: 2026-11-24, Phase 4 preparations done.

## Bootstrap phases
| Phase | Status |
|---|---|
| 0 Audit | done |
| 1 Proposal | approved (all recommended defaults) |
| 2 Environment | done: real env 10 OK / 1 WARN (no Kaggle creds) / 0 FAIL; fresh rebuild from environment.yml 0 FAIL |
| 3 Workflow (lesson-sync skill, scripts, projects/_template) | done; scripts tested, skill untested until Phase 4 |
| 4 Pilot: /lesson-sync 1 1 | next; all prerequisites met |
| 5 Publish prep (README, LICENSE, squash, rename, push) | todo; every step needs explicit OK |
| 6 Roadmap of mini-projects | todo (proposal only) |

## Decisions
- Repo name `deep-learning-journey`, MIT license.
- Commits: concise messages, no AI attribution; disclosure lives in README + docs/ai-workflow.md
  (ADR-0002 amended 2026-11-24).
- Squash plan: local backup branch + bundle; one initial commit; delete and recreate the GitHub repo rather than
  force-push (purges the copyrighted notebook from GitHub). Each step needs confirmation.
- Image search: `ddgs` by default, SerpAPI (fastbook ch. 2 since 2026-09) as fallback.
- Env: micromamba only (ADR-0001). AI policy: ADR-0002.
- Editor: Cursor over WSL (VS Code-compatible; `.cursor/rules/` mirrors the learning policy).
  JupyterLab in the browser is the alternative (verified to start, with jupytext loaded).

## Uncommitted working tree (nothing committed yet, by design until Phase 5)
- Staged: deletions of the Docker/env files, renames of exercise.ipynb and environment.yml.
- New: CLAUDE.md x3, .claude/skills/lesson-sync/, upstream-sources.toml, projects/_template/,
  scripts/{fetch_upstream,run_notebook,scaffold_lesson}.py, docs/, scripts/check_env.py, scripts/nb_cells.py, .githooks/,
  .vscode/ (settings, tasks, extensions), .cursor/rules/, jupytext.toml, .gitattributes, journal/.
- Local git config: nbstripout filter installed, `core.hooksPath=.githooks`.

## Open issues
- Lesson 1 preliminary observations (unverified, for the Phase 4 pilot):
  - ddgs 9.16 caps image results at ~35 per query (lesson asks for 200).
  - ddgs `backend="duckduckgo"` errors; `auto` falls back to Bing.
  - **Which source is newer is unresolved.** The Kaggle bird notebook's lastRunTime is
    2024-10-05 (from `kaggle kernels list`); the course22 copy's last commit is 2024-10-08.
    The local Kaggle copy (2025-12-30) pins `duckduckgo_search>=6.2`, but course22 does not.
    Compare the Kaggle version number and content in the pilot.
- Owner to confirm in Cursor: Python + Jupyter extensions installed on the WSL side, and
  the kernel picker shows fastai-course.
- PySide6 stays in the env (required by conda's `matplotlib` package); spacy stays (fastai needs it).

## Next step
Phase 4: run `/lesson-sync 1 1` (start by reading this file). Fix the skill where it
falls short and report what changed.
