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
echo "→ Step 3/5: Installing project dependencies..."
cd /workspaces/amplifier
make install
echo "  ✓ Dependencies installed"

# Step 4: Configure shell to unset GITHUB_TOKEN automatically
echo ""
echo "→ Step 4/5: Configuring shell environment..."
BASHRC_PATH="$HOME/.bashrc"

# Add GITHUB_TOKEN unsetting to .bashrc if not already present
if ! grep -q "# Amplifier: Unset GITHUB_TOKEN" "$BASHRC_PATH" 2>/dev/null; then
    echo "" >> "$BASHRC_PATH"
    echo "# Amplifier: Unset GITHUB_TOKEN to prevent conflicts with gh CLI" >> "$BASHRC_PATH"
    echo "# This allows 'gh auth login' to work properly without token interference" >> "$BASHRC_PATH"
    echo "unset GITHUB_TOKEN 2>/dev/null || true" >> "$BASHRC_PATH"
    echo "  ✓ Added GITHUB_TOKEN unsetting to .bashrc"
else
    echo "  ✓ GITHUB_TOKEN unsetting already configured"
fi

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

# Step 5: Create post-setup guide
echo ""
echo "→ Step 5/5: Creating setup guide..."
cat > /workspaces/amplifier/.devcontainer/POST_SETUP_README.md << 'EOF'
# Amplifier Codespace Setup Complete! 🎉

Your development environment is ready. Here's what was configured:

## What Happened Automatically

✅ **Git Configuration** - Auto-create upstream branches on first push
✅ **pnpm Setup** - Configured and updated to latest version
✅ **Dependencies** - All project dependencies installed via `make install`
✅ **Python venv** - Virtual environment created and auto-activation configured
✅ **GITHUB_TOKEN** - Automatically unset in new terminals (prevents gh CLI conflicts)

## Next Steps

### 1. Complete GitHub Authentication

The Codespace automatically provides a GITHUB_TOKEN, but for working with amplifier-dev, you need to authenticate via `gh auth login`:

```bash
gh auth login
```

Follow the prompts to authenticate. This is required for:
- Accessing private repositories
- Managing submodules
- Push/pull operations

### 2. Setup Amplifier-dev (Branch-Specific)

If you're working on the amplifier-v2 branch:

```bash
./ai_working/amplifier-v2/setup-amplifier-dev.sh
```

This will:
- Verify gh authentication
- Update git remotes
- Initialize all submodules
- Configure safe directories

### 3. Start Developing

```bash
claude
```

## Useful Commands

- **Update everything:** `./ai_working/amplifier-v2/freshen-parent.sh`
- **Run checks:** `make check`
- **Run tests:** `make test`
- **See all commands:** `make help`

## Documentation

- **Bootstrap Guide:** `ai_working/amplifier-v2/BOOTSTRAP_GUIDE.md`
- **Git Workflow:** `ai_working/amplifier-v2/git_workflow/SUBMODULE_WORKFLOW.md`

---

**Note:** New terminals will automatically:
- Unset GITHUB_TOKEN (prevents conflicts)
- Activate Python virtual environment

No manual environment setup needed! 🚀
EOF

echo "  ✓ Post-setup guide created"

# Unset GITHUB_TOKEN for this session
unset GITHUB_TOKEN 2>/dev/null || true

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "   ✅ Post-Create Setup Complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📝 Next steps: See POST_SETUP_README.md"
echo ""
