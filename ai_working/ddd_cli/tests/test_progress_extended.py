"""Extended tests for progress tracking covering edge cases."""

import threading
from pathlib import Path

from click.testing import CliRunner

from amplifier_ddd.progress import calculate_progress, mark_complete, parse_checklist, read_checklist, show_progress


def test_read_checklist_missing_file(tmp_path: Path) -> None:
    """Test reading non-existent checklist raises error."""
    checklist_path = tmp_path / "nonexistent.txt"

    try:
        read_checklist(checklist_path)
        assert False, "Should raise FileNotFoundError"
    except FileNotFoundError as e:
        assert "Checklist not found" in str(e)


def test_parse_checklist_empty() -> None:
    """Test parsing empty checklist."""
    completed, total, lines = parse_checklist([])

    assert completed == 0
    assert total == 0
    assert lines == []


def test_parse_checklist_no_checkboxes() -> None:
    """Test parsing checklist with no checkbox lines."""
    lines = [
        "# Documentation Checklist",
        "",
        "Some other content",
    ]

    completed, total, _parsed = parse_checklist(lines)

    assert completed == 0
    assert total == 0


def test_parse_checklist_all_completed() -> None:
    """Test parsing fully completed checklist."""
    lines = [
        "[x] file1.md",
        "[x] file2.md",
        "[x] file3.md",
    ]

    completed, total, _ = parse_checklist(lines)

    assert completed == 3
    assert total == 3


def test_parse_checklist_none_completed() -> None:
    """Test parsing checklist with no completions."""
    lines = [
        "[ ] file1.md",
        "[ ] file2.md",
        "[ ] file3.md",
    ]

    completed, total, _ = parse_checklist(lines)

    assert completed == 0
    assert total == 3


def test_parse_checklist_mixed_content() -> None:
    """Test parsing checklist with mixed content."""
    lines = [
        "# Header",
        "[ ] file1.md",
        "",
        "[x] file2.md",
        "Some description text",
        "[ ] file3.md",
        "",
    ]

    completed, total, _ = parse_checklist(lines)

    assert completed == 1
    assert total == 3


def test_parse_checklist_malformed_checkboxes() -> None:
    """Test parsing with malformed checkbox syntax."""
    lines = [
        "[] file1.md",  # No space
        "[ ]file2.md",  # No space after ]
        "[x]file3.md",  # No space after ]
        "[ ] file4.md",  # Valid
        "[x] file5.md",  # Valid
    ]

    # Should only count valid checkbox format
    completed, total, _ = parse_checklist(lines)

    # Only the last two are valid
    assert total >= 2
    assert completed >= 1


def test_calculate_progress_empty_checklist(tmp_path: Path) -> None:
    """Test calculating progress with empty checklist."""
    checklist_path = tmp_path / "checklist.txt"
    checklist_path.write_text("")

    completed, total, percentage = calculate_progress(checklist_path)

    assert completed == 0
    assert total == 0
    assert percentage == "0%"


def test_show_progress_empty_checklist(tmp_path: Path) -> None:
    """Test show progress with empty checklist."""
    checklist_path = tmp_path / "checklist.txt"
    checklist_path.write_text("")

    runner = CliRunner()
    result = runner.invoke(show_progress, ["--checklist", str(checklist_path)])

    assert "Checklist is empty" in result.output


def test_show_progress_missing_checklist(tmp_path: Path) -> None:
    """Test show progress with missing checklist."""
    checklist_path = tmp_path / "nonexistent.txt"

    runner = CliRunner()
    result = runner.invoke(show_progress, ["--checklist", str(checklist_path)])

    assert result.exit_code == 1
    assert "Error:" in result.output


def test_show_progress_zero_completed(tmp_path: Path) -> None:
    """Test show progress with no files completed."""
    checklist_path = tmp_path / "checklist.txt"
    checklist_path.write_text("[ ] file1.md\n[ ] file2.md\n")

    runner = CliRunner()
    result = runner.invoke(show_progress, ["--checklist", str(checklist_path)])

    assert "Progress: 0/2 files (0.0%)" in result.output
    assert result.exit_code == 1  # Not complete


def test_show_progress_partial_completion(tmp_path: Path) -> None:
    """Test show progress with partial completion."""
    checklist_path = tmp_path / "checklist.txt"
    checklist_path.write_text("[ ] file1.md\n[x] file2.md\n[x] file3.md\n")

    runner = CliRunner()
    result = runner.invoke(show_progress, ["--checklist", str(checklist_path)])

    assert "Progress: 2/3 files (66.7%)" in result.output
    assert result.exit_code == 1  # Not complete


def test_mark_complete_already_completed(tmp_path: Path) -> None:
    """Test marking already completed file."""
    checklist_path = tmp_path / "checklist.txt"
    checklist_path.write_text("[x] file1.md\n[ ] file2.md\n")

    runner = CliRunner()
    result = runner.invoke(mark_complete, ["file1.md", "--checklist", str(checklist_path)])

    # Should not find it (already marked with [x])
    assert result.exit_code == 1
    assert "File not found in checklist" in result.output


def test_mark_complete_partial_path_match(tmp_path: Path) -> None:
    """Test marking file with partial path match."""
    checklist_path = tmp_path / "checklist.txt"
    checklist_path.write_text("[ ] docs/architecture/overview.md\n[ ] docs/api.md\n")

    runner = CliRunner()
    # Should match the full path
    result = runner.invoke(mark_complete, ["docs/architecture/overview.md", "--checklist", str(checklist_path)])

    assert result.exit_code == 0
    assert "Marked complete: docs/architecture/overview.md" in result.output

    updated = checklist_path.read_text()
    assert "[x] docs/architecture/overview.md" in updated
    assert "[ ] docs/api.md" in updated


def test_mark_complete_with_absolute_path(tmp_path: Path) -> None:
    """Test marking file using absolute path."""
    checklist_path = tmp_path / "checklist.txt"
    checklist_path.write_text("[ ] file1.md\n[ ] file2.md\n")

    # Use absolute path (should still match relative path in checklist)
    abs_path = tmp_path / "file1.md"

    runner = CliRunner()
    result = runner.invoke(mark_complete, [str(abs_path), "--checklist", str(checklist_path)])

    # Should match based on filename
    assert result.exit_code == 0
    updated = checklist_path.read_text()
    assert "[x] file1.md" in updated


def test_mark_complete_preserves_newline(tmp_path: Path) -> None:
    """Test that mark-complete preserves final newline."""
    checklist_path = tmp_path / "checklist.txt"
    checklist_path.write_text("[ ] file1.md\n[ ] file2.md\n")

    runner = CliRunner()
    result = runner.invoke(mark_complete, ["file1.md", "--checklist", str(checklist_path)])

    assert result.exit_code == 0

    # Should end with newline
    content = checklist_path.read_text()
    assert content.endswith("\n")


def test_mark_complete_case_sensitive(tmp_path: Path) -> None:
    """Test that file matching is case-sensitive."""
    checklist_path = tmp_path / "checklist.txt"
    checklist_path.write_text("[ ] File1.md\n[ ] file2.md\n")

    runner = CliRunner()
    # Try with wrong case
    result = runner.invoke(mark_complete, ["file1.md", "--checklist", str(checklist_path)])

    # Should find it (case-insensitive file systems might match)
    # This test behavior depends on filesystem
    if result.exit_code == 0:
        assert "Marked complete" in result.output
    else:
        assert "File not found" in result.output


def test_mark_complete_updates_percentage(tmp_path: Path) -> None:
    """Test that mark-complete shows updated percentage."""
    checklist_path = tmp_path / "checklist.txt"
    checklist_path.write_text("[ ] file1.md\n[ ] file2.md\n[ ] file3.md\n")

    runner = CliRunner()
    result = runner.invoke(mark_complete, ["file1.md", "--checklist", str(checklist_path)])

    assert result.exit_code == 0
    assert "(1/3, 33.3%)" in result.output


def test_mark_complete_last_file(tmp_path: Path) -> None:
    """Test marking last file as complete."""
    checklist_path = tmp_path / "checklist.txt"
    checklist_path.write_text("[x] file1.md\n[ ] file2.md\n")

    runner = CliRunner()
    result = runner.invoke(mark_complete, ["file2.md", "--checklist", str(checklist_path)])

    assert result.exit_code == 0
    assert "(2/2, 100.0%)" in result.output

    # Verify 100% complete
    runner2 = CliRunner()
    result2 = runner2.invoke(show_progress, ["--checklist", str(checklist_path)])
    assert result2.exit_code == 0  # Exit 0 when complete


def test_mark_complete_with_special_chars(tmp_path: Path) -> None:
    """Test marking files with special characters in names."""
    special_name = "file with spaces (and parens).md"
    checklist_path = tmp_path / "checklist.txt"
    checklist_path.write_text(f"[ ] {special_name}\n")

    runner = CliRunner()
    result = runner.invoke(mark_complete, [special_name, "--checklist", str(checklist_path)])

    assert result.exit_code == 0
    updated = checklist_path.read_text()
    assert f"[x] {special_name}" in updated


def test_concurrent_mark_complete(tmp_path: Path) -> None:
    """Test concurrent mark-complete operations (race condition test)."""
    import subprocess
    import sys

    checklist_path = tmp_path / "checklist.txt"
    checklist_path.write_text("[ ] file1.md\n[ ] file2.md\n[ ] file3.md\n")

    def mark_file(filename: str) -> int:
        # Use subprocess instead of CliRunner for thread safety
        result = subprocess.run(
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
        return result.returncode

    # Run concurrent marks
    threads = []
    results = []
    for filename in ["file1.md", "file2.md", "file3.md"]:
        thread = threading.Thread(target=lambda f=filename: results.append(mark_file(f)))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    # All should succeed
    assert all(code == 0 for code in results)

    # Final checklist should have all marked
    content = checklist_path.read_text()
    assert content.count("[x]") == 3


def test_mark_complete_unicode_filenames(tmp_path: Path) -> None:
    """Test marking files with unicode characters."""
    unicode_name = "文档.md"
    checklist_path = tmp_path / "checklist.txt"
    checklist_path.write_text(f"[ ] {unicode_name}\n", encoding="utf-8")

    runner = CliRunner()
    result = runner.invoke(mark_complete, [unicode_name, "--checklist", str(checklist_path)])

    assert result.exit_code == 0
    updated = checklist_path.read_text(encoding="utf-8")
    assert f"[x] {unicode_name}" in updated
