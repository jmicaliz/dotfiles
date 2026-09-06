#!/usr/bin/env python3
"""PostToolUse(Edit|Write): flag hard-wrapped prose in markdown files.

The standing rule is one paragraph per line — no hard wrapping in README.md,
CLAUDE.md, or any other markdown. Two consecutive prose lines therefore mean a
wrapped paragraph. Code fences, frontmatter, tables, lists, headings, and
indented blocks are all exempt.
"""

import json
import re
import sys

FENCE = re.compile(r"^\s*(?:```|~~~)")
# Lines that start a structural block rather than prose.
NON_PROSE = re.compile(
    r"""^(?:\s*$                    # blank
        |\s{4,}\S                   # indented code
        |\s*\#{1,6}\s               # heading
        |\s*[-*+]\s                 # bullet
        |\s*\d+[.)]\s               # ordered item
        |\s*>                       # blockquote
        |\s*\|                      # table row
        |\s*(?:```|~~~)             # fence
        |\s*(?:-{3,}|={3,}|\*{3,})\s*$   # rule / setext underline
        |\s*\[[^\]]+\]:             # link reference definition
        |\s*<                       # raw html
        |\s*:{3,}                   # directive
        |\s*\*\*[^*]+\*\*:?\s*$     # standalone bold label
        )""",
    re.VERBOSE,
)

# A genuine hard wrap continues a sentence, so the continuation line starts
# lowercase. Requiring that keeps emoji pseudo-lists ("- Don't: ..."), standalone
# links, and other intentional line breaks out of the results. It trades a little
# recall for precision, which is the right trade for an advisory hook.
CONTINUATION = re.compile(r"^\s*[a-z]")


def wrapped_line_numbers(text: str) -> list[int]:
    lines = text.splitlines()
    start = 0

    # Skip YAML frontmatter.
    if lines and lines[0].strip() == "---":
        for index in range(1, len(lines)):
            if lines[index].strip() in ("---", "..."):
                start = index + 1
                break

    in_fence = False
    hits: list[int] = []
    previous_was_prose = False
    paragraph_reported = False
    run_start = 0

    for index in range(start, len(lines)):
        line = lines[index]

        if FENCE.match(line):
            in_fence = not in_fence
            previous_was_prose = False
            paragraph_reported = False
            continue
        if in_fence:
            continue

        is_prose = not NON_PROSE.match(line)
        if is_prose and not previous_was_prose:
            # First line of a new prose run; report against this line if it wraps.
            run_start = index
            paragraph_reported = False
        elif is_prose and CONTINUATION.match(line) and not paragraph_reported:
            hits.append(run_start + 1)
            paragraph_reported = True
        previous_was_prose = is_prose

    return hits


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        sys.exit(0)

    path = (payload.get("tool_input") or {}).get("file_path") or ""
    if not path.lower().endswith((".md", ".markdown")):
        sys.exit(0)

    try:
        with open(path, encoding="utf-8") as handle:
            text = handle.read()
    except OSError:
        sys.exit(0)

    hits = wrapped_line_numbers(text)
    if not hits:
        sys.exit(0)

    shown = ", ".join(str(n) for n in hits[:10])
    if len(hits) > 10:
        shown += f" (+{len(hits) - 10} more)"

    json.dump(
        {
            "hookSpecificOutput": {
                "hookEventName": "PostToolUse",
                "additionalContext": (
                    f"{path} contains hard-wrapped prose at line(s): {shown}. "
                    "This project's convention is one paragraph per line with no hard "
                    "wrapping in markdown. Rejoin each wrapped paragraph into a single line."
                ),
            }
        },
        sys.stdout,
    )
    sys.exit(0)


if __name__ == "__main__":
    main()
