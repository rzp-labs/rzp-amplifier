#!/usr/bin/env python3
"""
PostToolUse hook: Show warning after orchestrator uses implementation tools.
Does NOT block - just provides feedback to guide future behavior.

Exit codes:
  0: Always (informational only, never blocks)
"""

import json
import os
import sys
from pathlib import Path

MODIFICATION_TOOLS = {"Edit", "Write", "MultiEdit", "NotebookEdit"}


def main() -> None:
    """Show informational message after implementation tool use."""
    try:
        # Read JSON input from stdin
        input_data = json.load(sys.stdin)
        tool_name = input_data.get("tool_name") or input_data.get("toolName", "")

        # Only care about modification tools
        if tool_name not in MODIFICATION_TOOLS:
            sys.exit(0)

        # Check if agent is active (agents using tools is expected)
        agent_state_file = (
            Path(os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())) / ".claude" / "state" / "agent_active"
        )
        if agent_state_file.exists():
            # Agent active - this is expected behavior
            sys.exit(0)

        # Main orchestrator used implementation tool - show informational message
        file_path = input_data.get("toolInput", {}).get("file_path", "unknown")

        message = f"""
ℹ️  ORCHESTRATOR IMPLEMENTATION NOTICE

Tool: {tool_name}
File: {file_path}

Consider delegating to specialized agents via Task tool:
  Task → modular-builder: "Implement [specification]"

Available agents: modular-builder, bug-hunter, test-coverage,
                  refactor-architect, zen-architect, integration-specialist

This is informational - operation was allowed.
See CLAUDE.md for delegation patterns.
"""

        # Write to stderr (visible to user)
        print(message, file=sys.stderr)

    except Exception:
        # Silent failure for hooks - never break workflow
        pass

    # Always exit 0 (informational only)
    sys.exit(0)


if __name__ == "__main__":
    main()
