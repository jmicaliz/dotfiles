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
  mm = ""
  branch = ""

  if [ $# -eq 2 ]; then
    mm = $1
    branch = $2
  elif [ $# -eq 1 ]; then
    mm = "main"
    branch = $1
  else
    echo "Need to supply at least branch name if using main"
  fi

  if [ -n "$branch"]; then
    git checkout $mm
    git pull
    git checkout $branch
    git rebase $mm

    hash=$(git rev-parse $mm)
    git rebase -i $hash
    echo "Don't forget to push when ready: git push -f origin $branch" 
  fi
}