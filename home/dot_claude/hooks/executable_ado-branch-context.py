#!/usr/bin/env python3
"""SessionStart: surface the ADO ticket implied by the current branch name.

Branches are named after their ADO work item (e.g. 382692-automate-foundry-ingestion),
so the ticket ID is already on disk. Injecting it up front means it survives compaction
and is available to /create-pr and /push without being re-derived.
"""

import json
import re
import subprocess
import sys

TICKET = re.compile(r"^(?:ado[-_/]?)?(?P<id>\d{5,7})[-_/]?(?P<slug>.*)$", re.IGNORECASE)
ADO_PROJECT = "R37 AR Follow Up App"


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

    match = TICKET.match(branch)
    if match:
        ticket = match.group("id")
        lines.append(f"ADO work item: {ticket} (inferred from the branch name)")
        lines.append(f'- Look it up in Azure DevOps project "{ADO_PROJECT}" if details are needed.')
        lines.append(
            f"- Use {ticket} for PR titles and ADO updates rather than re-deriving it."
        )
    else:
        lines.append(
            "Branch name carries no ADO ticket ID; ask before assuming one for PRs."
        )

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
