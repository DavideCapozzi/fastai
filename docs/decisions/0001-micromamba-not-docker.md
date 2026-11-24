# ADR-0001: micromamba instead of Docker

- Status: accepted
- Date: 2026-11-23

## Context
The repo started with a `docker-compose.yml` and `env/Dockerfile` (JupyterLab container with
GPU passthrough). In practice the course ran in a micromamba env on WSL2. Docker Desktop's WSL
integration was off and there is no `docker` command in WSL, so the Docker files were never
used and had drifted (they still pinned `numpy<2` and listed retired packages).

Requirements: a GPU (RTX 3060 Laptop, 6 GB) inside WSL2, notebooks from VS Code, a time budget
of about 4 h/week with little setup overhead, and a setup that others can reproduce.

## Decision
Use a single micromamba env, `fastai-course`, defined by a root `environment.yml`. Conda
supplies only Python, pip and graphviz; everything else is a pinned pip package, with PyTorch
coming from the CUDA 12.4 wheel index. `scripts/check_env.py` verifies GPU, pins, imports
and services. The Docker files are deleted.

## Consequences
- One fewer layer between VS Code, the GPU and the notebooks. Nothing to rebuild.
- Reproducibility comes from `environment.yml` pins plus `check_env.py`, not from a container
  image. The OS-level CUDA driver comes from Windows.
- If a hosted or CI runtime is ever needed, Kaggle notebooks or a CPU-only CI job cover it.
  A Dockerfile can be reintroduced then, generated from `environment.yml`.
