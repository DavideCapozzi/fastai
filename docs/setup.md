# Setup

Local-first on WSL2 Ubuntu with an RTX 3060 Laptop GPU (6 GB VRAM). Runs that do not fit
go to Kaggle GPUs. Why micromamba and not Docker: [ADR-0001](decisions/0001-micromamba-not-docker.md).

## 1. Create the environment

Prerequisites: [micromamba](https://mamba.readthedocs.io/en/latest/installation/micromamba-installation.html),
an NVIDIA driver on the Windows side (`nvidia-smi` must work inside WSL).

```bash
micromamba env create -f environment.yml
micromamba run -n fastai-course pip install --no-deps fastbook==0.0.29
micromamba run -n fastai-course python scripts/check_env.py
```

fastbook is installed without dependencies because it pins `ipywidgets<8` for no functional
reason; see [course-compat](course-compat.md#env-fastbook-ipywidgets-pin).

## 2. Repo tooling (once per clone)

```bash
micromamba run -n fastai-course nbstripout --install --attributes .gitattributes
git config core.hooksPath .githooks
```

- **nbstripout** removes notebook outputs when files are staged; the working copy keeps them.
- **jupytext** pairs every notebook with a `py:percent` file (`jupytext.toml`). The
  pre-commit hook syncs pairs under `course/` and `projects/`. You can also sync by hand
  with the VS Code task "Sync jupytext pair" or `jupytext --sync <file>`.

## 3. Editor

**Cursor (main editor).** Cursor is a VS Code fork and reads the same `.vscode/` settings.
1. From WSL: `cd ~/fastai && cursor .`. The bottom-left corner should show `WSL: Ubuntu`.
2. Accept the recommended extensions (`.vscode/extensions.json`): Python, Jupyter and
   Claude Code. They install on the WSL side.
3. `.vscode/settings.json` points the interpreter at `~/micromamba/envs/fastai-course/bin/python`.
   For notebooks, pick that interpreter from the kernel picker (top right).
4. You can open either the `.ipynb` (notebook UI) or the `.py` (run `# %%` cells with
   Shift+Enter). Run the health check with Ctrl+Shift+P → "Tasks: Run Task" → "Check environment".
5. **Learning policy:** `.cursor/rules/learning-policy.mdc` makes Cursor's AI follow the same rules
   as Claude Code. Cursor **Tab** autocomplete is not covered by rules, and it writes code for
   you. Turn it off while working in `course/`: Cursor Settings → Tab, or the status-bar toggle.

**JupyterLab in the browser (alternative, closest to the old Docker setup).**
```bash
cd ~/fastai && micromamba run -n fastai-course jupyter lab --no-browser
```
Open the printed `http://localhost:8888/lab?token=...` URL in a Windows browser. WSL2 forwards
localhost. In JupyterLab, jupytext updates the paired `.py` on every save.

VS Code also works with the same steps (`code .`).

## 4. Credentials (never committed)

| Service | What | Where | Permissions |
|---|---|---|---|
| Kaggle (legacy key) | `kaggle.json` from kaggle.com → Settings → API | `~/.config/kaggle/kaggle.json` | `chmod 600` |
| Kaggle (new token) | API token | `KAGGLE_API_TOKEN` env var or `~/.kaggle/access_token` | `chmod 600` |
| SerpAPI (optional) | API key, used only by the fastbook ch. 2 image-search path | `SERP_API_KEY` env var | n/a |

Use **one** Kaggle method. kaggle ≥2 reads `kaggle.json` from `~/.kaggle/` if that directory
exists, otherwise from `~/.config/kaggle/`. Creating `~/.kaggle/access_token` therefore
makes a `kaggle.json` in `~/.config/kaggle/` invisible. `check_env.py` warns about that case.
It only checks that the files exist and their permissions; it never reads them.

## Changing the environment

1. `pip install --dry-run <pkg>` and look for downgrades of existing packages.
2. Install. Then run `pip check` and `scripts/check_env.py`.
3. Add or update the `==` pin in `environment.yml`. check_env compares installed versions
   against those pins and warns about drift.
4. If the change works around course code, add an entry to `course-compat.md`.

## Troubleshooting

- **`ImportError: cannot import name ... from 'kagglesdk' (unknown location)`** after
  upgrading kaggle 1.7 → 2.x: kaggle 1.7 shipped its own copy of `kagglesdk`, and
  uninstalling it deletes files that belong to the separately installed `kagglesdk`. Fix:
  `pip install --force-reinstall --no-deps kagglesdk==<pinned version>`.
- **`import kaggle` prints "Authentication required"**: no credentials yet. The import still
  succeeds.
- **CUDA not available**: run `nvidia-smi` in WSL. Update the Windows driver; do not install
  a CUDA toolkit inside WSL.
