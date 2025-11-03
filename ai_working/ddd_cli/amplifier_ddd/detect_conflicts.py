"""Terminology conflict detection for DDD Phase 2."""

import re
from collections import Counter, defaultdict
from pathlib import Path

import click

from .config import DEFAULT_EXCLUSIONS
from .utils import should_exclude


def find_term_variants(content: str, base_term: str) -> list[str]:
    """Find all variants of a term in content.

    Args:
        content: Text content to search
        base_term: Base term to find variants of

    Returns:
        List of found variants
    """
    variants = []

    # Generate common variants
    words = base_term.split()

    # Original
    variants.append(base_term)

    # CamelCase
    camel_case = "".join(word.capitalize() for word in words)
    variants.append(camel_case)

    # snake_case
    snake_case = "_".join(word.lower() for word in words)
    variants.append(snake_case)

    # lowercase
    variants.append(base_term.lower())

    # UPPERCASE
    variants.append(base_term.upper())

    # Find which variants exist in content
    found_variants = []
    for variant in variants:
        # Use word boundary to avoid partial matches
        pattern = rf"\b{re.escape(variant)}\b"
        if re.search(pattern, content):
            found_variants.append(variant)

    return found_variants


def check_term_conflicts(files: list[Path], terms: list[str]) -> dict[str, dict[str, list[tuple[Path, int]]]]:
    """Check files for terminology conflicts.

    Args:
        files: List of files to check
        terms: List of terms (comma-separated variants)

    Returns:
        Dictionary of term -> variant -> list of (file, line) occurrences
    """
    results = {}

    for term_group in terms:
        variants = [v.strip() for v in term_group.split(",")]
        occurrences: dict[str, list[tuple[Path, int]]] = defaultdict(list)

        for file_path in files:
            try:
                content = file_path.read_text(encoding="utf-8")
                lines = content.splitlines()

                for variant in variants:
                    pattern = rf"\b{re.escape(variant)}\b"
                    for line_num, line in enumerate(lines, start=1):
                        if re.search(pattern, line):
                            occurrences[variant].append((file_path, line_num))

            except Exception as e:
                click.echo(
                    click.style(f"Warning: Could not read {file_path}: {e}", fg="yellow"),
                    err=True,
                )

        if occurrences:
            results[variants[0]] = dict(occurrences)

    return results


def auto_detect_conflicts(files: list[Path]) -> dict[str, dict[str, list[tuple[Path, int]]]]:
    """Auto-detect terminology conflicts using heuristics.

    Args:
        files: List of files to check

    Returns:
        Dictionary of suspected conflicts
    """
    # Find all capitalized multi-word terms
    all_terms: Counter = Counter()

    for file_path in files:
        try:
            content = file_path.read_text(encoding="utf-8")

            # Find capitalized multi-word terms (e.g., "Query Engine")
            pattern = r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+\b"
            matches = re.findall(pattern, content)
            all_terms.update(matches)

        except Exception:
            continue

    # For top 10 terms, check for variants
    conflicts = {}
    for term, _count in all_terms.most_common(10):
        # Generate all files content
        all_content = ""
        for file_path in files:
            try:
                all_content += file_path.read_text(encoding="utf-8")
            except Exception:
                continue

        variants = find_term_variants(all_content, term)

        # If multiple variants found, it's a conflict
        if len(variants) > 1:
            # Now find occurrences per variant
            occurrences: dict[str, list[tuple[Path, int]]] = defaultdict(list)

            for file_path in files:
                try:
                    content = file_path.read_text(encoding="utf-8")
                    lines = content.splitlines()

                    for variant in variants:
                        pattern = rf"\b{re.escape(variant)}\b"
                        for line_num, line in enumerate(lines, start=1):
                            if re.search(pattern, line):
                                occurrences[variant].append((file_path, line_num))

                except Exception:
                    continue

            conflicts[term] = dict(occurrences)

    return conflicts


def generate_conflict_report(conflicts: dict[str, dict[str, list[tuple[Path, int]]]]) -> str:
    """Generate markdown report of conflicts.

    Args:
        conflicts: Dictionary of conflicts

    Returns:
        Markdown report string
    """
    if not conflicts:
        return "# Terminology Conflict Report\n\n✅ No conflicts detected\n"

    report_lines = ["# Terminology Conflict Report", ""]

    for base_term, variants in conflicts.items():
        if not variants or len(variants) <= 1:
            continue

        report_lines.append(f'## Inconsistent Term: "{base_term}"')
        report_lines.append("")

        # Count occurrences per variant
        variant_counts = {v: len(occs) for v, occs in variants.items()}
        most_common = max(variant_counts, key=variant_counts.get)  # type: ignore[arg-type]

        report_lines.append("### Variants Found:")
        for i, (variant, occurrences) in enumerate(variants.items(), start=1):
            count = len(occurrences)
            report_lines.append(f'{i}. "{variant}": {count} occurrences')

            # Show first 3 locations
            for file_path, line_num in occurrences[:3]:
                report_lines.append(f"   - {file_path}:{line_num}")

            if len(occurrences) > 3:
                report_lines.append(f"   - ... and {len(occurrences) - 3} more")

        report_lines.append("")
        report_lines.append("### Recommendation")
        report_lines.append(f'Most common: "{most_common}" ({variant_counts[most_common]} occurrences)')
        report_lines.append("**ESCALATE to human for canonical term decision.**")
        report_lines.append("")

    return "\n".join(report_lines)


@click.command()
@click.argument("project_dir", type=click.Path(exists=True, path_type=Path))
@click.option("--terms", help="Comma-separated term variants to check (e.g., 'Query Engine,QueryEngine')")
@click.option("--auto-detect", is_flag=True, help="Use heuristics to find conflicts")
def detect_conflicts(project_dir: Path, terms: str | None, auto_detect: bool) -> None:
    """Find terminology inconsistencies across documentation.

    Checks for inconsistent terminology usage such as:
    - "Query Engine" vs "QueryEngine" vs "query engine"
    - "API Key" vs "APIKey" vs "api_key"

    Example:
        amplifier-ddd detect-conflicts orchestrator/ --terms "Query Engine,QueryEngine"
        amplifier-ddd detect-conflicts . --auto-detect
    """
    if not terms and not auto_detect:
        click.echo(click.style("Error: Must specify either --terms or --auto-detect", fg="red"))
        raise SystemExit(1)

    # Find all .md files
    files = []
    for md_file in project_dir.glob("**/*.md"):
        try:
            relative_path = md_file.relative_to(project_dir)
        except ValueError:
            relative_path = md_file

        if should_exclude(relative_path, DEFAULT_EXCLUSIONS):
            continue

        files.append(md_file)

    if not files:
        click.echo(click.style("No markdown files found", fg="yellow"))
        return

    click.echo(f"Checking {len(files)} files for terminology conflicts...")

    # Detect conflicts
    if auto_detect:
        conflicts = auto_detect_conflicts(files)
    else:
        term_list = [t.strip() for t in terms.split(";")]  # type: ignore[union-attr]
        conflicts = check_term_conflicts(files, term_list)

    # Generate report
    report = generate_conflict_report(conflicts)
    click.echo(report)

    # Exit code 2 if conflicts found (distinct from other failures)
    if conflicts and any(len(v) > 1 for v in conflicts.values()):
        raise SystemExit(2)
