"""
Comprehensive tests for PreToolUse hook (orchestrator boundary enforcement).

Tests the actual hook script execution via subprocess, covering:
- Tool detection (blocked vs allowed)
- Session detection (orchestrator vs agent)
- Emergency bypass handling
- JSON output format
- Error handling (fail-open)
- Message content
"""

import json
import os
import subprocess
from pathlib import Path
from typing import Any

HOOK_PATH = Path("/workspaces/rzp-amplifier/.claude/hooks/pre-tool-use-boundary.py")


def run_hook(input_data: dict[str, Any], env_vars: dict[str, str] | None = None) -> tuple[dict[str, Any], int]:
    """
    Execute the PreToolUse hook script and return parsed output and exit code.

    Args:
        input_data: JSON input to pass to hook
        env_vars: Additional environment variables to set

    Returns:
        Tuple of (parsed JSON output, exit code)
    """
    env = os.environ.copy()
    if env_vars:
        env.update(env_vars)
    else:
        # Ensure bypass flag is NOT set by default
        env.pop("AMPLIFIER_BYPASS_BOUNDARY", None)
        env.pop("CLAUDE_AGENT_NAME", None)

    result = subprocess.run(
        [str(HOOK_PATH)],
        input=json.dumps(input_data),
        capture_output=True,
        text=True,
        env=env,
    )

    output = json.loads(result.stdout) if result.stdout else {}
    return output, result.returncode


class TestToolDetection:
    """Tests for detecting blocked vs allowed tools."""

    def test_blocks_edit_tool(self) -> None:
        """Edit tool should be blocked for orchestrator."""
        output, exit_code = run_hook({"tool_name": "Edit"})

        assert exit_code == 0
        assert output["hookSpecificOutput"]["permissionDecision"] == "deny"
        assert "Edit" in output["hookSpecificOutput"]["permissionDecisionReason"]

    def test_blocks_write_tool(self) -> None:
        """Write tool should be blocked for orchestrator."""
        output, exit_code = run_hook({"tool_name": "Write"})

        assert exit_code == 0
        assert output["hookSpecificOutput"]["permissionDecision"] == "deny"
        assert "Write" in output["hookSpecificOutput"]["permissionDecisionReason"]

    def test_blocks_multiedit_tool(self) -> None:
        """MultiEdit tool should be blocked for orchestrator."""
        output, exit_code = run_hook({"tool_name": "MultiEdit"})

        assert exit_code == 0
        assert output["hookSpecificOutput"]["permissionDecision"] == "deny"

    def test_blocks_notebookedit_tool(self) -> None:
        """NotebookEdit tool should be blocked for orchestrator."""
        output, exit_code = run_hook({"tool_name": "NotebookEdit"})

        assert exit_code == 0
        assert output["hookSpecificOutput"]["permissionDecision"] == "deny"

    def test_allows_read_tool(self) -> None:
        """Read tool should be allowed (analysis tool)."""
        output, exit_code = run_hook({"tool_name": "Read"})

        assert exit_code == 0
        assert output["hookSpecificOutput"]["permissionDecision"] == "allow"
        # Should be silent (no permissionDecisionReason)
        assert "permissionDecisionReason" not in output["hookSpecificOutput"]

    def test_allows_task_tool(self) -> None:
        """Task tool should be allowed (delegation tool)."""
        output, exit_code = run_hook({"tool_name": "Task"})

        assert exit_code == 0
        assert output["hookSpecificOutput"]["permissionDecision"] == "allow"
        assert "permissionDecisionReason" not in output["hookSpecificOutput"]

    def test_allows_bash_tool(self) -> None:
        """Bash tool should be allowed (testing/validation)."""
        output, exit_code = run_hook({"tool_name": "Bash"})

        assert exit_code == 0
        assert output["hookSpecificOutput"]["permissionDecision"] == "allow"

    def test_allows_grep_tool(self) -> None:
        """Grep tool should be allowed (analysis tool)."""
        output, exit_code = run_hook({"tool_name": "Grep"})

        assert exit_code == 0
        assert output["hookSpecificOutput"]["permissionDecision"] == "allow"

    def test_allows_todowrite_tool(self) -> None:
        """TodoWrite tool should be allowed (planning tool)."""
        output, exit_code = run_hook({"tool_name": "TodoWrite"})

        assert exit_code == 0
        assert output["hookSpecificOutput"]["permissionDecision"] == "allow"


class TestSessionDetection:
    """Tests for detecting agent vs orchestrator sessions."""

    def test_allows_agent_session_with_edit(self) -> None:
        """Agent sessions can use Edit tool."""
        output, exit_code = run_hook({"tool_name": "Edit"}, {"CLAUDE_AGENT_NAME": "modular-builder"})

        assert exit_code == 0
        assert output["hookSpecificOutput"]["permissionDecision"] == "allow"
        # Should be silent (agents don't need warnings)
        assert "permissionDecisionReason" not in output["hookSpecificOutput"]

    def test_allows_agent_session_with_write(self) -> None:
        """Agent sessions can use Write tool."""
        output, exit_code = run_hook({"tool_name": "Write"}, {"CLAUDE_AGENT_NAME": "test-coverage"})

        assert exit_code == 0
        assert output["hookSpecificOutput"]["permissionDecision"] == "allow"

    def test_blocks_orchestrator_session_with_edit(self) -> None:
        """Orchestrator (no CLAUDE_AGENT_NAME) cannot use Edit."""
        # Explicitly ensure CLAUDE_AGENT_NAME is not set
        output, exit_code = run_hook({"tool_name": "Edit"}, {})

        assert exit_code == 0
        assert output["hookSpecificOutput"]["permissionDecision"] == "deny"

    def test_blocks_orchestrator_session_with_write(self) -> None:
        """Orchestrator cannot use Write."""
        output, exit_code = run_hook({"tool_name": "Write"}, {})

        assert exit_code == 0
        assert output["hookSpecificOutput"]["permissionDecision"] == "deny"


class TestEmergencyBypass:
    """Tests for emergency bypass flag handling."""

    def test_bypass_flag_allows_blocked_tool(self) -> None:
        """AMPLIFIER_BYPASS_BOUNDARY=true allows blocked tools."""
        output, exit_code = run_hook({"tool_name": "Edit"}, {"AMPLIFIER_BYPASS_BOUNDARY": "true"})

        assert exit_code == 0
        assert output["hookSpecificOutput"]["permissionDecision"] == "allow"

    def test_bypass_flag_includes_warning(self) -> None:
        """Bypass should include warning message."""
        output, exit_code = run_hook({"tool_name": "Write"}, {"AMPLIFIER_BYPASS_BOUNDARY": "true"})

        assert exit_code == 0
        reason = output["hookSpecificOutput"]["permissionDecisionReason"]
        assert "BYPASS ACTIVE" in reason
        assert "emergency mode" in reason
        assert "Write" in reason

    def test_bypass_flag_case_insensitive(self) -> None:
        """Bypass flag should work with different cases."""
        output, exit_code = run_hook({"tool_name": "Edit"}, {"AMPLIFIER_BYPASS_BOUNDARY": "TRUE"})

        assert exit_code == 0
        assert output["hookSpecificOutput"]["permissionDecision"] == "allow"

    def test_bypass_flag_false_does_not_bypass(self) -> None:
        """AMPLIFIER_BYPASS_BOUNDARY=false should not bypass."""
        output, exit_code = run_hook({"tool_name": "Edit"}, {"AMPLIFIER_BYPASS_BOUNDARY": "false"})

        assert exit_code == 0
        assert output["hookSpecificOutput"]["permissionDecision"] == "deny"


class TestJsonOutputFormat:
    """Tests for correct JSON output structure."""

    def test_deny_returns_correct_json_structure(self) -> None:
        """Deny response should have correct JSON structure."""
        output, exit_code = run_hook({"tool_name": "Edit"})

        assert "hookSpecificOutput" in output
        assert "hookEventName" in output["hookSpecificOutput"]
        assert output["hookSpecificOutput"]["hookEventName"] == "PreToolUse"
        assert "permissionDecision" in output["hookSpecificOutput"]
        assert "permissionDecisionReason" in output["hookSpecificOutput"]

    def test_allow_returns_correct_json_structure(self) -> None:
        """Allow response should have correct JSON structure."""
        output, exit_code = run_hook({"tool_name": "Read"})

        assert "hookSpecificOutput" in output
        assert output["hookSpecificOutput"]["hookEventName"] == "PreToolUse"
        assert output["hookSpecificOutput"]["permissionDecision"] == "allow"

    def test_output_includes_permission_decision(self) -> None:
        """All outputs should include permissionDecision field."""
        for tool in ["Edit", "Read", "Task"]:
            output, _ = run_hook({"tool_name": tool})
            assert "permissionDecision" in output["hookSpecificOutput"]
            assert output["hookSpecificOutput"]["permissionDecision"] in ["allow", "deny"]

    def test_hook_event_name_is_correct(self) -> None:
        """hookEventName should always be PreToolUse."""
        for tool in ["Edit", "Write", "Read", "Task"]:
            output, _ = run_hook({"tool_name": tool})
            assert output["hookSpecificOutput"]["hookEventName"] == "PreToolUse"


class TestErrorHandling:
    """Tests for error handling and fail-open behavior."""

    def test_invalid_json_input_fails_open(self) -> None:
        """Invalid JSON should fail-open (allow operation)."""
        env = os.environ.copy()
        env.pop("AMPLIFIER_BYPASS_BOUNDARY", None)
        env.pop("CLAUDE_AGENT_NAME", None)

        result = subprocess.run(
            [str(HOOK_PATH)],
            input="not valid json",
            capture_output=True,
            text=True,
            env=env,
        )

        # Should fail-open: allow operation
        output = json.loads(result.stdout) if result.stdout else {}
        assert output.get("hookSpecificOutput", {}).get("permissionDecision") == "allow"
        # Should log error to stderr
        assert "ERROR" in result.stderr or result.returncode == 0

    def test_missing_tool_name_fails_open(self) -> None:
        """Missing tool_name should be treated as allowed (not in blocked list)."""
        output, exit_code = run_hook({})

        assert exit_code == 0
        assert output["hookSpecificOutput"]["permissionDecision"] == "allow"

    def test_empty_tool_name_fails_open(self) -> None:
        """Empty tool_name should be treated as allowed (not in blocked list)."""
        output, exit_code = run_hook({"tool_name": ""})

        assert exit_code == 0
        assert output["hookSpecificOutput"]["permissionDecision"] == "allow"

    def test_null_tool_name_fails_open(self) -> None:
        """Null tool_name should be treated as allowed."""
        output, exit_code = run_hook({"tool_name": None})

        assert exit_code == 0
        assert output["hookSpecificOutput"]["permissionDecision"] == "allow"


class TestMessageContent:
    """Tests for message content in deny responses."""

    def test_deny_message_includes_tool_name(self) -> None:
        """Deny message should mention the specific tool."""
        for tool in ["Edit", "Write", "MultiEdit", "NotebookEdit"]:
            output, _ = run_hook({"tool_name": tool})
            reason = output["hookSpecificOutput"]["permissionDecisionReason"]
            assert tool in reason

    def test_deny_message_suggests_delegation(self) -> None:
        """Deny message should suggest using Task for delegation."""
        output, _ = run_hook({"tool_name": "Edit"})
        reason = output["hookSpecificOutput"]["permissionDecisionReason"]

        assert "Task" in reason
        assert "delegate" in reason.lower()

    def test_deny_message_lists_allowed_tools(self) -> None:
        """Deny message should list allowed tools."""
        output, _ = run_hook({"tool_name": "Write"})
        reason = output["hookSpecificOutput"]["permissionDecisionReason"]

        # Should list analysis/delegation tools
        assert "Read" in reason
        assert "Task" in reason
        assert "Bash" in reason

    def test_deny_message_lists_blocked_tools(self) -> None:
        """Deny message should list blocked tools."""
        output, _ = run_hook({"tool_name": "Edit"})
        reason = output["hookSpecificOutput"]["permissionDecisionReason"]

        # Should list all blocked tools
        assert "Edit" in reason
        assert "Write" in reason
        assert "MultiEdit" in reason
        assert "NotebookEdit" in reason

    def test_deny_message_includes_bypass_instructions(self) -> None:
        """Deny message should mention emergency bypass."""
        output, _ = run_hook({"tool_name": "Edit"})
        reason = output["hookSpecificOutput"]["permissionDecisionReason"]

        assert "AMPLIFIER_BYPASS_BOUNDARY" in reason
        assert "emergency" in reason.lower() or "bypass" in reason.lower()

    def test_deny_message_references_documentation(self) -> None:
        """Deny message should reference decision documentation."""
        output, _ = run_hook({"tool_name": "Write"})
        reason = output["hookSpecificOutput"]["permissionDecisionReason"]

        assert "003-orchestrator-boundary-phase-3-enforcement.md" in reason


class TestExitCodes:
    """Tests for correct exit codes."""

    def test_successful_allow_exits_zero(self) -> None:
        """Allowing operation should exit 0."""
        _, exit_code = run_hook({"tool_name": "Read"})
        assert exit_code == 0

    def test_successful_deny_exits_zero(self) -> None:
        """Denying operation should exit 0 (not an error)."""
        _, exit_code = run_hook({"tool_name": "Edit"})
        assert exit_code == 0

    def test_bypass_exits_zero(self) -> None:
        """Bypass should exit 0."""
        _, exit_code = run_hook({"tool_name": "Edit"}, {"AMPLIFIER_BYPASS_BOUNDARY": "true"})
        assert exit_code == 0


class TestEdgeCases:
    """Tests for edge cases and unusual inputs."""

    def test_unknown_tool_name_allowed(self) -> None:
        """Unknown tools should be allowed (not in blocked list)."""
        output, exit_code = run_hook({"tool_name": "UnknownTool"})

        assert exit_code == 0
        assert output["hookSpecificOutput"]["permissionDecision"] == "allow"

    def test_case_sensitive_tool_matching(self) -> None:
        """Tool matching should be case-sensitive."""
        # "edit" (lowercase) should NOT be blocked
        output, _ = run_hook({"tool_name": "edit"})
        assert output["hookSpecificOutput"]["permissionDecision"] == "allow"

        # "Edit" (proper case) should be blocked
        output, _ = run_hook({"tool_name": "Edit"})
        assert output["hookSpecificOutput"]["permissionDecision"] == "deny"

    def test_extra_input_fields_ignored(self) -> None:
        """Extra fields in input should be ignored gracefully."""
        output, exit_code = run_hook({"tool_name": "Read", "extra_field": "ignored", "another": 123})

        assert exit_code == 0
        assert output["hookSpecificOutput"]["permissionDecision"] == "allow"

    def test_agent_name_empty_string_treated_as_orchestrator(self) -> None:
        """Empty CLAUDE_AGENT_NAME should be treated as orchestrator."""
        output, _ = run_hook({"tool_name": "Edit"}, {"CLAUDE_AGENT_NAME": ""})

        # Empty string is falsy in Python, so should block
        assert output["hookSpecificOutput"]["permissionDecision"] == "deny"
