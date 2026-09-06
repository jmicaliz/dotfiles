# User-Level CLAUDE.md

## Claude Rules

Always follow the following:

- BE CONCISE. Nothing too verbose. Outline and straight to the point.
- Avoid em dash usage

## Python projects

For any Python work — existing repos or new projects — follow the `python-conventions` skill (uv, pyproject.toml, Makefile targets, Ruff, mypy, pytest, Click, loguru).

## Code comments

Default to **zero** comments. Naming carries the meaning; a comment is an admission the code failed to.

Write a comment only when it explains a *why* the code cannot:

- A business rule or spec constraint that looks arbitrary otherwise.
- A workaround for an upstream bug or platform quirk (name it, link it).
- A non-obvious invariant or ordering dependency that will break if someone reorders.

Never:

- Restate the line below it (`# increment counter`, `# loop over rows`).
- Narrate the edit for the reviewer (`# changed to use X`, `# new`, `# added for TPID support`). That belongs in the PR body, not the source.
- Add banner or section dividers (`# ---- Helpers ----`).
- Add a `TODO` unless I asked for one.

Docstrings: one line, imperative, only when the name plus signature genuinely leave the purpose ambiguous. No `Args:` / `Returns:` / `Raises:` blocks unless a parameter has a non-obvious contract. Types are in the signature already, do not restate them.

Length cap: one line per comment. If it needs a paragraph, it is documentation, put it in the README or the PR.
