"""Main CLI entry point for DDD utilities."""

import click

from .detect_conflicts import detect_conflicts
from .generate_report import generate_report
from .list_docs import list_docs
from .progress import progress_group
from .verify_retcon import verify_retcon


@click.group(name="ddd")
@click.version_option()
def ddd_cli() -> None:
    """Document-Driven Development utilities.

    Tools for DDD Phase 2 workflows:
    - File discovery and checklist generation
    - Progress tracking
    - Retcon verification
    - Status report generation
    - Conflict detection
    """


# Add all commands
ddd_cli.add_command(list_docs, name="list-docs")
ddd_cli.add_command(progress_group, name="progress")
ddd_cli.add_command(verify_retcon, name="verify-retcon")
ddd_cli.add_command(generate_report, name="generate-report")
ddd_cli.add_command(detect_conflicts, name="detect-conflicts")


if __name__ == "__main__":
    ddd_cli()
