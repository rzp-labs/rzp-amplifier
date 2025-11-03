"""Shared utilities for DDD CLI tools."""

import time
from pathlib import Path
from typing import Any


def atomic_write(content: str, filepath: Path) -> None:
    """Write file atomically using temp file + rename pattern.

    Args:
        content: Content to write
        filepath: Target file path
    """
    filepath.parent.mkdir(parents=True, exist_ok=True)
    temp_path = filepath.with_suffix(filepath.suffix + ".tmp")

    # Write to temp file
    temp_path.write_text(content, encoding="utf-8")

    # Atomic rename
    temp_path.replace(filepath)


def retry_file_operation(func: Any, max_retries: int = 3, retry_delay: float = 0.1) -> Any:
    """Retry file operation with exponential backoff.

    Args:
        func: Function to retry
        max_retries: Maximum retry attempts
        retry_delay: Initial delay in seconds

    Returns:
        Result of func()

    Raises:
        OSError: If all retries fail
    """
    for attempt in range(max_retries):
        try:
            return func()
        except OSError as e:
            if e.errno == 5 and attempt < max_retries - 1:  # I/O error
                time.sleep(retry_delay)
                retry_delay *= 2
            else:
                raise
    return None  # Should never reach here due to raise in loop


def should_exclude(path: Path, exclusions: list[str]) -> bool:
    """Check if path should be excluded.

    Args:
        path: Path to check
        exclusions: List of exclusion patterns

    Returns:
        True if path should be excluded
    """
    path_str = str(path)
    return any(exclusion in path_str.split("/") for exclusion in exclusions)


def format_percentage(completed: int, total: int) -> str:
    """Format completion percentage.

    Args:
        completed: Number of completed items
        total: Total number of items

    Returns:
        Formatted percentage string
    """
    if total == 0:
        return "0%"
    percentage = (completed / total) * 100
    return f"{percentage:.1f}%"
