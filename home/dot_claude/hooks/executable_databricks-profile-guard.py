#!/usr/bin/env python3
"""PreToolUse(Bash): require an explicit profile on Databricks CLI calls.

The standing convention is "never auto-select a profile". With --profile omitted
the CLI silently falls back to the [__settings__] default (currently `prp`), so a
forgotten flag runs against the wrong workspace without any visible signal.

Deny a profile-less invocation outright.
"""

import json
import re
import sys

# `databricks` used as a command word: at the start, after a shell separator, or
# behind env assignments / a `uv run`-style runner prefix.
INVOCATION = re.compile(
    r"""(?:^|[;&|(]|\n)          # start of string or shell separator
        \s*
        (?:\w+=\S+\s+)*          # optional VAR=value prefixes
        (?:\S*uv\s+run\s+|\S*poetry\s+run\s+)?   # optional runner prefix
        databricks\s+            # the CLI itself (not `databricks-sdk` etc.)
        (?P<rest>[^;&|\n]*)""",
    re.VERBOSE,
)

PROFILE = re.compile(r"(?:^|\s)(?:--profile[=\s]+|-p\s+)(?P<name>[\w.-]+)")

# Subcommands that legitimately need no profile.
PROFILELESS = re.compile(
    r"^(?:-h\b|--help\b|--version\b|-v\b|configure\b|auth\s+(?:login|profiles)\b)"
)

ENV_PROFILE = re.compile(r"DATABRICKS_CONFIG_PROFILE\s*=")


def block(reason: str) -> None:
    """Hard-block via exit code 2, which takes precedence over allow rules."""
    print(reason, file=sys.stderr)
    sys.exit(2)



def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        sys.exit(0)

    command = (payload.get("tool_input") or {}).get("command") or ""
    if "databricks" not in command:
        sys.exit(0)

    for match in INVOCATION.finditer(command):
        rest = match.group("rest").strip()
        if PROFILELESS.match(rest):
            continue

        profile = PROFILE.search(rest)
        if not profile:
            if ENV_PROFILE.search(command):
                continue
            block(
                "Databricks CLI call has no --profile. Omitting it silently uses the "
                "[__settings__] default workspace. Re-run with an explicit --profile "
                "chosen by the user rather than guessed; the session context lists them."
            )

    sys.exit(0)


if __name__ == "__main__":
    main()
