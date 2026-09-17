---
description: Creates a PR that squashes the commits into one, uses the PR template, and updates Jira.
---
Follow this exact workflow to create a PR:
1. Verify the branch exists on origin. If not, push it first.
2. Verify the branch is up-to-date with `origin/main`. If it is, skip to step 6.
3. Rebase onto `origin/main`.
4. Squash all commits on the branch into one, keeping the commit message from the first (oldest) commit. If that message is uninformative (contains `wip`, `fix`, `update`, or is under 10 characters), synthesize a new message from the branch name and diff, and present it for confirmation before squashing.
5. Push the squashed branch with `git push --force-with-lease`. If the push fails (blocked by admin policy on this machine), print the exact command for the user to run in another terminal, then wait for them to confirm before continuing.
6. Analyze the feature branch and review the full diff against the main branch.
7. If tests are missing, documentation is missing, or `TODO` statements remain in the diff, ask the user to address them before continuing.
8. Fill in the PR template at `.github/pull_request_template.md` as the PR body, completing all sections based on the analysis. If no template exists, use a structured format with summary, changes made, testing, and checklist.
9. Create the PR using `gh pr create` with the filled-in template.
