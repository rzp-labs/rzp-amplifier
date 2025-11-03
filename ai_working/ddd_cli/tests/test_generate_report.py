"""Tests for report generation functionality."""

from pathlib import Path

from click.testing import CliRunner

from amplifier_ddd.generate_report import generate_report, generate_report_content


def test_generate_report_content_basic(tmp_path: Path) -> None:
    """Test basic report generation."""
    # Create checklist
    checklist = tmp_path / "checklist.txt"
    checklist.write_text("[ ] file1.md\n[x] file2.md\n")

    # Generate report
    report = generate_report_content(tmp_path, checklist, include_diff=False)

    assert "# DDD Phase 2 - Documentation Status Report" in report
    assert "Progress" in report
    assert "Git Status" in report
    assert "Approval Checklist" in report


def test_generate_report_content_missing_checklist(tmp_path: Path) -> None:
    """Test report generation with missing checklist."""
    checklist = tmp_path / "nonexistent.txt"

    report = generate_report_content(tmp_path, checklist, include_diff=False)

    assert "Checklist not found" in report


def test_generate_report_command(tmp_path: Path) -> None:
    """Test generate-report CLI command."""
    # Create checklist
    checklist = tmp_path / "checklist.txt"
    checklist.write_text("[ ] file1.md\n[x] file2.md\n")

    # Create output directory
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    output_path = output_dir / "report.md"

    runner = CliRunner()
    result = runner.invoke(
        generate_report,
        [
            str(tmp_path),
            "--checklist",
            str(checklist),
            "--output",
            str(output_path),
        ],
    )

    assert result.exit_code == 0
    assert "Report generated" in result.output
    assert output_path.exists()

    # Verify report content
    report_content = output_path.read_text()
    assert "# DDD Phase 2" in report_content


def test_generate_report_with_diff(tmp_path: Path) -> None:
    """Test report generation with diff included."""
    checklist = tmp_path / "checklist.txt"
    checklist.write_text("[ ] file1.md\n")

    output_path = tmp_path / "report.md"

    runner = CliRunner()
    result = runner.invoke(
        generate_report,
        [
            str(tmp_path),
            "--checklist",
            str(checklist),
            "--output",
            str(output_path),
            "--include-diff",
        ],
    )

    assert result.exit_code == 0
    assert output_path.exists()
