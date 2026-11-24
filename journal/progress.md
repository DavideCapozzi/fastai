# Progress (session handoff)

Read this first when resuming. Updated: 2026-11-24, Phase 4 pilot run done; owner's turn on lesson 1.

## Bootstrap phases
| Phase | Status |
|---|---|
| 0 Audit | done |
| 1 Proposal | approved (all recommended defaults) |
| 2 Environment | done: real env 10 OK / 1 WARN (no Kaggle creds) / 0 FAIL; fresh rebuild from environment.yml 0 FAIL |
| 3 Workflow (lesson-sync skill, scripts, projects/_template) | done; scripts tested, skill untested until Phase 4 |
| 4 Pilot: /lesson-sync 1 1 | done 2026-11-24: baseline Kaggle v10 runs OK with 2 patches (docs/compat-patches/P1-L01.toml); scaffold in course/part1/01-getting-started/ |
| Lesson 1 (owner) | next: owner works through the scaffold |
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

## Git state
- Setup committed and pushed by the owner on 2026-11-24: `3401c0a` "Set up micromamba env,
  lesson-sync tooling and docs" on DavideCapozzi/fastai (main in sync with origin).
  Old history (with the copied upstream notebook) remains until the Phase 5 squash/recreate.
- Local git config: nbstripout filter installed, `core.hooksPath=.githooks`.

## Open issues
- P1-L01 findings are in docs/course-compat.md (4 entries). Resolved in the pilot: Kaggle v10
  (2026-11-21) is newer than course22 (2024-10-08). Open caveat: ddgs caps at ~35 images per
  query, worked around with 4 query variants (workaround, not upstream-identical data).
- ddgs `backend="duckduckgo"` errors; `auto` falls back to Bing (unverified in the pilot run).
- Cursor setup confirmed by owner on 2026-11-24 (extensions, kernel, Tab off for course/).
- PySide6 stays in the env (required by conda's `matplotlib` package); spacy stays (fastai needs it).

## Remaining phases: specs from the owner's bootstrap brief
**Phase 4: Pilot.** Run `/lesson-sync 1 1` end to end. Do NOT solve the lesson for the owner
(scaffold only). Fix the skill and scripts where they fall short, and report what changed.
Then update this file.

**Phase 5: Publish prep.**
- README showcase: who the owner is in one line, what the repo is, how it is organised, the
  AI usage policy ("How I use AI", the disclosure home together with docs/ai-workflow.md),
  a progress table, links to projects and compat notes.
- Add LICENSE (MIT). Prepare the GitHub description and topics.
- Then, **each step only after the owner's explicit confirmation**: squash the history (local
  backup branch + bundle first), rename/recreate the repo as `deep-learning-journey`,
  update the remote, push.

**Phase 6: Roadmap (proposal only).** Map the Part 1 lessons to 4–5 mini-projects on
industry-valued topics with public data, varied across vision, NLP, tabular, recommendation
and from-scratch work. For each: dataset + license, goal, metric, the lesson it builds on, whether it
fits in 6 GB VRAM, an effort estimate at ~4 h/week, and flagship potential. Mark the two
strongest flagship candidates. (Owner advice, 2026-11-24: flagship projects may get their own
repos, pinned on the GitHub profile.)

**Standing working style:** concise output; for each phase, say what was done, what was
verified (command + result) and what remains. Ask before deleting/moving files, removing or
downgrading packages, committing, pushing or publishing. After the bootstrap: one lesson per
session, started with `/lesson-sync`; tutoring and project sessions are separate and short.

## Next step
Owner: open course/part1/01-getting-started/01-getting-started.ipynb, read fastbook ch. 1,
build the bird classifier. Then Phase 5 (publish prep), on the owner's go-ahead.
