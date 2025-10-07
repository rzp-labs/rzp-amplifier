# config_resolution.md

**Owner:** App/CLI layer (not kernel).  
**Purpose:** Build a *Mount Plan* for the kernel using a clear precedence:

1. **Default** (package resource: `amplifier/default-config.toml`).
2. **User** (`~/.amplifier/config.toml`).
3. **Project** (`./.amplifier/config.toml`).
4. **Explicit** (`--config` file path).
5. **Inline overrides** (CLI flags, e.g. `--provider openai --model gpt-4o`).

> The kernel receives the **final plan** as a dict. It never reads files or chooses defaults.

### Mount Plan shape (example)
```toml
[session]
orchestrator = "loop-basic"
context = "context-simple"
search_paths = ["./.amplifier/modules", "~/.amplifier/modules"]

[providers]
anthropic = { model = "claude-3-5", api_key = "env:ANTHROPIC_API_KEY" }
openai    = { model = "gpt-4o-mini", api_key = "env:OPENAI_API_KEY" }

[tools]
filesystem = { root = "." }
bash       = { shell = "/bin/bash" }

[hooks]
logging    = { enabled = true }
redaction  = { enabled = true }
```
