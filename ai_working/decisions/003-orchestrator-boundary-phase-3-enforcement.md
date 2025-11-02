# [DECISION-003] Orchestrator Boundary System - Phase 3 Enforcement Mode

**Date**: 2025-11-02
**Status**: Planned (Phase 2 active, Phase 3 documented)
**Depends On**: [DECISION-002] Pure Delegation Architecture

## Context

The orchestrator boundary system enforces architectural separation between Claude Code's main orchestrator and specialized agents. This decision record documents **Phase 3 (Enforcement Mode)** requirements, implementation plan, and activation criteria.

### Current State: Phase 2 (Validation Mode)

**Active Since**: 2025-11-02
**Purpose**: Data gathering and validation testing
**Behavior**: Detects violations, logs warnings, **does not block operations**

**Implementation**:
- `validate_orchestrator_boundary()` in `.claude/tools/hook_post_tool_use.py`
- Returns `{"status": "warning"}` for violations
- Logs detailed warning messages to console and hook logs
- Records violations in DelegationAudit system (when enabled)

**Key Insight**: Phase 2 validates the detection logic and gathers data on violation patterns without disrupting workflow.

### The Problem Phase 3 Solves

**Architectural Intent**: Main orchestrator delegates ALL file modifications to specialized agents via Task tool

**Current Gap**: Phase 2 detects violations but doesn't prevent them, allowing:
- Main orchestrator using Edit/Write/MultiEdit directly
- Bypassing specialized agents designed for code changes
- Weakening architectural boundaries over time

**Phase 3 Goal**: Transform warnings into hard blocks, enforcing delegation pattern

## Decision

Implement **Phase 3 (Enforcement Mode)** that blocks orchestrator boundary violations while maintaining emergency bypass capability.

### What Changes

**Phase 2 (Current)**:
```python
# Violation detected → Log warning, allow operation
return {"status": "warning", "message": violation_msg}
```

**Phase 3 (Enforcement)**:
```python
# Violation detected → Return error, BLOCK operation
return {"status": "error", "message": violation_msg}
```

### Core Behavior

**Blocked Operations** (main orchestrator):
- ❌ Edit, Write, MultiEdit, NotebookEdit on any file
- Must delegate via: `Task: modular-builder "Implement fix for X"`

**Allowed Operations** (main orchestrator):
- ✅ Read, Grep, Glob, Bash (information gathering)
- ✅ TodoWrite, AskUserQuestion (coordination)
- ✅ Task (delegation to agents)

**Always Allowed** (specialized agents):
- ✅ All tools including Edit/Write (agents can modify files)
- Detection via `detect_agent_session()` in hook

### Emergency Bypass

**Purpose**: Prevent complete workflow blockage if detection fails

**Mechanism**: Environment variable override
```bash
export AMPLIFIER_BYPASS_BOUNDARY=true  # Disable enforcement
```

**Usage**:
- User sets before starting Claude Code session
- Hook checks at runtime: `if os.getenv("AMPLIFIER_BYPASS_BOUNDARY") == "true": return {"status": "allowed"}`
- Log bypass usage for later investigation

**When to Use**:
- Detection incorrectly identifies agent as main orchestrator
- Emergency fix needed during critical work
- Testing architectural changes that modify boundary rules

## Rationale

### Why Block Instead of Warn

**Architectural Integrity**:
- Warnings are easily ignored under time pressure
- Violations accumulate and weaken boundaries
- Hard blocks enforce intended architecture

**Learning Reinforcement**:
- Immediate feedback shapes correct behavior
- Clear error messages teach delegation pattern
- Builds muscle memory for Task-based workflow

**Data Validation**:
- Phase 2 proves detection works accurately
- Blocking only activates after validation period
- Known edge cases documented and handled

### Why Emergency Bypass

**Pragmatic Safety Net**:
- Complex detection can have edge cases
- User productivity trumps perfect enforcement
- Better than disabling system entirely

**Debugging Aid**:
- Bypass usage indicates detection problems
- Logged for later investigation
- Informs refinements to detection logic

### Alignment with Philosophy

**From IMPLEMENTATION_PHILOSOPHY.md**:
- **Ruthless Simplicity**: Clear rule - orchestrator delegates, agents execute
- **Fail Fast**: Immediate blocking vs silent degradation
- **Pragmatic Trust**: Emergency bypass when needed

**From MODULAR_DESIGN_PHILOSOPHY.md**:
- **Bricks & Studs**: Orchestrator and agents are separate bricks with defined interfaces
- **Clear Contracts**: Orchestrator cannot breach agent boundaries

## Implementation Requirements

### Step 1: Modify `validate_orchestrator_boundary()` Return

**File**: `.claude/tools/hook_post_tool_use.py`

**Current Phase 2 Code** (line 106):
```python
return {"status": "warning", "message": violation_msg, "file": file_path, "tool": tool_name}
```

**Phase 3 Change**:
```python
# Phase 3: Block violations
return {"status": "error", "message": violation_msg, "file": file_path, "tool": tool_name}
```

**Impact**: Hook protocol interprets `"status": "error"` as blocking response

### Step 2: Add Emergency Bypass Check

**File**: `.claude/tools/hook_post_tool_use.py`

**Location**: Top of `validate_orchestrator_boundary()` function (after line 51)

**Code to Add**:
```python
def validate_orchestrator_boundary(tool_name: str, tool_input: dict, session_id: str | None = None) -> dict:
    """Enforce main orchestrator cannot modify files directly.

    Phase 3: Enforcement (blocks violations unless bypassed)
    """
    import os

    # Emergency bypass for critical situations
    if os.getenv("AMPLIFIER_BYPASS_BOUNDARY") == "true":
        logger.warning("⚠️ BOUNDARY ENFORCEMENT BYPASSED via environment variable")
        logger.warning("This should only be used for emergencies or debugging")
        return {"status": "allowed", "bypassed": True}

    # ... rest of existing function
```

**Additional Logging**:
```python
# When blocking (replace current Phase 2 warning)
logger.error(f"🚫 BLOCKING {tool_name} on {file_path} - orchestrator boundary violation")

# Update violation message for Phase 3
violation_msg = f"""
🚫 ORCHESTRATOR BOUNDARY VIOLATION - OPERATION BLOCKED

Main Claude attempted to use {tool_name} on: {file_path}

Your Role: Orchestrator (read-only, delegation-focused)
  ✅ Allowed: Read, Grep, TodoWrite, Task, Bash, AskUserQuestion
  ❌ BLOCKED: Edit, Write, MultiEdit (must delegate via Task)

Required Action: Use Task tool to delegate to specialized agent

Available Agents:
  • modular-builder: Code implementation and module creation
  • bug-hunter: Bug diagnosis and fix implementation
  • test-coverage: Test creation and coverage
  • refactor-architect: Code refactoring

Example Delegation:
  Task: modular-builder
  Prompt: "Implement fix for {file_path}: [specification]"

Emergency Bypass (use only when detection is incorrect):
  export AMPLIFIER_BYPASS_BOUNDARY=true

Phase 3: This operation has been BLOCKED.
""".strip()
```

### Step 3: Update Hook Main Function

**File**: `.claude/tools/hook_post_tool_use.py`

**Current Code** (lines 145-149):
```python
boundary_result = validate_orchestrator_boundary(tool_name, tool_input, session_id)
if boundary_result["status"] == "warning":
    # In Phase 2, we log the warning but don't block
    logger.warning(f"Boundary violation detected: {tool_name} on {boundary_result.get('file', 'unknown')}")
```

**Phase 3 Change**:
```python
boundary_result = validate_orchestrator_boundary(tool_name, tool_input, session_id)

if boundary_result["status"] == "error":
    # Phase 3: Return error to Claude Code, blocking the operation
    error_output = {
        "error": boundary_result["message"],
        "metadata": {
            "violationType": "orchestrator_boundary",
            "tool": boundary_result.get("tool"),
            "file": boundary_result.get("file"),
            "bypassed": boundary_result.get("bypassed", False),
            "source": "amplifier_boundary_enforcement"
        }
    }
    json.dump(error_output, sys.stdout)
    logger.error(f"🚫 BLOCKED {tool_name} on {boundary_result.get('file', 'unknown')}")
    return  # Exit hook, operation blocked
```

### Step 4: Update Documentation

**Files to Update**:

1. **`.claude/tools/hook_post_tool_use.py` docstring**:
```python
"""
Claude Code hook for PostToolUse events - validates claims and enforces boundaries.

Phase 3 (Active): Blocks orchestrator boundary violations
- Main orchestrator: Read-only, delegates via Task
- Agents: Full Edit/Write capabilities
- Emergency bypass: AMPLIFIER_BYPASS_BOUNDARY=true
"""
```

2. **`CLAUDE.md` or `AGENTS.md`**:
```markdown
## Orchestrator Boundary System (Phase 3: Enforcement)

**Active Since**: [activation date]

Main Claude orchestrator must delegate ALL file modifications to specialized agents:

**Blocked Tools** (orchestrator): Edit, Write, MultiEdit, NotebookEdit
**Required Pattern**: Task tool → specialized agent → agent modifies files
**Emergency Bypass**: `export AMPLIFIER_BYPASS_BOUNDARY=true`

See [DECISION-003](ai_working/decisions/003-orchestrator-boundary-phase-3-enforcement.md)
```

3. **This decision record** (update status when activated):
```markdown
**Status**: Active (activated YYYY-MM-DD)
```

### Step 5: Testing Requirements

**Pre-Activation Tests** (verify in Phase 2 environment):

1. **Violation Detection**:
```bash
# Test: Main orchestrator attempts Edit
# Expected: Warning logged, operation allowed (Phase 2)
# Verify: Hook log shows detection
```

2. **Agent Allowance**:
```bash
# Test: Agent spawned via Task attempts Edit
# Expected: Operation allowed (agents can modify)
# Verify: No warning or block
```

3. **Session Detection**:
```bash
# Test: detect_agent_session() accuracy
# Expected: Correctly distinguishes main vs agent
# Verify: Hook logs show correct session type
```

**Post-Activation Tests** (after Phase 3 enabled):

1. **Blocking Works**:
```bash
# Test: Main orchestrator attempts Edit
# Expected: Error returned, operation BLOCKED
# Verify: Claude Code shows error message
```

2. **Emergency Bypass**:
```bash
export AMPLIFIER_BYPASS_BOUNDARY=true
# Test: Violation should be allowed
# Expected: Warning logged, operation allowed
# Verify: Bypass logged in hook logs
```

3. **Agent Operations Unchanged**:
```bash
# Test: Agent workflows continue normally
# Expected: No disruption to agent modifications
```

**Regression Tests**:
- All existing Claude Code workflows still function
- Memory system validation still works
- Hook doesn't block non-modification tools

## Activation Criteria

### When to Activate Phase 3

**Data Requirements** (from Phase 2):
- [ ] **Minimum 2 weeks** of Phase 2 operation
- [ ] **50+ tool uses** captured in logs for pattern analysis
- [ ] **Zero false positives** in session detection (agents not misidentified as main)
- [ ] **Violation patterns documented** (what gets blocked, how often)

**Validation Requirements**:
- [ ] **Detection accuracy confirmed**: `detect_agent_session()` works reliably
- [ ] **User workflow understanding**: Team knows delegation pattern
- [ ] **Agent coverage validated**: All needed file modifications can be delegated
- [ ] **Hook stability verified**: No crashes or unexpected errors

**Preparation Requirements**:
- [ ] **Documentation updated**: Users know what's changing and why
- [ ] **Bypass mechanism tested**: Emergency override works correctly
- [ ] **Rollback plan validated**: Can revert to Phase 2 quickly if needed

### Metrics to Review

**From DelegationAudit logs** (if enabled):
```python
# Questions to answer from Phase 2 data:
1. How many violations per session?
2. Which files are most commonly targeted?
3. What tools are used most (Edit vs Write vs MultiEdit)?
4. Are violations concentrated or distributed?
5. Any patterns suggesting architectural issues?
```

**From hook logs** (`/tmp/claude-hook-post-tool-use.log`):
```bash
# Check for:
1. Session detection errors
2. False positive warnings
3. Hook crashes or exceptions
4. Performance issues (hook too slow?)
```

### Red Flags (DO NOT ACTIVATE if present)

- ⛔ **Agent detection unreliable**: Sessions misidentified >5% of the time
- ⛔ **Critical workflow blocked**: Essential operations can't be delegated
- ⛔ **Hook instability**: Crashes or errors >1% of executions
- ⛔ **User confusion**: Team doesn't understand delegation pattern
- ⛔ **Insufficient agent coverage**: Missing specialized agents for common tasks

### Green Lights (SAFE TO ACTIVATE)

- ✅ **Detection accuracy >95%**: Rare or zero false positives
- ✅ **Stable operation**: No hook crashes in 2+ weeks
- ✅ **Pattern clarity**: Understand what will be blocked
- ✅ **Agent maturity**: Specialized agents handle common modifications
- ✅ **Team readiness**: Users know delegation pattern
- ✅ **Bypass tested**: Emergency override works

## Rollback Plan

### If Phase 3 Causes Issues

**Symptoms that trigger rollback**:
- Blocking legitimate agent operations
- Emergency bypass needed >10% of sessions
- User productivity significantly impacted
- Hook crashes or errors spike

### Rollback Procedure

**Immediate (Emergency)**:
```bash
# User can bypass instantly
export AMPLIFIER_BYPASS_BOUNDARY=true
# Continue working, file issue for investigation
```

**System-Wide Revert**:

1. **Modify hook** (`.claude/tools/hook_post_tool_use.py`):
```python
# Change line 106 back to Phase 2:
return {"status": "warning", "message": violation_msg, ...}

# Update main() to not block on errors (lines 145-149):
if boundary_result["status"] == "warning":  # Changed from "error"
    logger.warning(f"Boundary violation: {tool_name}...")
    # Don't return error to Claude Code
```

2. **Update documentation**:
```markdown
**Status**: Reverted to Phase 2 (validation mode)
**Reason**: [specific issue that triggered rollback]
**Investigation**: [link to GitHub issue or log analysis]
```

3. **Analyze failure**:
- Review hook logs for error patterns
- Check DelegationAudit for blocked operations
- Interview users about impact
- Identify detection improvements needed

### Recovery Criteria

**When is it safe to retry Phase 3?**

- ✅ Root cause identified and fixed
- ✅ Detection accuracy improved
- ✅ Additional testing completed
- ✅ User concerns addressed
- ✅ Bypass mechanism enhanced if needed

## Consequences

### Positive (Expected Benefits)

- **Architectural integrity**: Boundaries enforced consistently
- **Clear workflow**: Orchestrator role vs agent role well-defined
- **Better code organization**: Modifications go through specialized agents
- **Reduced errors**: Specialized agents have better context for changes
- **Learning reinforcement**: Immediate feedback teaches delegation pattern

### Negative (Accepted Trade-offs)

- **Initial friction**: Users must learn new workflow
- **Extra step**: Must use Task instead of direct Edit
- **Detection complexity**: Session identification could have edge cases
- **Bypass temptation**: Users might overuse emergency override

### Risks

**High Confidence Mitigations**:
- ⚠️ **False positives blocking agents**: Phase 2 data validates detection accuracy
- ⚠️ **User workflow disruption**: Emergency bypass provides safety valve
- ⚠️ **Hook performance impact**: Minimal - validation is fast, no LLM calls

**Lower Confidence Mitigations**:
- ⚠️ **Detection edge cases**: Bypass mechanism handles unexpected scenarios
- ⚠️ **User resistance**: Clear documentation and rationale help adoption

## Review Triggers

This decision should be reconsidered if:

- [ ] **Bypass usage >25%**: Detection too aggressive or inaccurate
- [ ] **User complaints persistent**: Workflow friction too high after 30 days
- [ ] **Agent coverage gaps**: Common operations can't be delegated
- [ ] **Hook errors spike**: Reliability issues emerge
- [ ] **Architectural change**: Orchestrator boundary model evolves
- [ ] **After 6 months**: General review of effectiveness

## References

### Prior Decisions
- [DECISION-002] Pure Delegation Architecture - Establishes modular boundaries

### Implementation Context
- **Phase 1**: Initial boundary concept and detection logic
- **Phase 2**: Validation mode (active since 2025-11-02)
- **Phase 3**: This document - enforcement mode

### Architecture Guidance
- zen-architect analysis (2025-11-02 session)
- amplifier-cli-architect recommendations
- Pure Delegation Architecture principles

### Related Code
- `.claude/tools/hook_post_tool_use.py` - Hook implementation
- `amplifier/orchestration.py` - DelegationAudit (if exists)
- `.claude/AGENTS_CATALOG.md` - Available specialized agents

### Philosophy Alignment
- [IMPLEMENTATION_PHILOSOPHY.md](../../ai_context/IMPLEMENTATION_PHILOSOPHY.md)
- [MODULAR_DESIGN_PHILOSOPHY.md](../../ai_context/MODULAR_DESIGN_PHILOSOPHY.md)

## Activation Checklist

When ready to activate Phase 3, complete these steps:

### Pre-Activation
- [ ] Review Phase 2 data (minimum 2 weeks, 50+ tool uses)
- [ ] Confirm detection accuracy >95%
- [ ] Verify zero false positives in recent logs
- [ ] Test emergency bypass mechanism
- [ ] Update all documentation
- [ ] Brief team on changes and bypass procedure

### Activation
- [ ] Modify `validate_orchestrator_boundary()` return to `"status": "error"`
- [ ] Add emergency bypass check
- [ ] Update main() to handle error status
- [ ] Update hook docstring
- [ ] Commit with clear message: "feat: Activate Phase 3 orchestrator boundary enforcement"
- [ ] Update this decision record status to "Active"

### Post-Activation Monitoring
- [ ] Monitor hook logs for errors (first 48 hours)
- [ ] Track bypass usage frequency
- [ ] Collect user feedback
- [ ] Verify agent workflows unaffected
- [ ] Review after 1 week, 2 weeks, 1 month

### Success Criteria
- [ ] No unexpected blocking of agent operations
- [ ] Bypass usage <10% of sessions
- [ ] No hook crashes or errors
- [ ] User workflow adapts within 2 weeks
- [ ] Violations decrease over time (pattern learning)

## Notes

### Design Philosophy

This three-phase rollout embodies **ruthless simplicity** and **pragmatic trust**:

1. **Phase 1**: Build detection without enforcement
2. **Phase 2**: Validate detection in production (current)
3. **Phase 3**: Enforce only after proven reliable (this plan)

**Key insight**: Don't enforce until detection is validated with real data.

### Architectural Intent

The orchestrator boundary enforces **modular design philosophy**:
- **Main orchestrator**: Read-only, coordination-focused
- **Specialized agents**: Execute file modifications with proper context
- **Clear contracts**: Task tool is the interface between layers

This mirrors **Pure Delegation Architecture** [DECISION-002] at the AI workflow level.

### Future Enhancements (Not Required for Phase 3)

These could be explored after Phase 3 is stable:

- **Delegation suggestions**: Hook recommends which agent to use
- **Auto-delegation**: Orchestrator can trigger Task automatically
- **Metrics dashboard**: Visualize violation patterns over time
- **Agent routing rules**: More sophisticated agent selection logic
- **Graduated enforcement**: Soft blocks (requires confirmation) before hard blocks

**Status**: Ideas only - Phase 3 focuses on core blocking mechanism
