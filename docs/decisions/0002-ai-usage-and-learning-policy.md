# ADR-0002: AI usage and learning policy

- Status: accepted
- Date: 2026-11-23 (amended 2026-11-24: disclosure moved from commit trailers to docs)

## Context
I use an AI coding agent (Claude Code) in this repo. The repo has two purposes: to learn deep
learning properly, and to show recruiters what I can do. Both fail if the agent writes the
learning code or the core of the projects. I would not learn it, and the portfolio would
misrepresent my skills. The agent is still very useful for environment work, keeping the course
code running on today's stack, reviewing, and explaining.

## Decision

**Lessons (`course/`): the agent is a tutor, not an author.**
- I write all lesson code. When I am stuck, the agent climbs a hint ladder one rung at a time:
  (1) a guiding question, (2) the concept plus a pointer to the lesson, book chapter or docs,
  (3) a skeleton or pseudo-code, (4) the full solution, **only** when I write "show solution".
  Such a cell is marked `# solution shown by agent`.
- The agent explains theory on request, quizzes me (fastbook questionnaires), and reviews my
  code after I write it without rewriting my cells.
- `notes.md` for each lesson is in my own words. The agent only flags misconceptions.

**Projects (`projects/`):** I own the modelling, data and evaluation decisions and the core
code. The agent may write plumbing (environment, CI, tests, Gradio wrappers, download scripts,
scaffolding) and reviews everything.

**Course compatibility:** keeping upstream course code running on today's stack (the
`/lesson-sync` workflow, `docs/course-compat.md`) is agent work that I review. It is
plumbing, not learning content.

**Disclosure:** AI involvement is disclosed in the documentation (the README's "How I use AI"
section and `docs/ai-workflow.md`), not in commit metadata. Commit messages are concise, describe
the change, and carry no AI attribution. Splitting commits by author would be ceremony: what
matters to a reader is a clear statement of who did what, and whether I can explain all of it.

## Consequences
- Progress is slower than letting the agent write everything. That is deliberate.
- Every lesson notebook cell without the `# solution shown by agent` marker is my own work.
  Tooling and compatibility docs are agent-built under my direction, as the README states.
- The rules live in `CLAUDE.md`, `course/CLAUDE.md` and `projects/CLAUDE.md`, so the agent
  loads them automatically. The README summarises them for readers.
