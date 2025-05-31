#!/bin/bash

# Change to the directory of the script
cd "$(dirname "${BASH_SOURCE}")";

# If debian-based system, install some necessary libraries
if [ -f /etc/debian_version ]; then
    echo "Installing necessary libraries for Debian-based systems..."
    sudo apt update && sudo apt install -y build-essential procps curl file git
fi

# Clone the repository
git pull origin main;

# Install Homebrew
if ! command -v brew &>/dev/null; then
    echo "Installing Homebrew..."
    NONINTERACTIVE=1 /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

    if [ "$(uname)" == "Darwin" ]; then
        eval "$(/opt/homebrew/bin/brew shellenv)"
    else
        eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"
    fi
else
    echo "Homebrew is already installed."
fi

# Install zsh
if ! command -v zsh &>/dev/null; then
    echo "Installing zsh..."
    if [ "$(uname)" == "Darwin" ]; then
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
if [ "$0" != "zsh" ]; then
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
        cp -r "$plugin_dir" "$HOME/.oh-my-zsh/custom/plugins"
    fi
done

# Add .zshrc
cp -f jm.zshrc $HOME/.zshrc

source $HOME/.zshrc

# Add homebrew installs
brew update
brew bundle --file ./Brewfile

# Add starship toml
mkdir -p $HOME/.config 
cp -f ./configs/starship.toml $HOME/.config/starship.toml

# Add direnv toml
mkdir -p $HOME/.config/direnv
cp -f ./configs/direnv.toml $HOME/.config/direnv/direnv.toml

# Add .gitconfig
cp -f ./configs/.gitconfig $HOME/.gitconfig

# Make repos directory
mkdir -p $HOME/repos

echo "Bootstrap completed!"