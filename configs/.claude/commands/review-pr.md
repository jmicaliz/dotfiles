---
description: Manually trigger a code review of a specific GitHub Pull Request.
argument-hint: <PR_NUMBER> [--verbose]
---
Perform a structured code review for GitHub PR #$ARGUMENTS.
## Execution Steps
1. **Context Gathering**: Run `gh pr view $ARGUMENTS --json title,body,baseRefName` to understand the PR's purpose and target branch.
2. **Fetch Changes**: Use `gh pr diff $ARGUMENTS` to retrieve the full code diff.
3. **Analysis**:
   - Evaluate for **logic errors** and **security risks**.
   - Check if the changes match the architectural standards in any `CLAUDE.md` files in the repository.
4. **Output Format**:
   - Provide a **Summary Table** of findings organized by Severity:
     - Important: bug that should be fixed before merging
     - Nit: minor issue, worth fixing but not blocking 
     - Pre-existing: bug that exists in the codebase but was not introduced by this PR
   - List actionable feedback as a bulleted list.
## Constraints
- Only use `$ARGUMENTS` to identify the PR.
- If the `--verbose` flag is present in `$ARGUMENTS`, include explanations of why each change was flagged.