# Amplifier CLI

Command-line interface for the Amplifier AI-powered modular development platform.

## Installation

```bash
# Install from PyPI (when published)
pip install amplifier-cli

# Install from source
pip install -e .

# Or use with uvx directly from GitHub
uvx --from git+https://github.com/microsoft/amplifier-cli amplifier --help
```

## Quick Start

```bash
# Initialize a configuration
amplifier init

# Run a single command
amplifier run "Create a Python function to calculate fibonacci numbers"

# Start interactive chat mode
amplifier run --mode chat

# Use a specific provider
amplifier run --provider anthropic --model claude-sonnet-4.5 "Your prompt"

# List installed modules
amplifier module list

# Get info about a specific module
amplifier module info loop-basic
```

## Configuration

The CLI can be configured via:
- Command-line options (highest priority)
- Configuration file (`amplifier.toml` or custom path via `--config`)
- Environment variables

Example configuration:
```toml
[provider]
name = "anthropic"
model = "claude-sonnet-4.5"

[modules]
orchestrator = "loop-basic"
context = "context-simple"

[session]
max_tokens = 100000
auto_compact = true
```

## Module Management

The CLI provides commands to manage Amplifier modules:

- `amplifier module list` - List all installed modules
- `amplifier module info <name>` - Show detailed module information
- `amplifier module list --type agent` - List modules by type

## Development

This CLI is part of the Amplifier ecosystem. For development:

1. See [amplifier-dev](https://github.com/microsoft/amplifier-dev) for the development workspace
2. See [amplifier-core](https://github.com/microsoft/amplifier-core) for the core library

## License

MIT - See LICENSE file for details
