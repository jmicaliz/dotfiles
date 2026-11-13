---
description: Quick self-review for personal repos. One capped Claude pass, fix must-fix findings, push, and open the PR.
disable-model-invocation: true
---

Follow this exact workflow. Run one review pass only: never repeat it or raise its effort level.

**The bar.** A finding is must-fix only if it is in code this branch changed and is either a correctness or data-safety bug (wrong results, a crash, lost or corrupted data, a security hole, or exposed secrets) or duplication the branch adds that breaks the reuse rules in the loaded `CLAUDE.md` or `AGENTS.md` files (such as a value or logic copied from existing code, a test whose only job is keeping two copies in sync, or a function, macro, or model that differs from an existing one by one detail). A sync check those rules allow is not duplication, and with no reuse rules loaded, duplication is not must-fix. Confirm it against the code before accepting it. Fix duplication in this branch by reusing or parameterizing the existing code, even when that means moving it or updating an existing caller. If the fix needs a refactor that touches unrelated callers, leave it and list it in the report as a separate PR to merge before this one. Dismiss everything else with a one-line reason. Pre-existing bugs and duplication are dismissed too, but listed in the report as follow-up candidates.

1. **Preflight.** Stop if `git branch --show-current` is the default branch, or if `git status --porcelain` is not empty (commit with the `push` command first). Then `git fetch origin`.
2. **Base branch.** Use the repo's default branch: `git symbolic-ref --short refs/remotes/origin/HEAD`, minus the `origin/` prefix.
3. **Local checks.** Run what the repo's `CLAUDE.md`, `CONTRIBUTING.md`, or `Makefile` defines as its pre-PR check (for example `make check`). Fix failures and commit them; if you can't, stop and report. If nothing is defined, say so and continue.
4. **Review.** Run the `code-review` skill with `medium origin/<base>...HEAD` and wait for its findings. Fix the must-fix findings, re-run step 3, and commit with a message like `Address self-review findings`.
5. **Push.** `git push -u origin HEAD`. If the push is denied, print that command for the user and stop.
6. **Open the PR.** If `gh pr view --json state` shows an open PR, skip this step. Otherwise run the `create-pr` command with `<base>` as the base branch.
7. **Report and stop.** List what was fixed, what was dismissed and why, the follow-up candidates, and any refactor that must land first as its own PR.
