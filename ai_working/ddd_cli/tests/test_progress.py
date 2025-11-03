"""Tests for progress tracking functionality."""

from pathlib import Path

from click.testing import CliRunner

from amplifier_ddd.progress import calculate_progress, mark_complete, parse_checklist, show_progress


def test_parse_checklist_basic() -> None:
    """Test basic checklist parsing."""
    lines = [
        "[ ] file1.md",
        "[x] file2.md",
        "[ ] file3.md",
    ]

    completed, total, parsed_lines = parse_checklist(lines)

    assert completed == 1
    assert total == 3
    assert parsed_lines == lines


def test_parse_checklist_mixed_case() -> None:
    """Test checklist with mixed case completion markers."""
    lines = [
        "[ ] file1.md",
        "[X] file2.md",  # Uppercase X
        "[x] file3.md",
    ]

    completed, total, _ = parse_checklist(lines)

    assert completed == 2
    assert total == 3


def test_calculate_progress(tmp_path: Path) -> None:
    """Test progress calculation."""
    checklist_path = tmp_path / "checklist.txt"
    checklist_path.write_text("[ ] file1.md\n[x] file2.md\n[ ] file3.md\n")

    completed, total, percentage = calculate_progress(checklist_path)

    assert completed == 1
    assert total == 3
    assert percentage == "33.3%"


def test_show_progress_command(tmp_path: Path) -> None:
    """Test show progress CLI command."""
    checklist_path = tmp_path / "checklist.txt"
    checklist_path.write_text("[ ] file1.md\n[x] file2.md\n[x] file3.md\n")

    runner = CliRunner()
    result = runner.invoke(show_progress, ["--checklist", str(checklist_path)])

    assert "Progress: 2/3 files (66.7%)" in result.output
    assert result.exit_code == 1  # Not 100% complete


def test_show_progress_complete(tmp_path: Path) -> None:
    """Test show progress when 100% complete."""
    checklist_path = tmp_path / "checklist.txt"
    checklist_path.write_text("[x] file1.md\n[x] file2.md\n")

    runner = CliRunner()
    result = runner.invoke(show_progress, ["--checklist", str(checklist_path)])

    assert "Progress: 2/2 files (100.0%)" in result.output
    assert result.exit_code == 0  # Complete


def test_mark_complete_command(tmp_path: Path) -> None:
    """Test mark-complete CLI command."""
    checklist_path = tmp_path / "checklist.txt"
    checklist_path.write_text("[ ] file1.md\n[ ] file2.md\n")

    runner = CliRunner()
    result = runner.invoke(mark_complete, ["file1.md", "--checklist", str(checklist_path)])

    assert result.exit_code == 0
    assert "Marked complete: file1.md" in result.output

    # Verify file updated
    updated_content = checklist_path.read_text()
    assert "[x] file1.md" in updated_content
    assert "[ ] file2.md" in updated_content


def test_mark_complete_not_found(tmp_path: Path) -> None:
    """Test mark-complete with non-existent file."""
    checklist_path = tmp_path / "checklist.txt"
    checklist_path.write_text("[ ] file1.md\n")

    runner = CliRunner()
    result = runner.invoke(mark_complete, ["nonexistent.md", "--checklist", str(checklist_path)])

    assert result.exit_code == 1
    assert "File not found in checklist" in result.output
