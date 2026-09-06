---
description: Organize a settings.json permissions file by tool type, then alphabetically, grouped sanely.
---

Reorganize the `permissions` arrays in a Claude Code `settings.json`. The target file is `$ARGUMENTS`;
if none is given, default to `./configs/.claude/settings.json` in the current repo (or the settings.json the user
has open).

Follow this exact workflow:

1. Read the global settings file at `/Users/US10060262/.claude/settings.json`. If it doesn't exist or has no
   `permissions` object, skip to step 2. Otherwise, for each permissions array present there (`allow`, `deny`,
   `ask`, and any others), find entries that exist in the global file but are missing from the corresponding
   array in the target file, and append them to that array in the target file (creating the array if it isn't
   present yet). This is additive only — do not remove or modify any existing entries in the target file during
   this step.
2. Read the target file. Confirm it is valid JSON and has a `permissions` object. If not, report the problem
   and stop without writing.
3. Reorder every permissions array (`allow`, `deny`, `ask`, and any others present) using the rules below.
   Apply the same rules to each array independently. Do NOT touch other top-level keys (e.g. `model`), and do
   NOT add, remove, or reword any permission entry — this is a reordering only.
4. Sort into these top-level groups, in this order:
   1. `Bash(...)` entries.
   2. Other native-tool entries (`Read`, `Edit`, `Write`, `Glob`, `Grep`, `NotebookEdit`, etc.), the tool
      names sorted alphabetically.
   3. `WebFetch(...)` then `WebSearch`.
   4. `mcp__...` entries.
5. Within the Bash group: sort by the inner command string alphabetically (so `Bash(git add:*)`, `Bash(git
   commit:*)`, … stay together and command families like `git` and `gh` naturally cluster).
6. Within the mcp group: sort alphabetically, which clusters entries by server (`mcp__<server>__<tool>`) and
   then by tool name inside each server.
7. Separate visually distinct clusters with a single blank line (JSON permits whitespace between array
   elements — this is how the file already groups things). Insert a blank line between:
   - each top-level group,
   - each Bash command family (when the first word after `Bash(` changes, e.g. `git` → `gh` → `grep`),
   - each mcp server.
   Collapse any runs of 2+ blank lines down to exactly one, and strip stray trailing spaces.
8. Preserve the file's existing indentation style (match the surrounding JSON — 4 spaces here).
9. If you notice exact-duplicate entries within an array, do NOT delete them silently — list them for the user
   after writing so they can decide.
10. Write the file back, then run a JSON validity check (e.g. pipe it through a JSON parser) to confirm it still
    parses. Report the check result and a short summary of what was regrouped (including any entries added from
    the global settings file in step 1).
