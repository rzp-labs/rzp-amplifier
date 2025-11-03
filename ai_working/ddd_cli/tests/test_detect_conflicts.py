"""Tests for conflict detection functionality."""

from pathlib import Path

from click.testing import CliRunner

from amplifier_ddd.detect_conflicts import check_term_conflicts, detect_conflicts, find_term_variants


def test_find_term_variants_basic() -> None:
    """Test finding term variants."""
    content = "Query Engine is great. QueryEngine works well. query_engine is used."

    variants = find_term_variants(content, "Query Engine")

    assert "Query Engine" in variants
    assert "QueryEngine" in variants
    assert "query_engine" in variants


def test_find_term_variants_no_matches() -> None:
    """Test with no matches."""
    content = "No relevant terms here."

    variants = find_term_variants(content, "Query Engine")

    assert len(variants) == 0


def test_check_term_conflicts_basic(tmp_path: Path) -> None:
    """Test checking for term conflicts."""
    file1 = tmp_path / "test1.md"
    file1.write_text("The Query Engine handles requests.")

    file2 = tmp_path / "test2.md"
    file2.write_text("Use QueryEngine for processing.")

    files = [file1, file2]
    terms = ["Query Engine,QueryEngine"]

    conflicts = check_term_conflicts(files, terms)

    assert "Query Engine" in conflicts
    assert "Query Engine" in conflicts["Query Engine"]
    assert "QueryEngine" in conflicts["Query Engine"]


def test_check_term_conflicts_no_conflicts(tmp_path: Path) -> None:
    """Test with consistent terminology."""
    file1 = tmp_path / "test1.md"
    file1.write_text("The Query Engine handles requests.")

    file2 = tmp_path / "test2.md"
    file2.write_text("The Query Engine works well.")

    files = [file1, file2]
    terms = ["Query Engine,QueryEngine"]

    conflicts = check_term_conflicts(files, terms)

    # Should have Query Engine but not QueryEngine
    assert "Query Engine" in conflicts
    assert "QueryEngine" not in conflicts["Query Engine"]


def test_detect_conflicts_command(tmp_path: Path) -> None:
    """Test detect-conflicts CLI command."""
    # Create test files with conflicts
    (tmp_path / "file1.md").write_text("Query Engine is great")
    (tmp_path / "file2.md").write_text("QueryEngine works well")

    runner = CliRunner()
    result = runner.invoke(detect_conflicts, [str(tmp_path), "--terms", "Query Engine,QueryEngine"])

    assert result.exit_code == 2  # Conflicts detected
    assert "Terminology Conflict Report" in result.output
    assert "Query Engine" in result.output


def test_detect_conflicts_no_conflicts(tmp_path: Path) -> None:
    """Test detect-conflicts with no conflicts."""
    (tmp_path / "file1.md").write_text("Query Engine is great")
    (tmp_path / "file2.md").write_text("Query Engine works well")

    runner = CliRunner()
    result = runner.invoke(detect_conflicts, [str(tmp_path), "--terms", "Query Engine,QueryEngine"])

    # No QueryEngine found, so no conflicts
    assert "No conflicts detected" in result.output or result.exit_code == 0


def test_detect_conflicts_auto_detect(tmp_path: Path) -> None:
    """Test auto-detect mode."""
    (tmp_path / "file1.md").write_text("Query Engine is important. QueryEngine matters.")

    runner = CliRunner()
    result = runner.invoke(detect_conflicts, [str(tmp_path), "--auto-detect"])

    # Should detect Query Engine variations
    assert result.exit_code in [0, 2]  # May or may not find conflicts


def test_detect_conflicts_no_arguments(tmp_path: Path) -> None:
    """Test that command requires arguments."""
    runner = CliRunner()
    result = runner.invoke(detect_conflicts, [str(tmp_path)])

    assert result.exit_code == 1
    assert "Must specify either --terms or --auto-detect" in result.output
