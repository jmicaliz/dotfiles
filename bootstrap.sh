#!/bin/bash

# Change to the directory of the script
cd "$(dirname "${BASH_SOURCE}")";

# Detect the platform once; later steps branch on these.
# SteamOS (Steam Deck) is Arch-based with a read-only root filesystem, so
# anything that writes outside $HOME (pacman, chsh, snap) is unavailable or
# gets reverted by the next OS update. Homebrew lives in /home/linuxbrew,
# which is on the writable partition, so it survives updates.
IS_STEAMOS=false
if grep -qs '^ID=steamos' /etc/os-release; then
    IS_STEAMOS=true
    echo "Detected SteamOS — using the read-only-root friendly path."

    # The deck user has no password by default, which makes sudo unusable.
    if ! sudo -v; then
        echo "sudo is not usable. Set a password first with 'passwd', then re-run this script."
        exit 1
    fi

    if ! command -v curl &>/dev/null; then
        echo "curl is required to install Homebrew but is not present."
        echo "Install it with: sudo steamos-readonly disable && sudo pacman -S curl"
        exit 1
    fi
fi

# If debian-based system, install some necessary libraries
if [ -f /etc/debian_version ]; then
    echo "Installing necessary libraries for Debian-based systems..."
    sudo apt update && sudo apt install -y build-essential procps curl file git && sudo apt upgrade -y && sudo apt autoremove -y
fi

# Pull the latest changes for whichever branch is checked out
DOTFILES_BRANCH="$(git rev-parse --abbrev-ref HEAD 2>/dev/null)"
if [ -z "$DOTFILES_BRANCH" ] || [ "$DOTFILES_BRANCH" = "HEAD" ]; then
    echo "Not on a branch — skipping git pull."
else
    git pull origin "$DOTFILES_BRANCH"
fi

# Install Homebrew
if ! command -v brew &>/dev/null; then
    echo "Installing Homebrew..."
    NONINTERACTIVE=1 /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
else
    echo "Homebrew is already installed."
fi

# Ensure brew is on PATH for the rest of this script (even if it was already installed)
if [ "$(uname)" = "Darwin" ]; then
    eval "$(/opt/homebrew/bin/brew shellenv)"
else
    eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"
fi

# Install zsh
if ! command -v zsh &>/dev/null; then
    echo "Installing zsh..."
    if [ "$(uname)" = "Darwin" ]; then
        brew install zsh
    elif [ "$IS_STEAMOS" = true ]; then
        # pacman would write to the read-only root and be wiped by OS updates.
        brew install zsh
    elif [ -f /etc/debian_version ]; then
        sudo apt update && sudo apt install -y zsh
    elif [ -f /etc/redhat-release ]; then
        sudo yum install -y zsh
    else
        echo "Unsupported OS. Please install zsh manually."
        exit 1
    fi
fi

# Change default shell to zsh
if [ "$IS_STEAMOS" = true ]; then
    # chsh writes to /etc/passwd and requires the shell in /etc/shells; both are
    # on the read-only root and are reverted by OS updates. Hand off from
    # .bashrc instead, which lives in $HOME and persists.
    if ! grep -qs 'dotfiles: hand off to zsh' "$HOME/.bashrc"; then
        echo "Adding zsh hand-off to ~/.bashrc (chsh is not durable on SteamOS)..."
        cat >> "$HOME/.bashrc" <<'EOF'

# dotfiles: hand off to zsh (SteamOS cannot persist a chsh)
if [ -x /home/linuxbrew/.linuxbrew/bin/brew ]; then
    eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"
fi
if [ -z "$ZSH_VERSION" ] && [[ $- == *i* ]] && command -v zsh >/dev/null; then
    exec zsh
fi
EOF
    else
        echo "zsh hand-off is already in ~/.bashrc."
    fi
elif [ "$SHELL" != "$(which zsh)" ]; then
    echo "Changing default shell to zsh..."
    chsh -s "$(which zsh)"
else
    echo "Default shell is already zsh."
fi

# Install Oh My Zsh
if [ ! -d "$HOME/.oh-my-zsh" ]; then
    echo "Installing Oh My Zsh..."
    sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended
else
    echo "Oh My Zsh is already installed."
fi

# Install custom_commands
for plugin_dir in plugins/*; do
    if [ -d "$plugin_dir" ]; then
        cp -rf "$plugin_dir" "$HOME/.oh-my-zsh/custom/plugins"
    fi
done

# Add .zshrc
cp -f jm.zshrc $HOME/.zshrc

# Add homebrew installs
brew update

# Homebrew 6+ requires non-official taps to be trusted before it will load
# their formulae, and an untrusted tap aborts the entire bundle. Trust the taps
# the Brewfile uses. (Guarded: `brew trust` does not exist before Homebrew 6.
# SteamOS skips the hashicorp tap entirely — see the Brewfile.)
if [ "$IS_STEAMOS" != true ] && brew trust --help &>/dev/null; then
    brew trust --tap hashicorp/tap
fi

# SteamOS has no system C compiler, and Homebrew's gcc only installs versioned
# binaries (gcc-16, c++-16), so nothing satisfies Homebrew's compiler
# requirement -- which breaks gcc's own post-install step. Homebrew looks in
# HOMEBREW_PREFIX/bin before /usr/bin, so unversioned symlinks there fix it
# without touching the read-only root.
if [ "$IS_STEAMOS" = true ]; then
    brew install gcc || true
    BREW_BIN="$(brew --prefix)/bin"
    # gcc-[0-9]* matches gcc-16 but not gcc-ar-16 / gcc-nm-16 / gcc-ranlib-16
    GCC_VERSIONED="$(ls "$BREW_BIN"/gcc-[0-9]* 2>/dev/null | sort -V | tail -1)"
    CXX_VERSIONED="$(ls "$BREW_BIN"/g++-[0-9]* 2>/dev/null | sort -V | tail -1)"
    if [ -n "$GCC_VERSIONED" ] && [ ! -e "$BREW_BIN/cc" ]; then
        echo "Linking $(basename "$GCC_VERSIONED") as cc/gcc (SteamOS has no system compiler)..."
        ln -sf "$GCC_VERSIONED" "$BREW_BIN/cc"
        ln -sf "$GCC_VERSIONED" "$BREW_BIN/gcc"
        [ -n "$CXX_VERSIONED" ] && ln -sf "$CXX_VERSIONED" "$BREW_BIN/c++"
        [ -n "$CXX_VERSIONED" ] && ln -sf "$CXX_VERSIONED" "$BREW_BIN/g++"
        # gcc's post-install failed earlier for want of a compiler; retry now.
        brew postinstall gcc || true
    fi
fi

# A stale .incomplete file in the download cache makes an otherwise successful
# pour report failure, and it persists until removed.
rm -f "$(brew --cache)"/downloads/*.incomplete 2>/dev/null

if ! brew bundle --file ./Brewfile; then
    echo "WARNING: 'brew bundle' failed — some Brewfile tools are missing. See the error above."
fi

# Install Claude Code on Linux (macOS installs it via the Brewfile cask)
if [ "$(uname)" != "Darwin" ]; then
    if ! command -v claude &>/dev/null; then
        echo "Installing Claude Code..."
        curl -fsSL https://claude.ai/install.sh | bash
    else
        echo "Claude Code is already installed."
    fi
fi

# Add starship toml
mkdir -p $HOME/.config 
cp -f ./configs/starship.toml $HOME/.config/starship.toml

# Add direnv toml
mkdir -p $HOME/.config/direnv
cp -f ./configs/direnv.toml $HOME/.config/direnv/direnv.toml

# Add .gitconfig
cp -f ./configs/.gitconfig $HOME/.gitconfig

# Add .gitignore_global
cp -f ./configs/.gitignore_global $HOME/.gitignore_global

# Add Claude Code settings
mkdir -p $HOME/.claude
cp -rf ./configs/.claude/* $HOME/.claude/

# Install VS Code
VSCODE_FLATPAK_ID="com.visualstudio.code"
if [ "$(uname)" = "Darwin" ]; then
    VSCODE_USER_DIR="$HOME/Library/Application Support/Code/User"
elif [ "$IS_STEAMOS" = true ]; then
    # snapd is not available on SteamOS. Install per-user via Flatpak so the app
    # lives in $HOME and survives OS updates.
    if ! command -v flatpak &>/dev/null; then
        echo "Skipping VS Code install — flatpak not found."
    elif flatpak info --user "$VSCODE_FLATPAK_ID" &>/dev/null; then
        echo "VS Code is already installed."
    else
        echo "Installing VS Code via Flatpak..."
        flatpak remote-add --if-not-exists --user flathub https://flathub.org/repo/flathub.flatpakrepo
        flatpak install -y --user flathub "$VSCODE_FLATPAK_ID"
    fi
    VSCODE_USER_DIR="$HOME/.var/app/$VSCODE_FLATPAK_ID/config/Code/User"
else
    if ! command -v code &>/dev/null; then
        echo "Installing VS Code..."
        sudo snap install code --classic
    else
        echo "VS Code is already installed."
    fi
    VSCODE_USER_DIR="$HOME/.config/Code/User"
fi

# Copy VS Code settings
mkdir -p "$VSCODE_USER_DIR"
cp -f ./configs/vscode/settings.json "$VSCODE_USER_DIR/settings.json"

# Install VS Code extensions
# Prefer the Remote SSH server binary (newer: ~/.vscode-server/code-<hash>; older: ~/.vscode-server/bin/.../code-server),
# then fall back to a locally installed `code` CLI (e.g. desktop VS Code on macOS or Linux),
# then to the Flatpak's bundled CLI (SteamOS).
VSCODE_CLI=()
VSCODE_BIN=$(find ~/.vscode-server -maxdepth 1 -name "code-*" -type f 2>/dev/null | head -1)
if [ -z "$VSCODE_BIN" ]; then
    VSCODE_BIN=$(find ~/.vscode-server/bin -maxdepth 3 -name "code-server" -not -path "*/legacy-mode/*" 2>/dev/null | head -1)
fi
if [ -z "$VSCODE_BIN" ] && command -v code &>/dev/null; then
    VSCODE_BIN="code"
fi
if [ -n "$VSCODE_BIN" ]; then
    VSCODE_CLI=("$VSCODE_BIN")
elif command -v flatpak &>/dev/null && flatpak info --user "$VSCODE_FLATPAK_ID" &>/dev/null; then
    VSCODE_CLI=(flatpak run --user --command=code "$VSCODE_FLATPAK_ID")
fi
if [ ${#VSCODE_CLI[@]} -gt 0 ]; then
    echo "Installing VS Code extensions..."
    while IFS= read -r extension || [ -n "$extension" ]; do
        [ -z "$extension" ] && continue
        "${VSCODE_CLI[@]}" --install-extension "$extension" --force 2>&1 | grep -v "DeprecationWarning\|node --trace"
    done < ./configs/vscode/extensions.txt
else
    echo "Skipping VS Code extension install — no VS Code CLI found (open VS Code, or connect via Remote SSH, then re-run)."
fi

# Make repos directory
mkdir -p $HOME/repos

echo "Bootstrap completed!"