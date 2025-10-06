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

> [!NOTE]
> This project is not currently accepting external contributions, but we're actively working toward opening this up. We value community input and look forward to collaborating in the future. For now, feel free to fork and experiment!

Most contributions require you to agree to a
Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us
the rights to use your contribution. For details, visit [Contributor License Agreements](https://cla.opensource.microsoft.com).

When you submit a pull request, a CLA bot will automatically determine whether you need to provide
a CLA and decorate the PR appropriately (e.g., status check, comment). Simply follow the instructions
provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or
contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.

## Trademarks

This project may contain trademarks or logos for projects, products, or services. Authorized use of Microsoft
trademarks or logos is subject to and must follow
[Microsoft's Trademark & Brand Guidelines](https://www.microsoft.com/legal/intellectualproperty/trademarks/usage/general).
Use of Microsoft trademarks or logos in modified versions of this project must not cause confusion or imply Microsoft sponsorship.
Any use of third-party trademarks or logos are subject to those third-party's policies.
