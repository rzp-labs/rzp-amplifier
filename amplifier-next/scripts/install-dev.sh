#!/bin/bash
# Development installation script for Amplifier

echo "Installing Amplifier development environment..."

# Install core in editable mode
echo "Installing amplifier-core..."
pip install -e ./amplifier-core

# Install CLI in editable mode
echo "Installing amplifier-cli..."
pip install -e ./amplifier-cli

# Install all modules in editable mode
for module in amplifier-mod-*; do
    if [ -d "$module" ]; then
        echo "Installing $module..."
        pip install -e ./$module
    fi
done

echo "Installation complete!"
echo ""
echo "Usage examples:"
echo "  amplifier run --config test-full-features.toml --mode chat"
echo "  amplifier run --config test-anthropic-config.toml --mode chat"
echo ""
echo "Commands available:"
echo "  amplifier run --help    # Show all options"
echo "  amplifier module list   # List installed modules"
