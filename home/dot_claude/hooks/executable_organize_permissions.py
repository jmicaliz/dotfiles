#!/usr/bin/env python3
"""Merge global permissions into a settings.json and reorder its permissions arrays."""

import json
import re
import sys
from collections import Counter
from pathlib import Path

GROUP_ORDER = {"Bash(": 0, "WebFetch(": 2, "WebSearch": 2, "mcp__": 3}


def group(entry: str) -> int:
    for prefix, order in GROUP_ORDER.items():
        if entry.startswith(prefix):
            return order
    return 1


def sort_key(entry: str) -> tuple[int, str]:
    return group(entry), entry.removeprefix("Bash(")


def cluster(entry: str) -> str:
    if entry.startswith("Bash("):
        return "bash:" + re.split(r"[\s:)]", entry.removeprefix("Bash("), 1)[0]
    if entry.startswith("mcp__"):
        return "mcp:" + entry.split("__")[1]
    return str(group(entry))


def render(entries: list[str], indent: str) -> str:
    lines = ["["]
    previous = None
    for entry in sorted(entries, key=sort_key):
        current = cluster(entry)
        if previous is not None and current != previous:
            lines.append("")
        lines.append(f"{indent}    {json.dumps(entry)},")
        previous = current
    lines[-1] = lines[-1].rstrip(",")
    lines.append(f"{indent}]")
    return "\n".join(lines)


def string_arrays(permissions: dict) -> dict[str, list[str]]:
    return {
        name: values
        for name, values in permissions.items()
        if isinstance(values, list) and all(isinstance(v, str) for v in values)
    }


def merge_global(permissions: dict, global_path: Path) -> dict[str, list[str]]:
    if not global_path.is_file():
        return {}
    global_permissions = json.loads(global_path.read_text(encoding="utf-8")).get("permissions")
    if not isinstance(global_permissions, dict):
        return {}
    added: dict[str, list[str]] = {}
    for name, values in string_arrays(global_permissions).items():
        target = permissions.setdefault(name, [])
        missing = [v for v in values if v not in target]
        if missing:
            target.extend(missing)
            added[name] = missing
    return added


def main() -> None:
    if len(sys.argv) < 2:
        sys.exit("usage: organize_permissions.py <settings.json> [global-settings.json]")
    target_path = Path(sys.argv[1])
    global_path = Path(sys.argv[2]) if len(sys.argv) > 2 else Path.home() / ".claude/settings.json"

    settings = json.loads(target_path.read_text(encoding="utf-8"))
    permissions = settings.get("permissions")
    if not isinstance(permissions, dict):
        sys.exit(f"{target_path} has no permissions object; nothing written")

    added = merge_global(permissions, global_path)
    arrays = string_arrays(permissions)
    for name in arrays:
        permissions[name] = f"__PERMISSIONS_{name}__"

    text = json.dumps(settings, indent=4, ensure_ascii=False)
    for name, entries in arrays.items():
        placeholder = re.compile(rf'^(?P<indent>\s*)"{re.escape(name)}": "__PERMISSIONS_{re.escape(name)}__"', re.M)
        match = placeholder.search(text)
        replacement = f'{match.group("indent")}"{name}": {render(entries, match.group("indent"))}'
        text = text[: match.start()] + replacement + text[match.end() :]
    text += "\n"

    json.loads(text)
    target_path.write_text(text, encoding="utf-8")

    print(f"Wrote {target_path}; JSON re-parses.")
    for name, values in added.items():
        print(f"Added from {global_path} to {name}: {', '.join(values)}")
    for name, entries in arrays.items():
        duplicates = [e for e, n in Counter(entries).items() if n > 1]
        if duplicates:
            print(f"Exact duplicates left in {name} for you to decide: {', '.join(duplicates)}")


if __name__ == "__main__":
    main()
