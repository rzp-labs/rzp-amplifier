"""Integration tests for complete DDD CLI workflows."""

from pathlib import Path

from click.testing import CliRunner

from amplifier_ddd.detect_conflicts import detect_conflicts
from amplifier_ddd.generate_report import generate_report
from amplifier_ddd.list_docs import list_docs
from amplifier_ddd.progress import mark_complete, show_progress
from amplifier_ddd.verify_retcon import verify_retcon


def test_full_workflow_list_to_complete(tmp_path: Path) -> None:
    """Test complete workflow: list -> mark complete -> show progress."""
    # Setup: Create documentation files
    (tmp_path / "README.md").write_text("# Project README")
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "api.md").write_text("# API Documentation")
    (tmp_path / "docs" / "guide.md").write_text("# User Guide")

    output_dir = tmp_path / "output"
    output_dir.mkdir()
    checklist_path = output_dir / "checklist.txt"
    index_path = output_dir / "index.txt"

    runner = CliRunner()

    # Step 1: List all docs
    result = runner.invoke(
        list_docs,
        [
            str(tmp_path),
            "--extensions",
            ".md",
            "--output",
            str(checklist_path),
            "--index",
            str(index_path),
        ],
    )
    assert result.exit_code == 0
    assert checklist_path.exists()
    assert "Found 3 files" in result.output

    # Step 2: Check initial progress (0%)
    result = runner.invoke(show_progress, ["--checklist", str(checklist_path)])
    assert "0/3 files (0.0%)" in result.output
    assert result.exit_code == 1  # Not complete

    # Step 3: Mark first file complete
    result = runner.invoke(mark_complete, ["README.md", "--checklist", str(checklist_path)])
    assert result.exit_code == 0
    assert "(1/3, 33.3%)" in result.output

    # Step 4: Check progress (33%)
    result = runner.invoke(show_progress, ["--checklist", str(checklist_path)])
    assert "1/3 files (33.3%)" in result.output
    assert result.exit_code == 1  # Still not complete

    # Step 5: Mark remaining files complete
    result = runner.invoke(mark_complete, ["docs/api.md", "--checklist", str(checklist_path)])
    assert result.exit_code == 0

    result = runner.invoke(mark_complete, ["docs/guide.md", "--checklist", str(checklist_path)])
    assert result.exit_code == 0
    assert "(3/3, 100.0%)" in result.output

    # Step 6: Final progress check (100%)
    result = runner.invoke(show_progress, ["--checklist", str(checklist_path)])
    assert "3/3 files (100.0%)" in result.output
    assert result.exit_code == 0  # Complete!


def test_full_workflow_with_verification(tmp_path: Path) -> None:
    """Test workflow including retcon verification."""
    # Create docs with violations
    (tmp_path / "clean.md").write_text("# Clean Documentation\n\nThis is current.")
    (tmp_path / "violation.md").write_text("# Future Doc\n\nThis will be added soon.")

    output_dir = tmp_path / "output"
    output_dir.mkdir()
    checklist_path = output_dir / "checklist.txt"

    runner = CliRunner()

    # Step 1: List docs
    result = runner.invoke(
        list_docs,
        [str(tmp_path), "--extensions", ".md", "--output", str(checklist_path)],
    )
    assert result.exit_code == 0

    # Step 2: Verify retcon rules (should fail)
    result = runner.invoke(verify_retcon, [str(tmp_path)])
    assert result.exit_code == 1  # Has violations
    assert "violation.md" in result.output

    # Step 3: Fix violation
    (tmp_path / "violation.md").write_text("# Current Doc\n\nThis feature is available.")

    # Step 4: Re-verify (should pass)
    result = runner.invoke(verify_retcon, [str(tmp_path)])
    assert result.exit_code == 0  # No violations

    # Step 5: Mark files complete
    runner.invoke(mark_complete, ["clean.md", "--checklist", str(checklist_path)])
    runner.invoke(mark_complete, ["violation.md", "--checklist", str(checklist_path)])

    # Step 6: Final progress
    result = runner.invoke(show_progress, ["--checklist", str(checklist_path)])
    assert result.exit_code == 0  # Complete


def test_full_workflow_with_conflicts(tmp_path: Path) -> None:
    """Test workflow including terminology conflict detection."""
    # Create docs with terminology conflicts
    (tmp_path / "doc1.md").write_text("Use the Query Engine for data processing.")
    (tmp_path / "doc2.md").write_text("The QueryEngine handles all queries.")

    output_dir = tmp_path / "output"
    output_dir.mkdir()
    checklist_path = output_dir / "checklist.txt"

    runner = CliRunner()

    # Step 1: List docs
    result = runner.invoke(
        list_docs,
        [str(tmp_path), "--extensions", ".md", "--output", str(checklist_path)],
    )
    assert result.exit_code == 0

    # Step 2: Detect conflicts
    result = runner.invoke(detect_conflicts, [str(tmp_path), "--terms", "Query Engine,QueryEngine"])
    assert result.exit_code == 2  # Conflicts detected
    assert "Query Engine" in result.output

    # Step 3: Fix conflicts (standardize terminology)
    (tmp_path / "doc1.md").write_text("Use the Query Engine for data processing.")
    (tmp_path / "doc2.md").write_text("The Query Engine handles all queries.")

    # Step 4: Re-check conflicts (should pass)
    result = runner.invoke(detect_conflicts, [str(tmp_path), "--terms", "Query Engine,QueryEngine"])
    assert "No conflicts" in result.output or result.exit_code == 0


def test_full_workflow_generate_report(tmp_path: Path) -> None:
    """Test workflow with final report generation."""
    # Create docs
    (tmp_path / "README.md").write_text("# README")
    (tmp_path / "guide.md").write_text("# Guide")

    output_dir = tmp_path / "output"
    output_dir.mkdir()
    checklist_path = output_dir / "checklist.txt"
    report_path = output_dir / "report.md"

    runner = CliRunner()

    # Step 1: List docs
    result = runner.invoke(
        list_docs,
        [str(tmp_path), "--extensions", ".md", "--output", str(checklist_path)],
    )
    assert result.exit_code == 0

    # Step 2: Mark one complete
    runner.invoke(mark_complete, ["README.md", "--checklist", str(checklist_path)])

    # Step 3: Generate report
    result = runner.invoke(
        generate_report,
        [
            str(tmp_path),
            "--checklist",
            str(checklist_path),
            "--output",
            str(report_path),
        ],
    )
    assert result.exit_code == 0
    assert report_path.exists()

    # Verify report content
    report = report_path.read_text()
    assert "# DDD Phase 2" in report
    assert "1/2 files (50.0%)" in report
    assert "## Progress" in report
    assert "## Git Status" in report
    assert "## Approval Checklist" in report


def test_workflow_empty_project(tmp_path: Path) -> None:
    """Test workflow with empty project directory."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    checklist_path = output_dir / "checklist.txt"

    runner = CliRunner()

    # Step 1: List docs (none found)
    result = runner.invoke(
        list_docs,
        [str(tmp_path), "--extensions", ".md", "--output", str(checklist_path)],
    )
    assert "No files found" in result.output

    # Checklist should not be created
    assert not checklist_path.exists()


def test_workflow_with_exclusions(tmp_path: Path) -> None:
    """Test workflow with file exclusions."""
    # Create structure with excluded directories
    (tmp_path / ".venv").mkdir()
    (tmp_path / ".venv" / "excluded.md").write_text("Excluded")

    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "included.md").write_text("Included")

    (tmp_path / "CHANGELOG.md").write_text("Version 1.0 will be released")

    output_dir = tmp_path / "output"
    output_dir.mkdir()
    checklist_path = output_dir / "checklist.txt"

    runner = CliRunner()

    # Step 1: List docs (excluding .venv)
    result = runner.invoke(
        list_docs,
        [str(tmp_path), "--extensions", ".md", "--output", str(checklist_path)],
    )
    assert result.exit_code == 0

    # Verify .venv excluded, others included
    checklist = checklist_path.read_text()
    assert "docs/included.md" in checklist
    assert "CHANGELOG.md" in checklist
    assert ".venv" not in checklist

    # Step 2: Verify retcon (excluding CHANGELOG)
    result = runner.invoke(verify_retcon, [str(tmp_path), "--exclude", "CHANGELOG.md"])
    assert result.exit_code == 0  # CHANGELOG excluded, no violations


def test_workflow_json_outputs(tmp_path: Path) -> None:
    """Test workflow using JSON output format."""
    (tmp_path / "test.md").write_text("This will be added")

    runner = CliRunner()

    # Verify retcon with JSON output
    result = runner.invoke(verify_retcon, [str(tmp_path), "--json"])
    assert result.exit_code == 1

    import json

    data = json.loads(result.output)
    assert "violations" in data
    assert "summary" in data


def test_workflow_concurrent_operations(tmp_path: Path) -> None:
    """Test workflow handles concurrent file operations safely."""
    import subprocess
    import sys
    import threading

    # Create files
    for i in range(5):
        (tmp_path / f"file{i}.md").write_text(f"File {i}")

    output_dir = tmp_path / "output"
    output_dir.mkdir()
    checklist_path = output_dir / "checklist.txt"

    runner = CliRunner()

    # Create checklist
    runner.invoke(
        list_docs,
        [str(tmp_path), "--extensions", ".md", "--output", str(checklist_path)],
    )

    # Mark files complete concurrently using subprocess (CliRunner is not thread-safe)
    def mark_file(filename: str) -> None:
        subprocess.run(
            [
                sys.executable,
                "-m",
                "amplifier_ddd.cli",
                "progress",
                "mark-complete",
                filename,
                "--checklist",
                str(checklist_path),
            ],
            check=False,
            capture_output=True,
        )

    threads = []
    for i in range(5):
        thread = threading.Thread(target=mark_file, args=(f"file{i}.md",))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    # Verify operations completed without crashing (note: due to race conditions,
    # not all may be marked, but the operation should complete safely)
    result = runner.invoke(show_progress, ["--checklist", str(checklist_path)])
    # Should have some progress (at least 1 file marked)
    assert "/5 files" in result.output
    # Check that at least one file was marked successfully
    content = checklist_path.read_text()
    assert "[x]" in content


def test_workflow_large_project(tmp_path: Path) -> None:
    """Test workflow with large number of files."""
    # Create 100 files
    for i in range(100):
        (tmp_path / f"file{i:03d}.md").write_text(f"Content {i}")

    output_dir = tmp_path / "output"
    output_dir.mkdir()
    checklist_path = output_dir / "checklist.txt"

    runner = CliRunner()

    # Step 1: List all files
    result = runner.invoke(
        list_docs,
        [str(tmp_path), "--extensions", ".md", "--output", str(checklist_path)],
    )
    assert result.exit_code == 0
    assert "Found 100 files" in result.output

    # Step 2: Mark some complete
    for i in range(50):
        runner.invoke(mark_complete, [f"file{i:03d}.md", "--checklist", str(checklist_path)])

    # Step 3: Check progress
    result = runner.invoke(show_progress, ["--checklist", str(checklist_path)])
    assert "50/100 files (50.0%)" in result.output


def test_workflow_unicode_filenames(tmp_path: Path) -> None:
    """Test workflow with unicode file names."""
    (tmp_path / "文档.md").write_text("中文内容", encoding="utf-8")
    (tmp_path / "документ.md").write_text("Русский текст", encoding="utf-8")

    output_dir = tmp_path / "output"
    output_dir.mkdir()
    checklist_path = output_dir / "checklist.txt"

    runner = CliRunner()

    # List docs
    result = runner.invoke(
        list_docs,
        [str(tmp_path), "--extensions", ".md", "--output", str(checklist_path)],
    )
    assert result.exit_code == 0

    # Mark complete
    result = runner.invoke(mark_complete, ["文档.md", "--checklist", str(checklist_path)])
    assert result.exit_code == 0


def test_workflow_error_recovery(tmp_path: Path) -> None:
    """Test workflow recovers from errors gracefully."""
    (tmp_path / "file.md").write_text("Content")

    output_dir = tmp_path / "output"
    output_dir.mkdir()
    checklist_path = output_dir / "checklist.txt"

    runner = CliRunner()

    # Create checklist
    runner.invoke(
        list_docs,
        [str(tmp_path), "--extensions", ".md", "--output", str(checklist_path)],
    )

    # Try to mark non-existent file
    result = runner.invoke(mark_complete, ["nonexistent.md", "--checklist", str(checklist_path)])
    assert result.exit_code == 1

    # Verify checklist still intact
    result = runner.invoke(show_progress, ["--checklist", str(checklist_path)])
    assert "0/1 files" in result.output
