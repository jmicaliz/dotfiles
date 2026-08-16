# CLAUDE.md - dotfiles
Personal dotfiles for macOS, Debian/Ubuntu Linux, and SteamOS (Steam Deck) development environments, managed via Oh My Zsh and bootstrapped with `bootstrap.sh`. The bootstrap script and `jm.zshrc` detect the OS (`uname` / `/etc/debian_version` / `ID=steamos` in `/etc/os-release`) and branch where behavior differs (Homebrew prefix, package install, VS Code, Claude Code). When adding setup steps, keep them cross-platform: guard OS-specific commands and prefer Homebrew where it works everywhere.

SteamOS has a read-only root filesystem that OS updates revert, so on that platform anything written outside `$HOME` is off-limits: no `pacman`, no `chsh` (a `.bashrc` hand-off `exec`s zsh instead), and no `snap` (VS Code comes from a per-user Flatpak). Homebrew is the package manager there because `/home/linuxbrew` sits on the writable partition. When adding a step, prefer one that only touches `$HOME`.

SteamOS also has no system C compiler, so any formula lacking a Linux bottle would build from source and fail. The `Brewfile` sets a `steamos` flag and gates such formulae behind `unless steamos`; when adding a formula, check `brew info --json=v2 <name>` for an `x86_64_linux` bottle first. `bootstrap.sh` symlinks Homebrew's versioned `gcc-N` as `cc`/`gcc` in the Homebrew prefix, which Homebrew searches before `/usr/bin`.
## Repo Structure
- `jm.zshrc` - the main zshrc; copied to `~/.zshrc` by bootstrap
- `bootstrap.sh` - idempotent setup script, run with `./bootstrap.sh`
- `Brewfile` - Homebrew packages
- `plugins/` - custom Oh My Zsh plugins, each in their own subdirectory
- `configs/` - config files copied to their target locations by bootstrap
