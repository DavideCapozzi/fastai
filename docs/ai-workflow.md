# How I use AI in this repo

I use [Claude Code](https://claude.com/claude-code), an AI coding agent, as a **tutor, reviewer
and plumber, not as an author** of my learning code. The policy and its rationale are in
[ADR-0002](decisions/0002-ai-usage-and-learning-policy.md). This page describes how it works
in practice.

## Who writes what

| Area | Me | Agent |
|---|---|---|
| Lesson notebooks (`course/`) | all code | hints (hint ladder), theory, quizzes, code review |
| Lesson notes (`notes.md`) | all text | flags misconceptions only |
| Projects (`projects/`): framing, data, model, evaluation, core code | ✔ | questions, options, review |
| Projects: env, download scripts, CI, tests, Gradio wrappers | review | ✔ |
| Course compatibility (`docs/course-compat.md`, `/lesson-sync`) | review, approve | ✔ |
| Environment, tooling, these docs' structure | review, approve | ✔ |

**The hint ladder.** When I'm stuck, the agent gives (1) a guiding question, then (2) the concept
and where to read about it, then (3) a skeleton, and only if I write "show solution", (4) the
solution. That cell is marked `# solution shown by agent`.

**Disclosure.** AI involvement is stated here and in the README, not in commit messages.
The environment, scripts, `/lesson-sync` workflow and course-compatibility notes were built
by the agent under my direction and review. In my lesson notebooks, the only agent-written
cells are those marked `# solution shown by agent`.

## Workflow

1. **New lesson:** `/lesson-sync <part> <lesson>`
   ([skill](../.claude/skills/lesson-sync/SKILL.md)). The agent finds the official sources (Kaggle
   notebook, fastai/course22, fastbook) and takes the most recently updated one as the baseline.
   It runs that notebook headless on my GPU, fixes what no longer works on today's library versions,
   documents each fix in [course-compat.md](course-compat.md) only after a verified re-run, and
   creates an empty notebook for me.
2. **Study session:** I watch the lesson, write my notebook and `notes.md`, and ask the agent
   for hints, explanations or a quiz.
3. **Review:** the agent reviews my code and notes and points out issues without rewriting them.
4. **Mini-project** every 1–2 lessons, from [projects/_template](../projects/_template/README.md).

## Tooling that keeps it cheap
- `CLAUDE.md` files hold the rules: root (general), `course/` (tutor mode), `projects/`.
- `journal/progress.md` is the hand-off between sessions; each session starts by reading it.
- Scripts make the repetitive parts deterministic: `check_env.py`, `fetch_upstream.py`,
  `run_notebook.py`, `scaffold_lesson.py`, and `nb_cells.py` (reads notebooks without base64 noise).
- Upstream course material stays in a gitignored `upstream/` folder
  ([licenses](upstream-licenses.md)); only a manifest with versions is committed.
