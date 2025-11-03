"""Status report generation for DDD Phase 2."""

from pathlib import Path

import click

try:
    import git

    HAS_GIT = True
except ImportError:
    HAS_GIT = False

from .config import DEFAULT_CHECKLIST_PATH, DEFAULT_REPORT_PATH
from .progress import calculate_progress


def get_git_status(project_dir: Path) -> dict[str, str | list[str]]:
    """Get git status information.

    Args:
        project_dir: Project directory

    Returns:
        Dictionary with git status information
    """
    if not HAS_GIT:
        return {"error": "GitPython not installed"}

    try:
        repo = git.Repo(project_dir, search_parent_directories=True)

        # Get current branch
        branch = repo.active_branch.name if not repo.head.is_detached else "DETACHED"

        # Get staged changes
        staged_files = [item.a_path for item in repo.index.diff("HEAD") if item.a_path is not None]

        # Get unstaged changes
        unstaged_files = [item.a_path for item in repo.index.diff(None) if item.a_path is not None]

        # Get untracked files
        untracked_files = repo.untracked_files

        return {
            "branch": branch,
            "staged": staged_files,
            "unstaged": unstaged_files,
            "untracked": untracked_files,
        }
    except git.InvalidGitRepositoryError:
        return {"error": "Not a git repository"}
    except Exception as e:
        return {"error": str(e)}


def get_git_diff_summary(project_dir: Path) -> str:
    """Get git diff summary statistics.

    Args:
        project_dir: Project directory

    Returns:
        Diff summary string
    """
    if not HAS_GIT:
        return "GitPython not installed"

    try:
        repo = git.Repo(project_dir, search_parent_directories=True)

        # Get cached diff (staged changes)
        diff_output = repo.git.diff("--cached", "--stat")

        return diff_output if diff_output else "No staged changes"
    except Exception as e:
        return f"Error getting diff: {e}"


def generate_report_content(project_dir: Path, checklist_path: Path, include_diff: bool) -> str:
    """Generate markdown report content.

    Args:
        project_dir: Project directory
        checklist_path: Path to checklist
        include_diff: Whether to include full diff

    Returns:
        Markdown report string
    """
    report_lines = ["# DDD Phase 2 - Documentation Status Report", ""]

    # Progress section
    try:
        completed, total, percentage = calculate_progress(checklist_path)
        report_lines.append("## Progress")
        report_lines.append(f"- **Completion**: {completed}/{total} files ({percentage})")
        report_lines.append("")
    except FileNotFoundError:
        report_lines.append("## Progress")
        report_lines.append("- Checklist not found")
        report_lines.append("")

    # Git status section
    git_status = get_git_status(project_dir)
    report_lines.append("## Git Status")

    if "error" in git_status:
        report_lines.append(f"- Error: {git_status['error']}")
    else:
        report_lines.append(f"- **Branch**: {git_status['branch']}")
        report_lines.append(f"- **Staged files**: {len(git_status['staged'])}")
        report_lines.append(f"- **Unstaged files**: {len(git_status['unstaged'])}")
        report_lines.append(f"- **Untracked files**: {len(git_status['untracked'])}")

        if git_status["staged"]:
            report_lines.append("")
            report_lines.append("### Staged Files")
            for file in git_status["staged"][:20]:  # Limit to 20
                report_lines.append(f"- {file}")
            if len(git_status["staged"]) > 20:
                report_lines.append(f"- ... and {len(git_status['staged']) - 20} more")

    report_lines.append("")

    # Diff summary section
    report_lines.append("## Git Diff Summary")
    diff_summary = get_git_diff_summary(project_dir)
    report_lines.append("```")
    report_lines.append(diff_summary)
    report_lines.append("```")
    report_lines.append("")

    # Full diff section (if requested)
    if include_diff and HAS_GIT:
        try:
            repo = git.Repo(project_dir, search_parent_directories=True)
            full_diff = repo.git.diff("--cached")
            if full_diff:
                report_lines.append("## Full Diff")
                report_lines.append("```diff")
                report_lines.append(full_diff)
                report_lines.append("```")
                report_lines.append("")
        except Exception as e:
            report_lines.append(f"Error getting full diff: {e}")
            report_lines.append("")

    # Approval checklist
    report_lines.append("## Approval Checklist")
    report_lines.append("- [ ] All documentation updates completed")
    report_lines.append("- [ ] Retcon rules verified (no future tense/historical refs)")
    report_lines.append("- [ ] Terminology conflicts resolved")
    report_lines.append("- [ ] Changes reviewed and approved")
    report_lines.append("- [ ] Ready to commit")
    report_lines.append("")

    return "\n".join(report_lines)


@click.command()
@click.argument("project_dir", type=click.Path(exists=True, path_type=Path))
@click.option("--checklist", default=DEFAULT_CHECKLIST_PATH, type=Path, help="Checklist path")
@click.option("--include-diff", is_flag=True, help="Include full git diff in report")
@click.option("--output", default=DEFAULT_REPORT_PATH, type=Path, help="Output path")
def generate_report(project_dir: Path, checklist: Path, include_diff: bool, output: Path) -> None:
    """Generate comprehensive status report for human review.

    Creates a markdown report including:
    - Progress summary
    - Git status
    - Diff summary
    - Approval checklist

    Example:
        amplifier-ddd generate-report orchestrator/
        amplifier-ddd generate-report . --include-diff
        amplifier-ddd generate-report . --output custom_report.md
    """
    if not HAS_GIT:
        click.echo(
            click.style(
                "Warning: GitPython not installed. Git features disabled.",
                fg="yellow",
            )
        )
        click.echo("Install with: pip install gitpython")
        click.echo("")

    click.echo(f"Generating status report for {project_dir}...")

    # Generate report
    report_content = generate_report_content(project_dir, checklist, include_diff)

    # Write report
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(report_content, encoding="utf-8")

    click.echo(click.style(f"✓ Report generated: {output}", fg="green"))
