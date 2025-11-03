# DDD CLI Utilities

CLI utilities for Document-Driven Development Phase 2 workflows.

## Overview

This toolkit provides 5 utilities to streamline DDD Phase 2 documentation workflows:

1. **File Discovery** - Generate checklists of documentation files
2. **Progress Tracking** - Monitor completion status
3. **Retcon Verification** - Validate writing rules compliance
4. **Status Report** - Generate comprehensive reports for review
5. **Conflict Detection** - Find terminology inconsistencies

## Installation

```bash
cd ai_working/ddd_cli
make install
```

## Commands

### 1. File Discovery & Checklist Generation

Generate a checklist of all documentation files to update:

```bash
amplifier-ddd list-docs <project-dir>
```

**Options:**
- `--extensions` - File extensions to include (default: `.md,.yaml,.toml,.json`)
- `--exclude` - Additional paths to exclude
- `--output` - Output checklist path (default: `ai_working/ddd/docs_checklist.txt`)
- `--index` - Output index path (default: `ai_working/ddd/docs_index.txt`)

**Example:**
```bash
# Discover all docs in orchestrator/
amplifier-ddd list-docs orchestrator/

# Custom extensions
amplifier-ddd list-docs . --extensions .md,.rst --exclude temp/
```

**Output:**
- `ai_working/ddd/docs_index.txt` - Raw list of files
- `ai_working/ddd/docs_checklist.txt` - Checklist format with `[ ]` prefix

### 2. Progress Tracking

Track completion of documentation updates:

```bash
# Show current progress
amplifier-ddd progress show

# Mark a file as complete
amplifier-ddd progress mark-complete <file-path>
```

**Options:**
- `--checklist` - Path to checklist file (default: `ai_working/ddd/docs_checklist.txt`)

**Example:**
```bash
# Show progress
amplifier-ddd progress show
# Output: ○ Progress: 5/20 files (25.0%)

# Mark file complete
amplifier-ddd progress mark-complete docs/architecture.md
# Output: ✓ Marked complete: docs/architecture.md (6/20, 30.0%)

# Custom checklist
amplifier-ddd progress show --checklist custom_checklist.txt
```

### 3. Retcon Verification

Verify retcon writing rules compliance:

```bash
amplifier-ddd verify-retcon <project-dir>
```

**Rules Checked:**
- No future tense language (`will be`, `coming soon`, `planned`)
- No historical references (`previously`, `used to`, `old way`)
- No transition language (`instead of`, `rather than`, `no longer`)
- No version numbers (`v1.0`, `version 2`)
- No migration notes (`Migration:`, `Migrating from`)

**Options:**
- `--strict` - Enable strict mode (all rules must pass)
- `--exclude` - Files to exclude (default: `CHANGELOG.md`)
- `--json` - JSON output format

**Example:**
```bash
# Check all markdown files
amplifier-ddd verify-retcon orchestrator/

# Exclude specific files
amplifier-ddd verify-retcon . --exclude CHANGELOG.md --exclude docs/history.md

# JSON output for programmatic use
amplifier-ddd verify-retcon . --json > violations.json
```

**Output:**
```markdown
# Retcon Verification Report

## ✅ PASSED (3 rules)
- No future tense language
- No historical references
- No transition language

## ❌ VIOLATIONS (2 found)

### Future Tense Language
- docs/setup.md:42: "This will be added in v2.0"
- README.md:15: "Support coming soon for Windows"

## Summary
- 3/5 checks passed
- 2 violations across 2 files
```

### 4. Status Report Generation

Generate comprehensive status report for human review:

```bash
amplifier-ddd generate-report <project-dir>
```

**Options:**
- `--checklist` - Checklist path (default: `ai_working/ddd/docs_checklist.txt`)
- `--include-diff` - Include full git diff in report
- `--output` - Output path (default: `ai_working/ddd/docs_status.md`)

**Example:**
```bash
# Basic report
amplifier-ddd generate-report orchestrator/

# With full diff
amplifier-ddd generate-report . --include-diff

# Custom output location
amplifier-ddd generate-report . --output custom_report.md
```

**Output:** `ai_working/ddd/docs_status.md`

Report includes:
- Progress summary
- Git status (branch, staged files, etc.)
- Git diff summary
- Approval checklist

### 5. Conflict Detection

Find terminology inconsistencies across documentation:

```bash
amplifier-ddd detect-conflicts <project-dir>
```

**Options:**
- `--terms` - Comma-separated term variants to check
- `--auto-detect` - Use heuristics to find conflicts

**Example:**
```bash
# Check specific terms
amplifier-ddd detect-conflicts orchestrator/ --terms "Query Engine,QueryEngine,query_engine"

# Auto-detect conflicts
amplifier-ddd detect-conflicts . --auto-detect
```

**Output:**
```markdown
# Terminology Conflict Report

## Inconsistent Term: "Query Engine"

### Variants Found:
1. "Query Engine" (capitalized): 5 occurrences
   - docs/architecture.md:42
   - docs/api.md:15

2. "QueryEngine" (CamelCase): 3 occurrences
   - README.md:88

### Recommendation
Most common: "Query Engine" (5 occurrences)
ESCALATE to human for canonical term decision.
```

## Development

### Run Tests

```bash
make test
```

### Run Checks (Linting & Type Checking)

```bash
make check
```

### Format Code

```bash
make format
```

## Architecture

```
amplifier_ddd/
├── __init__.py          # Package initialization
├── cli.py               # Main CLI entry point
├── list_docs.py         # File discovery
├── progress.py          # Progress tracking
├── verify_retcon.py     # Retcon verification
├── generate_report.py   # Status report generation
├── detect_conflicts.py  # Conflict detection
├── config.py            # Configuration management
└── utils.py             # Shared utilities

tests/
├── test_list_docs.py
├── test_progress.py
├── test_verify_retcon.py
├── test_generate_report.py
└── test_detect_conflicts.py
```

## Exit Codes

- `0` - Success
- `1` - General error or retcon violations
- `2` - Terminology conflicts detected (distinct from retcon violations)

## Philosophy

Built following Amplifier patterns:
- **Ruthless simplicity** - Each utility does ONE thing well
- **Unix philosophy** - Composable tools
- **Human-usable** - Not just for agents
- **Incremental saves** - Save progress after every operation
- **Clear visibility** - Show what's happening
- **Defensive file I/O** - Atomic writes and retry logic

## License

MIT
