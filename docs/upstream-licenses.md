# Upstream licenses

Checked 2026-11-23 with `gh api repos/<repo>` and by reading each repo's LICENSE and README.
This is a reading of the published terms, not legal advice.

| Source | License | What it means here |
|---|---|---|
| [fastai/course22](https://github.com/fastai/course22) (Part 1 notebooks) | **None declared** (no LICENSE file; README silent) | Default copyright: all rights reserved. Not redistributed here. |
| Kaggle notebooks by Jeremy Howard (linked from course.fast.ai) | No license stated on the notebooks | Same: not redistributed here. |
| [fastai/fastbook](https://github.com/fastai/fastbook) | Code: **GPL-3.0**. Prose (incl. all markdown cells): **no redistribution or change of format**; private copies/forks only; no commercial use | No upstream prose here. Substantial fastbook code copied into this repo would have to stay GPL-3.0. |
| [fastai/fastai](https://github.com/fastai/fastai) | Apache-2.0 | Library, used as a dependency. |
| [fastai/course22p2](https://github.com/fastai/course22p2) (Part 2) | Apache-2.0 | Relevant for Part 2. |

## Rules that follow

1. Upstream notebooks are cached in `upstream/` (gitignored) and recorded in
   `upstream-sources.toml` (URL, commit SHA or Kaggle version, fetch date). They are never committed.
2. Lesson notebooks in `course/` contain only my own code and prose, plus links to upstream.
   Short API calls that follow the course (for example `vision_learner(dls, resnet18)`) are normal
   library usage, not copied material.
3. `docs/course-compat.md` quotes upstream code only as minimal snippets (an import line,
   a function call) where needed to describe a discrepancy, with a link to the source.
4. This repo's own content is MIT-licensed (see `LICENSE`). That license does not cover
   upstream material.
