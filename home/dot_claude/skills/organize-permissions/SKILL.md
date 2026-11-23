---
description: Organize a settings.json permissions file by tool type, then alphabetically, grouped sanely.
---

Run `python3 ~/.claude/hooks/organize_permissions.py <target>`, where `<target>` is `$ARGUMENTS` or, if empty, `~/.dotfiles/home/.chezmoitemplates/claude-settings-base.json` (or the settings.json I have open). The script merges entries from `~/.claude/settings.json` that the target lacks, reorders every permissions array (Bash, other native tools, WebFetch/WebSearch, mcp__) with blank lines between clusters, re-validates the JSON, and prints what it added plus any exact duplicates. Relay that output; leave duplicates in place for me to decide.
