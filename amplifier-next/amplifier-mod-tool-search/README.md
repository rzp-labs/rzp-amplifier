# Search Tools Module

Self-contained search tools module for Amplifier, providing grep and glob functionality for file searching and content searching.

## Purpose

This module provides essential search capabilities:
- **GrepTool**: Search file contents using regex patterns
- **GlobTool**: Find files matching glob patterns

## Installation

```bash
pip install -e .
```

## Configuration

Add to your Amplifier configuration:

```yaml
modules:
  search:
    module: "amplifier-mod-tool-search"
    config:
      max_results: 100      # Default max results for both tools
      allowed_paths:        # Paths allowed for searching
        - "."
      grep:
        max_file_size: 10485760  # 10MB max file size for grep
      glob:
        max_results: 1000   # Override for glob specifically
```

## Tools

### GrepTool

Search file contents with regex patterns.

**Input:**
```json
{
  "pattern": "TODO|FIXME",
  "path": "src",
  "recursive": true,
  "ignore_case": false,
  "include": "*.py",
  "exclude": "*_test.py",
  "context_lines": 2
}
```

**Features:**
- Regular expression pattern matching
- Recursive directory searching
- Case sensitivity control
- File pattern filtering (include/exclude)
- Context lines around matches
- Binary file detection and skipping
- Large file protection (configurable max size)

**Output:**
```json
{
  "pattern": "TODO|FIXME",
  "matches": 5,
  "results": [
    {
      "file": "src/main.py",
      "line_no": 42,
      "content": "# TODO: Implement this function",
      "context": [
        {"line_no": 40, "content": "def process():", "is_match": false},
        {"line_no": 41, "content": "    \"\"\"Process data.\"\"\"", "is_match": false},
        {"line_no": 42, "content": "    # TODO: Implement this function", "is_match": true},
        {"line_no": 43, "content": "    pass", "is_match": false}
      ]
    }
  ]
}
```

### GlobTool

Find files matching glob patterns.

**Input:**
```json
{
  "pattern": "**/*.py",
  "path": ".",
  "type": "file",
  "exclude": ["*_test.py", "*.pyc"]
}
```

**Features:**
- Standard glob pattern matching
- Type filtering (file/dir/any)
- Multiple exclusion patterns
- File size information
- Configurable result limits

**Output:**
```json
{
  "pattern": "**/*.py",
  "base_path": ".",
  "count": 10,
  "matches": [
    {
      "path": "src/main.py",
      "type": "file",
      "size": 1234
    },
    {
      "path": "src/utils.py",
      "type": "file",
      "size": 567
    }
  ]
}
```

## Design Philosophy

This module follows Amplifier's modular design principles:

- **Self-contained**: All functionality within the module directory
- **Simple interface**: Clear input/output contracts via ToolResult
- **Fail gracefully**: Meaningful error messages, partial results on file errors
- **Performance conscious**: File size limits, result limits, binary detection
- **Zero dependencies**: Uses only Python standard library + amplifier-core

## Error Handling

Both tools handle errors gracefully:

- Invalid patterns return clear error messages
- Non-existent paths are reported
- File access errors don't stop the entire search
- Results are truncated at max_results with indication

## Security

- Configurable allowed_paths restriction (future enhancement)
- Max file size protection against memory exhaustion
- Binary file detection to avoid processing non-text files

## Testing

```bash
# Install in development mode
pip install -e .

# Run basic tests (when available)
pytest tests/
```

## Module Contract

**Purpose**: Provide file and content search capabilities

**Inputs**: Search patterns and paths via tool execute() methods

**Outputs**: ToolResult with matched files or content

**Side Effects**: None (read-only operations)

**Dependencies**: amplifier-core

## Regeneration Specification

This module can be regenerated from this specification:
- Two tools: GrepTool and GlobTool
- Standard execute() interface returning ToolResult
- Configuration via __init__ parameters
- Mount function returning tool instances
- No external dependencies beyond amplifier-core