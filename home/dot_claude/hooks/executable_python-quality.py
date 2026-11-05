#!/usr/bin/env python3
"""PostToolUse(Edit|Write): format and lint edited Python using the file's own toolchain.

Repos here mix toolchains -- tools/dataset_codegen is uv + Ruff + mypy, while the
r37_ingest_core root is conda + pylint. Rather than hardcode paths, walk up from the
edited file to the nearest pyproject.toml and dispatch on what that project declares:

  [tool.ruff]   -> uv run ruff format + ruff check --fix   (autofix, then report)
  [tool.pylint] -> pylint --errors-only                    (report only, best effort)

Anything else, or a missing tool, is a silent no-op. A formatter hook must never be
the reason an edit appears to fail.
"""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

TIMEOUT = 120
EXTRA_PATH = ("/opt/homebrew/bin", "/usr/local/bin", str(Path.home() / ".local/bin"))


def tool(name: str) -> str | None:
    path = os.pathsep.join((*EXTRA_PATH, os.environ.get("PATH", "")))
    return shutil.which(name, path=path)


def run(args: list[str], cwd: Path) -> tuple[int, str]:
    try:
        result = subprocess.run(
            args, cwd=cwd, capture_output=True, text=True, timeout=TIMEOUT
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return 1, f"{args[0]} could not run: {exc}"
    return result.returncode, (result.stdout + result.stderr).strip()


def nearest_project(path: Path) -> tuple[Path, str] | None:
    for parent in path.parents:
        pyproject = parent / "pyproject.toml"
        if not pyproject.is_file():
            continue
        try:
            text = pyproject.read_text(encoding="utf-8")
        except OSError:
            return None
        if "[tool.ruff" in text:
            return parent, "ruff"
        if "[tool.pylint" in text:
            return parent, "pylint"
        return parent, "unknown"
    return None


def report(message: str) -> None:
    json.dump(
        {
            "hookSpecificOutput": {
                "hookEventName": "PostToolUse",
                "additionalContext": message,
            }
        },
        sys.stdout,
    )
    sys.exit(0)


def handle_ruff(project: Path, target: Path) -> None:
    uv = tool("uv")
    if not uv:
        sys.exit(0)

    rel = str(target)
    before = target.read_bytes() if target.is_file() else b""

    run([uv, "run", "ruff", "format", rel], project)
    code, output = run([uv, "run", "ruff", "check", "--fix", rel], project)

    after = target.read_bytes() if target.is_file() else b""
    reformatted = before != after

    notes = []
    if reformatted:
        notes.append(
            f"Ruff reformatted/autofixed {target.name}. Re-read it before editing again "
            "so your view matches disk."
        )
    if code != 0 and output:
        notes.append(f"Ruff reports remaining issues that need a manual fix:\n{output}")

    if notes:
        report("\n\n".join(notes))
    sys.exit(0)


def handle_pylint(project: Path, target: Path) -> None:
    pylint = tool("pylint")
    if not pylint:
        # Not installed in this environment (repo builds via conda); nothing to do.
        sys.exit(0)

    code, output = run([pylint, "--errors-only", str(target)], project)
    if code != 0 and output:
        report(f"pylint errors in {target.name}:\n{output}")
    sys.exit(0)


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        sys.exit(0)

    raw = (payload.get("tool_input") or {}).get("file_path") or ""
    if not raw.endswith(".py"):
        sys.exit(0)

    target = Path(raw)
    if not target.is_absolute():
        target = Path(payload.get("cwd") or ".") / target
    if not target.is_file():
        sys.exit(0)

    found = nearest_project(target.resolve())
    if not found:
        sys.exit(0)

    project, kind = found
    if kind == "ruff":
        handle_ruff(project, target.resolve())
    elif kind == "pylint":
        handle_pylint(project, target.resolve())
    sys.exit(0)


if __name__ == "__main__":
    main()
