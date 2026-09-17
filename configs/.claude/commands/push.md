---
description: Stage, commit, and push changes to the current branch.
---
Follow this exact workflow:
1. Run `git status` and `git diff` to review all staged and unstaged changes.
2. Stage the relevant changed files. Do not stage files that contain secrets or credentials.
3. Write a concise commit message that summarizes the changes, focusing on the "why" rather than the "what". For multi-line messages (subject plus body), pass the message via a HEREDOC to avoid shell-quoting issues:

    ```bash
    git commit -m "$(cat <<'EOF'
    Subject line

    Body paragraph explaining the why.
    EOF
    )"
    ```

4. Present the commit message to the user and ask for confirmation. If the user wants changes, revise the message accordingly before proceeding.
5. Commit to the current branch, then push with `git push`. If the push fails (blocked by admin policy on this machine), print the exact push command for the user to run in another terminal.
