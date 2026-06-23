# dotfiles
This repository contains my personal dotfiles and setup scripts for configuring a development environment on **macOS** and **Debian/Ubuntu Linux**. It automates the installation of essential tools, custom configurations, and shell enhancements, including `zsh` and `Oh My Zsh`. The same `bootstrap.sh` detects the OS and does the right thing on each platform.

## Purpose
The goal of this repository is to provide a streamlined way to set up a new development environment with my preferred tools and configurations. The `bootstrap.sh` script handles the installation of dependencies, configuration files, and custom plugins.

## Features
- Cross-platform: a single `bootstrap.sh` works on macOS and Debian/Ubuntu, branching on the OS where needed.
- Installs essential system libraries for Debian-based systems.
- Installs and configures [Homebrew](https://brew.sh/) for managing packages (Apple Silicon `/opt/homebrew` or Linuxbrew).
- Installs and sets up `zsh` as the default shell.
- Installs [Oh My Zsh](https://ohmyz.sh/) and custom plugins.
- Copies `.zshrc` and other configuration files to the appropriate locations.
- Installs Python using `pyenv` and sets the latest version as the default.
- Installs additional tools and utilities via Homebrew (e.g., `starship`, `fzf`, `poetry`).
- Configures the `starship` prompt and other customizations.

## Installation

### Prerequistes
You might need to create an ssh key. Look [here](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent?platform=linux) for how to do that.

### Using Git and the Bootstrap Script
Clone this repository to your preferred location (e.g., `~/.dotfiles`) and run the bootstrap script:

```shell
git clone https://github.com/jmicaliz/dotfiles.git ~/.dotfiles
cd ~/.dotfiles
source bootstrap.sh
```

The `bootstrap.sh` script will:
1. Pull the latest changes from the repository.
2. Install required tools and libraries.
3. Configure `zsh` as the default shell.
4. Install and configure Python using `pyenv`.
5. Set up custom plugins and configurations.

### Updating
To update your dotfiles and reapply the configurations, navigate to the repository and run the bootstrap script again:

```shell
cd ~/.dotfiles
source bootstrap.sh
```

## Customizations
- **Shell Prompt**: Configured using [Starship](https://starship.rs/). The configuration is stored in `starship.toml`.
- **Custom Plugins**: Includes custom `zsh` plugins located in the `plugins/` directory.
- **Python Management**: Uses `pyenv` and `pyenv-virtualenv` for managing Python versions and virtual environments.

## Tools Installed via Homebrew
The following tools are installed via the `Brewfile`:
- Development tools: `gcc`, `openssl`, `readline`, `sqlite3`, `zlib`, `tcl-tk@8`
- Shell enhancements: `starship`, `fzf`, `ripgrep`
- Python tools: `pyenv`, `pyenv-virtualenv`, `poetry`
- Utilities: `jq`, `httpie`, `pgcli`, `tlrc`
- Additional tools: `kona`, `rlwrap`

## Notes
- This setup supports macOS and Debian/Ubuntu Linux. On other distros (e.g. Fedora/RHEL) some steps fall back gracefully but may need manual adjustment.
- On Linux, VS Code is installed via `snap` and Claude Code via the official install script; on macOS both are installed via Homebrew casks.
- VS Code extensions install against a Remote SSH server binary if present, otherwise the local `code` CLI — so connect via VS Code (or open it locally) at least once.
- Also, need to install a [Nerd Font](https://www.nerdfonts.com/font-downloads) to see all the cool icons.
