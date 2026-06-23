# CLAUDE.md - dotfiles
Personal dotfiles for macOS and Debian/Ubuntu Linux development environments, managed via Oh My Zsh and bootstrapped with `bootstrap.sh`. The bootstrap script and `jm.zshrc` detect the OS (`uname` / `/etc/debian_version`) and branch where behavior differs (Homebrew prefix, package install, VS Code, Claude Code). When adding setup steps, keep them cross-platform: guard OS-specific commands and prefer Homebrew where it works on both.
## Repo Structure
- `jm.zshrc` - the main zshrc; copied to `~/.zshrc` by bootstrap
- `bootstrap.sh` - idempotent setup script, run with `./bootstrap.sh`
- `Brewfile` - Homebrew packages
- `plugins/` - custom Oh My Zsh plugins, each in their own subdirectory
- `configs/` - config files copied to their target locations by bootstrap
