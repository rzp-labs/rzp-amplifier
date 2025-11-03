"""Extended tests for list_docs functionality covering edge cases."""

from pathlib import Path

from click.testing import CliRunner

from amplifier_ddd.list_docs import discover_files, list_docs


def test_discover_files_nested_deep(tmp_path: Path) -> None:
    """Test discovery in deeply nested directories."""
    # Create 5 levels of nesting
    nested = tmp_path / "level1" / "level2" / "level3" / "level4" / "level5"
    nested.mkdir(parents=True)
    (nested / "deep.md").write_text("Deep file")
    (tmp_path / "root.md").write_text("Root file")

    files = discover_files(tmp_path, [".md"], [])

    assert len(files) == 2
    assert Path("root.md") in files
    assert Path("level1/level2/level3/level4/level5/deep.md") in files


def test_discover_files_special_chars_in_names(tmp_path: Path) -> None:
    """Test files with special characters in names."""
    special_names = [
        "file with spaces.md",
        "file-with-dashes.md",
        "file_with_underscores.md",
        "file.multiple.dots.md",
        "file[brackets].md",
        "file(parens).md",
    ]

    for name in special_names:
        (tmp_path / name).write_text("Content")

    files = discover_files(tmp_path, [".md"], [])

    assert len(files) == len(special_names)
    for name in special_names:
        assert Path(name) in files


def test_discover_files_mixed_extensions(tmp_path: Path) -> None:
    """Test discovery with multiple extensions."""
    (tmp_path / "file1.md").write_text("Markdown")
    (tmp_path / "file2.rst").write_text("RST")
    (tmp_path / "file3.txt").write_text("Text")
    (tmp_path / "file4.yaml").write_text("YAML")
    (tmp_path / "file5.json").write_text("JSON")

    files = discover_files(tmp_path, [".md", ".rst", ".yaml"], [])

    assert len(files) == 3
    assert Path("file1.md") in files
    assert Path("file2.rst") in files
    assert Path("file4.yaml") in files
    assert Path("file3.txt") not in files


def test_discover_files_case_sensitive_extensions(tmp_path: Path) -> None:
    """Test that extensions are case-sensitive."""
    (tmp_path / "file.md").write_text("Lower")
    (tmp_path / "file.MD").write_text("Upper")

    files_lower = discover_files(tmp_path, [".md"], [])
    files_upper = discover_files(tmp_path, [".MD"], [])

    assert Path("file.md") in files_lower
    assert Path("file.MD") not in files_lower
    assert Path("file.MD") in files_upper
    assert Path("file.md") not in files_upper


def test_discover_files_hidden_files(tmp_path: Path) -> None:
    """Test discovery includes hidden files (starting with .)."""
    (tmp_path / ".hidden.md").write_text("Hidden")
    (tmp_path / "visible.md").write_text("Visible")

    files = discover_files(tmp_path, [".md"], [])

    assert len(files) == 2
    assert Path(".hidden.md") in files
    assert Path("visible.md") in files


def test_discover_files_multiple_exclusions(tmp_path: Path) -> None:
    """Test discovery with multiple exclusion patterns."""
    # Create structure with multiple excluded dirs
    (tmp_path / ".venv").mkdir()
    (tmp_path / ".venv" / "file1.md").write_text("Excluded 1")

    (tmp_path / "node_modules").mkdir()
    (tmp_path / "node_modules" / "file2.md").write_text("Excluded 2")

    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "file3.md").write_text("Excluded 3")

    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "file4.md").write_text("Included")

    files = discover_files(tmp_path, [".md"], [".venv", "node_modules", ".git"])

    assert len(files) == 1
    assert Path("src/file4.md") in files


def test_discover_files_exclusion_anywhere_in_path(tmp_path: Path) -> None:
    """Test that exclusions work at any level of the path."""
    # Create structure where excluded dir is not at root
    (tmp_path / "project").mkdir()
    (tmp_path / "project" / ".venv").mkdir()
    (tmp_path / "project" / ".venv" / "file.md").write_text("Excluded")

    (tmp_path / "project" / "src").mkdir()
    (tmp_path / "project" / "src" / "file.md").write_text("Included")

    files = discover_files(tmp_path, [".md"], [".venv"])

    assert len(files) == 1
    assert Path("project/src/file.md") in files


def test_discover_files_large_directory(tmp_path: Path) -> None:
    """Test discovery with many files."""
    # Create 100 files
    for i in range(100):
        (tmp_path / f"file{i:03d}.md").write_text(f"Content {i}")

    files = discover_files(tmp_path, [".md"], [])

    assert len(files) == 100
    # Verify sorting
    assert files[0] == Path("file000.md")
    assert files[-1] == Path("file099.md")


def test_discover_files_no_extension_files_ignored(tmp_path: Path) -> None:
    """Test that files without extensions are ignored."""
    (tmp_path / "README").write_text("No extension")
    (tmp_path / "Makefile").write_text("No extension")
    (tmp_path / "README.md").write_text("Has extension")

    files = discover_files(tmp_path, [".md"], [])

    assert len(files) == 1
    assert Path("README.md") in files


def test_list_docs_no_files_found(tmp_path: Path) -> None:
    """Test list-docs when no files match criteria."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()

    runner = CliRunner()
    result = runner.invoke(
        list_docs,
        [
            str(tmp_path),
            "--extensions",
            ".nonexistent",
            "--output",
            str(output_dir / "checklist.txt"),
            "--index",
            str(output_dir / "index.txt"),
        ],
    )

    assert "No files found matching criteria" in result.output
    # Should not create files when no matches
    assert not (output_dir / "checklist.txt").exists()
    assert not (output_dir / "index.txt").exists()


def test_list_docs_with_custom_exclusions(tmp_path: Path) -> None:
    """Test list-docs with user-provided exclusions."""
    # Create structure
    (tmp_path / "temp").mkdir()
    (tmp_path / "temp" / "test.md").write_text("Temp")
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "guide.md").write_text("Docs")

    output_dir = tmp_path / "output"
    output_dir.mkdir()

    runner = CliRunner()
    result = runner.invoke(
        list_docs,
        [
            str(tmp_path),
            "--extensions",
            ".md",
            "--exclude",
            "temp",
            "--output",
            str(output_dir / "checklist.txt"),
            "--index",
            str(output_dir / "index.txt"),
        ],
    )

    assert result.exit_code == 0

    checklist = (output_dir / "checklist.txt").read_text()
    assert "docs/guide.md" in checklist
    assert "temp/test.md" not in checklist


def test_list_docs_extensions_without_dot(tmp_path: Path) -> None:
    """Test list-docs handles extensions without leading dot."""
    (tmp_path / "file.md").write_text("Test")

    output_dir = tmp_path / "output"
    output_dir.mkdir()

    runner = CliRunner()
    result = runner.invoke(
        list_docs,
        [
            str(tmp_path),
            "--extensions",
            "md",  # Without dot
            "--output",
            str(output_dir / "checklist.txt"),
            "--index",
            str(output_dir / "index.txt"),
        ],
    )

    assert result.exit_code == 0
    checklist = (output_dir / "checklist.txt").read_text()
    assert "file.md" in checklist


def test_list_docs_extension_summary(tmp_path: Path) -> None:
    """Test list-docs shows summary by extension."""
    (tmp_path / "file1.md").write_text("Test")
    (tmp_path / "file2.md").write_text("Test")
    (tmp_path / "file3.rst").write_text("Test")
    (tmp_path / "file4.yaml").write_text("Test")

    output_dir = tmp_path / "output"
    output_dir.mkdir()

    runner = CliRunner()
    result = runner.invoke(
        list_docs,
        [
            str(tmp_path),
            "--extensions",
            ".md,.rst,.yaml",
            "--output",
            str(output_dir / "checklist.txt"),
            "--index",
            str(output_dir / "index.txt"),
        ],
    )

    assert result.exit_code == 0
    assert "Found 4 files" in result.output
    assert ".md: 2 files" in result.output
    assert ".rst: 1 files" in result.output
    assert ".yaml: 1 files" in result.output


def test_list_docs_creates_output_directories(tmp_path: Path) -> None:
    """Test list-docs creates output directories if needed."""
    (tmp_path / "file.md").write_text("Test")

    # Output directory doesn't exist yet
    output_path = tmp_path / "deep" / "nested" / "output" / "checklist.txt"
    index_path = tmp_path / "deep" / "nested" / "output" / "index.txt"

    runner = CliRunner()
    result = runner.invoke(
        list_docs,
        [
            str(tmp_path),
            "--extensions",
            ".md",
            "--output",
            str(output_path),
            "--index",
            str(index_path),
        ],
    )

    assert result.exit_code == 0
    assert output_path.exists()
    assert index_path.exists()


def test_list_docs_index_and_checklist_content(tmp_path: Path) -> None:
    """Test that index and checklist have correct format."""
    (tmp_path / "file1.md").write_text("Test")
    (tmp_path / "file2.md").write_text("Test")

    output_dir = tmp_path / "output"
    output_dir.mkdir()

    runner = CliRunner()
    result = runner.invoke(
        list_docs,
        [
            str(tmp_path),
            "--extensions",
            ".md",
            "--output",
            str(output_dir / "checklist.txt"),
            "--index",
            str(output_dir / "index.txt"),
        ],
    )

    assert result.exit_code == 0

    # Verify index format (no checkbox)
    index = (output_dir / "index.txt").read_text()
    assert "file1.md\n" in index
    assert "file2.md\n" in index
    assert "[ ]" not in index

    # Verify checklist format (with checkbox)
    checklist = (output_dir / "checklist.txt").read_text()
    assert "[ ] file1.md\n" in checklist
    assert "[ ] file2.md\n" in checklist


def test_list_docs_sorted_output(tmp_path: Path) -> None:
    """Test that output files are sorted alphabetically."""
    # Create files in non-alphabetical order
    (tmp_path / "zebra.md").write_text("Z")
    (tmp_path / "apple.md").write_text("A")
    (tmp_path / "banana.md").write_text("B")

    output_dir = tmp_path / "output"
    output_dir.mkdir()

    runner = CliRunner()
    result = runner.invoke(
        list_docs,
        [
            str(tmp_path),
            "--extensions",
            ".md",
            "--output",
            str(output_dir / "checklist.txt"),
            "--index",
            str(output_dir / "index.txt"),
        ],
    )

    assert result.exit_code == 0

    checklist = (output_dir / "checklist.txt").read_text()
    lines = [line for line in checklist.split("\n") if line]

    # Should be alphabetically sorted
    assert lines[0] == "[ ] apple.md"
    assert lines[1] == "[ ] banana.md"
    assert lines[2] == "[ ] zebra.md"
