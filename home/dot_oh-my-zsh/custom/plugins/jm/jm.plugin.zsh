# Custom commands
jm_load_dotenv(){
  if [ -f .env ]; then
    # Open .env, pipe to sed which ignores lines starting with "#", then execute each export
    export $(cat .env | sed 's/#.*//g' | xargs)
  fi
}

jm_print_colors(){
  for i in {0..255}
      do print -Pn "%K{$i}  %k%F{$i}${(l:3::0:)i}%f " ${${(M)$((i%6)):#3}:+$'\n'}
  done
}

jm_git_commit(){
  local mm branch remote base

  if [ $# -eq 2 ]; then
    mm="$1"
    branch="$2"
  elif [ $# -eq 1 ]; then
    mm="main"
    branch="$1"
  else
    echo "Need to supply at least branch name if using main" >&2
    return 1
  fi

  git rev-parse --git-dir >/dev/null 2>&1 || { echo "Not in a git repo" >&2; return 1; }

  remote="${JM_GIT_REMOTE:-origin}"

  # Never check out the base branch: in a worktree it may be checked out
  # elsewhere, and git refuses. Rebase onto the remote-tracking ref instead.
  git fetch "$remote" "$mm" || return 1
  base="$remote/$mm"
  git rev-parse --verify --quiet "$base" >/dev/null || { echo "No such branch: $base" >&2; return 1; }

  # Keep the local base branch fresh too, but only when no worktree has it out.
  if ! git worktree list --porcelain | grep -qx "branch refs/heads/$mm"; then
    git fetch --quiet "$remote" "$mm:$mm" 2>/dev/null
  fi

  if [ "$(git symbolic-ref --quiet --short HEAD)" != "$branch" ]; then
    git switch "$branch" || return 1
  fi

  git rebase -i "$base" || { echo "Rebase onto $base stopped; resolve, then: git rebase --continue" >&2; return 1; }

  echo "Don't forget to push when ready: git push -f origin $branch"
}

alias jm_pyact='source .venv/bin/activate'
alias jm_pydeact='deactivate'
