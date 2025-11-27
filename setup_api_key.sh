#!/bin/bash
# Setup script for OpenAI API key

echo "============================================================"
echo "MagnifyingMed - API Key Setup"
echo "============================================================"
echo ""
echo "This script will help you set up your OpenAI API key."
echo ""

# Check if key is already set
if [ -n "$OPENAI_API_KEY" ]; then
    echo "✓ OPENAI_API_KEY is already set in your current session."
    echo ""
    read -p "Do you want to update it? (y/n): " update_key
    if [ "$update_key" != "y" ]; then
        echo "Keeping existing key."
        exit 0
    fi
fi

echo "To get your OpenAI API key:"
echo "1. Go to https://platform.openai.com/api-keys"
echo "2. Sign in or create an account"
echo "3. Click 'Create new secret key'"
echo "4. Copy the key (it starts with 'sk-...')"
echo ""
read -p "Enter your OpenAI API key: " api_key

if [ -z "$api_key" ]; then
    echo "No key provided. Exiting."
    exit 1
fi

# Determine shell and config file
if [ -n "$ZSH_VERSION" ]; then
    CONFIG_FILE="$HOME/.zshrc"
    SHELL_NAME="zsh"
elif [ -n "$BASH_VERSION" ]; then
    CONFIG_FILE="$HOME/.bashrc"
    SHELL_NAME="bash"
else
    CONFIG_FILE="$HOME/.profile"
    SHELL_NAME="shell"
fi

# Check if key already exists in config file
if grep -q "OPENAI_API_KEY" "$CONFIG_FILE" 2>/dev/null; then
    echo ""
    echo "Found existing OPENAI_API_KEY in $CONFIG_FILE"
    read -p "Do you want to replace it? (y/n): " replace
    if [ "$replace" == "y" ]; then
        # Remove old key
        if [[ "$OSTYPE" == "darwin"* ]]; then
            # macOS
            sed -i '' '/^export OPENAI_API_KEY=/d' "$CONFIG_FILE"
        else
            # Linux
            sed -i '/^export OPENAI_API_KEY=/d' "$CONFIG_FILE"
        fi
        echo "" >> "$CONFIG_FILE"
        echo "# OpenAI API Key for MagnifyingMed" >> "$CONFIG_FILE"
        echo "export OPENAI_API_KEY='$api_key'" >> "$CONFIG_FILE"
        echo "✓ Updated API key in $CONFIG_FILE"
    else
        echo "Keeping existing key in config file."
    fi
else
    # Add new key
    echo "" >> "$CONFIG_FILE"
    echo "# OpenAI API Key for MagnifyingMed" >> "$CONFIG_FILE"
    echo "export OPENAI_API_KEY='$api_key'" >> "$CONFIG_FILE"
    echo "✓ Added API key to $CONFIG_FILE"
fi

# Set for current session
export OPENAI_API_KEY="$api_key"
echo "✓ Set API key for current session"

echo ""
echo "============================================================"
echo "Setup complete!"
echo "============================================================"
echo ""
echo "The API key has been:"
echo "  ✓ Added to $CONFIG_FILE (will be loaded in new terminals)"
echo "  ✓ Set for your current session"
echo ""
echo "To use it in your current terminal, run:"
echo "  source $CONFIG_FILE"
echo ""
echo "Or start a new terminal session."
echo ""

