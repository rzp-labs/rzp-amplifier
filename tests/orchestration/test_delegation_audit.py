"""Tests for DelegationAudit class.

Tests the audit logging system that tracks file modifications and
identifies orchestrator boundary violations.
"""

import json

from amplifier.orchestration import DelegationAudit


class TestDelegationAuditBasics:
    """Basic functionality tests for DelegationAudit."""

    def test_initialization(self, tmp_path):
        """Can initialize with session ID."""
        audit = DelegationAudit("test-session-123")
        assert audit.session_id == "test-session-123"
        assert str(audit.audit_file).endswith("test-session-123/delegation_audit.jsonl")

    def test_creates_session_directory(self, tmp_path, monkeypatch):
        """Creates session directory if it doesn't exist."""
        monkeypatch.chdir(tmp_path)
        audit = DelegationAudit("new-session")

        # Record something to trigger file creation
        audit.record_modification("test.py", "Edit", "main")

        assert audit.audit_file.exists()
        assert audit.audit_file.parent.exists()


class TestRecordModification:
    """Tests for recording file modifications."""

    def test_record_main_modification(self, tmp_path, monkeypatch):
        """Can record main orchestrator modification."""
        monkeypatch.chdir(tmp_path)
        audit = DelegationAudit("session-1")

        audit.record_modification("src/app.py", "Edit", "main")

        # Verify file was created
        assert audit.audit_file.exists()

        # Verify content
        with open(audit.audit_file) as f:
            record = json.loads(f.readline())

        assert record["file"] == "src/app.py"
        assert record["tool"] == "Edit"
        assert record["source"] == "main"
        assert "timestamp" in record

    def test_record_agent_modification(self, tmp_path, monkeypatch):
        """Can record agent modification."""
        monkeypatch.chdir(tmp_path)
        audit = DelegationAudit("session-2")

        audit.record_modification("src/utils.py", "Write", "agent")

        with open(audit.audit_file) as f:
            record = json.loads(f.readline())

        assert record["file"] == "src/utils.py"
        assert record["tool"] == "Write"
        assert record["source"] == "agent"

    def test_record_multiple_modifications(self, tmp_path, monkeypatch):
        """Can record multiple modifications."""
        monkeypatch.chdir(tmp_path)
        audit = DelegationAudit("session-3")

        audit.record_modification("file1.py", "Edit", "main")
        audit.record_modification("file2.py", "Write", "agent")
        audit.record_modification("file3.py", "MultiEdit", "main")

        # Verify all three records
        with open(audit.audit_file) as f:
            lines = f.readlines()

        assert len(lines) == 3
        records = [json.loads(line) for line in lines]

        assert records[0]["file"] == "file1.py"
        assert records[1]["file"] == "file2.py"
        assert records[2]["file"] == "file3.py"

    def test_appends_to_existing_file(self, tmp_path, monkeypatch):
        """Appends to existing audit file."""
        monkeypatch.chdir(tmp_path)
        audit = DelegationAudit("session-4")

        # First modification
        audit.record_modification("first.py", "Edit", "main")

        # Second modification (should append)
        audit.record_modification("second.py", "Write", "main")

        with open(audit.audit_file) as f:
            lines = f.readlines()

        assert len(lines) == 2


class TestGetViolations:
    """Tests for retrieving boundary violations."""

    def test_empty_audit_file(self, tmp_path, monkeypatch):
        """Returns empty list when no audit file exists."""
        monkeypatch.chdir(tmp_path)
        audit = DelegationAudit("empty-session")

        violations = audit.get_violations()
        assert violations == []

    def test_no_violations(self, tmp_path, monkeypatch):
        """Returns empty list when only agent modifications exist."""
        monkeypatch.chdir(tmp_path)
        audit = DelegationAudit("clean-session")

        audit.record_modification("file1.py", "Edit", "agent")
        audit.record_modification("file2.py", "Write", "agent")

        violations = audit.get_violations()
        assert violations == []

    def test_single_violation(self, tmp_path, monkeypatch):
        """Returns violation when main modifies file."""
        monkeypatch.chdir(tmp_path)
        audit = DelegationAudit("violation-session")

        audit.record_modification("bad.py", "Edit", "main")

        violations = audit.get_violations()
        assert len(violations) == 1
        assert violations[0]["file"] == "bad.py"
        assert violations[0]["source"] == "main"

    def test_multiple_violations(self, tmp_path, monkeypatch):
        """Returns all violations."""
        monkeypatch.chdir(tmp_path)
        audit = DelegationAudit("multi-violation")

        audit.record_modification("file1.py", "Edit", "main")
        audit.record_modification("file2.py", "Write", "agent")  # Not a violation
        audit.record_modification("file3.py", "MultiEdit", "main")
        audit.record_modification("file4.py", "Edit", "main")

        violations = audit.get_violations()
        assert len(violations) == 3

        violation_files = [v["file"] for v in violations]
        assert "file1.py" in violation_files
        assert "file3.py" in violation_files
        assert "file4.py" in violation_files
        assert "file2.py" not in violation_files

    def test_mixed_sources(self, tmp_path, monkeypatch):
        """Only returns main source violations."""
        monkeypatch.chdir(tmp_path)
        audit = DelegationAudit("mixed-session")

        # Mix of main and agent modifications
        audit.record_modification("main1.py", "Edit", "main")
        audit.record_modification("agent1.py", "Edit", "agent")
        audit.record_modification("main2.py", "Write", "main")
        audit.record_modification("agent2.py", "Write", "agent")

        violations = audit.get_violations()
        assert len(violations) == 2

        for v in violations:
            assert v["source"] == "main"


class TestValidateSession:
    """Tests for session validation."""

    def test_clean_session(self, tmp_path, monkeypatch):
        """Clean session returns clean status."""
        monkeypatch.chdir(tmp_path)
        audit = DelegationAudit("clean")

        audit.record_modification("file.py", "Edit", "agent")

        result = audit.validate_session()
        assert result["status"] == "clean"
        assert result["count"] == 0
        assert result["violations"] == []

    def test_violated_session(self, tmp_path, monkeypatch):
        """Violated session returns violated status."""
        monkeypatch.chdir(tmp_path)
        audit = DelegationAudit("violated")

        audit.record_modification("bad.py", "Edit", "main")

        result = audit.validate_session()
        assert result["status"] == "violated"
        assert result["count"] == 1
        assert len(result["violations"]) == 1

    def test_violation_count(self, tmp_path, monkeypatch):
        """Returns correct violation count."""
        monkeypatch.chdir(tmp_path)
        audit = DelegationAudit("count-test")

        # Add 5 violations
        for i in range(5):
            audit.record_modification(f"file{i}.py", "Edit", "main")

        result = audit.validate_session()
        assert result["count"] == 5
        assert len(result["violations"]) == 5


class TestReport:
    """Tests for human-readable report generation."""

    def test_clean_session_report(self, tmp_path, monkeypatch):
        """Clean session returns success message."""
        monkeypatch.chdir(tmp_path)
        audit = DelegationAudit("clean-report")

        audit.record_modification("file.py", "Edit", "agent")

        report = audit.report()
        assert "✅ Clean session" in report
        assert "properly delegated" in report

    def test_single_violation_report(self, tmp_path, monkeypatch):
        """Single violation report shows file and tool."""
        monkeypatch.chdir(tmp_path)
        audit = DelegationAudit("single-report")

        audit.record_modification("bad.py", "Edit", "main")

        report = audit.report()
        assert "⚠️" in report
        assert "1 boundary violation" in report
        assert "bad.py" in report
        assert "Edit" in report

    def test_multiple_violations_report(self, tmp_path, monkeypatch):
        """Multiple violations report shows all violations."""
        monkeypatch.chdir(tmp_path)
        audit = DelegationAudit("multi-report")

        audit.record_modification("file1.py", "Edit", "main")
        audit.record_modification("file2.py", "Write", "main")
        audit.record_modification("file3.py", "MultiEdit", "main")

        report = audit.report()
        assert "3 boundary violation" in report
        assert "file1.py" in report
        assert "file2.py" in report
        assert "file3.py" in report

    def test_truncates_long_reports(self, tmp_path, monkeypatch):
        """Long reports are truncated after 10 violations."""
        monkeypatch.chdir(tmp_path)
        audit = DelegationAudit("long-report")

        # Add 15 violations
        for i in range(15):
            audit.record_modification(f"file{i}.py", "Edit", "main")

        report = audit.report()
        assert "15 boundary violation" in report
        assert "... and 5 more" in report

    def test_report_includes_guidance(self, tmp_path, monkeypatch):
        """Report includes delegation guidance."""
        monkeypatch.chdir(tmp_path)
        audit = DelegationAudit("guidance-report")

        audit.record_modification("file.py", "Edit", "main")

        report = audit.report()
        assert "delegate" in report.lower()
        assert "Task tool" in report


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_empty_file_path(self, tmp_path, monkeypatch):
        """Handles empty file path."""
        monkeypatch.chdir(tmp_path)
        audit = DelegationAudit("empty-path")

        audit.record_modification("", "Edit", "main")

        violations = audit.get_violations()
        assert len(violations) == 1
        assert violations[0]["file"] == ""

    def test_special_characters_in_path(self, tmp_path, monkeypatch):
        """Handles special characters in file paths."""
        monkeypatch.chdir(tmp_path)
        audit = DelegationAudit("special-chars")

        special_path = "path/with spaces/and-dashes/file (1).py"
        audit.record_modification(special_path, "Edit", "main")

        violations = audit.get_violations()
        assert len(violations) == 1
        assert violations[0]["file"] == special_path

    def test_concurrent_sessions(self, tmp_path, monkeypatch):
        """Different sessions maintain separate audit files."""
        monkeypatch.chdir(tmp_path)

        audit1 = DelegationAudit("session-a")
        audit2 = DelegationAudit("session-b")

        audit1.record_modification("file1.py", "Edit", "main")
        audit2.record_modification("file2.py", "Write", "main")

        violations1 = audit1.get_violations()
        violations2 = audit2.get_violations()

        assert len(violations1) == 1
        assert len(violations2) == 1
        assert violations1[0]["file"] == "file1.py"
        assert violations2[0]["file"] == "file2.py"

    def test_malformed_jsonl_line(self, tmp_path, monkeypatch):
        """Handles malformed JSONL lines gracefully."""
        monkeypatch.chdir(tmp_path)
        audit = DelegationAudit("malformed")

        # Create audit file with malformed line
        audit.audit_file.parent.mkdir(parents=True, exist_ok=True)
        with open(audit.audit_file, "w") as f:
            f.write('{"file": "good.py", "tool": "Edit", "source": "main"}\n')
            f.write("this is not json\n")
            f.write('{"file": "also-good.py", "tool": "Write", "source": "main"}\n')

        # Should skip malformed line
        violations = audit.get_violations()
        # Note: Current implementation doesn't handle this - this test documents expected behavior
        # Implementation should add try/except around json.loads in get_violations()
        assert len(violations) >= 2  # At minimum, should get the valid records
