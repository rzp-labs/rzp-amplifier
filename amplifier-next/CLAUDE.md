# Amplifier Project Context

This file contains project-specific context and instructions for AI assistants working with Amplifier.

## Project Overview

Amplifier is a modular AI agent platform that enables:
- Multi-provider LLM support (Anthropic Claude, OpenAI GPT)
- Pluggable tool system for extending capabilities
- Sub-agent delegation for complex tasks
- Persistent context across sessions
- Command system for interactive control

## Core Philosophy

- **Ruthless Simplicity**: Keep implementations as simple as possible
- **Modular Design**: Each module is self-contained with clear interfaces
- **Fail Gracefully**: Provide meaningful errors, never crash
- **Direct Approach**: Avoid unnecessary abstractions

## Architecture

The system consists of:
- **amplifier-core**: Core session, coordinator, and interfaces
- **Provider modules**: LLM provider integrations
- **Tool modules**: Filesystem, bash, web, search, task delegation
- **Context modules**: Simple and persistent context managers
- **Orchestrator modules**: Agent loop implementations

## Development Guidelines

1. Every module is independently installable
2. Use entry points for module discovery
3. Follow the Tool/Provider/Context interfaces
4. Test modules in isolation before integration
5. Document module contracts in README.md

## Testing

Run interactive sessions with:
```bash
amplifier run --config test-full-features.toml --mode chat
```

Test specific features:
- `/think` - Enable read-only plan mode
- `/tools` - List available tools
- `/status` - Show session information
