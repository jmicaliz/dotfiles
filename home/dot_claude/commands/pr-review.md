---
description: Run the built-in code-review, then re-present its findings as F1, F2, ... with label, example, failure, evidence, and fix. Same arguments as /code-review.
disable-model-invocation: true
---

Follow this workflow:

0. **Check out the target head.** Only when the target is a PR number or a branch; with no target or a path target, skip to step 1. The built-in reads surrounding files from the working tree, so this must finish before step 1.
   - Resolve the SHA in one Bash call so no other fetch can overwrite `FETCH_HEAD` in between. PR: `git fetch origin pull/<n>/head && git rev-parse FETCH_HEAD`. Branch: `git fetch origin <branch> && git rev-parse FETCH_HEAD`; if a local `<branch>` exists and `FETCH_HEAD` is an ancestor of it (`git merge-base --is-ancestor FETCH_HEAD <branch>`), use the local SHA instead so unpushed commits are reviewed. A branch with no remote copy uses its local SHA.
   - `<git-common-dir>` is `git rev-parse --path-format=absolute --git-common-dir` and `<main-root>` is its parent, so both point at the main checkout even when this session starts in another worktree.
   - Path: `<main-root>/.claude/worktrees/pr-<n>-review`, with a slug of the branch name in place of `<n>` for a branch.
   - No worktree there: `git worktree add --detach <path> <sha>`. Never check out the branch by name and never create a branch.
   - Worktree there: if `git -C <path> status --porcelain` shows changes, stop and ask. Else if its HEAD is not `<sha>`, run `git -C <path> checkout --detach <sha>`. Else reuse it.
   - If `git -C <main-root> check-ignore -q .claude/worktrees/` fails, append `.claude/worktrees/` to `<git-common-dir>/info/exclude`.
   - Move this session into it with the `EnterWorktree` tool, `path: <path>`, not `cd`, so the session is filed under the worktree and resumable from its window. Confirm with `pwd`. Run step 1 and every later step, including "expand F2", from there.
   - Open it: `code -n <path>`. If `code` is not on `PATH`, skip this and say so.
   - Create or sync no `uv` env unless a test must run; then `uv sync` only the touched sub-project inside the worktree.
1. **Run the review.** Invoke the `code-review` skill with these arguments, unchanged: `$ARGUMENTS` (none if that is empty). It runs in the background; do nothing else until its findings arrive. If it fails or times out, say so and stop; do not review the diff yourself. If its instructions load into this turn instead, follow them, including the `ReportFindings` call, then continue here: I asked for the report in step 4, so print it even though the skill says not to print findings as text.
2. **Check every finding yourself.** Read the cited lines, their callers, and their tests until you can fill in every field of the layout from the code. Do not start subagents or another review. With `--fix`, check against the working tree after the built-in's edits. If a finding does not hold, leave it out of the F list and add a `Dropped on re-check:` line under the table with its location and the evidence that rules it out.
3. **Label and number.** `Important`: a bug a reviewer should block on. `Nit`: real but minor, including cleanups. `Pre-existing`: real, but the faulty lines predate the reviewed diff (check the diff or `git blame`), even when the diff touches the same function. Order Important, then Pre-existing, then Nit, keeping the built-in's order within each label, and number them F1, F2, ... in that order.
4. **Report** in the layout below. First relay any one-line notice the built-in opened with (reused effort level, `--max-findings`, what `--comment` posted). With no findings, say so in one line with the branch and short SHA, then the worktree line if step 0 ran, and stop. After step 0, the SHA is the fetched head SHA, and with `--fix` say the edits are uncommitted in the worktree, not pushed. This report is local output: never post it anywhere, even with `--comment`.
5. **Expand on request.** When I say "expand F2", go deeper on that finding only, in this session: the full call path, the evidence, and a draft fix as a diff.

**Layout.** Link targets are paths from the workspace root, or absolute when the reviewed checkout is outside the workspace. The line under each heading has the link, the built-in's category if it gave one, and its verdict (Confirmed or Plausible); when it gave no verdict, write `Re-checked: Confirmed` (you traced it in the code) or `Re-checked: Plausible` (credible, not proven) instead, so the source is clear. With `--fix`, end that line with `fixed` or `skipped: <why>`. Leave out **Same issue at** when the bug appears only once.

```markdown
**2 Important**, 1 other · `<branch>` at `<12-char SHA>` · `<target>` · <level>

| ID | Label | Location | Title |
| --- | --- | --- | --- |
| F1 | Important | [path/file.py:42](path/file.py#L42) | Title that names the defect in plain words |

### F1 · Important · Title that names the defect in plain words

[path/file.py:42](path/file.py#L42) · correctness · Confirmed

- **Claim:** what the code does today and why that is wrong.
- **Example:** a concrete input, row, or call sequence that triggers it.
- **Failure scenario:** what then happens (wrong rows, crash, lost data) and who is hit (tables, TPIDs, envs, consumers).
- **Evidence:** `path/file.py:42` what it shows; `path/other.py:7` what it shows.
- **Same issue at:** `path/file.py:90`.
- **Suggestion:** the specific change, then any alternative you rejected and why.

---

- F1 · Important · Title that names the defect in plain words

Say "expand F2" to dig into one finding in this session.

Worktree: `<path>` · remove with `git worktree remove <path>`
```

The `Worktree:` line appears only when step 0 ran. Never remove the worktree yourself, and never call `ExitWorktree` with `remove`.
