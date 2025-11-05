#!/usr/bin/env python3
"""
PreToolUse hook: Block orchestrator from using implementation tools.

Enforces the orchestrator boundary by blocking Edit, Write, MultiEdit, and NotebookEdit
operations when called from the main orchestrator. Agents are allowed to use these tools.

Exit codes:
  0: Success (operation allowed or denied with proper JSON)
  1: Error (fail-open - allows operation)
"""

import json
import os
import sys


def main() -> None:
    """Process PreToolUse hook and decide whether to allow/deny operation."""
    try:
        # Read JSON input from stdin
        input_data = json.load(sys.stdin)
        tool_name = input_data.get("tool_name", "")

        # Emergency bypass
        if os.getenv("AMPLIFIER_BYPASS_BOUNDARY", "").lower() == "true":
            allow_with_warning(f"⚠️  BYPASS ACTIVE: Allowing {tool_name} (emergency mode)")
            return

        # Define blocked tools (implementation tools)
        blocked_tools = {"Edit", "Write", "MultiEdit", "NotebookEdit"}

        # If tool not in blocked list, allow silently
        if tool_name not in blocked_tools:
            allow_silent()
            return

        # Check if this is an agent session (agents can use implementation tools)
        agent_name = os.getenv("CLAUDE_AGENT_NAME", "")
        if agent_name:
            allow_silent()
            return

        # Main orchestrator trying to use blocked tool - DENY
        deny_with_message(tool_name)

    except Exception as e:
        # Fail-open: On error, allow the operation (don't break workflow)
        print(f"ERROR in pre-tool-use-boundary hook: {e}", file=sys.stderr)
        allow_silent()


def allow_silent() -> None:
    """Allow operation without message."""
    output = {"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "allow"}}
    print(json.dumps(output))
    sys.exit(0)


def allow_with_warning(message: str) -> None:
    """Allow operation but show warning message."""
    output = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "allow",
            "permissionDecisionReason": message,
        }
    }
    print(json.dumps(output))
    sys.exit(0)


def deny_with_message(tool_name: str) -> None:
    """Deny operation with helpful message."""
    message = f"""🚫 ORCHESTRATOR BOUNDARY VIOLATION

You attempted to use {tool_name} directly.

Your Role: Orchestrator (read-only, delegation-focused)
  ✅ Allowed: Read, Grep, Glob, TodoWrite, Task, Bash, AskUserQuestion
  ❌ BLOCKED: Edit, Write, MultiEdit, NotebookEdit (must delegate via Task)

Required Action: Use Task tool to delegate to specialized agent

Example:
  Task → modular-builder: "Implement [specification]"

Available Agents: modular-builder, bug-hunter, test-coverage,
                  refactor-architect, zen-architect, integration-specialist

Emergency Bypass: export AMPLIFIER_BYPASS_BOUNDARY=true

See: ai_working/decisions/003-orchestrator-boundary-phase-3-enforcement.md"""

    output = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": message,
        }
    }
    print(json.dumps(output))
    sys.exit(0)


if __name__ == "__main__":
    main()
