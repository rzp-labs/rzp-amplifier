#!/bin/bash
# Development installation script for Amplifier

echo "Installing Amplifier development environment..."

# Install core in editable mode
echo "Installing amplifier-core..."
pip install -e ./amplifier-core

# Install all modules in editable mode
for module in amplifier-mod-*; do
    if [ -d "$module" ]; then
        echo "Installing $module..."
        pip install -e ./$module
    fi
done

echo "Installation complete!"
echo "You can now run: amplifier chat"
