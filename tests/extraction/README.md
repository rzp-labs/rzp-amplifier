# Memory Extraction Test Suite

Comprehensive test coverage for the memory extraction system to catch issues before commit.

## Test Coverage Summary

### ✅ 51 Total Tests (All Passing)

**Test Breakdown:**
- **Unit Tests**: 30 tests covering core extraction functionality
- **Integration Tests**: 13 tests covering end-to-end flows
- **Configuration Tests**: 8 tests covering environment variables and settings

## Coverage Areas

### 1. Exception Handling (`test_core.py`)
Tests that exceptions are properly propagated, not swallowed:

- ✅ `TimeoutError` propagates from extraction
- ✅ `JSONDecodeError` propagates from parsing
- ✅ General exceptions propagate with context
- ✅ Errors have informative messages

**What this prevents:**
- Silent failures where extraction fails but no error is raised
- Exceptions being caught and ignored without logging
- Generic error messages that don't help debugging

### 2. Status Reporting (`test_status.py`)
Tests metadata structure and status tracking:

- ✅ Success metadata includes all required fields
- ✅ Timeout errors have clear messages
- ✅ JSON decode errors are descriptive
- ✅ Metadata includes extraction method and timestamp
- ✅ Memory counts are accurate

**What this prevents:**
- Missing status information after extraction
- Unclear error messages
- Lost metadata about extraction source

### 3. Configuration (`test_config.py`)
Tests environment variable configuration:

- ✅ Default values are correct
- ✅ `MEMORY_SYSTEM_ENABLED` flag works
- ✅ `MEMORY_EXTRACTION_TIMEOUT` is configurable
- ✅ `MEMORY_EXTRACTION_MODEL` is configurable
- ✅ Storage directory is configurable
- ✅ Singleton pattern works correctly

**What this prevents:**
- Configuration not being respected
- Environment variables not overriding defaults
- Multiple config instances causing conflicts

### 4. Message Formatting (`test_core.py`)
Tests conversation processing:

- ✅ System messages are filtered out
- ✅ Hook messages are excluded
- ✅ Max messages limit is respected
- ✅ Content truncation works
- ✅ Real conversation content is preserved

**What this prevents:**
- System/hook noise contaminating extractions
- Timeouts from processing too many messages
- Memory leaks from unbounded content

### 5. End-to-End Flow (`test_memory_extraction.py`)
Tests complete extraction pipeline:

- ✅ Transcript → extraction → storage works
- ✅ Failed extraction preserves transcript
- ✅ Multiple sessions don't interfere
- ✅ Memories persist across restarts
- ✅ Structured data is preserved

**What this prevents:**
- Data loss on extraction failure
- Cross-session contamination
- Missing key_learnings/decisions/issues

### 6. Error Recovery (`test_memory_extraction.py`)
Tests resilience to failures:

- ✅ Timeout doesn't corrupt existing storage
- ✅ JSON errors don't corrupt storage
- ✅ Partial failures are handled gracefully

**What this prevents:**
- Storage corruption on errors
- Loss of existing memories
- Cascading failures

## Running Tests

### Quick Run (All Extraction Tests)
```bash
uv run pytest tests/extraction/ tests/integration/test_memory_extraction.py -v
```

### With Coverage Report
```bash
uv run pytest tests/extraction/ tests/integration/test_memory_extraction.py --cov=amplifier.extraction --cov=amplifier.memory --cov-report=term-missing
```

### Using Test Runner Script
```bash
./tools/test_memory_extraction.sh
```

### Run Specific Test Category
```bash
# Unit tests only
uv run pytest tests/extraction/test_core.py -v

# Configuration tests only
uv run pytest tests/extraction/test_config.py -v

# Integration tests only
uv run pytest tests/integration/test_memory_extraction.py -v
```

## Test Fixtures

Located in `tests/fixtures/transcripts/`:

- **valid_session.jsonl**: Normal conversation with learnings and decisions
- **large_session.jsonl**: 20+ messages to test pagination
- **empty_session.jsonl**: Empty file edge case
- **corrupted_session.jsonl**: Malformed JSON to test error handling
- **system_messages_session.jsonl**: Mix of real and system messages

## Regression Tests

These tests specifically prevent the issues we just fixed:

### Silent Exception Swallowing
**Issue**: Exceptions were caught and logged but not re-raised
**Tests**:
- `test_extract_timeout_propagates`
- `test_extract_json_decode_error_propagates`
- `test_extract_general_exception_propagates`

### Missing Status Reporting
**Issue**: No visibility into extraction success/failure
**Tests**:
- `test_success_metadata_structure`
- `test_timeout_error_has_clear_message`
- `test_extraction_error_messages_are_informative`

### Timeout Misconfigurations
**Issue**: Hook timeout didn't account for extraction timeout
**Tests**:
- `test_env_override_timeout`
- `test_extractor_uses_config_timeout`

## Pre-Commit Integration

Add to `.claude/hooks/pre-commit`:
```bash
# Run extraction tests before allowing commit
pytest tests/extraction/ tests/integration/test_memory_extraction.py -v
if [ $? -ne 0 ]; then
    echo "❌ Memory extraction tests failed - fix before commit"
    exit 1
fi
```

## Success Criteria

All tests must pass before committing changes to:
- `amplifier/extraction/`
- `amplifier/memory/`
- `.claude/hooks/*` (if they interact with extraction)

## What These Tests Catch

✅ **Before Commit:**
- Broken exception handling
- Missing error logging
- Configuration not respected
- Silent failures
- Timeouts not propagating
- Missing metadata

❌ **Without These Tests:**
- Silent extraction failures in production
- Users experiencing timeouts with no visibility
- Configuration changes having no effect
- Data loss on errors
- Debugging nightmares from generic errors

## Test Maintenance

When adding new features to extraction:

1. **Add unit tests** for new functions/methods
2. **Add integration tests** for new workflows
3. **Update fixtures** if new message formats needed
4. **Run full suite** to ensure no regressions
5. **Update this README** with new coverage areas

## Performance

Test suite runs in **< 1 second** for fast feedback:
```
51 passed in 0.18s
```

Fast tests encourage:
- Running tests frequently
- Running before every commit
- Quick iteration cycles
