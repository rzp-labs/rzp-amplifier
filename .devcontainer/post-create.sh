#!/usr/bin/env bash
set -euo pipefail

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "   Amplifier Codespace Post-Create Setup"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Step 1: Setup pnpm
echo "→ Step 1/4: Setting up pnpm..."
if ! command -v pnpm &> /dev/null; then
    echo "  Installing pnpm..."
    npm install -g pnpm
fi

echo "  Configuring pnpm..."
pnpm setup

# Source bashrc to get pnpm in PATH
echo "  Loading pnpm PATH..."
source /home/vscode/.bashrc

echo "  Updating pnpm..."
pnpm self-update
echo "  ✓ pnpm configured and updated"

# Step 2: Install project dependencies
echo ""
echo "→ Step 2/4: Installing project dependencies..."
cd /workspaces/amplifier
make install
echo "  ✓ Dependencies installed"

# Step 3: Activate Python virtual environment
echo ""
echo "→ Step 3/4: Activating Python virtual environment..."
if [ -f .venv/bin/activate ]; then
    source .venv/bin/activate
    echo "  ✓ Virtual environment activated"
else
    echo "  ⚠ No virtual environment found (.venv/bin/activate missing)"
fi

# Step 4: Final check
echo ""
echo "→ Step 4/4: Verifying setup..."
echo "  Python: $(which python)"
echo "  pnpm: $(which pnpm)"
if command -v claude &> /dev/null; then
    echo "  claude: $(which claude)"
else
    echo "  claude: Not yet available (run setup-amplifier-dev.sh)"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "   ✅ Post-Create Setup Complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📝 Next steps:"
echo "   1. Run: ./ai_working/amplifier-v2/setup-amplifier-dev.sh"
echo "   2. See: ai_working/amplifier-v2/BOOTSTRAP_GUIDE.md"
echo ""
