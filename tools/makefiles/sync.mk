#==============================================================================
# sync.mk - Bidirectional directory synchronization
#
# Provides bidirectional sync capability between local development machines
# and a remote server, with the remote server as the authoritative source.
#
# Use Case:
# - Multiple development machines (e.g., Mac Mini, MacBook Pro)
# - Remote server as source of truth (e.g., Debian VM)
# - Sync .gitignored files (secrets, configs, .env)
# - Exclude build artifacts (node_modules, .venv, etc.)
#
# Configuration:
# Set AMPLIFIER_SYNC_REMOTE in .env or environment:
#   AMPLIFIER_SYNC_REMOTE=user@hostname:/path/to/remote
#
# Optional:
#   AMPLIFIER_SYNC_OPTIONS=additional rsync flags
#
# Dependencies: core.mk
#==============================================================================

.PHONY: sync-setup sync-status sync-pull sync-push sync-pull-dry sync-push-dry

# Rsync flags for sync operations
RSYNC_BASE_FLAGS := -avz --delete --exclude-from=.rsync-exclude
RSYNC_PULL_FLAGS := $(RSYNC_BASE_FLAGS)
RSYNC_PUSH_FLAGS := $(RSYNC_BASE_FLAGS)

# Check if sync is configured
SYNC_CONFIGURED := $(shell [ -n "$(AMPLIFIER_SYNC_REMOTE)" ] && echo "yes" || echo "no")

sync-setup: ## Validate sync dependencies and configuration
	@echo "🔧 Checking sync setup..."
	@echo ""
	@# Check if rsync is installed
	@if ! command -v rsync >/dev/null 2>&1; then \
		echo "❌ rsync not found!"; \
		echo ""; \
		echo "Install rsync:"; \
		echo "  macOS:  brew install rsync"; \
		echo "  Debian: sudo apt install rsync"; \
		echo ""; \
		exit 1; \
	fi
	@echo "✓ rsync found: $$(which rsync)"
	@# Get rsync version information
	@rsync_version=$$(rsync --version 2>&1 | head -1); \
	echo "  Version: $$rsync_version"
	@# Check protocol compatibility
	@protocol_version=$$(rsync --version 2>&1 | grep -oE 'protocol version [0-9]+' | grep -oE '[0-9]+' || echo "unknown"); \
	if [ "$$protocol_version" != "unknown" ]; then \
		if [ $$protocol_version -ge 29 ] && [ $$protocol_version -le 32 ]; then \
			echo "  ✓ Protocol version $$protocol_version (compatible)"; \
		else \
			echo "  ⚠️  Protocol version $$protocol_version (may have compatibility issues)"; \
		fi; \
	fi
	@echo ""
	@# Check if sync is configured
	@if [ "$(SYNC_CONFIGURED)" = "yes" ]; then \
		echo "✓ Sync configured"; \
		echo "  Remote: $(AMPLIFIER_SYNC_REMOTE)"; \
		if [ -n "$(AMPLIFIER_SYNC_OPTIONS)" ]; then \
			echo "  Options: $(AMPLIFIER_SYNC_OPTIONS)"; \
		fi; \
		echo ""; \
		echo "Testing SSH connectivity..."; \
		remote_host=$$(echo "$(AMPLIFIER_SYNC_REMOTE)" | cut -d: -f1); \
		if ssh -o ConnectTimeout=5 -o BatchMode=yes $$remote_host "echo 'SSH connection successful'" 2>/dev/null; then \
			echo "✓ SSH connection successful"; \
		else \
			echo "❌ SSH connection failed"; \
			echo ""; \
			echo "Troubleshooting:"; \
			echo "  1. Verify SSH key is set up: ssh-copy-id $$remote_host"; \
			echo "  2. Test manually: ssh $$remote_host"; \
			echo "  3. Check ~/.ssh/config for host alias"; \
			exit 1; \
		fi; \
	else \
		echo "ℹ️  Sync not configured (optional feature)"; \
		echo ""; \
		echo "To enable sync, add to .env:"; \
		echo "  AMPLIFIER_SYNC_REMOTE=user@hostname:/path/to/remote"; \
		echo ""; \
		echo "Example:"; \
		echo "  AMPLIFIER_SYNC_REMOTE=dev@server.example.com:/home/dev/amplifier"; \
	fi
	@echo ""
	@# Check if exclude file exists
	@if [ ! -f .rsync-exclude ]; then \
		echo "⚠️  .rsync-exclude file not found"; \
		echo "   Sync will include all files (not recommended)"; \
	else \
		echo "✓ .rsync-exclude file found"; \
	fi
	@echo ""
	@echo "✅ Sync setup complete!"

sync-status: ## Show current sync configuration and status
	@echo "Sync Status:"
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo ""
	@if [ "$(SYNC_CONFIGURED)" = "yes" ]; then \
		echo "Configuration:"; \
		echo "  Remote: $(AMPLIFIER_SYNC_REMOTE)"; \
		if [ -n "$(AMPLIFIER_SYNC_OPTIONS)" ]; then \
			echo "  Options: $(AMPLIFIER_SYNC_OPTIONS)"; \
		fi; \
		echo ""; \
		echo "Available commands:"; \
		echo "  make sync-pull      Pull from remote (remote wins)"; \
		echo "  make sync-push      Push to remote"; \
		echo "  make sync-pull-dry  Preview pull (no changes)"; \
		echo "  make sync-push-dry  Preview push (no changes)"; \
	else \
		echo "Sync is not configured."; \
		echo ""; \
		echo "To enable sync, add to .env:"; \
		echo "  AMPLIFIER_SYNC_REMOTE=user@hostname:/path/to/remote"; \
	fi
	@echo ""

sync-pull: ## Pull from remote server (remote always wins on conflicts)
	@if [ "$(SYNC_CONFIGURED)" != "yes" ]; then \
		echo "❌ Sync not configured. Set AMPLIFIER_SYNC_REMOTE in .env"; \
		echo "   Example: AMPLIFIER_SYNC_REMOTE=user@hostname:/path/to/remote"; \
		exit 1; \
	fi
	@echo "📥 Pulling from $(AMPLIFIER_SYNC_REMOTE)..."
	@echo ""
	@rsync $(RSYNC_PULL_FLAGS) $(AMPLIFIER_SYNC_OPTIONS) \
		$(AMPLIFIER_SYNC_REMOTE)/ . \
		--stats
	@echo ""
	@echo "✅ Pull complete! Remote changes applied."

sync-push: ## Push to remote server
	@if [ "$(SYNC_CONFIGURED)" != "yes" ]; then \
		echo "❌ Sync not configured. Set AMPLIFIER_SYNC_REMOTE in .env"; \
		echo "   Example: AMPLIFIER_SYNC_REMOTE=user@hostname:/path/to/remote"; \
		exit 1; \
	fi
	@echo "📤 Pushing to $(AMPLIFIER_SYNC_REMOTE)..."
	@echo ""
	@rsync $(RSYNC_PUSH_FLAGS) $(AMPLIFIER_SYNC_OPTIONS) \
		. $(AMPLIFIER_SYNC_REMOTE)/ \
		--stats
	@echo ""
	@echo "✅ Push complete! Local changes sent to remote."

sync-pull-dry: ## Preview pull operation (no changes made)
	@if [ "$(SYNC_CONFIGURED)" != "yes" ]; then \
		echo "❌ Sync not configured. Set AMPLIFIER_SYNC_REMOTE in .env"; \
		exit 1; \
	fi
	@echo "🔍 Previewing pull from $(AMPLIFIER_SYNC_REMOTE)..."
	@echo ""
	@rsync $(RSYNC_PULL_FLAGS) $(AMPLIFIER_SYNC_OPTIONS) --dry-run \
		$(AMPLIFIER_SYNC_REMOTE)/ . \
		--itemize-changes
	@echo ""
	@echo "ℹ️  This was a dry run. No changes were made."
	@echo "   Run 'make sync-pull' to apply these changes."

sync-push-dry: ## Preview push operation (no changes made)
	@if [ "$(SYNC_CONFIGURED)" != "yes" ]; then \
		echo "❌ Sync not configured. Set AMPLIFIER_SYNC_REMOTE in .env"; \
		exit 1; \
	fi
	@echo "🔍 Previewing push to $(AMPLIFIER_SYNC_REMOTE)..."
	@echo ""
	@rsync $(RSYNC_PUSH_FLAGS) $(AMPLIFIER_SYNC_OPTIONS) --dry-run \
		. $(AMPLIFIER_SYNC_REMOTE)/ \
		--itemize-changes
	@echo ""
	@echo "ℹ️  This was a dry run. No changes were made."
	@echo "   Run 'make sync-push' to apply these changes."
