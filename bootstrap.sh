#!/bin/bash
set -euo pipefail

# Wrapped in a function so bash parses the whole file before git pull can rewrite it mid-run.
main() {
    cd "$(dirname "${BASH_SOURCE[0]}")"

    if git rev-parse --abbrev-ref '@{u}' >/dev/null 2>&1; then
        git pull --ff-only || echo "bootstrap: git pull failed, applying local checkout as is" >&2
    fi

    CHEZMOI="$(command -v chezmoi || true)"
    if [ -z "$CHEZMOI" ]; then
        tmp="$(mktemp -d)"
        sh -c "$(curl -fsLS get.chezmoi.io)" -- -b "$tmp"
        CHEZMOI="$tmp/chezmoi"
    fi

    git config core.hooksPath .githooks
    "$CHEZMOI" init --apply --source "$PWD"

    upgrade_brew
}

upgrade_brew() {
    local brew
    for brew in /opt/homebrew/bin/brew /home/linuxbrew/.linuxbrew/bin/brew; do
        [ -x "$brew" ] && break
    done
    [ -x "$brew" ] || return 0
    eval "$("$brew" shellenv)"
    [ -x "$HOME/.sudo_askpass" ] && export SUDO_ASKPASS="$HOME/.sudo_askpass"

    brew update
    brew upgrade || echo "bootstrap: brew upgrade failed, some packages may be out of date" >&2
    brew cleanup
}

main "$@"
