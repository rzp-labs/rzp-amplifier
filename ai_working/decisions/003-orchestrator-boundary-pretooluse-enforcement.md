# [DECISION-003] Orchestrator Boundary System - PreToolUse Hook Enforcement

**Date**: 2025-11-02 (Revised 2025-11-06 - Superseded)
**Status**: Superseded by [DECISION-004] PostToolUse Warning Approach
**Depends On**: [DECISION-002] Pure Delegation Architecture

## Summary

The orchestrator boundary is enforced through **PreToolUse hooks** that block Edit/Write/MultiEdit/NotebookEdit operations in the main orchestrator session, requiring delegation to specialized agents via the Task tool.

## ⚠️ SUPERSEDED

This decision has been superseded by [DECISION-004] PostToolUse Warning Approach.

**Reason**: PreToolUse blocking hooks caused JavaScript heap exhaustion crashes. System now uses PostToolUse warnings instead of blocking.

**See**: `ai_working/decisions/004-post-tool-use-warnings.md` for current implementation.

The content below documents the PreToolUse blocking approach that was attempted but proved unstable.

---

### Correction from Previous Versions

**Previous error**: Claimed technical blocking was impossible because only PostToolUse hooks existed.

**Reality**: PreToolUse hooks CAN block tool calls before execution using `"permissionDecision": "deny"` in JSON output.

**Evidence**: Claude Code Hooks Reference documentation (lines 336-402) shows PreToolUse hooks receive tool calls BEFORE execution and can return blocking decisions.

## Why PreToolUse Enforcement

### The Architecture

**PreToolUse Hook Flow**:
```
Tool call requested → PreToolUse hook runs → Validation → Block or Allow → Tool executes (if allowed)
```

**Key Capability**: PreToolUse hooks can prevent tool execution entirely by returning:
```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "deny",
    "permissionDecisionReason": "Orchestrator must delegate to specialized agents"
  }
}
```

### Why This Works

**Technical blocking is possible**:
- Hook runs BEFORE tool execution
- `"permissionDecision": "deny"` prevents the tool from running
- `permissionDecisionReason` is shown to Claude for feedback
- File never gets modified (blocked before execution)

**Preserves learning**:
- Claude receives feedback when attempting blocked operations
- System prompt still explains the "why" (delegation philosophy)
- Violations physically prevented, not just discouraged

## Decision

Enforce orchestrator boundary through **PreToolUse hooks** that block file modification operations in the main orchestrator session.

### Implementation Specification

#### 1. PreToolUse Hook Script

**Create**: `/workspaces/rzp-amplifier/.claude/hooks/pre-tool-use-boundary.py`

```python
#!/usr/bin/env python3
"""
PreToolUse hook: Enforce orchestrator boundary by blocking direct file modifications.

The main orchestrator MUST delegate to specialized agents via Task tool.
Agents ARE allowed to use Edit/Write/MultiEdit/NotebookEdit tools.
"""

import os
import sys
import json

# Emergency bypass: AMPLIFIER_BYPASS_BOUNDARY=true
BYPASS_ENABLED = os.getenv("AMPLIFIER_BYPASS_BOUNDARY", "").lower() == "true"

# Tools that modify files (prohibited in orchestrator)
MODIFICATION_TOOLS = {"Edit", "Write", "MultiEdit", "NotebookEdit"}


def is_agent_session() -> bool:
    """
    Detect if current session is an agent (allowed) or main orchestrator (blocked).

    Claude Code provides session metadata via environment variables.
    Agents have CLAUDE_AGENT_NAME set, main orchestrator does not.
    """
    return os.getenv("CLAUDE_AGENT_NAME") is not None


def validate_boundary(tool_name: str, tool_input: dict) -> dict:
    """Validate orchestrator boundary for file modification tools."""

    # Only care about modification tools
    if tool_name not in MODIFICATION_TOOLS:
        return {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "allow"
            }
        }

    # Emergency bypass
    if BYPASS_ENABLED:
        return {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "allow"
            },
            "systemMessage": "⚠️ BOUNDARY BYPASS ACTIVE (AMPLIFIER_BYPASS_BOUNDARY=true)"
        }

    # Agents ARE allowed to modify files
    if is_agent_session():
        return {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "allow"
            }
        }

    # Main orchestrator is BLOCKED
    file_path = tool_input.get("file_path", "unknown")

    return {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": (
                f"🚫 ORCHESTRATOR BOUNDARY VIOLATION\n\n"
                f"Tool: {tool_name}\n"
                f"File: {file_path}\n\n"
                f"You MUST delegate file modifications to specialized agents:\n"
                f"  Task → modular-builder: 'Create/modify {file_path}'\n\n"
                f"Your role is orchestration, not implementation.\n"
                f"See CLAUDE.md for delegation patterns.\n\n"
                f"Emergency bypass: export AMPLIFIER_BYPASS_BOUNDARY=true"
            )
        }
    }


def main():
    """Main entry point for PreToolUse hook."""
    try:
        # Read hook input from stdin (JSON)
        hook_input = json.load(sys.stdin)

        tool_name = hook_input.get("toolName", "")
        tool_input = hook_input.get("toolInput", {})

        # Validate and return decision
        result = validate_boundary(tool_name, tool_input)
        print(json.dumps(result))

    except Exception as e:
        # On error, allow the operation (fail open)
        print(json.dumps({
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "allow"
            },
            "systemMessage": f"⚠️ Boundary hook error (allowing): {str(e)}"
        }))


if __name__ == "__main__":
    main()
```

**Make executable**:
```bash
chmod +x /workspaces/rzp-amplifier/.claude/hooks/pre-tool-use-boundary.py
```

#### 2. Claude Code Settings Configuration

**Update**: `/workspaces/rzp-amplifier/.claude/settings.json`

Add PreToolUse hook configuration in the `hooks` section:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Task",
        "hooks": [
          {
            "type": "command",
            "command": "$CLAUDE_PROJECT_DIR/.claude/tools/subagent-logger.py"
          }
        ]
      },
      {
        "matcher": "Edit|Write|MultiEdit|NotebookEdit",
        "hooks": [
          {
            "type": "command",
            "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/pre-tool-use-boundary.py"
          }
        ]
      }
    ],
    // ... other hooks remain unchanged
  }
}
```

**Note**: The matcher `"Edit|Write|MultiEdit|NotebookEdit"` triggers this hook only for file modification tools.

#### 3. System Prompt Guidance

**Maintain in CLAUDE.md**:
```markdown
## Orchestrator Boundary (ENFORCED via Hooks)

**Your Role**: Orchestrator/Manager/Coordinator - **NOT** implementer

**Phase 3 Active Since**: 2025-11-03
**Status**: Enforcement Mode (violations BLOCKED)

**ENFORCED Tool Boundaries**:

### ✅ YOU CAN Use (Orchestration Tools)
- Read, Grep, Glob: Understanding and analysis
- TodoWrite: Planning and task management
- Task: Delegation to specialized agents
- Bash: Testing, validation, environment checks
- AskUserQuestion: User engagement and clarification

### ❌ YOU CANNOT Use (Implementation Tools)
- Edit, Write, MultiEdit: Code modification (delegate to modular-builder)
- NotebookEdit: Notebook modification (delegate to appropriate agent)

**Enforcement**: PreToolUse hook BLOCKS operations completely
- Emergency bypass: `export AMPLIFIER_BYPASS_BOUNDARY=true`

**Required Workflow**:
1. ANALYZE (You): Read/Grep to understand problem
2. DESIGN (You): Create specification for solution
3. DELEGATE (You - REQUIRED): Task → specialized-agent with spec
4. VALIDATE (You): Bash → run tests to verify

**Example Delegation**:
Bad:  Using Edit tool directly (BLOCKED)
Good: Task → modular-builder: "Implement [specification]"

**This is not a suggestion—it's system-enforced architecture.**
```

### Expected Behavior

**Main Orchestrator Session**:
1. Attempts `Edit` on file → PreToolUse hook runs
2. Hook detects non-agent session → Returns `"permissionDecision": "deny"`
3. Tool call BLOCKED before execution
4. Claude receives feedback: "You MUST delegate to specialized agents"
5. File never modified

**Agent Session** (modular-builder, bug-hunter, etc.):
1. Attempts `Edit` on file → PreToolUse hook runs
2. Hook detects agent session (CLAUDE_AGENT_NAME set) → Returns `"permissionDecision": "allow"`
3. Tool call ALLOWED
4. Agent performs implementation normally

**Emergency Bypass**:
```bash
export AMPLIFIER_BYPASS_BOUNDARY=true
# Now Edit/Write/MultiEdit allowed in orchestrator
```

### Testing Verification

**Test 1: Orchestrator Blocked**
```
User: "Fix the typo in README.md"
Orchestrator: [Attempts Edit tool]
Hook: BLOCKS with "You MUST delegate to specialized agents"
Result: ✅ Boundary enforced
```

**Test 2: Agent Allowed**
```
Orchestrator: Task → modular-builder: "Fix typo in README.md"
modular-builder: [Uses Edit tool]
Hook: ALLOWS (agent session detected)
Result: ✅ Agent can implement
```

**Test 3: Emergency Bypass**
```bash
export AMPLIFIER_BYPASS_BOUNDARY=true
Orchestrator: [Uses Edit tool]
Hook: ALLOWS with warning message
Result: ✅ Bypass works
```

## Rationale

### Why PreToolUse Over System Prompt Alone

**Technical enforcement prevents mistakes**:
- System prompt explains "why" (philosophy)
- PreToolUse hook enforces "what" (rules)
- Together: Understanding + Prevention

**Immediate feedback**:
- Claude learns from blocked attempts
- Feedback includes correct delegation pattern
- No post-facto cleanup needed

**Simpler than PostToolUse detection**:
- Blocks BEFORE file modification
- No "undo" logic needed
- Clean failure mode

### Why Agent Detection Works

**CLAUDE_AGENT_NAME environment variable**:
- Set by Claude Code when running agents
- Not set in main orchestrator session
- Reliable session type detection

**Fail-open on errors**:
- If detection fails, allow the operation
- Prevents blocking legitimate agent work
- Logged warning helps debug

## Consequences

### Positive (Expected Benefits)

- **Architectural clarity**: Orchestrator boundary physically enforced
- **Prevention over detection**: Blocks violations before they occur
- **Immediate feedback**: Claude learns correct pattern from denials
- **Agent autonomy**: Specialized agents can still implement freely
- **Emergency override**: Bypass available when needed
- **Philosophy aligned**: Ruthless simplicity in hook logic (~60 lines)

### Accepted Trade-offs

- **Session detection dependency**: Relies on CLAUDE_AGENT_NAME being set correctly
- **JSON output requirement**: Must return proper hookSpecificOutput structure
- **Fail-open on errors**: Hook failures allow operations (prevents blocking workflow)
- **Emergency bypass exists**: Can be disabled if needed, but reduces enforcement

### Risks and Mitigations

**Risk**: Agent detection fails (CLAUDE_AGENT_NAME not set correctly)
**Mitigation**: Fail-open behavior + bypass flag allows manual override

**Risk**: Hook execution errors break workflow
**Mitigation**: Exception handling returns "allow" decision with warning

**Risk**: Bypass flag left enabled accidentally
**Mitigation**: Hook shows warning message when bypass active

## Review Triggers

This decision is now **superseded**. Original review triggers documented for historical context:

- [x] **Agent detection unreliable**: CLAUDE_AGENT_NAME doesn't exist (2025-11-06)
- [x] **Crashes**: JavaScript heap exhaustion with PreToolUse blocking (2025-11-06)
- [x] **Architectural change**: Moved to PostToolUse warnings (2025-11-06)

Current approach: See [DECISION-004]

## References

### Prior Decisions
- [DECISION-002] Pure Delegation Architecture - Establishes modular boundaries

### Related Code
- `.claude/hooks/pre-tool-use-boundary.py` - PreToolUse hook implementation
- `.claude/settings.json` - Hook configuration
- `CLAUDE.md` - System prompt with boundary explanation

### Philosophy Alignment
- [IMPLEMENTATION_PHILOSOPHY.md](../../ai_context/IMPLEMENTATION_PHILOSOPHY.md) - Ruthless simplicity
- [MODULAR_DESIGN_PHILOSOPHY.md](../../ai_context/MODULAR_DESIGN_PHILOSOPHY.md) - Bricks and studs

### Claude Code Documentation
- Claude Code Hooks Reference - Lines 336-402 (PreToolUse decision control)

---

## Historical Context: Evolution of Understanding

This decision went through three phases as we learned about Claude Code's hook architecture:

### Phase 1: Attempted PostToolUse Blocking (Failed)
**Assumption**: PostToolUse hooks could block by returning error status
**Reality**: PostToolUse runs AFTER file modification, cannot block past operations
**Learning**: Post-hooks are for detection only

### Phase 2: System Prompt Only (Interim)
**Approach**: Rely on CLAUDE.md instructions for self-enforcement
**Benefit**: Simple, aligned with philosophy
**Limitation**: No technical prevention, violations possible

### Phase 3: PreToolUse Blocking (Current)
**Discovery**: PreToolUse hooks CAN block via `"permissionDecision": "deny"`
**Benefit**: Technical enforcement + learning feedback
**Implementation**: This document's specification

### Key Learning

Read the documentation carefully. Claude Code has sophisticated hook capabilities including pre-execution blocking. The mistake was assuming only PostToolUse hooks existed without checking for PreToolUse in the reference docs.

**Always verify assumptions against official documentation.**

### Phase 4: State Flag Detection (2025-11-06)

**Discovery**: `CLAUDE_AGENT_NAME` environment variable doesn't exist
- Agents run in SAME session as orchestrator
- No environment variable differentiation possible
- Diagnostic logging revealed session_id is identical

**Solution Attempted**: Hook-based state flag lifecycle
- PreToolUse:Task creates `.claude/state/agent_active`
- Boundary hook checks flag existence
- SubagentStop removes flag after completion

**Critical Fix**: PreToolUse hooks MUST return JSON
- Missing JSON output caused JavaScript heap exhaustion crashes
- Claude Code retries infinitely waiting for JSON response

**Outcome**: State flag lifecycle worked correctly but blocking approach caused crashes.

### Phase 5: PostToolUse Warnings (2025-11-06)

**Problem**: Even with state flags, PreToolUse blocking caused instability
- JavaScript heap exhaustion crashes persisted
- Blocking approach too aggressive for hook system

**Final Solution**: [DECISION-004] PostToolUse Warning Approach
- Removed PreToolUse blocking entirely
- Switched to PostToolUse informational warnings
- System stable without crashes
- Guidance through messages rather than enforcement

**See**: `ai_working/decisions/004-post-tool-use-warnings.md`
