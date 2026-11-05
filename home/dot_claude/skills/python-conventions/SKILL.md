---
name: python-conventions
description: Default conventions for Python projects: uv for environments/packaging, pyproject.toml (no requirements.txt), Makefile targets for tasks, Ruff, mypy, pytest, Click, loguru. Use when working in any Python project (presence of pyproject.toml or .py files) or when setting up a new Python project, unless the repo specifies otherwise.
---

# Python project conventions

Default conventions for all Python projects unless a repo says otherwise.

When working in a repo that already has a `pyproject.toml`, **adapt to it** rather
than replacing it; the notes below are the defaults for new projects.

## Environment & packaging

- Use **uv** for everything: environments, dependencies, locking, and Python versions.
- Project metadata and dependencies live in **pyproject.toml** (PEP 621). Do **not** create `requirements.txt`.
- Commit `uv.lock`.

## Project structure

- src layout: code in `src/<pkg>/`, tests in `tests/` at the project root, one `test_<module>.py` per module.
- Build backend is hatchling. Set `requires-python` in `pyproject.toml` and pin the interpreter in `.python-version`.
- CLI projects expose one Click group as the entry point under `[project.scripts]`, with one module per command area and each registered on the group.
- Non-Python assets a package needs at runtime live inside `src/<pkg>/` so the wheel ships them. Read them with `importlib.resources`, not by repo-relative path.
- In a monorepo, shared Ruff and mypy config live at the root and each project extends them. Do not duplicate settings per project.

## Task commands

- The Makefile is the single source of truth for tests, formatting, type checking, and
  validation (`make test`, `make format`, `make typecheck`, `make check`, `make validate`).
  If a task has no target yet, add one wrapping the underlying `uv run ...` command.

## Linting & formatting

- Use **Ruff** for both linting and formatting (via `make format`).
- Line length **120**. Configure Ruff in `pyproject.toml` under `[tool.ruff]`, or extend the shared root config in a monorepo.
- Use **yamllint** for YAML, and **pre-commit** hooks.

## Type checking

- Use **mypy** (via `make typecheck`). Configure under `[tool.mypy]` in `pyproject.toml`, or use the shared root config in a monorepo.
- Write type hints on public functions. mypy passes with no errors.

## Testing

- Use **pytest** (via `make test`).
- Unit tests for most code. Fixtures and mocks use synthetic data, never PHI or PII.

## Libraries

- Click for CLIs, loguru for logging.

## Before considering a change done

- Run `make check` (format + typecheck + test) and ensure it passes.
