"""Tests for utility functions."""

from pathlib import Path

from amplifier_ddd.utils import atomic_write, format_percentage, retry_file_operation, should_exclude


def test_atomic_write_basic(tmp_path: Path) -> None:
    """Test basic atomic file writing."""
    output_file = tmp_path / "test.txt"
    content = "Test content\n"

    atomic_write(content, output_file)

    assert output_file.exists()
    assert output_file.read_text() == content


def test_atomic_write_creates_parent_dirs(tmp_path: Path) -> None:
    """Test atomic write creates parent directories."""
    output_file = tmp_path / "nested" / "dir" / "test.txt"
    content = "Test content\n"

    atomic_write(content, output_file)

    assert output_file.exists()
    assert output_file.read_text() == content


def test_atomic_write_overwrites_existing(tmp_path: Path) -> None:
    """Test atomic write overwrites existing file."""
    output_file = tmp_path / "test.txt"
    output_file.write_text("Old content\n")

    new_content = "New content\n"
    atomic_write(new_content, output_file)

    assert output_file.read_text() == new_content


def test_atomic_write_unicode(tmp_path: Path) -> None:
    """Test atomic write with unicode content."""
    output_file = tmp_path / "test.txt"
    content = "Unicode: ✓ 中文 émoji 🎉\n"

    atomic_write(content, output_file)

    assert output_file.exists()
    assert output_file.read_text() == content


def test_retry_file_operation_success() -> None:
    """Test retry with successful operation."""
    call_count = 0

    def successful_func() -> str:
        nonlocal call_count
        call_count += 1
        return "success"

    result = retry_file_operation(successful_func)

    assert result == "success"
    assert call_count == 1


def test_retry_file_operation_eventual_success() -> None:
    """Test retry with operation succeeding after failures."""
    call_count = 0

    def eventually_successful_func() -> str:
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            error = OSError("I/O error")
            error.errno = 5
            raise error
        return "success"

    result = retry_file_operation(eventually_successful_func, max_retries=3, retry_delay=0.01)

    assert result == "success"
    assert call_count == 3


def test_retry_file_operation_all_failures() -> None:
    """Test retry exhausting all attempts."""
    call_count = 0

    def failing_func() -> None:
        nonlocal call_count
        call_count += 1
        error = OSError("I/O error")
        error.errno = 5
        raise error

    try:
        retry_file_operation(failing_func, max_retries=3, retry_delay=0.01)
        assert False, "Should have raised OSError"
    except OSError:
        assert call_count == 3


def test_retry_file_operation_non_io_error() -> None:
    """Test retry with non-IO error raises immediately."""
    call_count = 0

    def non_io_error_func() -> None:
        nonlocal call_count
        call_count += 1
        raise OSError("Not an I/O error")

    try:
        retry_file_operation(non_io_error_func, max_retries=3, retry_delay=0.01)
        assert False, "Should have raised OSError"
    except OSError:
        assert call_count == 1  # Should not retry


def test_should_exclude_basic() -> None:
    """Test basic path exclusion."""
    assert should_exclude(Path(".venv/file.py"), [".venv"])
    assert should_exclude(Path("node_modules/lib/file.js"), ["node_modules"])
    assert not should_exclude(Path("src/main.py"), [".venv"])


def test_should_exclude_nested_paths() -> None:
    """Test exclusion with nested paths."""
    assert should_exclude(Path("project/.venv/lib/file.py"), [".venv"])
    assert should_exclude(Path("deep/nested/.git/config"), [".git"])
    assert not should_exclude(Path("project/src/.venv-name/file.py"), [".venv"])


def test_should_exclude_multiple_exclusions() -> None:
    """Test with multiple exclusion patterns."""
    exclusions = [".venv", "node_modules", ".git", "__pycache__"]

    assert should_exclude(Path(".venv/file.py"), exclusions)
    assert should_exclude(Path("node_modules/file.js"), exclusions)
    assert should_exclude(Path(".git/config"), exclusions)
    assert should_exclude(Path("src/__pycache__/file.pyc"), exclusions)
    assert not should_exclude(Path("src/main.py"), exclusions)


def test_should_exclude_partial_match() -> None:
    """Test exclusion doesn't match partial directory names."""
    # ".venv" should not match "my.venv" as a directory component
    assert not should_exclude(Path("my.venv/file.py"), [".venv"])
    assert should_exclude(Path(".venv/file.py"), [".venv"])


def test_format_percentage_basic() -> None:
    """Test basic percentage formatting."""
    assert format_percentage(1, 2) == "50.0%"
    assert format_percentage(1, 3) == "33.3%"
    assert format_percentage(2, 3) == "66.7%"


def test_format_percentage_zero_total() -> None:
    """Test percentage with zero total."""
    assert format_percentage(0, 0) == "0%"


def test_format_percentage_complete() -> None:
    """Test percentage at 100%."""
    assert format_percentage(10, 10) == "100.0%"


def test_format_percentage_zero_completed() -> None:
    """Test percentage at 0%."""
    assert format_percentage(0, 10) == "0.0%"


def test_format_percentage_rounding() -> None:
    """Test percentage rounding."""
    assert format_percentage(1, 6) == "16.7%"  # Rounds to 1 decimal
    assert format_percentage(2, 7) == "28.6%"
