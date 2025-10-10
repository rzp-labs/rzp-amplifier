#!/usr/bin/env bash
set -euo pipefail

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "   Amplifier Codespace Post-Create Setup"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Step 1: Configure Git
echo "→ Step 1/5: Configuring Git..."
git config --global push.autoSetupRemote true
echo "  ✓ Git configured"

# Step 2: Setup pnpm (if not already done)
echo ""
echo "→ Step 2/5: Setting up pnpm..."
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

# Step 3: Install project dependencies
echo ""
echo "→ Step 3/4: Installing project dependencies..."
cd /workspaces/amplifier
make install
echo "  ✓ Dependencies installed"

# Step 4: Configure Python venv auto-activation
echo ""
echo "→ Step 4/4: Configuring shell environment..."
BASHRC_PATH="$HOME/.bashrc"

# Add venv auto-activation to .bashrc if not already present
if ! grep -q "# Amplifier: Auto-activate venv" "$BASHRC_PATH" 2>/dev/null; then
    echo "" >> "$BASHRC_PATH"
    echo "# Amplifier: Auto-activate Python virtual environment" >> "$BASHRC_PATH"
    echo "if [ -f /workspaces/amplifier/.venv/bin/activate ] && [ -z \"\$VIRTUAL_ENV\" ]; then" >> "$BASHRC_PATH"
    echo "    source /workspaces/amplifier/.venv/bin/activate" >> "$BASHRC_PATH"
    echo "fi" >> "$BASHRC_PATH"
    echo "  ✓ Added venv auto-activation to .bashrc"
else
    echo "  ✓ venv auto-activation already configured"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "   ✅ Post-Create Setup Complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📝 Next steps:"
echo "   1. Authenticate: gh auth login"
echo "   2. See: ai_working/amplifier-v2/BOOTSTRAP_GUIDE.md"
echo ""
