# Testing Guide - Orchestrator Boundary Validation

## Quick Start

```bash
# Run all boundary validation tests
uv run pytest tests/orchestration/ tests/hooks/ -v

# Run with coverage report
uv run pytest tests/orchestration/ tests/hooks/ --cov=amplifier.orchestration --cov-report=term-missing
```

## Test Structure

```
tests/
├── orchestration/
│   ├── __init__.py
│   ├── README.md                          # Comprehensive documentation
│   ├── TESTING_GUIDE.md                   # This file
│   ├── test_boundary_validation.py        # 22 tests - core validation logic
│   └── test_delegation_audit.py           # 23 tests - audit logging
└── hooks/
    ├── __init__.py
    └── test_post_tool_use_boundary.py     # 15 tests - hook integration
```

## Running Specific Tests

### By File

```bash
# Boundary validation only
uv run pytest tests/orchestration/test_boundary_validation.py -v

# DelegationAudit only
uv run pytest tests/orchestration/test_delegation_audit.py -v

# Hook integration only
uv run pytest tests/hooks/test_post_tool_use_boundary.py -v
```

### By Class

```bash
# Agent detection tests only
uv run pytest tests/orchestration/test_boundary_validation.py::TestDetectAgentSession -v

# Violation tracking tests only
uv run pytest tests/orchestration/test_delegation_audit.py::TestGetViolations -v

# Hook behavior tests only
uv run pytest tests/hooks/test_post_tool_use_boundary.py::TestHookBoundaryValidation -v
```

### By Test Name

```bash
# Specific test
uv run pytest tests/orchestration/test_boundary_validation.py::TestDetectAgentSession::test_no_agent_markers -v

# Pattern matching
uv run pytest tests/orchestration/ -k "violation" -v
```

## Understanding Test Output

### Success

```
tests/orchestration/test_boundary_validation.py::TestDetectAgentSession::test_no_agent_markers PASSED [  4%]
```

### Failure

```
tests/orchestration/test_delegation_audit.py::TestEdgeCases::test_malformed_jsonl_line FAILED [100%]

=================================== FAILURES ===================================
___________________ TestEdgeCases.test_malformed_jsonl_line ____________________
...
E           json.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)
```

The detailed output shows:
- Which test failed
- The exact error
- The line of code that caused the failure

## Coverage Analysis

```bash
# Generate coverage report
uv run pytest tests/orchestration/ tests/hooks/ --cov=amplifier.orchestration --cov-report=term-missing

# Output shows:
Name                                          Stmts   Miss  Cover   Missing
---------------------------------------------------------------------------
amplifier/orchestration/__init__.py               2      0   100%
amplifier/orchestration/delegation_audit.py      43      1    98%   38
---------------------------------------------------------------------------
TOTAL                                            45      1    98%
```

**Reading the report:**
- `Stmts`: Total lines of code
- `Miss`: Lines not covered by tests
- `Cover`: Percentage coverage
- `Missing`: Line numbers not covered

## Debugging Test Failures

### 1. Run with verbose output

```bash
uv run pytest tests/orchestration/test_delegation_audit.py::TestEdgeCases::test_malformed_jsonl_line -vv
```

### 2. Show print statements

```bash
uv run pytest tests/orchestration/ -v -s
```

### 3. Show full traceback

```bash
uv run pytest tests/orchestration/ -v --tb=long
```

### 4. Drop into debugger on failure

```bash
uv run pytest tests/orchestration/ -v --pdb
```

## Writing New Tests

### Template

```python
"""Tests for new feature."""

import pytest
from amplifier.orchestration import DelegationAudit


class TestNewFeature:
    """Tests for the new feature."""

    def test_basic_functionality(self):
        """Test description."""
        # Arrange
        expected = "value"

        # Act
        result = function_to_test()

        # Assert
        assert result == expected

    def test_edge_case(self, tmp_path):
        """Test edge case description."""
        # Use tmp_path for file operations
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")

        result = process_file(test_file)

        assert result is not None
```

### Best Practices

1. **Clear naming** - Test names should describe what they verify
2. **One assertion per test** - Makes failures easier to debug
3. **Use fixtures** - `tmp_path` for file operations, `monkeypatch` for environment
4. **Document edge cases** - Explain why the edge case matters
5. **Test both success and failure** - Happy path and error conditions

### Fixtures Available

```python
def test_with_temp_dir(tmp_path):
    """tmp_path provides isolated temp directory."""
    pass

def test_with_env_vars(monkeypatch):
    """monkeypatch for environment variables."""
    monkeypatch.setenv("VAR_NAME", "value")
    monkeypatch.delenv("VAR_TO_DELETE", raising=False)
    pass
```

## Common Test Patterns

### Testing Environment Detection

```python
def test_agent_session_detected(self, monkeypatch):
    """Test with mocked environment."""
    # Clear environment
    with mock.patch.dict(os.environ, {}, clear=True):
        # Set specific variables
        os.environ["CLAUDE_SESSION_CONTEXT"] = "agent:modular-builder"

        # Test
        result = detect_agent_session()
        assert result is True
```

### Testing File Operations

```python
def test_audit_log_creation(self, tmp_path, monkeypatch):
    """Test with temporary directory."""
    monkeypatch.chdir(tmp_path)
    audit = DelegationAudit("test-session")

    audit.record_modification("file.py", "Edit", "main")

    assert audit.audit_file.exists()
```

### Testing Hook Behavior

```python
def test_hook_output(self, hook_script, sample_event):
    """Test hook with subprocess."""
    result = subprocess.run(
        [str(hook_script)],
        input=json.dumps(sample_event),
        capture_output=True,
        text=True,
        env={"MEMORY_SYSTEM_ENABLED": "true"}
    )

    assert result.returncode == 0
    output = json.loads(result.stdout)
    assert "warning" not in output
```

## Continuous Integration

These tests are designed to run in CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
- name: Run boundary validation tests
  run: |
    uv run pytest tests/orchestration/ tests/hooks/ -v --cov=amplifier.orchestration
```

## Performance Benchmarks

Current performance (as of 2025-11-02):

- **60 tests in ~2.16 seconds**
- **Average: 36ms per test**
- **Coverage computation adds ~1.4 seconds**

These are fast unit/integration tests suitable for TDD workflows.

## Troubleshooting

### "ModuleNotFoundError: No module named 'amplifier'"

Make sure you're in the project root and using `uv run`:

```bash
cd /workspaces/rzp-amplifier
uv run pytest tests/orchestration/ -v
```

### "Permission denied" errors

Tests create temporary directories. Ensure you have write permissions:

```bash
chmod +w tests/orchestration/
```

### "Import could not be resolved" in IDE

Make sure your IDE's Python interpreter points to `.venv/bin/python`.

### Tests pass locally but fail in CI

Check environment variables - CI may have different defaults:

```python
# Good: Explicit environment setup
with mock.patch.dict(os.environ, {"VAR": "value"}, clear=True):
    # test

# Bad: Assumes environment
os.getenv("VAR")  # May be different in CI
```

## Further Reading

- **README.md** - Comprehensive test documentation
- **TEST_SUMMARY.md** - Verification summary and results
- **CLAUDE.md** - Orchestrator boundary rules and philosophy
- **amplifier/orchestration/delegation_audit.py** - Implementation details
