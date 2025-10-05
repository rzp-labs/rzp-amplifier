# Amplifier Development Workspace

This repository contains all Amplifier repositories as submodules for convenient development.

## Repository Structure

```
amplifier-dev/
├── amplifier-core/           # Ultra-thin core (single maintainer)
├── amplifier-mod-loop-basic/ # Reference agent loop implementation
├── amplifier-mod-provider-anthropic/ # Anthropic provider
├── amplifier-mod-provider-openai/    # OpenAI provider
├── amplifier-mod-tool-filesystem/    # File operations (read, write, edit)
├── amplifier-mod-tool-bash/          # Command execution
├── amplifier-mod-context-simple/     # Basic context manager
├── amplifier-mod-hooks-formatter/    # Auto-formatting hooks
└── scripts/                           # Development utilities
```

## Quick Start

```bash
# Install all modules in development mode
./scripts/install-dev.sh

# Run tests across all modules
./scripts/test-all.sh

# Create a new module from template
./scripts/create-module.sh my-module tool
```

## Development Workflow

1. Clone with submodules:
```bash
git clone --recursive https://github.com/microsoft/amplifier-dev
cd amplifier-dev
```

2. Install core and modules:
```bash
pip install -e ./amplifier-core
pip install -e ./amplifier-mod-*
```

3. Run Amplifier with local modules:
```bash
amplifier --config dev-config.toml "Your prompt"
```

## Creating a New Module

Use the module creation script:
```bash
./scripts/create-module.sh my-tool tool
```

This creates `amplifier-mod-my-tool/` with the appropriate structure.

## Testing

Run all tests:
```bash
pytest
```

Run specific module tests:
```bash
cd amplifier-mod-loop-basic
pytest
```

## Contributing

Each module is a separate repository. To contribute:
1. Fork the specific module repository
2. Make your changes
3. Submit a PR to that module's repo
4. After approval, we'll update the submodule reference here

## License

MIT - See individual repositories for specific licenses.
