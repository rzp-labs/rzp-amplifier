"""Progress tracking for DDD Phase 2 documentation updates."""

from pathlib import Path

import click

from .config import DEFAULT_CHECKLIST_PATH
from .utils import atomic_write, format_percentage


def read_checklist(checklist_path: Path) -> list[str]:
    """Read checklist file and return lines.

    Args:
        checklist_path: Path to checklist file

    Returns:
        List of checklist lines

    Raises:
        FileNotFoundError: If checklist doesn't exist
    """
    if not checklist_path.exists():
        raise FileNotFoundError(f"Checklist not found: {checklist_path}")

    return checklist_path.read_text(encoding="utf-8").splitlines()


def parse_checklist(lines: list[str]) -> tuple[int, int, list[str]]:
    """Parse checklist and count completion.

    Args:
        lines: Checklist lines

    Returns:
        Tuple of (completed, total, lines)
    """
    completed = sum(1 for line in lines if line.startswith("[x]") or line.startswith("[X]"))
    total = sum(1 for line in lines if line.startswith("[") and "]" in line)
    return completed, total, lines


def calculate_progress(checklist_path: Path) -> tuple[int, int, str]:
    """Calculate progress from checklist.

    Args:
        checklist_path: Path to checklist file

    Returns:
        Tuple of (completed, total, percentage_string)
    """
    lines = read_checklist(checklist_path)
    completed, total, _ = parse_checklist(lines)
    percentage = format_percentage(completed, total)
    return completed, total, percentage


@click.group(name="progress")
def progress_group() -> None:
    """Progress tracking commands."""


@progress_group.command(name="show")
@click.option("--checklist", default=DEFAULT_CHECKLIST_PATH, type=Path, help="Checklist path")
def show_progress(checklist: Path) -> None:
    """Show completion percentage.

    Example:
        amplifier-ddd progress show
        amplifier-ddd progress show --checklist custom_checklist.txt
    """
    try:
        completed, total, percentage = calculate_progress(checklist)

        if total == 0:
            click.echo(click.style("Checklist is empty", fg="yellow"))
            return

        # Color based on completion
        if completed == total:
            color = "green"
            symbol = "✓"
        elif completed > 0:
            color = "yellow"
            symbol = "○"
        else:
            color = "red"
            symbol = "○"

        click.echo(click.style(f"{symbol} Progress: {completed}/{total} files ({percentage})", fg=color, bold=True))

        # Exit code: 0 if complete, 1 otherwise
        if completed < total:
            raise SystemExit(1)

    except FileNotFoundError as e:
        click.echo(click.style(f"Error: {e}", fg="red"))
        raise SystemExit(1) from e


@progress_group.command(name="mark-complete")
@click.argument("file_path")
@click.option("--checklist", default=DEFAULT_CHECKLIST_PATH, type=Path, help="Checklist path")
def mark_complete(file_path: str, checklist: Path) -> None:
    """Mark file as complete in checklist.

    FILE_PATH should match a file in the checklist (can be relative or absolute).

    Example:
        amplifier-ddd progress mark-complete docs/architecture.md
        amplifier-ddd progress mark-complete README.md
    """
    try:
        lines = read_checklist(checklist)
        completed, total, updated_lines = parse_checklist(lines)

        # Normalize file path for matching
        file_path_normalized = Path(file_path).as_posix()
        file_basename = Path(file_path).name

        # Find and update the line
        found = False
        for i, line in enumerate(updated_lines):
            # Try exact match first, then basename match
            if line.startswith("[ ]") and (file_path_normalized in line or file_basename in line):
                # Mark as complete
                updated_lines[i] = line.replace("[ ]", "[x]", 1)
                found = True
                completed += 1
                break

        if not found:
            click.echo(click.style(f"Error: File not found in checklist: {file_path}", fg="red"))
            click.echo("Hint: Use 'amplifier-ddd list-docs' to see available files")
            raise SystemExit(1)

        # Write updated checklist atomically
        checklist_content = "\n".join(updated_lines)
        if not checklist_content.endswith("\n"):
            checklist_content += "\n"
        atomic_write(checklist_content, checklist)

        # Show updated progress
        percentage = format_percentage(completed, total)
        click.echo(
            click.style(
                f"✓ Marked complete: {file_path} ({completed}/{total}, {percentage})",
                fg="green",
            )
        )

    except FileNotFoundError as e:
        click.echo(click.style(f"Error: {e}", fg="red"))
        raise SystemExit(1) from e
