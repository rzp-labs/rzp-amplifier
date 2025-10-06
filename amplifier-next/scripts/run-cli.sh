#!/bin/bash
# Run the amplifier CLI with proper Python path setup

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Set up Python path to include amplifier-core and amplifier-cli
export PYTHONPATH="$PROJECT_ROOT/amplifier-core:$PROJECT_ROOT/amplifier-cli:$PYTHONPATH"

# Also include user site-packages for dependencies like tomli
export PYTHONPATH="/home/vscode/.local/lib/python3.11/site-packages:$PYTHONPATH"

# Run the CLI with all arguments passed through
cd "$PROJECT_ROOT/amplifier-cli" && python -m amplifier_cli "$@"