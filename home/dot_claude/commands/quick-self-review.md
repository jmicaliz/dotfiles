---
description: Quick self-review for personal repos. One capped Claude pass, fix must-fix findings, push, and open the PR.
disable-model-invocation: true
---

Follow this exact workflow. Run one review pass only: never repeat it or raise its effort level.

**The bar.** A finding is must-fix only if it is a correctness or data-safety bug in code this branch changed: wrong results, a crash, lost or corrupted data, a security hole, or exposed secrets. Confirm it against the code before accepting it. Dismiss everything else with a one-line reason. Pre-existing bugs are dismissed too, but listed in the report as follow-up candidates.

1. **Preflight.** Stop if `git branch --show-current` is the default branch, or if `git status --porcelain` is not empty (commit with the `push` command first). Then `git fetch origin`.
2. **Base branch.** Use the repo's default branch: `git symbolic-ref --short refs/remotes/origin/HEAD`, minus the `origin/` prefix.
3. **Local checks.** Run what the repo's `CLAUDE.md`, `CONTRIBUTING.md`, or `Makefile` defines as its pre-PR check (for example `make check`). Fix failures and commit them; if you can't, stop and report. If nothing is defined, say so and continue.
4. **Review.** Run the `code-review` skill with `medium origin/<base>...HEAD` and wait for its findings. Fix the must-fix findings, re-run step 3, and commit with a message like `Address self-review findings`.
5. **Push.** `git push -u origin HEAD`. If the push is denied, print that command for the user and stop.
6. **Open the PR.** If `gh pr view --json state` shows an open PR, skip this step. Otherwise run the `create-pr` command with `<base>` as the base branch.
7. **Report and stop.** List what was fixed, what was dismissed and why, and the follow-up candidates.
