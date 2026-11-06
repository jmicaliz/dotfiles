#!/usr/bin/env python3
"""PreToolUse(Bash): keep commits off the default branch.

Bash(git commit:*) and Bash(git push:*) are broadly allowed, which a glob
permission cannot narrow. This enforces the two invariants that matter:
  1. never commit directly to master/main (work happens on a branch)
  2. never force-push the default branch
A commit chained with && after `git switch -c`/`git checkout -b` counts as
being on the new branch, since HEAD is read before the command runs.
"""

import json
import os
import re
import subprocess
import sys

DEFAULT_BRANCHES = {"master", "main"}

GIT_COMMIT = re.compile(r"(?:^|[;&|(]|\n)\s*(?:\w+=\S+\s+)*git\s+(?:-\S+\s+)*commit\b")
GIT_PUSH = re.compile(r"(?:^|[;&|(]|\n)\s*(?:\w+=\S+\s+)*git\s+(?:-\S+\s+)*push\b")
GIT_NEW_BRANCH = re.compile(
    r"(?:^|[;&|(]|\n)\s*(?:\w+=\S+\s+)*git\s+(?:-\S+\s+)*"
    r"(?:switch\s+(?:-c|-C|--create|--force-create)|checkout\s+(?:-b|-B))"
    r"\s+(?P<branch>[^\s;&|)]+)"
)
UNCHAINED = re.compile(r";|\n|\|\||(?<!\|)\|(?!\|)")
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


def branch_at_commit(command: str, commit_end: int, branch: str) -> str:
    """Return the branch a commit lands on when chained with && after creating one."""
    created = [m for m in GIT_NEW_BRANCH.finditer(command) if m.end() <= commit_end]
    if not created:
        return branch
    last = created[-1]
    if UNCHAINED.search(command[last.end() : commit_end]):
        return branch
    return last.group("branch").strip("'\"")


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        sys.exit(0)

    command = (payload.get("tool_input") or {}).get("command") or ""
    if "git" not in command:
        sys.exit(0)

    cwd = payload.get("cwd") or ""
    commit = GIT_COMMIT.search(command)
    is_commit = bool(commit)
    is_push = bool(GIT_PUSH.search(command))
    if not (is_commit or is_push):
        sys.exit(0)

    branch = current_branch(target_dir(command, cwd))

    commit_branch = branch_at_commit(command, commit.end(), branch) if commit else ""
    if commit_branch in DEFAULT_BRANCHES:
        block(
            f"Refusing to commit directly to {commit_branch}. "
            "Create a branch first, then commit there."
        )

    if is_push and FORCE.search(command) and branch in DEFAULT_BRANCHES:
        block(f"Refusing to force-push {branch}.")

    sys.exit(0)


if __name__ == "__main__":
    main()
