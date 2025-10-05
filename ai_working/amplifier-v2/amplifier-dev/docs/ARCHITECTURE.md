# Amplifier Architecture Documentation

## Overview

Amplifier is a modular AI agent system designed around an ultra-thin core with everything else implemented as swappable modules. This architecture enables parallel development, competing implementations, and rapid innovation while maintaining a stable foundation.

## Core Principles

### 1. Ultra-Thin Core
The core (`amplifier-core`) contains ONLY:
- Module coordination logic
- Standard interfaces (Protocol classes)
- Hook registry for lifecycle events
- Module loading infrastructure
- Session management

Total: ~1000 lines of code, maintained by a single developer.

### 2. Everything is a Module
Even the agent loop itself is a module that can be swapped out:
- **Orchestrators**: Different execution strategies (basic, streaming, parallel)
- **Providers**: LLM integrations (Anthropic, OpenAI, local models)
- **Tools**: Capabilities (filesystem, bash, web, git)
- **Agents**: Specialized workers (architect, debugger, reviewer)
- **Context Managers**: Message storage strategies
- **Hooks**: Lifecycle extensions

### 3. Stable Interfaces, Flexible Implementation
- Public APIs use Protocol classes (structural subtyping)
- No inheritance required - modules just need to match the interface
- Core interfaces NEVER break (only extend)
- Internal implementation can change freely

## Architecture Layers

```
┌─────────────────────────────────────┐
│         User Application            │
├─────────────────────────────────────┤
│        AmplifierSession             │  ← Entry point
├─────────────────────────────────────┤
│      Module Coordinator             │  ← Connects modules
├──────┬──────┬──────┬──────┬────────┤
│ Orch │Prov │Tools│Agents│Context   │  ← Mount points
└──────┴──────┴──────┴──────┴────────┘
       ↑      ↑      ↑      ↑
    Modules (separate packages/repos)
```

## Module Types

### Orchestrator Modules
Control the agent loop execution pattern:
- `loop-basic`: Standard while(tool_calls) pattern
- `loop-streaming`: Token-by-token streaming
- `loop-parallel`: Parallel tool execution
- `loop-multi-agent`: Swarm coordination

**Interface**:
```python
async def execute(prompt, context, providers, tools, hooks) -> str
```

### Provider Modules
Integrate with LLM providers:
- `provider-anthropic`: Claude models
- `provider-openai`: GPT models
- `provider-local`: Ollama, llama.cpp, etc.

**Interface**:
```python
async def complete(messages, **kwargs) -> ProviderResponse
def parse_tool_calls(response) -> List[ToolCall]
```

### Tool Modules
Add capabilities to the system:
- `tool-filesystem`: Read, write, edit files
- `tool-bash`: Execute commands
- `tool-web`: Search and fetch web content
- `tool-git`: Version control operations

**Interface**:
```python
async def execute(input: dict) -> ToolResult
```

### Agent Modules
Specialized workers for specific tasks:
- `agent-architect`: System design
- `agent-debugger`: Bug hunting
- `agent-reviewer`: Code review
- `agent-tester`: Test generation

**Interface**:
```python
async def execute(task: dict, context: AgentContext) -> AgentResult
```

### Context Manager Modules
Manage conversation state:
- `context-simple`: Basic message list
- `context-compact`: Auto-summarization
- `context-rag`: Retrieval-augmented
- `context-persistent`: Cross-session memory

**Interface**:
```python
async def add_message(message: dict)
async def get_messages() -> List[dict]
async def should_compact() -> bool
async def compact()
```

### Hook Modules
Extend lifecycle behavior:
- `hooks-backup`: Transcript preservation
- `hooks-formatter`: Auto-formatting
- `hooks-security`: Command validation
- `hooks-logger`: Detailed logging

**Interface**:
```python
async def handler(event: str, data: dict) -> HookResult
```

## Module Development

### Creating a New Module

1. Use the creation script:
```bash
./scripts/create-module.sh my-module tool
```

2. Implement the module:
```python
# amplifier_mod_my_module/__init__.py
async def mount(coordinator, config):
    """Mount function called by core."""
    module = MyModule(config)
    await coordinator.mount('tools', module, name='my_tool')
    return cleanup_function  # Optional
```

3. Register via entry points:
```toml
[project.entry-points."amplifier.modules"]
my-module = "amplifier_mod_my_module:mount"
```

### Module Communication

Modules communicate through:
1. **Mount Points**: Modules register at specific locations
2. **Hook System**: Lifecycle events with data passing
3. **Shared Context**: Via the coordinator

Modules should NOT:
- Import other modules directly
- Maintain global state
- Assume specific modules are present

## Configuration System

### Layered Configuration
1. Default configuration (in code)
2. User configuration (`~/.amplifier/config.toml`)
3. Project configuration (`.amplifier/config.toml`)
4. Environment variables
5. Command-line arguments

### Example Configuration
```toml
[session]
orchestrator = "loop-basic"
context = "context-simple"

[[providers]]
module = "provider-anthropic"
name = "anthropic"
config = { api_key = "${ANTHROPIC_API_KEY}" }

[[tools]]
module = "tool-filesystem"
config = { allowed_paths = ["."] }
```

## Lifecycle Events

### Standard Events
1. `session:start` - Session begins
2. `prompt:submit` - User prompt received
3. `tool:pre` - Before tool execution
4. `tool:post` - After tool execution
5. `context:pre-compact` - Before context compaction
6. `agent:spawn` - Subagent created
7. `agent:complete` - Subagent finished
8. `session:end` - Session ends

### Hook Execution
- Sequential by priority
- Short-circuit on 'deny'
- Data modification chain
- Error isolation

## Testing Strategy

### Module Testing
Each module includes:
- Unit tests for module logic
- Integration tests with mock coordinator
- Test fixtures for deterministic behavior

### System Testing
- End-to-end flows with real modules
- Module interaction testing
- Performance benchmarks
- Compatibility matrix

## Performance Considerations

### Module Loading
- Lazy loading when possible
- Entry point discovery cached
- Parallel module initialization

### Context Management
- Token counting for all providers
- Automatic compaction at thresholds
- Streaming support where available

### Resource Management
- Cleanup functions for all modules
- Timeout handling
- Memory limits

## Security Model

### Tool Safety
- Approval mechanisms for dangerous operations
- Sandboxing capabilities
- Command validation

### Provider Security
- API key management
- Rate limiting
- Cost tracking

### Module Isolation
- Modules cannot access each other directly
- Resource limits per module
- Capability-based permissions

## Deployment Patterns

### Development
```bash
pip install -e ./amplifier-core
pip install -e ./amplifier-mod-*
amplifier --config dev-config.toml chat
```

### Production
```bash
pip install amplifier-core
pip install amplifier-mod-{needed modules}
amplifier --config production.toml
```

### Docker
```dockerfile
FROM python:3.11
RUN pip install amplifier-core amplifier-mod-provider-anthropic
COPY config.toml /config.toml
CMD ["amplifier", "--config", "/config.toml"]
```

## Future Directions

### Planned Features
- Module marketplace/registry
- Hot module reloading
- Module versioning and compatibility
- Performance profiling per module
- Module composition patterns

### Extension Points
- Custom mount points
- New lifecycle events
- Module communication protocols
- Cross-module transactions
- Distributed module execution

## Philosophy

Amplifier embodies:
- **Unix Philosophy**: Do one thing well, compose simple tools
- **Linux Kernel Model**: Stable external API, flexible internals
- **Ruthless Simplicity**: Complexity only where necessary
- **Parallel Innovation**: Enable competing implementations
- **Single Maintainer Core**: Sustainable maintenance model
