# Amplifier v2 Usage Guide

This guide shows you how to use the amplifier system with real API providers (Anthropic and OpenAI).

## Prerequisites

1. **API Keys**: You need API keys from Anthropic and/or OpenAI. These should already be set in your environment:
   ```bash
   export ANTHROPIC_API_KEY="your-key-here"
   export OPENAI_API_KEY="your-key-here"
   ```

2. **Installation**: The amplifier CLI should already be installed and available in your PATH.

## Quick Start

### 1. Using Anthropic (Claude)

Create a config file `anthropic-config.toml`:

```toml
[provider]
name = "anthropic"
model = "claude-sonnet-4-5"

[modules]
orchestrator = "loop-basic"
context = "context-simple"
tools = ["filesystem", "bash"]

[session]
max_tokens = 100000
auto_compact = true
compact_threshold = 0.9
timeout = 3600

[logging]
level = "INFO"
```

Run a query:

```bash
amplifier run --config anthropic-config.toml "Write a hello world function in Python"
```

### 2. Using OpenAI (GPT-4)

Create a config file `openai-config.toml`:

```toml
[provider]
name = "openai"
model = "gpt-4o"

[modules]
orchestrator = "loop-basic"
context = "context-simple"
tools = ["filesystem", "bash"]

[session]
max_tokens = 100000
auto_compact = true
compact_threshold = 0.9
timeout = 3600

[logging]
level = "INFO"
```

Run a query:

```bash
amplifier run --config openai-config.toml "What is the capital of France?"
```

## Configuration Options

### Provider Section

The `[provider]` section specifies which LLM provider to use:

- **name**: Provider name (`"anthropic"`, `"openai"`, or `"mock"`)
- **model**: Model identifier (e.g., `"claude-sonnet-4-5"`, `"gpt-4o"`)

### Modules Section

The `[modules]` section specifies which amplifier modules to use:

- **orchestrator**: The main loop orchestrator (default: `"loop-basic"`)
- **context**: Context manager for conversation history (default: `"context-simple"`)
- **tools**: List of tools available to the agent (e.g., `["filesystem", "bash"]`)

### Session Section

The `[session]` section controls session behavior:

- **max_tokens**: Maximum tokens before compaction (default: 100000)
- **auto_compact**: Enable automatic context compaction (default: true)
- **compact_threshold**: Threshold for compaction (0.0-1.0, default: 0.9)
- **timeout**: Session timeout in seconds (default: 3600)

## Available Modules

### Orchestrators
- `loop-basic`: Basic agent loop (recommended)
- `loop-streaming`: Streaming responses

### Context Managers
- `context-simple`: Simple context manager (recommended)

### Tools
- `filesystem`: File system operations
- `bash`: Bash command execution
- `web`: Web scraping and HTTP requests

### Providers
- `provider-anthropic`: Anthropic Claude API
- `provider-openai`: OpenAI GPT API
- `provider-mock`: Mock provider for testing (returns "Task completed successfully")

## Programmatic Usage

You can also use amplifier as a Python library:

```python
import asyncio
from amplifier_core import AmplifierSession

async def main():
    config = {
        "session": {
            "orchestrator": "loop-basic",
            "context": "context-simple"
        },
        "context": {
            "config": {
                "max_tokens": 200_000,
                "compact_threshold": 0.92
            }
        },
        "providers": [
            {
                "module": "provider-anthropic",
                "config": {"model": "claude-sonnet-4-5"}
            }
        ],
        "tools": [],
        "agents": [],
        "hooks": []
    }

    session = AmplifierSession(config)
    await session.initialize()

    result = await session.execute("Write a hello world function in Python")
    print(result)

    await session.cleanup()

asyncio.run(main())
```

## Testing

Test scripts are provided in `amplifier-next/`:

- `test_anthropic.py`: Test Anthropic provider
- `test_openai.py`: Test OpenAI provider

Run them with:

```bash
cd amplifier-next
python test_anthropic.py
python test_openai.py
```

## Troubleshooting

### "No providers mounted" error

This was a bug in the CLI that has been fixed. Make sure you're using the latest version where:
1. Config is properly passed to `AmplifierSession`
2. The `--provider` option doesn't override config file unless explicitly specified

### API key not found

Ensure your API keys are set in your environment:

```bash
echo $ANTHROPIC_API_KEY
echo $OPENAI_API_KEY
```

If they're not set, add them to your shell profile or export them:

```bash
export ANTHROPIC_API_KEY="your-key-here"
export OPENAI_API_KEY="your-key-here"
```

### Mock provider being used instead of real provider

Make sure you're using `--config` flag and NOT specifying `--provider` on the command line. The config file provider will be used by default.

## Example Sessions

### Simple Q&A

```bash
amplifier run --config anthropic-config.toml "What is 2+2?"
# Output: 2 + 2 = 4
```

### Code Generation

```bash
amplifier run --config openai-config.toml "Write a function to calculate fibonacci numbers"
# Output: [Python code for fibonacci function]
```

### Interactive Mode

```bash
amplifier run --config anthropic-config.toml --mode chat
# Starts an interactive session where you can have a conversation
```

## Next Steps

- Explore the example files in `amplifier-next/examples/`
- Read the module documentation in each `amplifier-mod-*` directory
- Try creating custom tools and agents
- Experiment with different models and configurations
