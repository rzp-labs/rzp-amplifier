#!/bin/bash
# Amplifier-dev Branch Setup Script
# Automates amplifier-dev submodule initialization
# Run this AFTER .devcontainer/post-create.sh
# Safe to run multiple times (idempotent)

set -e  # Exit on error

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "   Amplifier-dev Setup"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Verify we're in the right place
if [ ! -d "amplifier-dev" ]; then
    echo "✗ Error: amplifier-dev directory not found"
    echo "  Are you in the project root? ($(pwd))"
    exit 1
fi

# Step 1: Verify authentication
echo "→ Step 1/4: Verifying authentication..."
if [ -n "${GITHUB_TOKEN:-}" ]; then
    echo "  ✓ Using GITHUB_TOKEN (Codespace environment)"
elif gh auth status &> /dev/null; then
    echo "  ✓ Authenticated with GitHub CLI"
else
    echo "  ✗ Not authenticated"
    echo ""
    echo "  Please run: gh auth login"
    echo "  After authentication, run this script again"
    echo ""
    exit 1
fi

# Step 2: Git fetch all remotes
echo ""
echo "→ Step 2/4: Fetching latest from all remotes..."
git fetch --all -p
echo "  ✓ Remotes updated"

# Step 3: Enter amplifier-dev and update submodules
echo ""
echo "→ Step 3/4: Entering amplifier-dev and updating submodules..."
cd amplifier-dev

# Sync and update all submodules
echo "  Syncing submodule configurations..."
git submodule sync

echo "  Updating submodules (this may take a moment)..."
git submodule update --init --recursive

# Mark all nested submodules as safe
echo "  Marking all nested submodules as safe..."
git submodule foreach --recursive 'git config --global --add safe.directory "$toplevel/$sm_path"'

echo "  ✓ amplifier-dev submodules updated"

# Return to root
cd ..

# Step 4: Verify setup
echo ""
echo "→ Step 4/4: Verifying setup..."
echo "  Parent repository: $(pwd)"
echo "  Submodule status:"
git submodule status | head -5
if [ $(git submodule status | wc -l) -gt 5 ]; then
    echo "  ... and $(( $(git submodule status | wc -l) - 5 )) more"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "   ✅ Amplifier-dev Setup Complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Your environment is ready! To activate it in THIS terminal:"
echo "  source ~/.amplifier-env"
echo ""
echo "Then you can start Claude Code:"
echo "  claude"
echo ""
echo "Useful commands:"
echo "  • Update everything:  ./ai_working/amplifier-v2/freshen-parent.sh"
echo "  • Push changes:       ./ai_working/amplifier-v2/push-parent.sh"
echo "  • Full workflow:      See ai_working/amplifier-v2/BOOTSTRAP_GUIDE.md"
echo ""
echo "Note: New terminals will have the environment activated automatically."
echo ""
