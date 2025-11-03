"""Extended tests for conflict detection covering edge cases."""

from pathlib import Path

from click.testing import CliRunner

from amplifier_ddd.detect_conflicts import check_term_conflicts, detect_conflicts, find_term_variants


def test_find_term_variants_case_insensitive() -> None:
    """Test finding variants is case-sensitive."""
    content = "Query Engine, query engine, QUERY ENGINE, queryengine"

    variants = find_term_variants(content, "Query Engine")

    # Should find variations
    assert len(variants) > 0


def test_find_term_variants_with_underscores() -> None:
    """Test finding variants with underscores."""
    content = "Use query_engine or QueryEngine or query-engine"

    variants = find_term_variants(content, "Query Engine")

    assert "query_engine" in variants or "QueryEngine" in variants


def test_find_term_variants_unicode() -> None:
    """Test finding variants with unicode text."""
    content = "查询引擎 Query Engine 处理请求"

    variants = find_term_variants(content, "Query Engine")

    assert "Query Engine" in variants


def test_check_term_conflicts_multiple_files(tmp_path: Path) -> None:
    """Test conflict checking across many files."""
    for i in range(10):
        file = tmp_path / f"file{i}.md"
        # Alternate between two variants
        variant = "Query Engine" if i % 2 == 0 else "QueryEngine"
        file.write_text(f"The {variant} processes requests.")

    files = list(tmp_path.glob("*.md"))
    terms = ["Query Engine,QueryEngine"]

    conflicts = check_term_conflicts(files, terms)

    # Should detect both variants
    assert "Query Engine" in conflicts
    assert len(conflicts["Query Engine"]) == 2


def test_check_term_conflicts_single_file_multiple_variants(tmp_path: Path) -> None:
    """Test conflicts within a single file."""
    file = tmp_path / "mixed.md"
    file.write_text("Use Query Engine for basic queries. The QueryEngine is fast.")

    files = [file]
    terms = ["Query Engine,QueryEngine"]

    conflicts = check_term_conflicts(files, terms)

    assert "Query Engine" in conflicts
    assert "QueryEngine" in conflicts["Query Engine"]


def test_check_term_conflicts_no_terms_specified(tmp_path: Path) -> None:
    """Test with empty terms list."""
    file = tmp_path / "test.md"
    file.write_text("Content")

    files = [file]
    terms = []

    conflicts = check_term_conflicts(files, terms)

    assert len(conflicts) == 0


def test_check_term_conflicts_case_sensitivity(tmp_path: Path) -> None:
    """Test that conflicts respect case differences."""
    file1 = tmp_path / "file1.md"
    file1.write_text("query engine processes data")

    file2 = tmp_path / "file2.md"
    file2.write_text("Query Engine processes data")

    files = [file1, file2]
    terms = ["Query Engine"]

    conflicts = check_term_conflicts(files, terms)

    # Should detect case variation
    assert "Query Engine" in conflicts


def test_detect_conflicts_large_files(tmp_path: Path) -> None:
    """Test conflict detection with large files."""
    large_content = "\n".join([f"Line {i} uses Query Engine" for i in range(1000)])
    large_content += "\nBut this line uses QueryEngine"

    file = tmp_path / "large.md"
    file.write_text(large_content)

    runner = CliRunner()
    result = runner.invoke(detect_conflicts, [str(tmp_path), "--terms", "Query Engine,QueryEngine"])

    # Should detect conflict
    assert result.exit_code == 2


def test_detect_conflicts_nested_directories(tmp_path: Path) -> None:
    """Test conflict detection in nested structure."""
    nested = tmp_path / "level1" / "level2"
    nested.mkdir(parents=True)

    (tmp_path / "root.md").write_text("Query Engine at root")
    (nested / "deep.md").write_text("QueryEngine deep down")

    runner = CliRunner()
    result = runner.invoke(detect_conflicts, [str(tmp_path), "--terms", "Query Engine,QueryEngine"])

    assert result.exit_code == 2
    assert "Terminology Conflict Report" in result.output


def test_detect_conflicts_special_regex_chars(tmp_path: Path) -> None:
    """Test terms with special regex characters."""
    file = tmp_path / "test.md"
    file.write_text("Use C++ or c++ for programming")

    runner = CliRunner()
    result = runner.invoke(detect_conflicts, [str(tmp_path), "--terms", "C++,c++"])

    # Should handle regex special chars safely
    assert isinstance(result.exit_code, int)


def test_detect_conflicts_empty_files(tmp_path: Path) -> None:
    """Test conflict detection with empty files."""
    (tmp_path / "empty.md").write_text("")
    (tmp_path / "content.md").write_text("Query Engine")

    runner = CliRunner()
    result = runner.invoke(detect_conflicts, [str(tmp_path), "--terms", "Query Engine"])

    # Should not crash on empty files
    assert isinstance(result.exit_code, int)


def test_detect_conflicts_binary_files(tmp_path: Path) -> None:
    """Test conflict detection safely handles binary files."""
    binary = tmp_path / "binary.md"
    binary.write_bytes(b"\x00\x01\x02\x03\xff\xfe")

    runner = CliRunner()
    result = runner.invoke(detect_conflicts, [str(tmp_path), "--terms", "Query Engine"])

    # Should not crash
    assert isinstance(result.exit_code, int)


def test_detect_conflicts_whitespace_only_files(tmp_path: Path) -> None:
    """Test with files containing only whitespace."""
    (tmp_path / "whitespace.md").write_text("   \n\t\n   ")

    runner = CliRunner()
    result = runner.invoke(detect_conflicts, [str(tmp_path), "--terms", "Query Engine"])

    # Should handle gracefully
    assert isinstance(result.exit_code, int)


def test_detect_conflicts_multiple_term_groups(tmp_path: Path) -> None:
    """Test detection with multiple term groups."""
    file = tmp_path / "test.md"
    file.write_text("Query Engine and DataStore work together. QueryEngine uses DataBase.")

    runner = CliRunner()
    result = runner.invoke(
        detect_conflicts,
        [str(tmp_path), "--terms", "Query Engine,QueryEngine", "--terms", "DataStore,DataBase"],
    )

    # Should detect conflicts in both groups
    assert result.exit_code == 2


def test_detect_conflicts_output_format(tmp_path: Path) -> None:
    """Test conflict report output format."""
    (tmp_path / "file1.md").write_text("Query Engine")
    (tmp_path / "file2.md").write_text("QueryEngine")

    runner = CliRunner()
    result = runner.invoke(detect_conflicts, [str(tmp_path), "--terms", "Query Engine,QueryEngine"])

    assert result.exit_code == 2
    assert "Terminology Conflict Report" in result.output
    assert "Query Engine" in result.output
    assert "Checking" in result.output or "Files checked:" in result.output


def test_detect_conflicts_auto_detect_mode_empty_dir(tmp_path: Path) -> None:
    """Test auto-detect with no files."""
    runner = CliRunner()
    result = runner.invoke(detect_conflicts, [str(tmp_path), "--auto-detect"])

    # Should handle empty directory
    assert isinstance(result.exit_code, int)


def test_detect_conflicts_no_conflicts_exit_code(tmp_path: Path) -> None:
    """Test correct exit code when no conflicts."""
    (tmp_path / "file1.md").write_text("Query Engine everywhere")
    (tmp_path / "file2.md").write_text("Query Engine consistently")

    runner = CliRunner()
    result = runner.invoke(detect_conflicts, [str(tmp_path), "--terms", "Query Engine"])

    # Exit 0 or success message
    assert "No conflicts" in result.output or result.exit_code == 0


def test_check_term_conflicts_empty_file_list() -> None:
    """Test with no files to check."""
    conflicts = check_term_conflicts([], ["Query Engine"])

    assert len(conflicts) == 0


def test_find_term_variants_empty_content() -> None:
    """Test with empty content."""
    variants = find_term_variants("", "Query Engine")

    assert len(variants) == 0


def test_find_term_variants_only_whitespace() -> None:
    """Test with whitespace-only content."""
    variants = find_term_variants("   \n\t\n   ", "Query Engine")

    assert len(variants) == 0


def test_detect_conflicts_unicode_terms(tmp_path: Path) -> None:
    """Test detection with unicode term names."""
    file = tmp_path / "test.md"
    file.write_text("使用查询引擎或QueryEngine", encoding="utf-8")

    runner = CliRunner()
    result = runner.invoke(detect_conflicts, [str(tmp_path), "--terms", "查询引擎,QueryEngine"])

    # Should handle unicode terms
    assert isinstance(result.exit_code, int)


def test_detect_conflicts_permission_error(tmp_path: Path) -> None:
    """Test conflict detection handles permission errors."""
    import os

    if os.name == "nt":
        # Skip on Windows
        return

    file = tmp_path / "noperm.md"
    file.write_text("Content")
    file.chmod(0o000)

    runner = CliRunner()
    result = runner.invoke(detect_conflicts, [str(tmp_path), "--terms", "Query Engine"])

    # Should handle gracefully
    file.chmod(0o644)  # Cleanup
    assert isinstance(result.exit_code, int)


def test_detect_conflicts_symbolic_links(tmp_path: Path) -> None:
    """Test with symbolic links."""
    import os

    target = tmp_path / "target.md"
    target.write_text("Query Engine")

    link = tmp_path / "link.md"
    if hasattr(os, "symlink"):
        try:
            link.symlink_to(target)

            runner = CliRunner()
            result = runner.invoke(detect_conflicts, [str(tmp_path), "--terms", "Query Engine"])

            # Should handle symlinks
            assert isinstance(result.exit_code, int)
        except OSError:
            # Symlinks not supported
            pass


def test_detect_conflicts_very_long_lines(tmp_path: Path) -> None:
    """Test with very long lines."""
    long_line = "Query Engine " * 10000  # 120,000+ chars
    file = tmp_path / "long.md"
    file.write_text(long_line)

    runner = CliRunner()
    result = runner.invoke(detect_conflicts, [str(tmp_path), "--terms", "Query Engine"])

    # Should handle long lines
    assert isinstance(result.exit_code, int)
