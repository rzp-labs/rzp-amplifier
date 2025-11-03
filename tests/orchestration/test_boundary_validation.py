"""Unit and integration tests for orchestrator boundary validation.

Tests the boundary enforcement system that ensures main Claude orchestrates
via Task delegation rather than modifying files directly.
"""

import os
from unittest import mock


# Import functions from hook (we'll need to make them importable)
def detect_agent_session_impl() -> bool:
    """Implementation of agent detection logic (mirroring hook logic)."""
    session_context = os.getenv("CLAUDE_SESSION_CONTEXT", "")
    if "agent:" in session_context:
        return True

    parent_tools = os.getenv("CLAUDE_PARENT_TOOLS", "").split(",")
    return "Task" in parent_tools


def validate_orchestrator_boundary_impl(tool_name: str, tool_input: dict) -> dict:
    """Implementation of boundary validation logic (mirroring hook logic).

    Phase 3: Returns 'error' status for violations, blocking operations.
    """
    modification_tools = {"Edit", "Write", "MultiEdit", "NotebookEdit"}

    if tool_name not in modification_tools:
        return {"status": "allowed"}

    # Emergency bypass check
    if os.getenv("AMPLIFIER_BYPASS_BOUNDARY") == "true":
        return {"status": "allowed", "bypassed": True}

    if detect_agent_session_impl():
        return {"status": "allowed"}

    file_path = tool_input.get("file_path", "unknown")
    violation_msg = f"Main Claude attempted to use {tool_name} on: {file_path}"

    # Phase 3: Return error status to block operations
    return {"status": "error", "message": violation_msg, "file": file_path, "tool": tool_name}


class TestDetectAgentSession:
    """Tests for agent session detection."""

    def test_no_agent_markers(self):
        """Returns False when no agent markers present."""
        with mock.patch.dict(os.environ, {"CLAUDE_SESSION_CONTEXT": "", "CLAUDE_PARENT_TOOLS": ""}, clear=True):
            assert detect_agent_session_impl() is False

    def test_session_context_marker(self):
        """Returns True when CLAUDE_SESSION_CONTEXT contains 'agent:'."""
        with mock.patch.dict(os.environ, {"CLAUDE_SESSION_CONTEXT": "agent:modular-builder"}, clear=True):
            assert detect_agent_session_impl() is True

    def test_parent_tools_marker(self):
        """Returns True when CLAUDE_PARENT_TOOLS contains 'Task'."""
        with mock.patch.dict(os.environ, {"CLAUDE_PARENT_TOOLS": "Read,Grep,Task,Edit"}, clear=True):
            assert detect_agent_session_impl() is True

    def test_both_markers_present(self):
        """Returns True when both markers present."""
        with mock.patch.dict(
            os.environ, {"CLAUDE_SESSION_CONTEXT": "agent:bug-hunter", "CLAUDE_PARENT_TOOLS": "Task"}, clear=True
        ):
            assert detect_agent_session_impl() is True

    def test_different_session_context(self):
        """Returns False when session context doesn't contain 'agent:'."""
        with mock.patch.dict(os.environ, {"CLAUDE_SESSION_CONTEXT": "main:session-123"}, clear=True):
            assert detect_agent_session_impl() is False

    def test_task_in_wrong_position(self):
        """Returns True when Task is in parent tools regardless of position."""
        with mock.patch.dict(os.environ, {"CLAUDE_PARENT_TOOLS": "Read,Task,Write"}, clear=True):
            assert detect_agent_session_impl() is True


class TestValidateOrchestratorBoundary:
    """Tests for orchestrator boundary validation."""

    def test_read_tool_allowed(self):
        """Non-modification tools return allowed status."""
        result = validate_orchestrator_boundary_impl("Read", {"file_path": "test.py"})
        assert result == {"status": "allowed"}

    def test_grep_tool_allowed(self):
        """Grep tool returns allowed status."""
        result = validate_orchestrator_boundary_impl("Grep", {"pattern": "test"})
        assert result == {"status": "allowed"}

    def test_bash_tool_allowed(self):
        """Bash tool returns allowed status."""
        result = validate_orchestrator_boundary_impl("Bash", {"command": "ls"})
        assert result == {"status": "allowed"}

    def test_agent_edit_allowed(self):
        """Agents using Edit should be allowed."""
        with mock.patch.dict(os.environ, {"CLAUDE_SESSION_CONTEXT": "agent:modular-builder"}, clear=True):
            result = validate_orchestrator_boundary_impl("Edit", {"file_path": "test.py"})
            assert result["status"] == "allowed"

    def test_agent_write_allowed(self):
        """Agents using Write should be allowed."""
        with mock.patch.dict(os.environ, {"CLAUDE_PARENT_TOOLS": "Task"}, clear=True):
            result = validate_orchestrator_boundary_impl("Write", {"file_path": "new.py"})
            assert result["status"] == "allowed"

    def test_agent_multiedit_allowed(self):
        """Agents using MultiEdit should be allowed."""
        with mock.patch.dict(os.environ, {"CLAUDE_SESSION_CONTEXT": "agent:refactor-architect"}, clear=True):
            result = validate_orchestrator_boundary_impl("MultiEdit", {"file_path": "code.py"})
            assert result["status"] == "allowed"

    def test_agent_notebookedit_allowed(self):
        """Agents using NotebookEdit should be allowed."""
        with mock.patch.dict(os.environ, {"CLAUDE_PARENT_TOOLS": "Task,Read"}, clear=True):
            result = validate_orchestrator_boundary_impl("NotebookEdit", {"notebook_path": "notebook.ipynb"})
            assert result["status"] == "allowed"

    def test_main_edit_triggers_error(self):
        """Main Claude using Edit should trigger error (Phase 3)."""
        with mock.patch.dict(os.environ, {}, clear=True):
            result = validate_orchestrator_boundary_impl("Edit", {"file_path": "test.py"})
            assert result["status"] == "error"
            assert result["file"] == "test.py"
            assert result["tool"] == "Edit"
            assert "Main Claude attempted" in result["message"]

    def test_main_write_triggers_error(self):
        """Main Claude using Write should trigger error (Phase 3)."""
        with mock.patch.dict(os.environ, {}, clear=True):
            result = validate_orchestrator_boundary_impl("Write", {"file_path": "new.py"})
            assert result["status"] == "error"
            assert result["file"] == "new.py"
            assert result["tool"] == "Write"

    def test_main_multiedit_triggers_error(self):
        """Main Claude using MultiEdit should trigger error (Phase 3)."""
        with mock.patch.dict(os.environ, {}, clear=True):
            result = validate_orchestrator_boundary_impl("MultiEdit", {"file_path": "code.py"})
            assert result["status"] == "error"
            assert result["tool"] == "MultiEdit"

    def test_main_notebookedit_triggers_error(self):
        """Main Claude using NotebookEdit should trigger error (Phase 3)."""
        with mock.patch.dict(os.environ, {}, clear=True):
            result = validate_orchestrator_boundary_impl("NotebookEdit", {"notebook_path": "notebook.ipynb"})
            assert result["status"] == "error"
            assert result["tool"] == "NotebookEdit"

    def test_emergency_bypass_allows_operations(self):
        """Emergency bypass allows operations with AMPLIFIER_BYPASS_BOUNDARY=true."""
        with mock.patch.dict(os.environ, {"AMPLIFIER_BYPASS_BOUNDARY": "true"}, clear=True):
            result = validate_orchestrator_boundary_impl("Edit", {"file_path": "test.py"})
            assert result["status"] == "allowed"
            assert result.get("bypassed") is True

    def test_bypass_requires_exact_true_value(self):
        """Emergency bypass only works with exact 'true' value."""
        # Should NOT bypass with other values
        for bypass_value in ["1", "yes", "True", "TRUE", ""]:
            with mock.patch.dict(os.environ, {"AMPLIFIER_BYPASS_BOUNDARY": bypass_value}, clear=True):
                result = validate_orchestrator_boundary_impl("Edit", {"file_path": "test.py"})
                assert result["status"] == "error", f"Bypass incorrectly activated for value: {bypass_value}"

    def test_unknown_file_path(self):
        """Handles missing file_path gracefully."""
        with mock.patch.dict(os.environ, {}, clear=True):
            result = validate_orchestrator_boundary_impl("Edit", {})
            assert result["status"] == "error"
            assert result["file"] == "unknown"


class TestIntegrationScenarios:
    """Integration tests for real-world scenarios."""

    def test_scenario_main_orchestrator_reads_and_delegates(self):
        """Main Claude should read files and delegate modifications."""
        with mock.patch.dict(os.environ, {}, clear=True):
            # Main can read
            read_result = validate_orchestrator_boundary_impl("Read", {"file_path": "src/app.py"})
            assert read_result["status"] == "allowed"

            # Main can grep
            grep_result = validate_orchestrator_boundary_impl("Grep", {"pattern": "def main"})
            assert grep_result["status"] == "allowed"

            # Main cannot edit directly (Phase 3: blocked)
            edit_result = validate_orchestrator_boundary_impl("Edit", {"file_path": "src/app.py"})
            assert edit_result["status"] == "error"

    def test_scenario_agent_full_permissions(self):
        """Agents have full file modification permissions."""
        with mock.patch.dict(os.environ, {"CLAUDE_SESSION_CONTEXT": "agent:modular-builder"}, clear=True):
            # Agent can read
            read_result = validate_orchestrator_boundary_impl("Read", {"file_path": "src/app.py"})
            assert read_result["status"] == "allowed"

            # Agent can edit
            edit_result = validate_orchestrator_boundary_impl("Edit", {"file_path": "src/app.py"})
            assert edit_result["status"] == "allowed"

            # Agent can write
            write_result = validate_orchestrator_boundary_impl("Write", {"file_path": "src/new.py"})
            assert write_result["status"] == "allowed"

    def test_scenario_multiple_violations(self):
        """Multiple violations are each detected (Phase 3: errors)."""
        with mock.patch.dict(os.environ, {}, clear=True):
            violations = []

            # First violation
            result1 = validate_orchestrator_boundary_impl("Edit", {"file_path": "file1.py"})
            if result1["status"] == "error":
                violations.append(result1)

            # Second violation
            result2 = validate_orchestrator_boundary_impl("Write", {"file_path": "file2.py"})
            if result2["status"] == "error":
                violations.append(result2)

            # Third violation
            result3 = validate_orchestrator_boundary_impl("MultiEdit", {"file_path": "file3.py"})
            if result3["status"] == "error":
                violations.append(result3)

            assert len(violations) == 3
            assert violations[0]["file"] == "file1.py"
            assert violations[1]["file"] == "file2.py"
            assert violations[2]["file"] == "file3.py"

    def test_scenario_mixed_operations(self):
        """Mixed allowed and blocked operations work correctly (Phase 3)."""
        with mock.patch.dict(os.environ, {}, clear=True):
            operations = [
                ("Read", {"file_path": "test.py"}, "allowed"),
                ("Edit", {"file_path": "test.py"}, "error"),
                ("Grep", {"pattern": "test"}, "allowed"),
                ("Write", {"file_path": "new.py"}, "error"),
                ("Bash", {"command": "ls"}, "allowed"),
                ("MultiEdit", {"file_path": "code.py"}, "error"),
            ]

            for tool_name, tool_input, expected_status in operations:
                result = validate_orchestrator_boundary_impl(tool_name, tool_input)
                assert result["status"] == expected_status, (
                    f"{tool_name} returned {result['status']}, expected {expected_status}"
                )
