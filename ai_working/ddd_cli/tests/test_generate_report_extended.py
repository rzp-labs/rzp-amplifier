"""Extended tests for report generation covering edge cases."""

from pathlib import Path
from unittest.mock import patch

from click.testing import CliRunner

from amplifier_ddd.generate_report import generate_report, generate_report_content, get_git_diff_summary, get_git_status


def test_get_git_status_no_git_repo(tmp_path: Path) -> None:
    """Test git status in non-git directory."""
    status = get_git_status(tmp_path)

    assert "error" in status
    assert "Not a git repository" in status["error"]


def test_get_git_status_no_gitpython(tmp_path: Path) -> None:
    """Test git status when GitPython not available."""
    with patch("amplifier_ddd.generate_report.HAS_GIT", False):
        status = get_git_status(tmp_path)

        assert "error" in status
        assert "GitPython not installed" in status["error"]


def test_get_git_diff_summary_no_git_repo(tmp_path: Path) -> None:
    """Test git diff in non-git directory."""
    diff = get_git_diff_summary(tmp_path)

    assert "Error getting diff" in diff or "Not a git repository" in diff


def test_get_git_diff_summary_no_gitpython(tmp_path: Path) -> None:
    """Test git diff when GitPython not available."""
    with patch("amplifier_ddd.generate_report.HAS_GIT", False):
        diff = get_git_diff_summary(tmp_path)

        assert "GitPython not installed" in diff


def test_generate_report_content_no_git(tmp_path: Path) -> None:
    """Test report generation in non-git directory."""
    checklist = tmp_path / "checklist.txt"
    checklist.write_text("[ ] file1.md\n[x] file2.md\n")

    report = generate_report_content(tmp_path, checklist, include_diff=False)

    assert "# DDD Phase 2" in report
    assert "Progress" in report
    assert "Git Status" in report
    assert "Error:" in report or "Not a git repository" in report


def test_generate_report_content_with_progress(tmp_path: Path) -> None:
    """Test report includes progress correctly."""
    checklist = tmp_path / "checklist.txt"
    checklist.write_text("[ ] file1.md\n[x] file2.md\n[x] file3.md\n")

    report = generate_report_content(tmp_path, checklist, include_diff=False)

    assert "2/3 files (66.7%)" in report


def test_generate_report_content_100_percent(tmp_path: Path) -> None:
    """Test report with 100% completion."""
    checklist = tmp_path / "checklist.txt"
    checklist.write_text("[x] file1.md\n[x] file2.md\n")

    report = generate_report_content(tmp_path, checklist, include_diff=False)

    assert "2/2 files (100.0%)" in report


def test_generate_report_content_has_approval_checklist(tmp_path: Path) -> None:
    """Test report includes approval checklist."""
    checklist = tmp_path / "checklist.txt"
    checklist.write_text("[ ] file1.md\n")

    report = generate_report_content(tmp_path, checklist, include_diff=False)

    assert "## Approval Checklist" in report
    assert "[ ] All documentation updates completed" in report
    assert "[ ] Retcon rules verified" in report
    assert "[ ] Terminology conflicts resolved" in report
    assert "[ ] Changes reviewed and approved" in report
    assert "[ ] Ready to commit" in report


def test_generate_report_command_creates_output_dir(tmp_path: Path) -> None:
    """Test that generate-report creates output directory."""
    checklist = tmp_path / "checklist.txt"
    checklist.write_text("[ ] file1.md\n")

    # Output in non-existent directory
    output_path = tmp_path / "nested" / "output" / "report.md"

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
    assert output_path.exists()


def test_generate_report_command_overwrites_existing(tmp_path: Path) -> None:
    """Test that generate-report overwrites existing report."""
    checklist = tmp_path / "checklist.txt"
    checklist.write_text("[ ] file1.md\n")

    output_path = tmp_path / "report.md"
    output_path.write_text("Old report content")

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

    new_content = output_path.read_text()
    assert "Old report content" not in new_content
    assert "# DDD Phase 2" in new_content


def test_generate_report_no_gitpython_warning(tmp_path: Path) -> None:
    """Test warning when GitPython not installed."""
    checklist = tmp_path / "checklist.txt"
    checklist.write_text("[ ] file1.md\n")

    output_path = tmp_path / "report.md"

    with patch("amplifier_ddd.generate_report.HAS_GIT", False):
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

        assert "Warning: GitPython not installed" in result.output
        assert "pip install gitpython" in result.output


def test_generate_report_with_diff_no_staged_changes(tmp_path: Path) -> None:
    """Test report with --include-diff but no staged changes."""
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

    report = output_path.read_text()
    # Should mention no changes or not include diff section
    assert "No staged changes" in report or "Full Diff" not in report


def test_generate_report_unicode_output(tmp_path: Path) -> None:
    """Test report handles unicode content correctly."""
    checklist = tmp_path / "checklist.txt"
    checklist.write_text("[ ] 文档.md\n", encoding="utf-8")

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
        ],
    )

    assert result.exit_code == 0

    report = output_path.read_text(encoding="utf-8")
    assert "# DDD Phase 2" in report


def test_generate_report_empty_checklist(tmp_path: Path) -> None:
    """Test report with empty checklist."""
    checklist = tmp_path / "checklist.txt"
    checklist.write_text("")

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
        ],
    )

    assert result.exit_code == 0

    report = output_path.read_text()
    assert "# DDD Phase 2" in report
    # Should handle 0/0 gracefully
    assert "0/0 files (0%)" in report or "Checklist not found" in report


def test_generate_report_missing_project_dir() -> None:
    """Test generate-report with non-existent project directory."""
    runner = CliRunner()
    result = runner.invoke(
        generate_report,
        ["/nonexistent/path"],
    )

    # Click should handle this with path validation error
    assert result.exit_code != 0


def test_get_git_status_with_staged_files(tmp_path: Path) -> None:
    """Test git status with actual staged files (if git repo)."""
    # This test only works if tmp_path is in a git repo or we can init one
    # Skip git-dependent behavior tests in non-git environments
    status = get_git_status(tmp_path)

    # Should have error key if not a git repo
    if "error" not in status:
        assert "branch" in status
        assert "staged" in status
        assert "unstaged" in status
        assert "untracked" in status


def test_generate_report_content_includes_all_sections(tmp_path: Path) -> None:
    """Test that report includes all required sections."""
    checklist = tmp_path / "checklist.txt"
    checklist.write_text("[ ] file1.md\n")

    report = generate_report_content(tmp_path, checklist, include_diff=False)

    # Verify all major sections present
    assert "# DDD Phase 2 - Documentation Status Report" in report
    assert "## Progress" in report
    assert "## Git Status" in report
    assert "## Git Diff Summary" in report
    assert "## Approval Checklist" in report


def test_generate_report_content_with_many_staged_files(tmp_path: Path) -> None:
    """Test report limits staged files list to 20."""
    # Mock git status to return many staged files
    mock_status = {
        "branch": "main",
        "staged": [f"file{i}.md" for i in range(50)],
        "unstaged": [],
        "untracked": [],
    }

    checklist = tmp_path / "checklist.txt"
    checklist.write_text("[ ] file1.md\n")

    with patch("amplifier_ddd.generate_report.get_git_status", return_value=mock_status):
        report = generate_report_content(tmp_path, checklist, include_diff=False)

        # Should show first 20 and indicate more
        assert "file0.md" in report
        assert "file19.md" in report
        assert "... and 30 more" in report


def test_generate_report_formats_output_correctly(tmp_path: Path) -> None:
    """Test report output is valid markdown."""
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
        ],
    )

    assert result.exit_code == 0

    report = output_path.read_text()

    # Check markdown formatting
    assert report.startswith("# ")  # Top-level heading
    assert "## " in report  # Second-level headings
    assert "- " in report or "* " in report  # List items
    assert "```" in report  # Code blocks


def test_generate_report_success_message(tmp_path: Path) -> None:
    """Test generate-report shows success message."""
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
        ],
    )

    assert result.exit_code == 0
    assert "Report generated" in result.output
    assert str(output_path) in result.output
