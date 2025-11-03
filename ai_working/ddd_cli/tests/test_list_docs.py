"""Tests for list_docs functionality."""

from pathlib import Path

from click.testing import CliRunner

from amplifier_ddd.list_docs import discover_files, list_docs


def test_discover_files_basic(tmp_path: Path) -> None:
    """Test basic file discovery."""
    # Create test files
    (tmp_path / "README.md").write_text("# Test")
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "guide.md").write_text("Guide")
    (tmp_path / "config.yaml").write_text("key: value")

    # Discover files
    files = discover_files(tmp_path, [".md", ".yaml"], [])

    # Verify
    assert len(files) == 3
    assert Path("README.md") in files
    assert Path("docs/guide.md") in files
    assert Path("config.yaml") in files


def test_discover_files_with_exclusions(tmp_path: Path) -> None:
    """Test file discovery with exclusions."""
    # Create test structure
    (tmp_path / ".venv").mkdir()
    (tmp_path / ".venv" / "file.md").write_text("Excluded")
    (tmp_path / "README.md").write_text("Included")

    # Discover with exclusions
    files = discover_files(tmp_path, [".md"], [".venv"])

    # Verify .venv excluded
    assert len(files) == 1
    assert Path("README.md") in files


def test_discover_files_empty_dir(tmp_path: Path) -> None:
    """Test discovery in empty directory."""
    files = discover_files(tmp_path, [".md"], [])
    assert len(files) == 0


def test_list_docs_command(tmp_path: Path) -> None:
    """Test list-docs CLI command."""
    # Create test files
    (tmp_path / "README.md").write_text("Test")
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "guide.md").write_text("Guide")

    # Create output directory
    output_dir = tmp_path / "output"
    output_dir.mkdir()

    # Run command
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

    # Verify success
    assert result.exit_code == 0
    assert "Found 2 files" in result.output

    # Verify files created
    checklist = (output_dir / "checklist.txt").read_text()
    assert "[ ] README.md" in checklist
    assert "[ ] docs/guide.md" in checklist

    index = (output_dir / "index.txt").read_text()
    assert "README.md" in index
    assert "docs/guide.md" in index
