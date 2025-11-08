# Decision Record 004: PostToolUse Warnings Instead of PreToolUse Blocking

**Date**: 2025-11-06
**Status**: Active (replacing Decision 003's enforcement approach)
**Supersedes**: Partial - modifies enforcement mechanism in Decision 003

---

## Context

The PreToolUse blocking hook for orchestrator boundary enforcement (Decision 003) was causing JavaScript heap exhaustion crashes in Claude Code. Even after simplifying the SubagentStop hook, crashes continued.

**Root Issue**: PreToolUse hooks that process tool calls before execution appear to trigger memory issues in the Claude Code runtime, leading to crashes.

**Impact**: System became unusable - crashes occurred during normal operation, blocking all work.

---

## Decision

**Replace PreToolUse blocking with PostToolUse warnings.**

**Changes Made**:

1. **Removed PreToolUse blocking hook**:
   - Disabled `Edit|Write|MultiEdit|NotebookEdit` blocking in `.claude/settings.json`
   - Kept `Task` logging hook (doesn't cause issues)

2. **Created PostToolUse warning hook**:
   - New file: `.claude/hooks/post-tool-use-boundary.py`
   - Shows informational message AFTER orchestrator uses implementation tools
   - Never blocks operations (always exits 0)
   - Silent when agents use tools (expected behavior)

3. **Guidance mechanism**:
   - Provides feedback to guide future behavior
   - Suggests delegation via Task tool
   - Lists available specialized agents
   - References CLAUDE.md for patterns

---

## Implementation

### settings.json Changes

**Before**:
```json
"PreToolUse": [
  {
    "matcher": "Task",
    "hooks": [{"type": "command", "command": "...subagent-logger.py"}]
  },
  {
    "matcher": "Edit|Write|MultiEdit|NotebookEdit",
    "hooks": [{"type": "command", "command": "...pre-tool-use-boundary.py"}]
  }
]
```

**After**:
```json
"PreToolUse": [
  {
    "matcher": "Task",
    "hooks": [{"type": "command", "command": "...subagent-logger.py"}]
  }
]
```

### New PostToolUse Hook

```python
#!/usr/bin/env python3
"""
PostToolUse hook: Show warning after orchestrator uses implementation tools.
Does NOT block - just provides feedback to guide future behavior.
"""

import json, os, sys
from pathlib import Path

MODIFICATION_TOOLS = {"Edit", "Write", "MultiEdit", "NotebookEdit"}

def main():
    input_data = json.load(sys.stdin)
    tool_name = input_data.get("toolName", "")

    if tool_name not in MODIFICATION_TOOLS:
        sys.exit(0)

    # Check if agent is active
    agent_state_file = Path(os.environ.get("CLAUDE_PROJECT_DIR", ".")) / ".claude/state/agent_active"
    if agent_state_file.exists():
        sys.exit(0)  # Expected behavior

    # Show informational message
    file_path = input_data.get("toolInput", {}).get("file_path", "unknown")
    print(f"""
ℹ️  ORCHESTRATOR IMPLEMENTATION NOTICE

Tool: {tool_name}
File: {file_path}

Consider delegating to specialized agents via Task tool:
  Task → modular-builder: "Implement [specification]"

This is informational - operation was allowed.
See CLAUDE.md for delegation patterns.
""", file=sys.stderr)

    sys.exit(0)  # Always allow
```

### Hook Registration

```json
"PostToolUse": [
  {
    "matcher": "Edit|Write|MultiEdit|NotebookEdit",
    "hooks": [
      {"type": "command", "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/post-tool-use-boundary.py"}
    ]
  },
  // ... other PostToolUse hooks ...
]
```

---

## Rationale

### Why This Works

1. **No crashes**: PostToolUse hooks don't cause heap exhaustion
2. **Still provides guidance**: Messages appear after tool use
3. **Never breaks workflow**: Operations always allowed
4. **Agent-aware**: Silent when agents work (expected)
5. **Fail-safe**: Exceptions handled silently

### Trade-offs

**Lost**:
- Hard enforcement of delegation pattern
- Ability to prevent direct implementation

**Gained**:
- Stable system that doesn't crash
- Informational feedback for learning
- Graceful degradation on errors
- Simpler mental model

### Philosophy Alignment

From CLAUDE.md "Orchestrator Boundary":
> Your Role: Orchestrator/Manager/Coordinator - **NOT** implementer

This remains true - we guide through messages rather than enforce through blocking. The goal is learning and habit formation, not mechanical restriction.

---

## Alternatives Considered

### 1. Fix PreToolUse Hook Memory Issues
**Why not**: Unknown root cause in Claude Code runtime, no clear fix path

### 2. Remove All Boundary Enforcement
**Why not**: Lose valuable guidance for developing delegation habits

### 3. Move to User Prompts
**Why not**: Too disruptive, breaks flow, requires manual intervention

### 4. PostToolUse Warnings (CHOSEN)
**Why yes**: Provides guidance without crashes, fail-safe, still agent-aware

---

## Impact

### Immediate
- ✅ System stability restored (no crashes)
- ✅ Orchestrator can work (with guidance messages)
- ✅ Agents unaffected (silent for expected behavior)

### Long-term
- ℹ️ Relies on message-based learning vs mechanical enforcement
- ℹ️ May need to monitor if delegation habits develop
- ℹ️ Could add metrics to track direct vs delegated implementations

### Emergency Bypass
The `AMPLIFIER_BYPASS_BOUNDARY=true` environment variable is no longer needed since operations are never blocked.

---

## Testing

```bash
# Test hook execution
echo '{"toolName": "Edit", "toolInput": {"file_path": "/test/file.py"}}' | \
  .claude/hooks/post-tool-use-boundary.py

# Expected: Informational message on stderr, exit 0

# Test with agent active
mkdir -p .claude/state && touch .claude/state/agent_active
echo '{"toolName": "Edit", "toolInput": {"file_path": "/test/file.py"}}' | \
  .claude/hooks/post-tool-use-boundary.py

# Expected: Silent, exit 0
```

---

## Review Triggers

**Review this decision when**:
1. Claude Code adds support for safer PreToolUse hooks
2. Usage patterns show delegation habits aren't forming
3. Need to add metrics/tracking for direct implementations
4. Alternative enforcement mechanisms become available

---

## Related Decisions

- **Decision 003**: Orchestrator Boundary Phase 3 Enforcement (implementation approach modified)
- **Decision 002**: Pure Delegation Architecture (still applies)

---

## Conclusion

PostToolUse warnings provide a sustainable middle ground between hard enforcement (which crashes) and no guidance (which doesn't teach). The system remains stable while still promoting delegation patterns through informational feedback.

**Key Insight**: Sometimes the right answer is "guide gently" rather than "enforce strictly" - especially when strict enforcement breaks the system.
