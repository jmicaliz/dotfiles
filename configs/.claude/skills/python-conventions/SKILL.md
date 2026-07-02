---
name: python-conventions
description: Default conventions for Python projects — uv for environments/packaging, pyproject.toml (no requirements.txt), Makefile targets for tasks, Ruff, mypy, pytest, Click, loguru. Use when working in any Python project (presence of pyproject.toml or .py files) or when setting up a new Python project, unless the repo specifies otherwise.
---

# Python project conventions

Default conventions for all Python projects unless a repo says otherwise.

There is a personal starter template (see any existing repo's `pyproject.toml`).
When working in a repo that already has a `pyproject.toml`, **adapt to it** rather
than replacing it; the notes below are the defaults for new projects.

## Environment & packaging
- Use **uv** for everything: environments, dependencies, locking, and Python versions.
- Project metadata and dependencies live in **pyproject.toml** (PEP 621). Do **not** create `requirements.txt`.
- Common commands:
  - `uv add <pkg>` / `uv add --dev <pkg>` — add runtime / dev dependencies.
  - `uv sync` — create/update the environment from the lockfile.
  - `uv run <cmd>` — run inside the project environment (e.g. `uv run python -m pkg`, `uv run pytest`).
- Commit `uv.lock`.

## Task commands — use the Makefile, not raw uv
- Run tests, formatting, type checking, and validation through **Makefile targets**
  (`make test`, `make format`, `make typecheck`, `make check`, `make validate`),
  **not** ad-hoc `uv run ...` commands.
- The Makefile is the single source of truth for how to run these tasks. If a task
  has no target yet, **add one to the Makefile** (wrapping the underlying `uv run ...`)
  rather than running the raw command.
- Raw `uv` is still correct for dependency management (`uv add`, `uv sync`, `uv lock`).

## Linting & formatting
- Use **Ruff** for both linting and formatting (via `make format`).
- Line length **120**; configure Ruff in `pyproject.toml` under `[tool.ruff]`.
- Use **yamllint** for YAML, and **pre-commit** hooks.

## Type checking
- Use **mypy** (via `make typecheck`). Configure under `[tool.mypy]` in `pyproject.toml`.
- Write type hints on public functions; aim to keep mypy clean.

## Testing
- Use **pytest** (via `make test`).
- Unit testing for most code, including mocks with sample (NON-PHI!) data

## CLI
- Use Click for CLI

## Logging
- Use **loguru** for logging

## Before considering a change done
- Run `make check` (format + typecheck + test) and ensure it passes.
