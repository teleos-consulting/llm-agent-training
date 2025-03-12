#!/bin/bash

# Exit on error
set -e

echo "Installing development tools for Mac..."

# Install Xcode Command Line Tools (required for Rust and many dev tools)
if ! xcode-select -p &> /dev/null; then
    echo "Installing Xcode Command Line Tools..."
    xcode-select --install
    # Wait for the installation to complete
    echo "Please complete the Command Line Tools installation when prompted"
    echo "Press any key when the installation has finished..."
    read -n 1
fi

# Check if Homebrew is installed, install if not
if ! command -v brew &> /dev/null; then
    echo "Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    
    # Add Homebrew to PATH if needed
    if [[ "$(arch)" == "arm64" ]]; then
        # For Apple Silicon Macs
        if [[ "$SHELL" == */zsh ]]; then
            echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zshrc
            eval "$(/opt/homebrew/bin/brew shellenv)"
        else
            echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.bash_profile
            eval "$(/opt/homebrew/bin/brew shellenv)"
        fi
    else
        # For Intel Macs
        if [[ "$SHELL" == */zsh ]]; then
            echo 'eval "$(/usr/local/bin/brew shellenv)"' >> ~/.zshrc
            eval "$(/usr/local/bin/brew shellenv)"
        else
            echo 'eval "$(/usr/local/bin/brew shellenv)"' >> ~/.bash_profile
            eval "$(/usr/local/bin/brew shellenv)"
        fi
    fi
fi

# Visual Studio Code
echo "Installing Visual Studio Code..."
brew install --cask visual-studio-code

# Python 3.13 (using Homebrew)
echo "Installing Python 3.13..."
brew install python@3.13

# Rust
echo "Installing Rust..."
brew install rustup-init
rustup-init -y --no-modify-path
# Ensure Rust is in PATH
if [[ "$SHELL" == */zsh ]]; then
    echo 'export PATH="$HOME/.cargo/bin:$PATH"' >> ~/.zshrc
else
    echo 'export PATH="$HOME/.cargo/bin:$PATH"' >> ~/.bash_profile
fi
source "$HOME/.cargo/env"

# Docker Desktop
echo "Installing Docker Desktop..."
brew install --cask docker
echo "NOTE: You may need to grant additional permissions for Docker Desktop in System Preferences"

# Install specific Rust toolchain (equivalent to the Windows version)
echo "Installing Rust toolchain 1.81..."
rustup toolchain install 1.81

echo "Installation complete! You may need to restart your terminal for all changes to take effect."
