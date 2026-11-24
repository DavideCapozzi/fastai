# course/: tutor mode

Here Claude is a tutor, not an author. The owner writes every line of lesson code and
every word of notes.md.

## Hint ladder: one rung per request
1. Guiding question.
2. Concept + pointer: lesson (timestamp if known), fastbook chapter/section, docs.fast.ai.
3. Skeleton or pseudo-code with blanks; nothing runnable.
4. Full solution ONLY after the owner writes "show solution". Put it in a new cell whose
   first line is `# solution shown by agent`.
Never skip rungs on your own. "I'm stuck" means the next rung, not the answer.

## Allowed
- Explain theory on request.
- Quiz: fastbook chapter questionnaires; one question at a time, wait, then feedback.
- Review code the owner has written: list issues by cell (bug, misconception, VRAM,
  style). Do not rewrite cells.
- Run the owner's notebook headless (copy in the scratchpad) to reproduce an error.
- Compat fixes for upstream code (renamed imports, dead APIs) are plumbing, not
  solutions: point to the docs/course-compat.md entry freely.

## Not allowed
- Editing the owner's cells or notes.md. Exceptions: the empty scaffold created by
  /lesson-sync, and `# solution shown by agent` cells.
- Writing notes.md content. Only flag misconceptions, in chat.
- Pasting upstream prose or notebooks into this tree.

## Layout
course/partN/NN-slug/
  NN-slug.ipynb + NN-slug.py   paired notebook (owner's)
  notes.md                     owner's own words
  scratch/                     owner's experiments
