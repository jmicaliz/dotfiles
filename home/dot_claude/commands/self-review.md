---
description: Self-review the branch before human review. Two capped Claude passes, open the PR, then at most two rounds of Copilot fixes. Never adds ready-for-review.
disable-model-invocation: true
---

Follow this exact workflow. The limits are the point: never add a review pass, repeat a finished one, or raise an effort level.

**The bar.** A finding is must-fix only if it is a correctness or data-safety bug in code this branch changed: wrong results, a crash, lost or corrupted data, a security hole, or exposed PHI or secrets. Confirm it against the code before accepting it. Dismiss everything else (style, naming, refactors, speculative issues with no concrete failing case) with a one-line reason. Pre-existing bugs are dismissed too, but listed in the report as follow-up candidates. Copilot's `blocking:` or `nit:` prefix is a hint, not the decision.

1. **Preflight.** Stop if `git branch --show-current` is `main`, `master`, or `develop`, or if `git status --porcelain` is not empty (commit with the `push` command first). Then `git fetch origin`.
2. **Base branch.** `hotfix-*` and `release-*` use `main`; everything else uses `develop` if `git rev-parse --verify --quiet origin/develop` succeeds, else `main`.
3. **Existing PR.** `gh pr view --json number,state,isDraft`. No open PR: go to step 4. Open draft: go to step 4, and in step 8 run `gh pr ready <n>` instead of `create-pr`. Open and ready: push if the branch is ahead of its remote, then go to step 9.
4. **Local checks.** Run what the repo's `CLAUDE.md` or `CONTRIBUTING.md` requires before a PR, such as `make check` in each touched project. Fix failures (on this first run, commit the fixes before continuing; when a later step re-runs this, that step's commit includes them); if you can't, stop and report. If nothing is documented, say so and continue.
5. **Broad pass.** Run the `code-review` skill with `high origin/<base>...HEAD`. It runs in the background; do nothing else until its findings arrive. Fix the must-fix findings, re-run step 4, and commit with a message in the `push` format, e.g. `ENGN-12: Address self-review findings`. If nothing was must-fix, skip step 6.
6. **Narrow pass.** Run `code-review` with `medium HEAD~1...HEAD` so it sees only the fix commit, and wait for its findings the same way. Fix any must-fix findings, re-run step 4, and commit if anything changed. No further Claude passes.
7. **Push.** `git push -u origin HEAD`. If the push is denied, print that command for the user and stop.
8. **Open the PR** with the `create-pr` skill. If it stops to ask something, relay the question and continue after the answer.
9. **Copilot round 1.** Wait for Copilot's review of the pushed head (see "Waiting for Copilot"). If it left no unresolved threads (see "Copilot threads"), go to step 11. Otherwise triage each thread with the bar and draft a one-line reply. Show the user a table (`path:line`, Copilot's point, fix or dismiss, reply) and wait for their OK or edits. Then fix, re-run step 4, and, if anything changed, commit and push once. Once the PR exists, never amend or force-push: reviewers need to see what changed. Post each reply, citing the fix commit's short SHA for fixes, and resolve each thread.
10. **Copilot round 2.** Only if step 9 pushed. Wait for Copilot's review of the new head. It often repeats comments that were already resolved; answer a repeat by pointing to the earlier reply. Fix only new must-fix findings and dismiss the rest, with the same table, OK, and fix, push, reply, resolve sequence. If this round pushes, Copilot will review once more; do not wait for it.
11. **Report and stop.** List what each pass fixed, what was dismissed and why, the follow-up candidates, and anything still open, including a Copilot review still pending from step 10. Tell the user to read the diff on GitHub and add `ready-for-review` themselves. Never add that label.

**Waiting for Copilot.** Run this in the background, never as a foreground sleep. It exits 0 once Copilot has reviewed the head commit, 2 if Copilot can't be requested, and 1 after 30 minutes. After 2 minutes it requests Copilot itself if nothing else has, since not every repo auto-requests it. On a non-zero exit, report and stop; running this command again resumes at step 9.

```bash
n=<pr-number>; sha=$(git rev-parse HEAD)
for i in $(seq 1 60); do
  gh api --paginate "repos/{owner}/{repo}/pulls/$n/reviews" \
    --jq "any(.[]; .user.login == \"copilot-pull-request-reviewer[bot]\" and .commit_id == \"$sha\")" | grep -q true && exit 0
  if [ "$i" -eq 5 ] && ! gh api "repos/{owner}/{repo}/pulls/$n/requested_reviewers" --jq '.users[].login' | grep -qi copilot; then
    gh pr edit "$n" --add-reviewer @copilot || exit 2
  fi
  sleep 30
done
exit 1
```

**Copilot threads.** Only reply to or resolve threads Copilot opened, never a human's. List the unresolved ones:

```bash
gh api graphql -F owner='{owner}' -F repo='{repo}' -F n=<pr-number> -f query='
  query($owner: String!, $repo: String!, $n: Int!) {
    repository(owner: $owner, name: $repo) { pullRequest(number: $n) {
      reviewThreads(first: 100) { nodes { id isResolved path line comments(first: 1) { nodes { author { login } body } } } }
    } }
  }' --jq '[.data.repository.pullRequest.reviewThreads.nodes[]
    | select((.isResolved | not) and .comments.nodes[0].author.login == "copilot-pull-request-reviewer")]'
```

Reply to a thread, then resolve it. The reply is read from stdin so apostrophes in it can't break the quoting:

```bash
gh api graphql -f id=<thread-id> -F body=@- -f query='mutation($id: ID!, $body: String!) { addPullRequestReviewThreadReply(input: {pullRequestReviewThreadId: $id, body: $body}) { comment { url } } }' <<'EOF'
<reply>
EOF
gh api graphql -f id=<thread-id> -f query='mutation($id: ID!) { resolveReviewThread(input: {threadId: $id}) { thread { isResolved } } }'
```
