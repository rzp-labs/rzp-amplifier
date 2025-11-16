# Bidirectional Sync for Multi-Machine Development

## Overview

Amplifier includes optional bidirectional sync functionality to help developers working across multiple machines (e.g., desktop workstation, laptop) keep their project synchronized with a remote server acting as the source of truth.

### Why Use Sync?

**Problem**: When developing across multiple machines, `.gitignored` files (secrets, configs, `.env` files) don't transfer via Git. Manually managing these files leads to:
- Missing configuration errors
- Time wasted troubleshooting "works on my other machine" issues
- Risk of accidentally committing secrets while trying to share them

**Solution**: Use rsync-based bidirectional sync to:
- Sync `.gitignored` files (secrets, configs, `.env`) between machines
- Exclude build artifacts (node_modules, .venv, etc.)
- Use a remote server as the authoritative source
- Resolve conflicts automatically (remote always wins)

## Architecture

```
┌─────────────┐         ┌─────────────┐         ┌─────────────┐
│  Mac Mini   │◄───────►│   Debian    │◄───────►│  MacBook    │
│   (Dev 1)   │  rsync  │     VM      │  rsync  │  Pro (Dev2) │
│             │         │  (Source)   │         │             │
└─────────────┘         └─────────────┘         └─────────────┘
```

**Workflow**:
1. **Before work**: Pull from remote (`make sync-pull`)
2. **During work**: Edit files locally
3. **After work**: Push to remote (`make sync-push`)
4. **Other machine**: Pull from remote to get latest changes

## Setup

### Prerequisites

1. **SSH access** to your remote server with key-based authentication
2. **rsync** installed on all machines (typically pre-installed)

### Initial Configuration

1. **Set up SSH keys** (if not already done):

   ```bash
   # Generate SSH key if needed
   ssh-keygen -t ed25519 -C "your_email@example.com"
   
   # Copy to remote server
   ssh-copy-id user@your-server.example.com
   
   # Test connection
   ssh user@your-server.example.com "echo 'SSH works!'"
   ```

2. **Configure sync in `.env`**:

   ```bash
   # Copy example file
   cp .env.example .env
   
   # Edit .env and add:
   AMPLIFIER_SYNC_REMOTE=user@your-server.example.com:/path/to/project
   ```

   Example:
   ```bash
   AMPLIFIER_SYNC_REMOTE=dev@server.example.com:/home/dev/amplifier
   ```

3. **Verify setup**:

   ```bash
   make sync-setup
   ```

   This will:
   - Check rsync is installed
   - Verify protocol compatibility
   - Test SSH connectivity
   - Confirm `.rsync-exclude` exists

## Usage

### Common Commands

```bash
# Check sync configuration and status
make sync-status

# Pull from remote (remote always wins on conflicts)
make sync-pull

# Push to remote
make sync-push

# Preview pull without making changes
make sync-pull-dry

# Preview push without making changes
make sync-push-dry
```

### Typical Workflow

**Starting work on Machine A**:
```bash
# Get latest from remote
make sync-pull

# Work on your changes
# ... edit files ...

# Push changes to remote when done
make sync-push
```

**Switching to Machine B**:
```bash
# Get latest from remote (includes changes from Machine A)
make sync-pull

# Continue work
# ... edit files ...

# Push when done
make sync-push
```

### Conflict Resolution

**Strategy**: Remote always wins

- On `make sync-pull`: Remote files overwrite local files if different
- On `make sync-push`: Local files overwrite remote files

**Best Practice**: Always pull before starting work to minimize conflicts.

## What Gets Synced

### Included (✅)

- All source code files
- Configuration files (including `.gitignored` ones)
- Secrets and API keys in `.env`
- Documentation
- Project-specific data in `.data/`

### Excluded (❌)

The following are excluded via `.rsync-exclude`:

- Build artifacts: `dist/`, `build/`, `output/`
- Dependencies: `node_modules/`, `.venv/`, `venv/`
- Cache directories: `__pycache__/`, `.cache/`, `.ruff_cache/`
- Git directory: `.git/`
- SSH keys: `.ssh/`, `**/.ssh/`
- OS files: `.DS_Store`, `Thumbs.db`
- Logs: `*.log`, `logs/`
- Databases: `*.db`, `*.sqlite`
- Machine-specific state: `.amplifier/local`, `.amplifier/transcripts`

### Customizing Exclusions

Edit `.rsync-exclude` to customize what gets excluded:

```bash
# Add your own patterns
echo "my-local-only-dir/" >> .rsync-exclude

# Comment out to sync data directory
# Edit .rsync-exclude and comment: # .data/
```

## Security Considerations

### ⚠️ Important Security Notes

1. **SSH Keys**: Ensure your SSH keys are properly secured with passphrases
2. **Secrets in Transit**: rsync transfers are encrypted via SSH
3. **Access Control**: Only sync with trusted remote servers you control
4. **Audit Trail**: Consider logging sync operations in sensitive environments

### Best Practices

- Use dedicated SSH keys for sync operations
- Restrict SSH key permissions to specific commands if possible
- Regularly audit what files are being synced
- Use `make sync-pull-dry` and `make sync-push-dry` to preview changes
- Keep remote server access restricted to authorized users

## Troubleshooting

### SSH Connection Fails

**Symptom**: `make sync-setup` reports "SSH connection failed"

**Solutions**:
1. Verify SSH key is set up: `ssh user@your-server "echo works"`
2. Check SSH config for host aliases: `cat ~/.ssh/config`
3. Ensure remote host is in known_hosts: `ssh-keyscan -H your-server >> ~/.ssh/known_hosts`

### Permission Denied Errors

**Symptom**: rsync reports "Permission denied" errors

**Solutions**:
1. Verify remote directory permissions: `ssh user@server "ls -la /path/to/project"`
2. Check if directories are owned by your user
3. Add problematic paths to `.rsync-exclude`

### Version Incompatibility

**Symptom**: `make sync-setup` warns about protocol version

**macOS**: System uses openrsync (protocol 29)
**Linux**: Typically uses GNU rsync (protocol 32)

**Solution**: These are compatible. Warning is informational only.

To upgrade macOS to GNU rsync:
```bash
brew install rsync
# Add to PATH: /opt/homebrew/bin before /usr/bin
```

### Files Not Syncing

**Symptom**: Some files don't appear after sync

**Solutions**:
1. Check if file matches pattern in `.rsync-exclude`
2. Use `make sync-pull-dry` to see what would be transferred
3. Check remote file permissions
4. Verify file exists on remote: `ssh user@server "ls -la /path/to/file"`

### Slow Sync Performance

**Solutions**:
1. Check network connection speed
2. Large binary files? Consider excluding them
3. Use compression: `AMPLIFIER_SYNC_OPTIONS="-z" make sync-pull`
4. Consider initial sync over faster network, then use for deltas

## Version Compatibility Matrix

| Platform | rsync Version | Protocol | Status |
|----------|---------------|----------|--------|
| macOS (system) | openrsync 2.6.9 | 29 | ✅ Compatible |
| macOS (homebrew) | rsync 3.x | 30-32 | ✅ Compatible |
| Debian/Ubuntu | rsync 3.2+ | 31-32 | ✅ Compatible |
| WSL2 (Ubuntu) | rsync 3.2+ | 31-32 | ✅ Compatible |

**Note**: rsync protocols 29-32 are backward compatible for basic sync operations.

## Advanced Configuration

### Custom rsync Options

Add custom flags via environment variable:

```bash
# In .env
AMPLIFIER_SYNC_OPTIONS=--verbose --progress --human-readable
```

Common options:
- `--verbose` : Show detailed file transfer information
- `--progress` : Show progress during transfer
- `--human-readable` : Display sizes in human-readable format
- `--compress` : Additional compression (may slow down on fast networks)
- `--bwlimit=RATE` : Limit bandwidth usage (e.g., --bwlimit=1000 for 1MB/s)

### SSH Connection Options

Configure SSH behavior in `~/.ssh/config`:

```ssh-config
Host my-dev-server
    HostName server.example.com
    User dev
    Port 22
    IdentityFile ~/.ssh/id_ed25519
    Compression yes
    ServerAliveInterval 60
```

Then use alias in .env:
```bash
AMPLIFIER_SYNC_REMOTE=my-dev-server:/home/dev/amplifier
```

## Alternative Approaches

If sync doesn't fit your workflow, consider:

1. **Git-based**: Use git + git-crypt for secrets
2. **Cloud sync**: Dropbox/Google Drive (risk of conflicts)
3. **Remote development**: Use VS Code Remote SSH
4. **Container-based**: Develop in containers with volume mounts

## FAQ

**Q: Can I sync between two local machines without a remote server?**

A: Yes, but you need one machine to act as the "remote". SSH from Machine A to Machine B directly.

**Q: What happens if I forget to pull before working?**

A: Your changes will overwrite remote when you push. Always pull first to minimize conflicts.

**Q: Can I use this with more than 2 machines?**

A: Yes! All machines sync with the same remote server. Always pull before working.

**Q: Does this replace Git?**

A: No! This syncs `.gitignored` files. Continue using Git for version control of source code.

**Q: What if my .env file has machine-specific settings?**

A: Use `.env.local` for machine-specific settings and exclude it from sync:
```bash
echo ".env.local" >> .rsync-exclude
```

**Q: Can I automate sync (auto-pull/push on file changes)?**

A: Currently manual only. Future versions may add watch-mode for automatic sync.

## Support

For issues or questions:
1. Run `make sync-setup` to verify configuration
2. Check logs and error messages
3. Review this documentation
4. Open an issue on GitHub with details
