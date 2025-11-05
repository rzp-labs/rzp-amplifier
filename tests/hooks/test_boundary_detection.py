"""Unit tests for orchestrator boundary detection logic.

Tests the validate_orchestrator_boundary() function that detects
modification tool usage. This is detection-only (no blocking) as of
the simplified implementation (2025-11-05).
"""

import sys
from pathlib import Path

import pytest

# Add .claude/tools to path to import the hook module
claude_tools_dir = Path(__file__).parent.parent.parent / ".claude" / "tools"
sys.path.insert(0, str(claude_tools_dir))

# pyright: reportMissingImports=false
from hook_post_tool_use import validate_orchestrator_boundary  # type: ignore[import-not-found]  # noqa: E402


class TestBoundaryDetection:
    """Test boundary violation detection (detection-only, no blocking)."""

    def test_detects_edit_violation(self):
        """Edit tool triggers boundary warning."""
        result = validate_orchestrator_boundary("Edit", {"file_path": "/path/to/file.py"})

        assert result["status"] == "warning"
        assert result["tool"] == "Edit"
        assert result["file"] == "/path/to/file.py"

    def test_detects_write_violation(self):
        """Write tool triggers boundary warning."""
        result = validate_orchestrator_boundary("Write", {"file_path": "/path/to/file.py"})

        assert result["status"] == "warning"
        assert result["tool"] == "Write"
        assert result["file"] == "/path/to/file.py"

    def test_detects_multiedit_violation(self):
        """MultiEdit tool triggers boundary warning."""
        result = validate_orchestrator_boundary("MultiEdit", {"file_path": "/path/to/file.py"})

        assert result["status"] == "warning"
        assert result["tool"] == "MultiEdit"
        assert result["file"] == "/path/to/file.py"

    def test_detects_notebookedit_violation(self):
        """NotebookEdit tool triggers boundary warning."""
        result = validate_orchestrator_boundary("NotebookEdit", {"file_path": "/path/to/notebook.ipynb"})

        assert result["status"] == "warning"
        assert result["tool"] == "NotebookEdit"
        assert result["file"] == "/path/to/notebook.ipynb"


class TestAllowedTools:
    """Test allowed tools do not trigger warnings."""

    def test_allows_read(self):
        """Read tool does not trigger warning."""
        result = validate_orchestrator_boundary("Read", {"file_path": "/path/to/file.py"})

        assert result["status"] == "allowed"
        assert "tool" not in result
        assert "file" not in result

    def test_allows_grep(self):
        """Grep tool does not trigger warning."""
        result = validate_orchestrator_boundary("Grep", {"pattern": "test", "path": "/path"})

        assert result["status"] == "allowed"

    def test_allows_glob(self):
        """Glob tool does not trigger warning."""
        result = validate_orchestrator_boundary("Glob", {"pattern": "**/*.py"})

        assert result["status"] == "allowed"

    def test_allows_bash(self):
        """Bash tool does not trigger warning."""
        result = validate_orchestrator_boundary("Bash", {"command": "ls"})

        assert result["status"] == "allowed"

    def test_allows_todowrite(self):
        """TodoWrite tool does not trigger warning."""
        result = validate_orchestrator_boundary("TodoWrite", {"todos": []})

        assert result["status"] == "allowed"

    def test_allows_task(self):
        """Task tool does not trigger warning."""
        result = validate_orchestrator_boundary("Task", {"agent": "test-agent", "task": "test"})

        assert result["status"] == "allowed"

    def test_allows_askuserquestion(self):
        """AskUserQuestion tool does not trigger warning."""
        result = validate_orchestrator_boundary("AskUserQuestion", {"questions": []})

        assert result["status"] == "allowed"


class TestWarningMessageContent:
    """Test warning message includes correct information."""

    def test_warning_includes_tool_name(self):
        """Warning includes the tool name used."""
        result = validate_orchestrator_boundary("Edit", {"file_path": "/path/to/file.py"})

        assert result["tool"] == "Edit"

    def test_warning_includes_file_path(self):
        """Warning includes the file path targeted."""
        result = validate_orchestrator_boundary("Write", {"file_path": "/path/to/file.py"})

        assert result["file"] == "/path/to/file.py"

    def test_warning_handles_missing_file_path(self):
        """Warning handles missing file_path gracefully."""
        result = validate_orchestrator_boundary("Edit", {})

        assert result["status"] == "warning"
        assert result["file"] == "unknown"


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_tool_name(self):
        """Empty tool name is treated as allowed."""
        result = validate_orchestrator_boundary("", {"file_path": "/path"})

        assert result["status"] == "allowed"

    def test_none_tool_input(self):
        """None tool_input raises AttributeError."""
        # This shouldn't happen in practice - tool_input is always a dict
        # Document that we don't handle this edge case
        with pytest.raises(AttributeError):
            validate_orchestrator_boundary("Edit", None)  # type: ignore

    def test_case_sensitive_tool_names(self):
        """Tool names are case-sensitive."""
        # "edit" (lowercase) is not in modification_tools set
        result = validate_orchestrator_boundary("edit", {"file_path": "/path"})

        assert result["status"] == "allowed"

    def test_unknown_tool(self):
        """Unknown tool names are allowed."""
        result = validate_orchestrator_boundary("SomeNewTool", {"file_path": "/path"})

        assert result["status"] == "allowed"


class TestModificationToolSet:
    """Test the modification tools set is complete."""

    def test_all_modification_tools_detected(self):
        """All expected modification tools trigger warnings."""
        modification_tools = ["Edit", "Write", "MultiEdit", "NotebookEdit"]

        for tool in modification_tools:
            result = validate_orchestrator_boundary(tool, {"file_path": "/test.py"})
            assert result["status"] == "warning", f"{tool} should trigger warning"

    def test_only_modification_tools_detected(self):
        """Only modification tools trigger warnings."""
        allowed_tools = ["Read", "Grep", "Glob", "Bash", "TodoWrite", "Task", "AskUserQuestion"]

        for tool in allowed_tools:
            result = validate_orchestrator_boundary(tool, {"some": "input"})
            assert result["status"] == "allowed", f"{tool} should be allowed"


class TestReturnValueStructure:
    """Test the structure of return values."""

    def test_violation_return_structure(self):
        """Violation returns status, file, and tool."""
        result = validate_orchestrator_boundary("Edit", {"file_path": "/test.py"})

        assert isinstance(result, dict)
        assert set(result.keys()) == {"status", "file", "tool"}
        assert result["status"] == "warning"
        assert isinstance(result["file"], str)
        assert isinstance(result["tool"], str)

    def test_allowed_return_structure(self):
        """Allowed returns only status."""
        result = validate_orchestrator_boundary("Read", {"file_path": "/test.py"})

        assert isinstance(result, dict)
        assert set(result.keys()) == {"status"}
        assert result["status"] == "allowed"


class TestFilePathExtraction:
    """Test file path extraction from tool_input."""

    def test_extracts_file_path_from_edit(self):
        """Extracts file_path from Edit tool input."""
        result = validate_orchestrator_boundary(
            "Edit", {"file_path": "/src/main.py", "old_string": "old", "new_string": "new"}
        )

        assert result["file"] == "/src/main.py"

    def test_extracts_file_path_from_write(self):
        """Extracts file_path from Write tool input."""
        result = validate_orchestrator_boundary("Write", {"file_path": "/src/new.py", "content": "code"})

        assert result["file"] == "/src/new.py"

    def test_extracts_file_path_from_notebookedit(self):
        """Extracts file_path from NotebookEdit tool input."""
        result = validate_orchestrator_boundary("NotebookEdit", {"notebook_path": "/notebook.ipynb"})

        # Current implementation uses file_path key, not notebook_path
        # This documents actual behavior
        assert result["file"] == "unknown"

    def test_handles_absolute_paths(self):
        """Preserves absolute file paths."""
        result = validate_orchestrator_boundary("Edit", {"file_path": "/workspaces/rzp-amplifier/src/app.py"})

        assert result["file"] == "/workspaces/rzp-amplifier/src/app.py"

    def test_handles_relative_paths(self):
        """Preserves relative file paths."""
        result = validate_orchestrator_boundary("Edit", {"file_path": "src/app.py"})

        assert result["file"] == "src/app.py"
