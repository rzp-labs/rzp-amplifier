# Recursive Workspace Architecture: Pure Delegation Pattern

**Architecture Pattern**: Pure Delegation
**Status**: Active
**Last Updated**: 2025-11-01

## Overview

The amplifier workspace uses a **Pure Delegation** architecture where the parent workspace delegates ALL operations to submodules without importing their code. This maintains true independence - each submodule is a standalone "brick" with its own virtual environment, dependencies, and build system.

## Core Principle

> **Parent workspace delegates operations to submodules. Submodules remain truly standalone.**

- **Parent**: Coordinates and delegates
- **Submodules**: Self-contained, independently testable
- **No cross-imports**: Parent never imports from submodule packages

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│ Parent Workspace (/workspaces/rzp-amplifier/)               │
│                                                              │
│ ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│ │ Parent .venv    │  │ pytest.ini      │  │ .claude/     │ │
│ │ (amplifier)     │  │ (excludes subs) │  │ hooks/       │ │
│ └─────────────────┘  └─────────────────┘  └──────────────┘ │
│                                                              │
│ ┌──────────────────────────────────────────────────────────┐ │
│ │ Makefile: Delegates to submodules                        │ │
│ │   check-all  → orchestrator/ + infrastructure/           │ │
│ │   test-all   → orchestrator/ + infrastructure/           │ │
│ └──────────────────────────────────────────────────────────┘ │
│                                                              │
│ ┌───────────────────────────┐  ┌────────────────────────┐   │
│ │ orchestrator/             │  │ infrastructure/        │   │
│ │ ├── .venv (own)           │  │ ├── .venv (own)        │   │
│ │ ├── pyproject.toml        │  │ ├── Makefile           │   │
│ │ ├── Makefile              │  │ └── ...                │   │
│ │ ├── tests/                │  └────────────────────────┘   │
│ │ └── src/orchestrator/     │                               │
│ └───────────────────────────┘                               │
└─────────────────────────────────────────────────────────────┘
```

## Three-Part Implementation

### 1. pytest Discovery Control

**File**: `pytest.ini`

The parent workspace pytest is configured to discover only parent-level tests, preventing ModuleNotFoundError when it would otherwise try to import from submodule packages.

```ini
[pytest]
testpaths = tests
norecursedirs = orchestrator infrastructure .venv ...
```

**Why**: Parent pytest runs in parent's venv where submodule packages aren't installed.

### 2. Makefile Separation

**File**: `Makefile`

Clear separation between parent-only and recursive operations:

- `make check` / `make test` → Parent workspace only
- `make check-all` / `make test-all` → Parent + all submodules recursively

**Delegation pattern**:
```makefile
check-all: check  ## Check parent + all submodules
	@make -C orchestrator check || true
	@make -C infrastructure check || true
```

**Why**: Explicit naming prevents confusion about scope.

### 3. Path-Based Hook Detection

**File**: `.claude/hooks/post-tool-use.sh`

Claude Code hooks detect which project files were modified and trigger appropriate checks in the correct virtual environment.

```bash
if echo "$MODIFIED_FILES" | grep -q "^orchestrator/"; then
    make -C orchestrator/ check
fi
```

**Why**: Hooks work from parent workspace regardless of which project is being modified.

## Module Interfaces ("Studs")

### Parent → Submodule Contract

Submodules MUST provide:
- **Makefile** with targets: `check`, `test`, `install`
- **Isolated .venv** (own virtual environment)
- **No imports** from parent or sibling submodules

Submodules MAY have:
- Own `.claude/hooks/` for local operations
- Own documentation and configuration

### Hook → Makefile Contract

- Hooks detect file paths to determine project
- Hooks call `make -C <project>/ check` for that project
- Each project's Makefile handles own venv activation

### pytest.ini Contract

- Parent pytest ONLY discovers `testpaths = tests`
- Parent pytest NEVER discovers submodule test directories
- Submodule tests run via recursive Makefile delegation

## Developer Workflow

### Working from Parent Workspace (Always)

All development happens from `/workspaces/rzp-amplifier/`:

```bash
# Check parent code only
make check

# Check all projects
make check-all

# Test parent only
make test

# Test all projects
make test-all

# Hooks automatically detect project and run appropriate checks
# No manual navigation to submodules needed
```

### Adding a New Submodule

1. Create git submodule with own `.venv` and `Makefile`
2. Add to `pytest.ini` norecursedirs
3. Add delegation target to parent `Makefile`
4. Update `.claude/hooks/post-tool-use.sh` path detection
5. Document submodule's interface contract

## Why Pure Delegation?

### Pros ✅

- **True independence**: Submodules remain standalone
- **Scalable**: Add submodules without coupling
- **Philosophy aligned**: Ruthless simplicity, modular design
- **Current system**: 90% already working this way
- **Clear boundaries**: No ambiguity about imports

### Trade-offs ⚖️

- **No cross-submodule imports**: Cannot write integration tests in parent that import from multiple submodules
- **Solution**: Use API-level integration tests (MCP/HTTP) instead of import-based tests

### Alternatives Rejected ❌

- **Editable installs**: Violates standalone principle, creates dependency conflicts
- **Hybrid approach**: Adds unnecessary complexity, unclear when to import vs delegate

## Testing Strategy

### Parent Tests
- Run with parent's venv
- Test parent-level code only
- Integration tests use API/MCP calls, not imports

### Submodule Tests
- Run with submodule's own venv
- Test submodule code in isolation
- No cross-submodule dependencies

### Recursive Tests
- `make test-all` runs parent tests + all submodule tests
- Each in appropriate venv
- Failures don't stop other projects (|| true pattern)

## Philosophy Alignment

### Ruthless Simplicity ✅
- Uses existing recursive.mk system
- Minimal pytest.ini configuration
- Direct Makefile delegation, no complex framework
- Rejected editable installs despite convenience

### Modular Design ✅
- Submodules are self-contained "bricks"
- Makefile targets are "studs" for connection
- Independent testing with own venvs
- Can rebuild any submodule without breaking parent

## Troubleshooting

### "ModuleNotFoundError when running make test"

**Cause**: Parent pytest discovering submodule tests
**Fix**: Verify `pytest.ini` excludes submodule directories

```bash
pytest --collect-only
# Should show ONLY parent tests/ directory
```

### "Hooks not firing for submodule modifications"

**Cause**: Hook path detection may need adjustment
**Fix**: Check `.claude/hooks/post-tool-use.sh` path patterns
**Debug**: View `/tmp/claude-hook-post-tool-use.log`

### "Submodule tests not running"

**Cause**: Submodule Makefile target missing or failing
**Fix**: Check submodule has `test` target in Makefile

```bash
make -C orchestrator/ test
# Should run orchestrator tests with orchestrator's venv
```

## References

- Decision Record: [002-pure-delegation-architecture.md](../../ai_working/decisions/002-pure-delegation-architecture.md)
- Implementation Philosophy: [IMPLEMENTATION_PHILOSOPHY.md](../../ai_context/IMPLEMENTATION_PHILOSOPHY.md)
- Modular Design: [MODULAR_DESIGN_PHILOSOPHY.md](../../ai_context/MODULAR_DESIGN_PHILOSOPHY.md)
- Parent Makefile: [Makefile](../../Makefile)
- Hook Script: [.claude/hooks/post-tool-use.sh](../../.claude/hooks/post-tool-use.sh)
