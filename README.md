# dotfiles

My dotfiles and setup scripts for **macOS**, **Debian/Ubuntu**, and **SteamOS (Steam Deck)**, managed with [chezmoi](https://www.chezmoi.io/). Templates detect the OS and machine type (`personal` or `work`) and install the right tools and config for each.

## What it sets up

- [Homebrew](https://brew.sh/) and the packages in the [Brewfile](home/.chezmoitemplates/Brewfile)
- `zsh` as the default shell, with [Oh My Zsh](https://ohmyz.sh/) and the custom plugins in `home/dot_oh-my-zsh/custom/plugins/`
- The [Starship](https://starship.rs/) prompt
- Python tooling via `uv`
- VS Code with settings and extensions, and Claude Code with settings and hooks
- Secrets exported from `~/.secrets.zsh`, pulled from a password manager at apply time

## Installation

### Prerequisites

You may need an SSH key for GitHub. See GitHub's guide to [generating a new SSH key](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent?platform=linux).

Install a [Nerd Font](https://www.nerdfonts.com/font-downloads) so the prompt icons render.

### New machine

```shell
git clone https://github.com/jmicaliz/dotfiles.git ~/.dotfiles
~/.dotfiles/bootstrap.sh
```

`bootstrap.sh` pulls the latest changes, fetches a temporary chezmoi if none is installed, and runs `chezmoi init --apply` against the checkout. The first run asks whether the machine is `personal` or `work` (and for the work email). Answers are saved in `~/.config/chezmoi/chezmoi.toml`.

Rerunning `bootstrap.sh` is safe. It pulls the repo, re-applies changes, then runs `brew update`, `brew upgrade`, and `brew cleanup`.

### Day to day

The `Makefile` wraps the common chezmoi commands. Run `make` to list them all.

```shell
make update                 # git pull + apply
make status                 # files that differ and scripts that would run
make dry-run                # what apply would do, without doing it
make edit FILE=~/.zshrc     # edit the source, then apply it
make upgrade                # brew update + upgrade all packages
make check                  # dotfiles-guard + Markdown lint
```

`make diff` prints rendered templates, including secrets from Keeper or Bitwarden, so avoid it when sharing your screen.

## Machine differences and secrets

- Templates branch on `.machine` and the OS. See `home/.chezmoi.toml.tmpl`.
- Secrets are never committed. Add references to `home/.chezmoidata/secrets.yaml`. They resolve from Bitwarden (`bw`) on personal machines and Keeper Commander (`keeper`) on work machines.
- This repo is public. A pre-commit hook (`dotfiles-guard`) blocks commits containing workplace-identifying text.

## SteamOS (Steam Deck)

The root filesystem is read-only and reverted by OS updates, so setup only touches `$HOME`:

- Packages come from Homebrew, since `/home/linuxbrew` is on the writable partition.
- `chsh` can't persist, so `~/.bashrc` hands interactive shells off to `zsh`.
- VS Code is a per-user Flatpak, with settings in `~/.var/app/com.visualstudio.code/config/Code/User`.
- There is no system C compiler. The brew-bundle script links Homebrew's `gcc-N` as `cc`/`gcc`, and formulae without a Linux bottle are skipped. Currently that means **terraform is not installed**.

Before the first run, set a sudo password (the `deck` user has none by default):

```shell
passwd
```

## Notes

- Other distros (Fedora, RHEL) may need manual fixes.
- VS Code comes from `snap` on Debian/Ubuntu, Flatpak on SteamOS, and a Homebrew cask on macOS. Claude Code uses the official install script, except on macOS, where it uses a cask.
- VS Code extensions install into a Remote SSH server if one exists, otherwise via the local `code` CLI. Open VS Code (or connect over SSH) once first.

## Linting

Markdown is linted with `markdownlint-cli2` (config in `.markdownlint-cli2.jsonc`) by the pre-commit hook. To fix issues automatically:

```shell
markdownlint-cli2 --fix "**/*.md" "**/*.md.tmpl"
```
