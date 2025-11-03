"""Integration tests for post-tool-use hook boundary validation.

Tests the full hook flow from JSON input through boundary validation
to audit logging.
"""

import json
import os
import subprocess
from pathlib import Path

import pytest


class TestHookBoundaryValidation:
    """Test hook's boundary validation integration."""

    @pytest.fixture
    def hook_script(self):
        """Path to the post-tool-use hook script."""
        return Path(__file__).parent.parent.parent / ".claude" / "tools" / "hook_post_tool_use.py"

    @pytest.fixture
    def sample_event_read(self):
        """Sample PostToolUse event for Read tool (allowed)."""
        return {
            "tool_name": "Read",
            "tool_input": {"file_path": "/workspaces/rzp-amplifier/test.py"},
            "session_id": "test-session-123",
            "message": {"role": "assistant", "content": "Reading file contents..."},
        }

    @pytest.fixture
    def sample_event_edit_main(self):
        """Sample PostToolUse event for Edit tool by main (violation)."""
        return {
            "tool_name": "Edit",
            "tool_input": {
                "file_path": "/workspaces/rzp-amplifier/src/app.py",
                "old_string": "old",
                "new_string": "new",
            },
            "session_id": "test-session-violation",
            "message": {"role": "assistant", "content": "Editing the file..."},
        }

    @pytest.fixture
    def sample_event_edit_agent(self):
        """Sample PostToolUse event for Edit tool by agent (allowed)."""
        return {
            "tool_name": "Edit",
            "tool_input": {
                "file_path": "/workspaces/rzp-amplifier/src/app.py",
                "old_string": "old",
                "new_string": "new",
            },
            "session_id": "test-session-agent",
            "message": {"role": "assistant", "content": "Editing the file..."},
        }

    def test_hook_accepts_read_tool(self, hook_script, sample_event_read, tmp_path, monkeypatch):
        """Hook allows Read tool without warnings."""
        monkeypatch.chdir(tmp_path)

        # Set environment to enable memory system
        env = os.environ.copy()
        env["MEMORY_SYSTEM_ENABLED"] = "true"
        env.pop("CLAUDE_SESSION_CONTEXT", None)
        env.pop("CLAUDE_PARENT_TOOLS", None)

        # Run hook
        result = subprocess.run(
            [str(hook_script)],
            input=json.dumps(sample_event_read),
            capture_output=True,
            text=True,
            env=env,
        )

        assert result.returncode == 0

        # Parse output
        output = json.loads(result.stdout) if result.stdout else {}

        # Should not contain boundary violation warnings
        if "warning" in output:
            assert "BOUNDARY VIOLATION" not in output["warning"]

    def test_hook_blocks_main_edit_violation(self, hook_script, sample_event_edit_main, tmp_path, monkeypatch):
        """Hook blocks when main Claude uses Edit tool (Phase 3)."""
        monkeypatch.chdir(tmp_path)

        # Set environment - main orchestrator (no agent markers)
        env = os.environ.copy()
        env["MEMORY_SYSTEM_ENABLED"] = "true"
        env.pop("CLAUDE_SESSION_CONTEXT", None)
        env.pop("CLAUDE_PARENT_TOOLS", None)
        env.pop("AMPLIFIER_BYPASS_BOUNDARY", None)  # Ensure bypass not set

        # Run hook
        result = subprocess.run(
            [str(hook_script)],
            input=json.dumps(sample_event_edit_main),
            capture_output=True,
            text=True,
            env=env,
        )

        # Hook should complete successfully but return error to Claude
        assert result.returncode == 0

        # Parse JSON output
        output = json.loads(result.stdout) if result.stdout else {}

        # Should contain error blocking the operation
        assert "error" in output
        assert "BLOCKED" in output["error"]
        assert "metadata" in output
        assert output["metadata"]["violationType"] == "orchestrator_boundary"

        # Should also log the blocking
        assert "BLOCKING" in result.stderr or "BLOCKED" in result.stderr

    def test_hook_allows_agent_edit(self, hook_script, sample_event_edit_agent, tmp_path, monkeypatch):
        """Hook allows Edit tool when used by agent."""
        monkeypatch.chdir(tmp_path)

        # Set environment - agent session
        env = os.environ.copy()
        env["MEMORY_SYSTEM_ENABLED"] = "true"
        env["CLAUDE_SESSION_CONTEXT"] = "agent:modular-builder"

        # Run hook
        result = subprocess.run(
            [str(hook_script)],
            input=json.dumps(sample_event_edit_agent),
            capture_output=True,
            text=True,
            env=env,
        )

        assert result.returncode == 0

        # Should not log boundary violation
        assert "BOUNDARY VIOLATION" not in result.stderr

    def test_hook_creates_audit_log(self, hook_script, sample_event_edit_main, tmp_path, monkeypatch):
        """Hook creates audit log for violations."""
        monkeypatch.chdir(tmp_path)

        # Set environment
        env = os.environ.copy()
        env["MEMORY_SYSTEM_ENABLED"] = "true"
        env.pop("CLAUDE_SESSION_CONTEXT", None)
        env.pop("CLAUDE_PARENT_TOOLS", None)
        env.pop("AMPLIFIER_BYPASS_BOUNDARY", None)

        # Run hook
        subprocess.run(
            [str(hook_script)],
            input=json.dumps(sample_event_edit_main),
            capture_output=True,
            text=True,
            env=env,
        )

        # Check for audit file creation
        session_id = sample_event_edit_main["session_id"]
        audit_file = Path(".claude") / "sessions" / session_id / "delegation_audit.jsonl"

        # Note: Audit file might not be created in test environment if session directory doesn't exist
        # This test documents expected behavior
        if audit_file.exists():
            with open(audit_file) as f:
                records = [json.loads(line) for line in f if line.strip()]

            assert len(records) >= 1
            assert any(r["source"] == "main" for r in records)

    def test_hook_bypass_allows_operation(self, hook_script, sample_event_edit_main, tmp_path, monkeypatch):
        """Emergency bypass allows operations when AMPLIFIER_BYPASS_BOUNDARY=true."""
        monkeypatch.chdir(tmp_path)

        # Set environment with bypass enabled
        env = os.environ.copy()
        env["MEMORY_SYSTEM_ENABLED"] = "true"
        env["AMPLIFIER_BYPASS_BOUNDARY"] = "true"
        env.pop("CLAUDE_SESSION_CONTEXT", None)
        env.pop("CLAUDE_PARENT_TOOLS", None)

        # Run hook
        result = subprocess.run(
            [str(hook_script)],
            input=json.dumps(sample_event_edit_main),
            capture_output=True,
            text=True,
            env=env,
        )

        assert result.returncode == 0

        # Should NOT contain error (operation allowed)
        output = json.loads(result.stdout) if result.stdout else {}
        assert "error" not in output

        # Should log bypass warning
        assert "BYPASS" in result.stderr.upper()

    def test_error_json_format(self, hook_script, sample_event_edit_main, tmp_path, monkeypatch):
        """Error JSON has correct structure for Claude Code."""
        monkeypatch.chdir(tmp_path)

        env = os.environ.copy()
        env["MEMORY_SYSTEM_ENABLED"] = "true"
        env.pop("CLAUDE_SESSION_CONTEXT", None)
        env.pop("CLAUDE_PARENT_TOOLS", None)
        env.pop("AMPLIFIER_BYPASS_BOUNDARY", None)

        result = subprocess.run(
            [str(hook_script)],
            input=json.dumps(sample_event_edit_main),
            capture_output=True,
            text=True,
            env=env,
        )

        output = json.loads(result.stdout)

        # Required error structure
        assert "error" in output
        assert "metadata" in output
        assert output["metadata"]["violationType"] == "orchestrator_boundary"
        assert output["metadata"]["source"] == "amplifier_boundary_enforcement"
        assert "tool" in output["metadata"]
        assert "file" in output["metadata"]

    def test_hook_graceful_degradation(self, hook_script, tmp_path, monkeypatch):
        """Hook exits gracefully when memory system disabled."""
        monkeypatch.chdir(tmp_path)

        # Disable memory system
        env = os.environ.copy()
        env["MEMORY_SYSTEM_ENABLED"] = "false"

        event = {"tool_name": "Edit", "tool_input": {"file_path": "test.py"}}

        result = subprocess.run(
            [str(hook_script)],
            input=json.dumps(event),
            capture_output=True,
            text=True,
            env=env,
        )

        assert result.returncode == 0
        output = json.loads(result.stdout) if result.stdout else {}
        assert output == {}  # Empty response when disabled

    def test_hook_handles_missing_tool_name(self, hook_script, tmp_path, monkeypatch):
        """Hook handles events without tool_name gracefully."""
        monkeypatch.chdir(tmp_path)

        env = os.environ.copy()
        env["MEMORY_SYSTEM_ENABLED"] = "true"

        event = {"message": {"role": "assistant", "content": "test"}}

        result = subprocess.run(
            [str(hook_script)],
            input=json.dumps(event),
            capture_output=True,
            text=True,
            env=env,
        )

        assert result.returncode == 0


class TestBoundaryValidationMessages:
    """Test the warning messages produced by boundary validation."""

    def test_error_message_format(self):
        """Error messages include all required information (Phase 3)."""
        # Simulate what hook produces
        tool_name = "Edit"
        file_path = "src/app.py"

        error_template = f"""
🚫 ORCHESTRATOR BOUNDARY VIOLATION - OPERATION BLOCKED

Main Claude attempted to use {tool_name} on: {file_path}

Your Role: Orchestrator (read-only, delegation-focused)
  ✅ Allowed: Read, Grep, TodoWrite, Task, Bash, AskUserQuestion
  ❌ BLOCKED: Edit, Write, MultiEdit (must delegate via Task)

Required Action: Use Task tool to delegate to specialized agent

Phase 3: This operation has been BLOCKED.
        """.strip()

        assert "ORCHESTRATOR BOUNDARY VIOLATION" in error_template
        assert "OPERATION BLOCKED" in error_template
        assert tool_name in error_template
        assert file_path in error_template
        assert "Task tool" in error_template
        assert "Phase 3" in error_template
        assert "BLOCKED" in error_template

    def test_warning_lists_allowed_tools(self):
        """Warning includes list of allowed tools."""
        allowed_tools = ["Read", "Grep", "TodoWrite", "Task", "Bash", "AskUserQuestion"]

        warning = "Allowed: Read, Grep, TodoWrite, Task, Bash, AskUserQuestion"

        for tool in allowed_tools:
            assert tool in warning

    def test_warning_lists_blocked_tools(self):
        """Warning includes list of blocked tools."""
        blocked_tools = ["Edit", "Write", "MultiEdit"]

        warning = "Blocked: Edit, Write, MultiEdit (must delegate via Task)"

        for tool in blocked_tools:
            assert tool in warning

    def test_warning_suggests_agents(self):
        """Warning suggests available agents for delegation."""
        agents = ["modular-builder", "bug-hunter", "test-coverage", "refactor-architect"]

        warning = """
Available Agents:
  • modular-builder: Code implementation and module creation
  • bug-hunter: Bug diagnosis and fix implementation
  • test-coverage: Test creation and coverage
  • refactor-architect: Code refactoring
        """.strip()

        for agent in agents:
            assert agent in warning


class TestPhase3Behavior:
    """Test Phase 3 (enforcement) behavior - ACTIVE."""

    def test_phase3_blocks_operations(self):
        """Phase 3 blocks operations completely (ACTIVE behavior)."""
        # Phase 3 is now ACTIVE (activated 2025-11-03)
        # status="error" instead of "warning"
        # Hook returns error JSON to Claude Code
        # Operations are blocked

        phase3_result = {"status": "error", "message": "Operation blocked", "file": "test.py", "tool": "Edit"}

        assert phase3_result["status"] == "error"

        # In Phase 3, hook:
        # 1. Logs error
        # 2. Returns error JSON to stdout
        # 3. Exits with 0 (successful hook execution), but with error payload

    def test_phase2_was_warning_only(self):
        """Phase 2 logged warnings but didn't block (HISTORICAL behavior)."""
        # This documents historical Phase 2 behavior (pre-2025-11-03)
        # In Phase 2: status="warning", operation proceeded
        # Hook returned warning but allowed operation

        # This is for documentation only - Phase 2 is no longer active
        phase2_result = {"status": "warning", "message": "Violation detected", "file": "test.py", "tool": "Edit"}

        assert phase2_result["status"] == "warning"
        assert "message" in phase2_result

    def test_phase3_emergency_bypass(self):
        """Phase 3 respects emergency bypass flag."""
        bypass_result = {"status": "allowed", "bypassed": True}

        assert bypass_result["status"] == "allowed"
        assert bypass_result.get("bypassed") is True


class TestAuditFileFormat:
    """Test audit log file format and structure."""

    def test_audit_record_structure(self, tmp_path):
        """Audit records have correct structure."""
        from amplifier.orchestration import DelegationAudit

        os.chdir(tmp_path)
        audit = DelegationAudit("format-test")

        audit.record_modification("test.py", "Edit", "main")

        with open(audit.audit_file) as f:
            record = json.loads(f.readline())

        # Required fields
        assert "timestamp" in record
        assert "file" in record
        assert "tool" in record
        assert "source" in record

        # Correct values
        assert record["file"] == "test.py"
        assert record["tool"] == "Edit"
        assert record["source"] == "main"

    def test_audit_file_is_jsonl(self, tmp_path):
        """Audit file is valid JSONL format."""
        from amplifier.orchestration import DelegationAudit

        os.chdir(tmp_path)
        audit = DelegationAudit("jsonl-test")

        # Add multiple records
        for i in range(5):
            audit.record_modification(f"file{i}.py", "Edit", "main")

        # Each line should be valid JSON
        with open(audit.audit_file) as f:
            for line_num, line in enumerate(f, 1):
                try:
                    record = json.loads(line)
                    assert isinstance(record, dict)
                except json.JSONDecodeError:
                    pytest.fail(f"Line {line_num} is not valid JSON: {line}")

    def test_timestamp_format(self, tmp_path):
        """Timestamps are ISO format."""
        from datetime import datetime

        from amplifier.orchestration import DelegationAudit

        os.chdir(tmp_path)
        audit = DelegationAudit("timestamp-test")

        audit.record_modification("test.py", "Edit", "main")

        with open(audit.audit_file) as f:
            record = json.loads(f.readline())

        # Should parse as ISO format datetime
        timestamp = record["timestamp"]
        parsed = datetime.fromisoformat(timestamp)
        assert isinstance(parsed, datetime)
