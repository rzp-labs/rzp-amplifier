# Test Coverage

Test coverage reporting is integrated into the standard test workflow.

## Running Tests with Coverage

```bash
make test
```

This automatically:
- Runs all tests in the parent workspace
- Collects coverage data for `amplifier/` and `.claude/tools/`
- Shows coverage report in terminal with missing line numbers
- Generates HTML report in `htmlcov/`
- Fails if coverage drops below 4%

## Understanding Coverage Output

### Terminal Report

```
Name                                    Stmts   Miss  Cover   Missing
---------------------------------------------------------------------
amplifier/extraction/core.py              163     87    47%   23-24, 75-78, 131
amplifier/memory/core.py                  138     40    71%   28-30, 89-97
---------------------------------------------------------------------
TOTAL                                     6792   6482     5%
```

- **Stmts**: Total executable statements
- **Miss**: Statements not covered by tests
- **Cover**: Percentage covered
- **Missing**: Line numbers not covered

### HTML Report

Open `htmlcov/index.html` in a browser for:
- Interactive visualization
- Line-by-line coverage highlighting
- Sortable tables by coverage %
- Jump to specific uncovered sections

## Coverage Configuration

Configuration in `pyproject.toml`:

```toml
[tool.coverage.run]
source = ["amplifier", ".claude/tools"]
omit = [
    "*/tests/*",
    "*/__pycache__/*",
    "*/.venv/*",
    "*/smoke_tests.py",
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "if __name__ == .__main__.:",
    "if TYPE_CHECKING:",
    "@abstractmethod",
]
show_missing = true
fail_under = 4  # Increase as coverage improves
```

## Improving Coverage

### Identify Gaps

**Terminal report shows missing lines**:
```
amplifier/extraction/core.py    47%   23-24, 75-78, 131, 148-214
```

Lines 148-214 are completely uncovered - priority for new tests.

**HTML report provides detail**:
- Click on file name to see exact uncovered code
- Red highlighting shows uncovered lines
- Green shows covered lines

### Strategic Testing

Focus on:

1. **Core modules** (extraction, memory, validation):
   - Target 70%+ coverage
   - These are the foundation

2. **Integration modules** (knowledge_synthesis, content_loader):
   - Target 50%+ coverage
   - Often harder to test, integration tests help

3. **CLI and utilities**:
   - Target 30%+ coverage
   - Often needs subprocess/filesystem mocking

### Increasing the Threshold

As coverage improves:

1. Update `fail_under` in `pyproject.toml`
2. Run `make test` to verify it passes
3. Commit the new threshold

**Goal**: Incrementally increase to 70% overall.

## Coverage Best Practices

### What to Test

✅ **High value**:
- Business logic and algorithms
- Error handling paths
- Edge cases and boundary conditions
- Integration between modules

❌ **Low value**:
- Simple getters/setters
- Framework boilerplate
- Generated code
- Trivial one-liners

### Using Coverage Pragmas

Mark lines that don't need coverage:

```python
def __repr__(self) -> str:  # pragma: no cover
    return f"Memory({self.id})"

if TYPE_CHECKING:  # pragma: no cover
    from typing import Protocol
```

These are automatically excluded via `exclude_lines` config.

## Troubleshooting

### Coverage Report Missing Files

**Problem**: File shows 0% coverage but has tests.

**Solution**: Check `[tool.coverage.run]` source paths include the module.

### Tests Pass but Coverage Fails

**Problem**: `FAIL Required test coverage of 4.0% not reached. Total coverage: 3.8%`

**Solution**: Either:
- Add more tests to reach threshold
- Lower threshold temporarily (with plan to increase)

### HTML Report Not Generated

**Problem**: No `htmlcov/` directory.

**Solution**: Ensure `--cov-report=html` flag in Makefile test target.

## Pure Delegation Architecture

Coverage works with the Pure Delegation model:

- **`make test`**: Parent workspace coverage only
- **`make test-all`**: Parent + all submodules (each shows own coverage)

Each project maintains own coverage thresholds in its `pyproject.toml`.
