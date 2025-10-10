#!/bin/bash
# Complete Codespace Setup - For amplifier-v2 branch
# NOTE: Universal setup now runs automatically via .devcontainer/post-create.sh
# This script only handles branch-specific setup
# For fresh Codespaces, post-create.sh runs first, then use this for branch setup

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "   Amplifier-v2 Branch Setup"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Note: Universal setup runs automatically in fresh Codespaces"
echo "      via .devcontainer/post-create.sh"
echo ""

cd "$PROJECT_ROOT"

# Check if universal setup has run
if [ ! -f ".venv/bin/activate" ]; then
    echo "⚠️  Virtual environment not found!"
    echo ""
    echo "Running universal setup first..."
    ./.devcontainer/post-create.sh
    echo ""
fi

# Check if venv needs activation
if [ -z "$VIRTUAL_ENV" ]; then
    echo "Activating virtual environment..."
    source .venv/bin/activate
    echo ""
fi

# Phase 2: Amplifier-dev setup
echo ""
echo "═══════════════════════════════════════════════════"
echo " Phase 2: Amplifier-dev Setup"
echo "═══════════════════════════════════════════════════"
echo ""

# Check gh auth before proceeding
if ! gh auth status &> /dev/null; then
    echo "⚠ GitHub CLI authentication required"
    echo ""
    echo "Please authenticate with GitHub:"
    echo ""
    read -p "Press Enter to start authentication (or Ctrl+C to cancel)..."
    gh auth login
    echo ""
fi

bash "$SCRIPT_DIR/setup-amplifier-dev.sh"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "   🎉 Complete Setup Finished!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Your Codespace is ready! Start Claude Code:"
echo "  claude"
echo ""
