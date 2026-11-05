#!/usr/bin/env python3
"""PreToolUse(Bash): keep commits off the default branch.

Bash(git commit:*) and Bash(git push:*) are broadly allowed, which a glob
permission cannot narrow. This enforces the two invariants that matter:
  1. never commit directly to master/main (work happens on ADO ticket branches)
  2. never force-push the default branch
"""

import json
import os
import re
import subprocess
import sys

DEFAULT_BRANCHES = {"master", "main"}

GIT_COMMIT = re.compile(r"(?:^|[;&|(]|\n)\s*(?:\w+=\S+\s+)*git\s+(?:-\S+\s+)*commit\b")
GIT_PUSH = re.compile(r"(?:^|[;&|(]|\n)\s*(?:\w+=\S+\s+)*git\s+(?:-\S+\s+)*push\b")
FORCE = re.compile(r"(?:^|\s)(?:--force(?!-with-lease)|-f)(?:\s|$)")
TARGET_DIR = re.compile(r"^\s*cd\s+(?P<dir>\S+)\s*&&|git\s+-C\s+(?P<gitdir>\S+)")


def block(reason: str) -> None:
    """Hard-block via exit code 2.

    `git commit` and `git push` are both on the allow list, and only an exit-2
    block is documented to take precedence over an allow rule. Returning JSON with
    permissionDecision "deny" would leave this guard inert for exactly the commands
    it exists to catch.
    """
    print(reason, file=sys.stderr)
    sys.exit(2)


def target_dir(command: str, cwd: str) -> str:
    match = TARGET_DIR.search(command)
    if not match:
        return cwd
    raw = (match.group("dir") or match.group("gitdir")).strip("'\"")
    return os.path.join(cwd, os.path.expanduser(os.path.expandvars(raw)))


def current_branch(cwd: str) -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=cwd or None,
            capture_output=True,
            text=True,
            timeout=5,
        )
    except (OSError, subprocess.SubprocessError):
        return ""
    return result.stdout.strip() if result.returncode == 0 else ""


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        sys.exit(0)

    command = (payload.get("tool_input") or {}).get("command") or ""
    if "git" not in command:
        sys.exit(0)

    cwd = payload.get("cwd") or ""
    is_commit = bool(GIT_COMMIT.search(command))
    is_push = bool(GIT_PUSH.search(command))
    if not (is_commit or is_push):
        sys.exit(0)

    branch = current_branch(target_dir(command, cwd))

    if is_commit and branch in DEFAULT_BRANCHES:
        block(
            f"Refusing to commit directly to {branch}. Create a branch named after the "
            "ADO ticket first (see the `worktree` skill), then commit there."
        )

    if is_push and FORCE.search(command) and branch in DEFAULT_BRANCHES:
        block(f"Refusing to force-push {branch}.")

    sys.exit(0)


if __name__ == "__main__":
    main()
