#!/usr/bin/env bash
set -euo pipefail

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "   Amplifier Codespace Post-Create Setup"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Step 1: Configure Git and Authentication
echo "→ Step 1/6: Configuring Git and authentication..."
git config --global push.autoSetupRemote true

# Handle authentication - work with Codespace environment
if [ -n "${GITHUB_TOKEN:-}" ]; then
    echo "  ✓ Using GITHUB_TOKEN for authentication (Codespace environment)"
    # Configure git to use the token for GitHub access
    git config --global url."https://${GITHUB_TOKEN}@github.com/".insteadOf "https://github.com/"
else
    echo "  ⚠ No GITHUB_TOKEN found. Please run: gh auth login"
fi

# Mark parent repository as safe directory (BEFORE any git operations)
echo "  Marking repository as safe directory..."
git config --global --add safe.directory /workspaces/amplifier
echo "  ✓ Git configured"

# Step 2: Initialize parent submodules
echo ""
echo "→ Step 2/6: Initializing parent submodules..."
cd /workspaces/amplifier
git submodule update --init
echo "  ✓ Parent submodules initialized"

# Mark all submodules as safe directories
echo "  Marking all submodules as safe directories..."
git submodule foreach 'git config --global --add safe.directory "$toplevel/$sm_path"'
echo "  ✓ All submodules marked as safe"

# Step 3: Setup pnpm
echo ""
echo "→ Step 3/6: Setting up pnpm..."
if ! command -v pnpm &> /dev/null; then
    echo "  Installing pnpm..."
    npm install -g pnpm
fi

# Check if pnpm is configured
if [ ! -d "$HOME/.local/share/pnpm" ]; then
    echo "  Configuring pnpm..."
    pnpm setup
    # Source bashrc to get pnpm in PATH for this script
    export PNPM_HOME="$HOME/.local/share/pnpm"
    case ":$PATH:" in
        *":$PNPM_HOME:"*) ;;
        *) export PATH="$PNPM_HOME:$PATH" ;;
    esac
    echo "  ✓ pnpm configured"
else
    echo "  ✓ pnpm already configured"
fi

# Update pnpm
echo "  Updating pnpm..."
pnpm self-update
echo "  ✓ pnpm updated"

# Step 4: Install project dependencies
echo ""
echo "→ Step 4/6: Installing project dependencies..."
cd /workspaces/amplifier
make install
echo "  ✓ Dependencies installed"

# Step 5: Create environment setup file
echo ""
echo "→ Step 5/6: Creating environment setup file..."
cat > "$HOME/.amplifier-env" << 'EOF'
# Amplifier Development Environment
# This file is sourced automatically in new terminals via .bashrc

# Python virtual environment
if [ -f "/workspaces/amplifier/.venv/bin/activate" ] && [ -z "$VIRTUAL_ENV" ]; then
    source /workspaces/amplifier/.venv/bin/activate
fi

# pnpm/claude path
export PNPM_HOME="$HOME/.local/share/pnpm"
case ":$PATH:" in
    *":$PNPM_HOME:"*) ;;
    *) export PATH="$PNPM_HOME:$PATH" ;;
esac

# Environment variables
export AMPLIFIER_ROOT="/workspaces/amplifier"
export AMPLIFIER_DEV="$AMPLIFIER_ROOT/amplifier-dev"

# Convenience aliases
alias amp-env='source ~/.amplifier-env'
alias amp-dev='cd $AMPLIFIER_DEV'
alias amp-root='cd $AMPLIFIER_ROOT'
EOF

# Add to .bashrc for persistence if not already present
BASHRC_PATH="$HOME/.bashrc"
if ! grep -q "source ~/.amplifier-env" "$BASHRC_PATH" 2>/dev/null; then
    echo "" >> "$BASHRC_PATH"
    echo "# Amplifier development environment" >> "$BASHRC_PATH"
    echo "if [ -f ~/.amplifier-env ]; then" >> "$BASHRC_PATH"
    echo "    source ~/.amplifier-env" >> "$BASHRC_PATH"
    echo "fi" >> "$BASHRC_PATH"
    echo "  ✓ Environment file created and linked in .bashrc"
else
    echo "  ✓ Environment file created (.bashrc already configured)"
fi

# Step 6: Source environment for this script
echo ""
echo "→ Step 6/6: Loading environment..."
source "$HOME/.amplifier-env"
echo "  ✓ Environment loaded"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "   ✅ Post-Create Setup Complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📝 To activate environment in THIS terminal, run:"
echo "   source ~/.amplifier-env"
echo ""
echo "📝 Next steps:"
echo "   1. Run: ./ai_working/amplifier-v2/setup-amplifier-dev.sh"
echo "   2. See: ai_working/amplifier-v2/BOOTSTRAP_GUIDE.md"
echo ""
echo "Note: New terminals will have the environment activated automatically."
echo ""
