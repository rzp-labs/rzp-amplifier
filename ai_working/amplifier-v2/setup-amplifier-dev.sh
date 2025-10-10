#!/bin/bash
# Amplifier-dev Branch Setup Script
# Automates steps 6-12 of the setup process
# Run this AFTER bootstrap-codespace.sh
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

# Step 6: Unset GITHUB_TOKEN
echo "→ Step 1/7: Clearing GITHUB_TOKEN..."
if [ -n "$GITHUB_TOKEN" ]; then
    unset GITHUB_TOKEN
    echo "  ✓ GITHUB_TOKEN cleared for this session"
    echo "  Note: All new terminals automatically unset GITHUB_TOKEN (configured in .bashrc)"
else
    echo "  ✓ GITHUB_TOKEN not set"
fi

# Step 7: Check gh authentication
echo ""
echo "→ Step 2/7: Checking GitHub CLI authentication..."

# Check if authenticated via gh auth login (not just GITHUB_TOKEN)
# We look for the config file that gh auth login creates
if [ -f "$HOME/.config/gh/hosts.yml" ] && grep -q "oauth_token:" "$HOME/.config/gh/hosts.yml" 2>/dev/null; then
    echo "  ✓ Already authenticated with GitHub CLI (gh auth login)"
elif gh auth status &> /dev/null; then
    echo "  ⚠ Authenticated via GITHUB_TOKEN, but need 'gh auth login'"
    echo ""
    echo "  Please run: gh auth login"
    echo "  This provides proper authentication for submodule access"
    echo "  After authentication, run this script again"
    echo ""
    exit 1
else
    echo "  ⚠ Not authenticated with GitHub CLI"
    echo ""
    echo "  Please run: gh auth login"
    echo "  After authentication, run this script again"
    echo ""
    exit 1
fi

# Step 8: Git fetch all remotes
echo ""
echo "→ Step 3/7: Fetching latest from all remotes..."
git fetch --all -p
echo "  ✓ Remotes updated"

# Step 9: Update parent submodules
echo ""
echo "→ Step 4/7: Updating parent repository submodules..."
git submodule sync && git submodule update --init
echo "  ✓ Parent submodules updated"

# Step 10-11: Configure amplifier-dev as safe directory
echo ""
echo "→ Step 5/7: Configuring amplifier-dev as safe directory..."
AMPLIFIER_DEV_PATH="$(pwd)/amplifier-dev"

# Check if already configured
if git config --global --get-all safe.directory | grep -q "^$AMPLIFIER_DEV_PATH$"; then
    echo "  ✓ Already configured as safe directory"
else
    git config --global --add safe.directory "$AMPLIFIER_DEV_PATH"
    echo "  ✓ Added to safe directories"
fi

# Step 12: Update amplifier-dev submodules
echo ""
echo "→ Step 6/7: Entering amplifier-dev and updating submodules..."
cd amplifier-dev

# Sync and update all submodules
echo "  Syncing submodule configurations..."
git submodule sync

echo "  Updating submodules (this may take a moment)..."
git submodule update --init --recursive

echo "  ✓ amplifier-dev submodules updated"

# Final step: Return to root
cd ..

echo ""
echo "→ Step 7/7: Verifying setup..."
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
echo "Next steps:"
echo "  1. Ensure virtual environment is activated:"
echo "     source .venv/bin/activate"
echo ""
echo "  2. Start Claude Code:"
echo "     claude"
echo ""
echo "Useful commands:"
echo "  • Update everything:  ./ai_working/amplifier-v2/freshen-parent.sh"
echo "  • Push changes:       ./ai_working/amplifier-v2/push-parent.sh"
echo "  • Full workflow:      See ai_working/amplifier-v2/BOOTSTRAP_GUIDE.md"
echo ""
