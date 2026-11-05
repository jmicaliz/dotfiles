#!/usr/bin/env python3
"""PostToolUse(Edit|Write): run dotfiles-guard on edits inside the dotfiles repo."""

import json
import subprocess
import sys
from pathlib import Path

DOTFILES = Path.home() / ".dotfiles"
GUARD = Path.home() / ".local" / "bin" / "dotfiles-guard"


def main() -> None:
    payload = json.load(sys.stdin)
    path = Path(payload.get("tool_input", {}).get("file_path", "")).resolve()
    if not GUARD.exists() or DOTFILES.resolve() not in path.parents:
        return
    result = subprocess.run([str(GUARD), str(path)], capture_output=True, text=True, check=False)
    if result.returncode:
        print(f"{result.stdout}{result.stderr}This repo is public: keep workplace identifiers in Keeper.", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
