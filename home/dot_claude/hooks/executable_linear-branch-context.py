#!/usr/bin/env python3
"""SessionStart: surface the Linear issue implied by the current branch name.

Branches are named after their Linear issue (e.g. engn-142-databricks-runs, see the
`worktree` skill), so the issue ID is already on disk. Injecting it up front means it
survives compaction and is available to /create-pr and /push without being re-derived.
"""

import json
import re
import subprocess
import sys

ISSUE = re.compile(r"^(?:[\w.-]+/)?(?P<team>[a-z][a-z0-9]{1,9})-(?P<number>\d+)(?:[-_/]|$)", re.IGNORECASE)


def git(cwd: str, *args: str) -> str:
    try:
        result = subprocess.run(
            ["git", *args], cwd=cwd or None, capture_output=True, text=True, timeout=5
        )
    except (OSError, subprocess.SubprocessError):
        return ""
    return result.stdout.strip() if result.returncode == 0 else ""


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        sys.exit(0)

    cwd = payload.get("cwd") or ""
    branch = git(cwd, "rev-parse", "--abbrev-ref", "HEAD")
    if not branch or branch == "HEAD":
        sys.exit(0)

    lines = [f"Current branch: {branch}"]

    match = ISSUE.match(branch)
    if match:
        issue = f"{match.group('team').upper()}-{match.group('number')}"
        lines.append(f"Linear issue: {issue} (inferred from the branch name)")
        lines.append("- Look it up with `mcp__linear__get_issue` if details are needed.")
        lines.append(f"- Use {issue} for PR titles and Linear updates rather than re-deriving it.")
    else:
        lines.append("Branch name carries no Linear issue ID; ask before assuming one for PRs.")

    dirty = git(cwd, "status", "--porcelain")
    if dirty:
        count = len([line for line in dirty.splitlines() if line.strip()])
        lines.append(f"Uncommitted changes: {count} path(s).")

    json.dump(
        {
            "hookSpecificOutput": {
                "hookEventName": "SessionStart",
                "additionalContext": "\n".join(lines),
            }
        },
        sys.stdout,
    )
    sys.exit(0)


if __name__ == "__main__":
    main()
