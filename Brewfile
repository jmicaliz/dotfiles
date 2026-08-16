# SteamOS ships no system C compiler and cannot durably install one (the root
# filesystem is read-only and reverted by OS updates), so formulae without a
# Linux bottle — which would build from source — are skipped there.
steamos = OS.linux? && File.exist?("/etc/os-release") &&
          File.read("/etc/os-release").match?(/^ID=steamos$/)

# Build dependencies
brew "gcc"
brew "libb2"
brew "openssl"
brew "readline"
brew "sqlite3"
brew "tcl-tk@8"
brew "xz"
brew "zlib"

# Shell & terminal
brew "starship"
brew "tmux"

# Languages & runtimes
brew "kona"
brew "node"
brew "fnm"
brew "rlwrap"
brew "uv"

# CLI utilities
brew "fzf"
brew "httpie"
brew "jq"
brew "ncdu"
brew "ripgrep"
brew "tlrc"

# Development
tap "hashicorp/tap" unless steamos
brew "ansible"
brew "coder"
brew "direnv"
brew "gh"
brew "pgcli"
brew "hashicorp/tap/terraform" unless steamos # no Linux bottle; source build
brew "rclone"

# Apps (casks are macOS-only; on Linux these are installed by bootstrap.sh)
cask "claude-code" if OS.mac?
cask "visual-studio-code" if OS.mac?
