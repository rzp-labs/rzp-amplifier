# Amplifier Filesystem Tools Module

Provides basic file operations for Amplifier agents.

## Purpose

Enables agents to read and write files within configured safe paths.

## Contract

**Module Type:** Tool
**Mount Point:** `tools`
**Entry Point:** `amplifier_mod_tool_filesystem:mount`

## Tools Provided

### `read`
Read the contents of a file.

**Input:**
- `path` (string): File path to read

**Output:**
- File contents as string
- Error if file not found or access denied

### `write`
Write content to a file.

**Input:**
- `path` (string): File path to write
- `content` (string): Content to write

**Output:**
- Success message with character count
- Creates parent directories if needed

## Configuration

```toml
[[tools]]
module = "tool-filesystem"
config = {
    allowed_paths = ["."],  # List of safe directory paths
    require_approval = false
}
```

## Security

- Access restricted to `allowed_paths` only
- Path traversal checks via `is_relative_to()`
- No arbitrary file system access

## Dependencies

- `amplifier-core>=1.0.0`
