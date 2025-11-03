"""Retcon writing rules verification for DDD Phase 2."""

import json
import re
from collections import defaultdict
from pathlib import Path

import click

from .config import DEFAULT_EXCLUSIONS
from .utils import should_exclude

# Retcon verification rules
RETCON_RULES = {
    "future_tense": {
        "pattern": r"\b(will be|coming soon|planned|going to|gonna)\b",
        "description": "Future tense language (implies transition)",
    },
    "historical_refs": {
        "pattern": r"\b(previously|used to|old way|in the past)\b",
        "description": "Historical references (implies transition)",
    },
    "transition_lang": {
        "pattern": r"\b(instead of|rather than|no longer|now use)\b",
        "description": "Transition language (implies before/after)",
    },
    "version_numbers": {
        "pattern": r"\bv[0-9]|version [0-9]\b",
        "description": "Version numbers (implies evolution)",
    },
    "migration_notes": {
        "pattern": r"\b(Migration:|Migrating from)\b",
        "description": "Migration notes (implies transition)",
    },
}


def check_file(file_path: Path, rules: dict[str, dict[str, str]]) -> dict[str, list[dict[str, str | int]]]:
    """Check a file for retcon violations.

    Args:
        file_path: Path to file to check
        rules: Dictionary of rule_name -> {pattern, description}

    Returns:
        Dictionary of rule_name -> list of violations
        Each violation is {line: line_number, text: matching_text}
    """
    violations: dict[str, list[dict[str, str | int]]] = defaultdict(list)

    try:
        content = file_path.read_text(encoding="utf-8")
        lines = content.splitlines()

        for rule_name, rule_config in rules.items():
            pattern = re.compile(rule_config["pattern"], re.IGNORECASE)

            for line_num, line in enumerate(lines, start=1):
                if pattern.search(line):
                    violations[rule_name].append({"line": line_num, "text": line.strip(), "file": str(file_path)})

    except Exception as e:
        click.echo(
            click.style(f"Warning: Could not read {file_path}: {e}", fg="yellow"),
            err=True,
        )

    return violations


def generate_markdown_report(all_violations: dict[str, list[dict[str, str | int]]], total_files: int) -> str:
    """Generate markdown report from violations.

    Args:
        all_violations: Dictionary of rule_name -> list of violations
        total_files: Total number of files checked

    Returns:
        Markdown report string
    """
    report_lines = ["# Retcon Verification Report", ""]

    # Count passing and failing rules
    passing_rules = [rule for rule, viols in all_violations.items() if not viols]
    failing_rules = [rule for rule, viols in all_violations.items() if viols]

    # Passing section
    if passing_rules:
        report_lines.append(f"## ✅ PASSED ({len(passing_rules)} rules)")
        for rule in passing_rules:
            rule_desc = RETCON_RULES[rule]["description"]
            report_lines.append(f"- No {rule_desc.lower()}")
        report_lines.append("")

    # Violations section
    if failing_rules:
        total_violations = sum(len(viols) for viols in all_violations.values())
        report_lines.append(f"## ❌ VIOLATIONS ({total_violations} found)")
        report_lines.append("")

        for rule in failing_rules:
            rule_desc = RETCON_RULES[rule]["description"]
            violations = all_violations[rule]
            report_lines.append(f"### {rule_desc}")
            for violation in violations:
                file_path = violation["file"]
                line_num = violation["line"]
                text = violation["text"]
                report_lines.append(f'- {file_path}:{line_num}: "{text}"')
            report_lines.append("")

    # Summary
    report_lines.append("## Summary")
    report_lines.append(f"- {len(passing_rules)}/{len(RETCON_RULES)} checks passed")
    if failing_rules:
        total_violations = sum(len(all_violations[rule]) for rule in failing_rules)
        files_with_violations = len({v["file"] for rule_viols in all_violations.values() for v in rule_viols})
        report_lines.append(f"- {total_violations} violations across {files_with_violations} files")
    report_lines.append(f"- {total_files} total files checked")
    report_lines.append("")

    return "\n".join(report_lines)


@click.command()
@click.argument("project_dir", type=click.Path(exists=True, path_type=Path))
@click.option("--strict", is_flag=True, help="Enable strict mode (all rules must pass)")
@click.option(
    "--exclude",
    multiple=True,
    default=["CHANGELOG.md"],
    help="Files to exclude (default: CHANGELOG.md)",
)
@click.option("--json", "json_output", is_flag=True, help="JSON output format")
def verify_retcon(project_dir: Path, strict: bool, exclude: tuple[str, ...], json_output: bool) -> None:
    """Verify retcon writing rules compliance.

    Checks all .md files in PROJECT_DIR for retcon violations:
    - No future tense language
    - No historical references
    - No transition language
    - No version numbers
    - No migration notes

    Example:
        amplifier-ddd verify-retcon orchestrator/
        amplifier-ddd verify-retcon . --exclude CHANGELOG.md --exclude docs/history.md
        amplifier-ddd verify-retcon . --json > violations.json
    """
    # Combine default exclusions with user-provided ones
    exclusion_list = list(DEFAULT_EXCLUSIONS) + list(exclude)

    # Find all .md files
    files = []
    for md_file in project_dir.glob("**/*.md"):
        try:
            relative_path = md_file.relative_to(project_dir)
        except ValueError:
            relative_path = md_file

        # Skip excluded files
        if should_exclude(relative_path, exclusion_list):
            continue

        # Skip files matching exclude patterns
        if any(excl in str(relative_path) for excl in exclude):
            continue

        files.append(md_file)

    if not files:
        if not json_output:
            click.echo(click.style("No markdown files found to check", fg="yellow"))
        return

    if not json_output:
        click.echo(f"Checking {len(files)} files for retcon violations...")

    # Check all files
    all_violations: dict[str, list[dict[str, str | int]]] = defaultdict(list)
    for file_path in files:
        violations = check_file(file_path, RETCON_RULES)
        for rule_name, viols in violations.items():
            all_violations[rule_name].extend(viols)

    # Generate output
    if json_output:
        # JSON output
        output = {
            "rules": RETCON_RULES,
            "violations": dict(all_violations),
            "summary": {
                "total_files": len(files),
                "total_violations": sum(len(v) for v in all_violations.values()),
                "passing_rules": sum(1 for v in all_violations.values() if not v),
                "failing_rules": sum(1 for v in all_violations.values() if v),
            },
        }
        click.echo(json.dumps(output, indent=2))
    else:
        # Markdown output
        report = generate_markdown_report(all_violations, len(files))
        click.echo(report)

    # Exit code
    has_violations = any(all_violations.values())
    if has_violations:
        raise SystemExit(1)
