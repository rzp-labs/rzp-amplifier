# Amplifier

AI-powered modular development platform that brings the power of AI coding assistants to your fingertips.

## 🚀 Quick Start

The fastest way to try Amplifier - no installation required:

```bash
# Run directly with uvx (Python 3.11+ required)
uvx --from git+https://github.com/microsoft/amplifier.git amplifier run "Create a Python web server"

# Or install globally
pip install git+https://github.com/microsoft/amplifier.git

# Then run
amplifier run "Write a function to parse CSV files"
```

## 🎯 What is Amplifier?

Amplifier is a modular AI development assistant that helps you:
- Generate code with AI assistance
- Work with multiple AI providers (Anthropic Claude, OpenAI GPT, etc.)
- Extend functionality through a rich module ecosystem
- Maintain context across long development sessions

## 📦 Installation Options

### Quick Try (No Installation)
```bash
# Requires Python 3.11+ and uvx
uvx --from git+https://github.com/microsoft/amplifier.git amplifier --help
```

### Standard Installation
```bash
# Install with default modules
pip install "amplifier[default] @ git+https://github.com/microsoft/amplifier.git"

# Install with Anthropic support
pip install "amplifier[anthropic] @ git+https://github.com/microsoft/amplifier.git"

# Install with all providers
pip install "amplifier[all] @ git+https://github.com/microsoft/amplifier.git"
```

### Development Installation
```bash
# Clone and install for development
git clone https://github.com/microsoft/amplifier.git
cd amplifier
pip install -e ".[all]"
```

## 🎮 Usage Examples

### Interactive Chat Mode
```bash
# Start an interactive session
amplifier run --mode chat

# With specific provider
amplifier run --mode chat --provider anthropic --model claude-sonnet-4.5
```

### Single Command Mode
```bash
# Execute a single task
amplifier run "Create a REST API with FastAPI"

# Use configuration file
amplifier run --config my-config.toml "Refactor this function"
```

### Module Management
```bash
# List available modules
amplifier module list

# Get module information
amplifier module info loop-basic
```

## ⚙️ Configuration

Create an `amplifier.toml` configuration file:

```toml
[provider]
name = "anthropic"  # or "openai", "mock" for testing
model = "claude-sonnet-4.5"

[modules]
orchestrator = "loop-basic"
context = "context-simple"

[session]
max_tokens = 100000
auto_compact = true
compact_threshold = 0.9
```

### Environment Variables

Set API keys for providers:
```bash
export ANTHROPIC_API_KEY="your-api-key"
export OPENAI_API_KEY="your-api-key"
```

## 🧩 Modules

Amplifier uses a modular architecture. Default modules include:

- **Orchestrators**: Control the AI agent loop
  - `loop-basic`: Standard sequential execution
  - `loop-streaming`: Real-time streaming responses
  
- **Providers**: Connect to AI models
  - `provider-anthropic`: Claude models
  - `provider-openai`: GPT models
  
- **Tools**: Extend capabilities
  - `tool-filesystem`: File operations
  - `tool-bash`: Command execution
  - `tool-web`: Web search and fetch

## 📚 Documentation

- [User Guide](./docs/USER_GUIDE.md) - Complete usage documentation
- [Module Catalog](./docs/MODULES.md) - Available modules and their features
- [Configuration Guide](./docs/CONFIG.md) - Detailed configuration options

## 🛠 For Developers

Want to build your own modules or contribute?

- **Development Workspace**: [microsoft/amplifier-dev](https://github.com/microsoft/amplifier-dev)
- **Core Library**: [microsoft/amplifier-core](https://github.com/microsoft/amplifier-core)
- **Module Development Guide**: [docs/DEVELOPER.md](./docs/DEVELOPER.md)

## 🤝 Community

- [Discussions](https://github.com/microsoft/amplifier/discussions) - Ask questions and share ideas
- [Issues](https://github.com/microsoft/amplifier/issues) - Report bugs or request features
- [Module Showcase](./docs/SHOWCASE.md) - Community-created modules

## 📄 License

MIT License - See [LICENSE](./LICENSE) file for details.

## 🎉 Getting Started

Ready to amplify your development? Try this:

```bash
# Your first Amplifier command
uvx --from git+https://github.com/microsoft/amplifier.git amplifier run \
  "Create a Python script that fetches weather data and sends a summary email"
```

Welcome to the future of AI-assisted development! 🚀
