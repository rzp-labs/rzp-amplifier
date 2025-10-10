#!/usr/bin/env bash
set -euo pipefail

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "   Amplifier Codespace Post-Create Setup"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Step 1: Setup pnpm
echo "→ Step 1/4: Setting up pnpm..."
if ! command -v pnpm &> /dev/null; then
    echo "  Installing pnpm globally..."
    npm install -g pnpm || {
        echo "  ❌ Failed to install pnpm"
        exit 1
    }
fi

echo "  Configuring pnpm environment..."
# Run pnpm setup and capture the shell commands it outputs
PNPM_HOME="${PNPM_HOME:-$HOME/.local/share/pnpm}"
export PNPM_HOME
export PATH="$PNPM_HOME:$PATH"

# Ensure pnpm setup modifies bashrc
pnpm setup || {
    echo "  ❌ pnpm setup failed"
    exit 1
}

# Manually add pnpm to current script's PATH
if [ -d "$PNPM_HOME" ]; then
    export PATH="$PNPM_HOME:$PATH"
    echo "  Added $PNPM_HOME to PATH for this session"
fi

# Verify pnpm is now available
if ! command -v pnpm &> /dev/null; then
    echo "  ❌ pnpm still not in PATH after setup"
    echo "  PATH: $PATH"
    exit 1
fi

echo "  Updating pnpm..."
pnpm self-update || echo "  ⚠ pnpm self-update failed (non-critical)"
echo "  ✓ pnpm configured (version: $(pnpm --version))"

# Step 2: Install project dependencies
echo ""
echo "→ Step 2/4: Installing project dependencies..."
cd /workspaces/amplifier || {
    echo "  ❌ Failed to cd to /workspaces/amplifier"
    exit 1
}

# Run make install and capture any errors
make install || {
    echo "  ❌ make install failed"
    echo "  Check if Makefile exists and all dependencies are available"
    exit 1
}
echo "  ✓ Dependencies installed"

# Step 3: Check Python virtual environment (don't activate - just verify)
echo ""
echo "→ Step 3/4: Checking Python virtual environment..."
if [ -f .venv/bin/activate ]; then
    echo "  ✓ Virtual environment exists at .venv"
    echo "  Python in venv: $(.venv/bin/python --version 2>&1 || echo 'Failed to get version')"
else
    echo "  ❌ No virtual environment found (.venv/bin/activate missing)"
    echo "  make install should have created this"
    exit 1
fi

# Step 4: Final verification
echo ""
echo "→ Step 4/4: Verifying setup..."
echo "  System Python: $(which python 2>/dev/null || echo 'not found')"
echo "  Venv Python: $(ls -la .venv/bin/python 2>/dev/null || echo 'not found')"
echo "  pnpm: $(which pnpm 2>/dev/null || echo 'not found') $(pnpm --version 2>/dev/null || echo '')"
echo "  Node: $(which node 2>/dev/null || echo 'not found') $(node --version 2>/dev/null || echo '')"

# Check if claude is available globally via pnpm
if command -v claude &> /dev/null; then
    echo "  claude: $(which claude) (version: $(claude --version 2>/dev/null || echo 'unknown'))"
else
    echo "  claude: Will be available after environment activation"
fi

echo ""
echo "→ Step 5/5: Configuring shell environment..."

# Ensure .bashrc has pnpm PATH (idempotent check)
if ! grep -q "# pnpm" ~/.bashrc 2>/dev/null; then
    echo "  Adding pnpm to .bashrc..."
    cat >> ~/.bashrc << 'EOF'

# pnpm
export PNPM_HOME="$HOME/.local/share/pnpm"
case ":$PATH:" in
  *":$PNPM_HOME:"*) ;;
  *) export PATH="$PNPM_HOME:$PATH" ;;
esac
# pnpm end
EOF
else
    echo "  ✓ pnpm already configured in .bashrc"
fi

# Ensure .bashrc activates venv (idempotent check)
if ! grep -q "amplifier/.venv/bin/activate" ~/.bashrc 2>/dev/null; then
    echo "  Adding venv activation to .bashrc..."
    cat >> ~/.bashrc << 'EOF'

# Amplifier Python virtual environment
if [ -f /workspaces/amplifier/.venv/bin/activate ]; then
    source /workspaces/amplifier/.venv/bin/activate
fi
EOF
else
    echo "  ✓ venv activation already configured in .bashrc"
fi

echo "  ✓ Shell environment configured"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "   ✅ Post-Create Setup Complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🎯 Environment is ready!"
echo ""
echo "To activate in THIS terminal, run:"
echo "   source ~/.bashrc"
echo ""
echo "New terminals will have the environment activated automatically."
echo ""
