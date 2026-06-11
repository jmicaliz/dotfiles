# User-Level CLAUDE.md

## Python projects

Default conventions for all Python projects unless a repo says otherwise.

### Environment & packaging
- Use **uv** for everything: environments, dependencies, locking, and Python versions.
- Project metadata and dependencies live in **pyproject.toml** (PEP 621). Do **not** create `requirements.txt`.
- Common commands:
  - `uv add <pkg>` / `uv add --dev <pkg>` — add runtime / dev dependencies.
  - `uv sync` — create/update the environment from the lockfile.
  - `uv run <cmd>` — run inside the project environment (e.g. `uv run python -m pkg`, `uv run pytest`).
- Commit `uv.lock`.

### Linting & formatting
- Use **Ruff** for both linting and formatting (`uv run ruff check` / `uv run ruff format`).
- Line length **120**; configure Ruff in `pyproject.toml` under `[tool.ruff]`.
- Use **yamllint** for YAML, and **pre-commit** hooks.

### Type checking
- Use **mypy** (`uv run mypy`). Configure under `[tool.mypy]` in `pyproject.toml`.
- Write type hints on public functions; aim to keep mypy clean.

### Testing
- Use **pytest** (`uv run pytest`).

### CLI
- Use Click for CLI

### Logging
- Use **loguru** for logging 

### Before considering a change done
- Run `uv run ruff format`, `uv run ruff check`, `uv run mypy`, and `uv run pytest` and ensure they pass.
