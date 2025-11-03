"""Tests for retcon verification functionality."""

from pathlib import Path

from click.testing import CliRunner

from amplifier_ddd.verify_retcon import RETCON_RULES, check_file, generate_markdown_report, verify_retcon


def test_check_file_no_violations(tmp_path: Path) -> None:
    """Test checking file with no violations."""
    test_file = tmp_path / "test.md"
    test_file.write_text("# Documentation\n\nThis is current documentation.")

    violations = check_file(test_file, RETCON_RULES)

    assert len(violations) == 0


def test_check_file_future_tense(tmp_path: Path) -> None:
    """Test detecting future tense violations."""
    test_file = tmp_path / "test.md"
    test_file.write_text("This feature will be added soon.")

    violations = check_file(test_file, RETCON_RULES)

    assert "future_tense" in violations
    assert len(violations["future_tense"]) == 1
    assert violations["future_tense"][0]["line"] == 1


def test_check_file_historical_refs(tmp_path: Path) -> None:
    """Test detecting historical reference violations."""
    test_file = tmp_path / "test.md"
    test_file.write_text("We previously used the old API.")

    violations = check_file(test_file, RETCON_RULES)

    assert "historical_refs" in violations
    assert len(violations["historical_refs"]) == 1


def test_check_file_multiple_violations(tmp_path: Path) -> None:
    """Test detecting multiple violations."""
    test_file = tmp_path / "test.md"
    test_file.write_text("This will be added.\nWe used to do it differently.\nInstead of the old way, use this.\n")

    violations = check_file(test_file, RETCON_RULES)

    assert len(violations) >= 3
    assert "future_tense" in violations
    assert "historical_refs" in violations
    assert "transition_lang" in violations


def test_generate_markdown_report_no_violations() -> None:
    """Test report generation with no violations."""
    violations = {}

    report = generate_markdown_report(violations, 5)

    assert "# Retcon Verification Report" in report
    assert "5 total files checked" in report


def test_generate_markdown_report_with_violations() -> None:
    """Test report generation with violations."""
    violations = {
        "future_tense": [{"line": 1, "text": "This will be added", "file": "test.md"}],
        "historical_refs": [],
    }

    report = generate_markdown_report(violations, 5)

    assert "# Retcon Verification Report" in report
    assert "❌ VIOLATIONS" in report
    assert "test.md:1" in report


def test_verify_retcon_command(tmp_path: Path) -> None:
    """Test verify-retcon CLI command."""
    # Create test files
    (tmp_path / "clean.md").write_text("# Clean documentation")
    (tmp_path / "violation.md").write_text("This will be added soon")

    runner = CliRunner()
    result = runner.invoke(verify_retcon, [str(tmp_path)])

    assert result.exit_code == 1  # Has violations
    assert "Retcon Verification Report" in result.output


def test_verify_retcon_with_exclusions(tmp_path: Path) -> None:
    """Test verify-retcon with file exclusions."""
    # Create test files
    (tmp_path / "CHANGELOG.md").write_text("Version 1.0 will be released")
    (tmp_path / "README.md").write_text("Current documentation")

    runner = CliRunner()
    result = runner.invoke(verify_retcon, [str(tmp_path), "--exclude", "CHANGELOG.md"])

    # CHANGELOG should be excluded, so no violations
    assert result.exit_code == 0


def test_verify_retcon_json_output(tmp_path: Path) -> None:
    """Test verify-retcon with JSON output."""
    (tmp_path / "test.md").write_text("This will be added")

    runner = CliRunner()
    result = runner.invoke(verify_retcon, [str(tmp_path), "--json"])

    assert result.exit_code == 1
    assert '"violations"' in result.output
    assert '"summary"' in result.output
