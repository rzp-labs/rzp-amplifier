# Amplifier Repository Structure

## Overview

Amplifier is now organized as a collection of focused repositories following the Linux kernel model - a stable core with everything else as modules.

## Repository Layout

### Core Repositories (microsoft/)

#### 1. `amplifier` - Main Entry Point
- **Purpose**: User-facing installation and experience
- **Audience**: End users who want to use Amplifier
- **Features**:
  - Simple installation via `pip` or `uvx`
  - Pre-configured with sensible defaults
  - Bundles core + CLI + default modules
  - Lightweight, focused on user experience
- **Installation**: 
  ```bash
  # Quick try
  uvx --from git+https://github.com/microsoft/amplifier.git amplifier --help
  
  # Install
  pip install git+https://github.com/microsoft/amplifier.git
  ```

#### 2. `amplifier-core` - Ultra-thin Library
- **Purpose**: Core coordination and interfaces (Linux kernel equivalent)
- **Audience**: Module developers
- **Features**:
  - Module discovery and loading
  - Hook system and lifecycle events
  - Session and context management
  - Stable public APIs (never break)
  - Internal implementation (can change)
- **Size**: ~1000 lines max
- **Maintainer**: Single person (expensive to change)

#### 3. `amplifier-cli` - Command Line Interface
- **Purpose**: CLI implementation (one of many possible UIs)
- **Audience**: CLI users and alternative CLI developers
- **Features**:
  - Command-line interface to amplifier-core
  - Module management commands
  - Configuration handling
  - Interactive and single-command modes
- **Note**: Other UIs possible (web, desktop, network)

#### 4. `amplifier-dev` - Development Workspace
- **Purpose**: Convenience setup for developers
- **Audience**: Module developers and core contributors
- **Features**:
  - All repos as submodules
  - Development scripts and tools
  - Test infrastructure
  - Module creation templates
  - Integration testing

### Module Repositories (microsoft/amplifier-mod-*)

Each module is its own repository with independent:
- Versioning
- Release cycle
- Maintainers
- Documentation

#### Reference Implementations

**Orchestrators** (control the agent loop):
- `amplifier-mod-loop-basic` - Standard sequential execution
- `amplifier-mod-loop-streaming` - Token streaming
- `amplifier-mod-loop-parallel` - Parallel tool execution

**Providers** (LLM connections):
- `amplifier-mod-provider-anthropic` - Claude models
- `amplifier-mod-provider-openai` - GPT models
- `amplifier-mod-provider-local` - Ollama/local models

**Tools** (capabilities):
- `amplifier-mod-tool-filesystem` - File operations
- `amplifier-mod-tool-bash` - Command execution
- `amplifier-mod-tool-web` - Web search/fetch
- `amplifier-mod-tool-git` - Git operations

**Agents** (specialized workers):
- `amplifier-mod-agent-architect` - System design
- `amplifier-mod-agent-debugger` - Bug hunting
- `amplifier-mod-agent-reviewer` - Code review
- `amplifier-mod-agent-tester` - Test generation

**Context Managers**:
- `amplifier-mod-context-simple` - Basic message list
- `amplifier-mod-context-compact` - Auto-summarization
- `amplifier-mod-context-rag` - Vector search

**Hooks** (lifecycle extensions):
- `amplifier-mod-hooks-formatter` - Auto-format code
- `amplifier-mod-hooks-backup` - Transcript preservation
- `amplifier-mod-hooks-security` - Command validation

## Installation Paths

### For End Users
```bash
# Just want to use Amplifier
pip install git+https://github.com/microsoft/amplifier.git

# Or try without installing
uvx --from git+https://github.com/microsoft/amplifier.git amplifier run "Hello"
```

### For Module Developers
```bash
# Get the development environment
git clone https://github.com/microsoft/amplifier-dev.git
cd amplifier-dev
./scripts/install-dev.sh

# Create new module
./scripts/create-module.sh my-tool tool
```

### For Core Contributors
```bash
# Same as module developers, but also:
# - Work primarily in modules, not core
# - Core changes require RFC process
# - Maintain backward compatibility
```

## Architecture Principles

### Core (amplifier-core)
- **Stable APIs**: Never break, only extend
- **Ultra-thin**: Minimal code, maximum modularity
- **Single maintainer**: One person can understand it all
- **No business logic**: Pure coordination

### Modules
- **Independent**: Own repo, versioning, releases
- **Focused**: Do one thing well
- **Composable**: Work together via interfaces
- **Replaceable**: Multiple implementations compete

### Development Philosophy
- **Linux kernel model**: Stable core, innovative userspace
- **Unix philosophy**: Small focused tools that compose
- **Ruthless simplicity**: Every line must justify existence
- **Working code**: Ship early, iterate often

## Usage Patterns

### Basic CLI Usage
```bash
amplifier run "Create a Python web server"
amplifier run --mode chat
amplifier module list
```

### Programmatic Usage
```python
from amplifier_core import AmplifierSession, SessionConfig

config = SessionConfig(provider={"name": "anthropic"})
session = AmplifierSession(config)
await session.initialize()
result = await session.execute("Your prompt")
```

### Custom Module
```python
# amplifier_mod_custom/__init__.py
async def mount(coordinator, config):
    tool = MyCustomTool(config)
    await coordinator.mount('tools', tool)
```

## Key Differences from Original

1. **No Claude Code dependency**: Complete replacement
2. **Everything is modular**: Even the agent loop
3. **Multiple UIs possible**: CLI is just one option
4. **Distributed development**: Parallel innovation
5. **Provider agnostic**: Any LLM can be used
6. **Stable foundation**: Core rarely changes

## Next Steps

### Phase 1: Foundation (Current)
- ✅ Core library (amplifier-core)
- ✅ CLI separation (amplifier-cli)
- ✅ Main entry point (amplifier)
- ✅ Basic modules
- ✅ Development environment

### Phase 2: Ecosystem
- [ ] Publish to PyPI
- [ ] Module marketplace/registry
- [ ] More provider implementations
- [ ] Community modules
- [ ] Web UI prototype

### Phase 3: Production
- [ ] Enterprise features
- [ ] Security hardening
- [ ] Performance optimization
- [ ] Monitoring/observability
- [ ] Cloud deployment options

## Benefits

**For Users**:
- Easy to install and use
- Choice of AI providers
- Extensible via modules
- Active ecosystem

**For Developers**:
- Clear module interfaces
- Independent development
- Fast iteration
- Compete with ideas

**For Microsoft**:
- Scalable development model
- Community contributions
- Innovation at edges
- Stable core maintenance

This architecture enables parallel innovation while maintaining stability - the best of both worlds.
