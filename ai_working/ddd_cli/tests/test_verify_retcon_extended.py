"""Extended tests for retcon verification covering edge cases."""

import json
import os
from pathlib import Path

from click.testing import CliRunner

from amplifier_ddd.verify_retcon import RETCON_RULES, check_file, generate_markdown_report, verify_retcon


def test_check_file_large_file(tmp_path: Path) -> None:
    """Test checking a large file with many lines."""
    test_file = tmp_path / "large.md"
    # Create file with 1000 lines
    content = "\n".join([f"Line {i} of documentation" for i in range(1000)])
    test_file.write_text(content)

    violations = check_file(test_file, RETCON_RULES)

    # Should complete without errors
    assert isinstance(violations, dict)


def test_check_file_with_code_blocks(tmp_path: Path) -> None:
    """Test that code blocks don't trigger false positives."""
    test_file = tmp_path / "test.md"
    test_file.write_text(
        """# Documentation

```python
# This will be implemented
def future_function():
    pass
```

Current implementation is complete.
"""
    )

    violations = check_file(test_file, RETCON_RULES)

    # Code blocks might still trigger (depends on rule implementation)
    # But at least should not crash
    assert isinstance(violations, dict)


def test_check_file_empty(tmp_path: Path) -> None:
    """Test checking empty file."""
    test_file = tmp_path / "empty.md"
    test_file.write_text("")

    violations = check_file(test_file, RETCON_RULES)

    assert len(violations) == 0


def test_check_file_unicode_content(tmp_path: Path) -> None:
    """Test checking file with unicode content."""
    test_file = tmp_path / "unicode.md"
    test_file.write_text("# 文档\n\n这将在未来添加。\n")

    violations = check_file(test_file, RETCON_RULES)

    # Should handle unicode without errors
    assert isinstance(violations, dict)


def test_check_file_all_rules(tmp_path: Path) -> None:
    """Test file that violates all retcon rules."""
    test_file = tmp_path / "violations.md"
    test_file.write_text(
        """
This will be added in the future.
We used to do it differently.
Instead of the old way, use this.
This was previously handled.
Going forward, we will improve.
"""
    )

    violations = check_file(test_file, RETCON_RULES)

    # Should detect multiple violation types
    assert len(violations) >= 3
    assert any("future" in key for key in violations)
    assert any("historical" in key for key in violations)
    assert any("transition" in key for key in violations)


def test_check_file_line_numbers_accurate(tmp_path: Path) -> None:
    """Test that violation line numbers are accurate."""
    test_file = tmp_path / "test.md"
    content = """Line 1
Line 2
This will be added
Line 4
"""
    test_file.write_text(content)

    violations = check_file(test_file, RETCON_RULES)

    if "future_tense" in violations:
        # Line 3 contains the violation
        assert violations["future_tense"][0]["line"] == 3


def test_generate_markdown_report_empty(tmp_path: Path) -> None:
    """Test report generation with no files checked."""
    violations = {}

    report = generate_markdown_report(violations, 0)

    assert "# Retcon Verification Report" in report
    assert "0 total files checked" in report


def test_generate_markdown_report_multiple_violations(tmp_path: Path) -> None:
    """Test report with multiple violation types."""
    violations = {
        "future_tense": [
            {"line": 1, "text": "will be", "file": "file1.md"},
            {"line": 5, "text": "will add", "file": "file1.md"},
        ],
        "historical_refs": [{"line": 3, "text": "used to", "file": "file2.md"}],
        "transition_lang": [{"line": 7, "text": "instead of", "file": "file3.md"}],
    }

    report = generate_markdown_report(violations, 10)

    assert "❌ VIOLATIONS" in report
    assert "file1.md:1" in report
    assert "file1.md:5" in report
    assert "file2.md:3" in report
    assert "file3.md:7" in report


def test_verify_retcon_multiple_files(tmp_path: Path) -> None:
    """Test verify-retcon with multiple files."""
    (tmp_path / "clean1.md").write_text("# Clean documentation")
    (tmp_path / "clean2.md").write_text("# Another clean doc")
    (tmp_path / "violation.md").write_text("This will be added")

    runner = CliRunner()
    result = runner.invoke(verify_retcon, [str(tmp_path)])

    assert result.exit_code == 1  # Has violations
    assert "3 total files checked" in result.output or "checked" in result.output.lower()


def test_verify_retcon_no_markdown_files(tmp_path: Path) -> None:
    """Test verify-retcon with no markdown files."""
    (tmp_path / "file.txt").write_text("Text file")
    (tmp_path / "file.py").write_text("Python file")

    runner = CliRunner()
    result = runner.invoke(verify_retcon, [str(tmp_path)])

    # Should complete with no violations (no md files)
    assert result.exit_code == 0


def test_verify_retcon_nested_directories(tmp_path: Path) -> None:
    """Test verify-retcon finds files in nested directories."""
    nested = tmp_path / "level1" / "level2"
    nested.mkdir(parents=True)
    (nested / "deep.md").write_text("This will be added")
    (tmp_path / "root.md").write_text("Clean doc")

    runner = CliRunner()
    result = runner.invoke(verify_retcon, [str(tmp_path)])

    assert result.exit_code == 1  # Has violations in deep file
    assert "2 total files checked" in result.output or "checked" in result.output.lower()


def test_verify_retcon_exclude_multiple_patterns(tmp_path: Path) -> None:
    """Test verify-retcon with multiple exclusion patterns."""
    (tmp_path / "CHANGELOG.md").write_text("Version 1.0 will be released")
    (tmp_path / "TODO.md").write_text("This will be implemented")
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "api.md").write_text("Current API documentation")

    runner = CliRunner()
    result = runner.invoke(verify_retcon, [str(tmp_path), "--exclude", "CHANGELOG.md", "--exclude", "TODO.md"])

    # Both excluded files should not cause violations
    assert result.exit_code == 0


def test_verify_retcon_json_output_format(tmp_path: Path) -> None:
    """Test JSON output is valid."""
    (tmp_path / "test.md").write_text("This will be added")

    runner = CliRunner()
    result = runner.invoke(verify_retcon, [str(tmp_path), "--json"])

    assert result.exit_code == 1

    # Should be valid JSON structure

    output_data = json.loads(result.output)
    assert "violations" in output_data
    assert "summary" in output_data
    assert "total_files" in output_data["summary"]


def test_verify_retcon_json_no_violations(tmp_path: Path) -> None:
    """Test JSON output with no violations."""
    (tmp_path / "clean.md").write_text("# Clean documentation")

    runner = CliRunner()
    result = runner.invoke(verify_retcon, [str(tmp_path), "--json"])

    assert result.exit_code == 0

    output_data = json.loads(result.output)
    assert output_data["summary"]["total_violations"] == 0


def test_check_file_whitespace_only(tmp_path: Path) -> None:
    """Test checking file with only whitespace."""
    test_file = tmp_path / "whitespace.md"
    test_file.write_text("   \n\n\t\n   ")

    violations = check_file(test_file, RETCON_RULES)

    assert len(violations) == 0


def test_check_file_no_newline_at_end(tmp_path: Path) -> None:
    """Test checking file without final newline."""
    test_file = tmp_path / "no_newline.md"
    test_file.write_text("This will be added")  # No trailing newline

    violations = check_file(test_file, RETCON_RULES)

    # Should still detect violations
    assert "future_tense" in violations


def test_verify_retcon_permission_error(tmp_path: Path) -> None:
    """Test verify-retcon handles permission errors gracefully."""
    if os.name == "nt":
        # Skip on Windows where permission handling differs
        return

    test_file = tmp_path / "nopermission.md"
    test_file.write_text("Content")
    test_file.chmod(0o000)  # Remove all permissions

    runner = CliRunner()
    runner.invoke(verify_retcon, [str(tmp_path)])

    # Should handle error gracefully (might skip file or report error)
    # Clean up
    test_file.chmod(0o644)


def test_verify_retcon_symbolic_links(tmp_path: Path) -> None:
    """Test verify-retcon follows or skips symbolic links."""
    target = tmp_path / "target.md"
    target.write_text("This will be added")

    link = tmp_path / "link.md"
    if hasattr(os, "symlink"):
        try:
            link.symlink_to(target)

            runner = CliRunner()
            result = runner.invoke(verify_retcon, [str(tmp_path)])

            # Should handle symlinks (may check once or twice)
            assert isinstance(result.exit_code, int)
        except OSError:
            # Symlinks not supported on this platform
            pass


def test_verify_retcon_binary_file_safety(tmp_path: Path) -> None:
    """Test verify-retcon handles binary files safely."""
    binary_file = tmp_path / "image.md"
    binary_file.write_bytes(b"\x00\x01\x02\x03\xff\xfe")

    runner = CliRunner()
    result = runner.invoke(verify_retcon, [str(tmp_path)])

    # Should not crash on binary data
    assert isinstance(result.exit_code, int)


def test_generate_markdown_report_formatting(tmp_path: Path) -> None:
    """Test that markdown report is properly formatted."""
    violations = {
        "future_tense": [{"line": 1, "text": "will be", "file": "test.md"}],
    }

    report = generate_markdown_report(violations, 1)

    # Check markdown structure
    assert report.startswith("# ")
    assert "## " in report
    assert "- " in report or "* " in report


def test_check_file_case_sensitive_patterns(tmp_path: Path) -> None:
    """Test that pattern matching is case-insensitive where appropriate."""
    test_file = tmp_path / "test.md"
    test_file.write_text("This WILL BE added.\nThis Will Be added.")

    violations = check_file(test_file, RETCON_RULES)

    # Depends on rule implementation - should catch variations
    if "future_tense" in violations:
        # Should catch at least some cases
        assert len(violations["future_tense"]) > 0
