---
name: worktree
description: Create a git worktree for a task, naming the branch after its Linear issue instead of a generic or auto-generated name. Use this whenever the user asks to start, create, or work in a worktree; this skill governs how the branch/worktree name is chosen before calling EnterWorktree.
---

# Worktree

Governs branch naming whenever a git worktree is created for this user. `EnterWorktree` generates a random name when none is given; this skill supplies a ticket-based name instead.

## Naming convention

Branch name (and worktree `name` param) must be:

```text
<ticket-id>-<shortened-description-of-ticket-title>
```

The ticket ID is the lowercase Linear issue identifier, e.g. `engn-142-databricks-runs` for `ENGN-142`, "Add pfe databricks runs to list a job's recent runs by name". Linear's GitHub integration links any branch containing the identifier to the issue.

- Omit the word "worktree"; `EnterWorktree` already places the checkout under `.claude/worktrees/`.
- The description segment should be a short kebab-case slug (3-5 words max) capturing the ticket title, not a verbatim copy of it.
- Only letters, digits, dots, underscores, and dashes are allowed (EnterWorktree constraint).

## Steps

1. **Identify the ticket.** If the user already gave a ticket ID or it's clear from conversation context, use it. Otherwise ask which ticket this worktree is for; don't guess or invent one, and don't fall back to a non-ticket name silently. If they don't have one yet, offer to create it in Linear with the `linear-create-ticket` skill.

2. **Get the ticket title.** Look it up with `mcp__linear__get_issue`, ignoring case in the ID (`ENGN-142` and `engn-142` from a branch name are the same issue). If Linear has no such issue, treat it as no ticket and ask.
   - If the user describes the ticket instead of giving an ID, search with `mcp__linear__list_issues` and `query`. Confirm the match before using it.
   - If the user already stated the title in conversation, you can skip the lookup.

3. **Build the slug** from the ticket title per the convention above. Prefer clarity over completeness.

4. **Call `EnterWorktree`** with `name` set to `<ticket-id>-<slug>`.

5. **Open the worktree in VS Code.** Run `code -n <worktree-path>` (the absolute path `EnterWorktree` reported). `-n` forces a fresh window so an existing one is never hijacked. This is a separate VS Code window; the Claude Code session itself stays put in the worktree directory, so no further action is needed for it. Skip this step only if `code` is not on `PATH`, and say so rather than failing silently.
