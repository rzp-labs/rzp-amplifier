"""File discovery and checklist generation for DDD Phase 2."""

from pathlib import Path

import click

from .config import DEFAULT_CHECKLIST_PATH, DEFAULT_EXCLUSIONS, DEFAULT_EXTENSIONS, DEFAULT_INDEX_PATH
from .utils import atomic_write, should_exclude


def discover_files(project_dir: Path, extensions: list[str], exclusions: list[str]) -> list[Path]:
    """Discover all documentation files in project directory.

    Args:
        project_dir: Root directory to search
        extensions: File extensions to include
        exclusions: Paths to exclude

    Returns:
        Sorted list of file paths relative to project_dir
    """
    files = []

    for ext in extensions:
        # Use recursive glob with the extension
        pattern = f"**/*{ext}"
        for file_path in project_dir.glob(pattern):
            # Convert to relative path for cleaner output
            try:
                relative_path = file_path.relative_to(project_dir)
            except ValueError:
                relative_path = file_path

            # Skip excluded paths
            if should_exclude(relative_path, exclusions):
                continue

            files.append(relative_path)

    # Sort alphabetically for consistent output
    return sorted(files)


@click.command()
@click.argument("project_dir", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--extensions",
    default=",".join(DEFAULT_EXTENSIONS),
    help="Comma-separated file extensions to include",
)
@click.option("--exclude", multiple=True, help="Additional paths to exclude")
@click.option("--output", default=DEFAULT_CHECKLIST_PATH, type=Path, help="Output checklist path")
@click.option("--index", default=DEFAULT_INDEX_PATH, type=Path, help="Output index path")
def list_docs(project_dir: Path, extensions: str, exclude: tuple[str, ...], output: Path, index: Path) -> None:
    """Generate checklist of all documentation files to update.

    Discovers all documentation files in PROJECT_DIR and creates:
    - docs_index.txt: Raw list of files
    - docs_checklist.txt: Checklist format with [ ] prefix

    Example:
        amplifier-ddd list-docs orchestrator/
        amplifier-ddd list-docs . --extensions .md,.rst --exclude temp/
    """
    # Parse extensions
    ext_list = [ext.strip() if ext.startswith(".") else f".{ext.strip()}" for ext in extensions.split(",")]

    # Combine default exclusions with user-provided ones
    exclusion_list = list(DEFAULT_EXCLUSIONS) + list(exclude)

    # Discover files
    click.echo(f"Discovering files in {project_dir}...")
    files = discover_files(project_dir, ext_list, exclusion_list)

    if not files:
        click.echo(click.style("No files found matching criteria", fg="yellow"))
        return

    # Group files by extension for summary
    by_extension: dict[str, int] = {}
    for file in files:
        ext = file.suffix
        by_extension[ext] = by_extension.get(ext, 0) + 1

    # Generate index (raw list)
    index_content = "\n".join(str(f) for f in files) + "\n"
    atomic_write(index_content, index)
    click.echo(f"✓ Created index: {index}")

    # Generate checklist (with [ ] prefix)
    checklist_content = "\n".join(f"[ ] {f}" for f in files) + "\n"
    atomic_write(checklist_content, output)
    click.echo(f"✓ Created checklist: {output}")

    # Print summary
    click.echo()
    click.echo(click.style(f"Found {len(files)} files", fg="green", bold=True))
    for ext, count in sorted(by_extension.items()):
        click.echo(f"  {ext}: {count} files")
