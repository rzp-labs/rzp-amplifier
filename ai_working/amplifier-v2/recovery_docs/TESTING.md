# Content Models & Real-Time Display: Testing Strategy

**Test Plan Date**: 2025-10-12
**Test Scope**: Complete content models system
**Test Priority**: Use after MVP implementation is complete
**Status**: Reference document for future testing

---

## ⚠️ Note

This document describes **comprehensive testing** for the content models system.

**For immediate implementation** (Phase 1), use basic verification only:
- Import tests (ensure no errors)
- Manual provider tests (verify thinking blocks work)
- Event emission verification (check logs)

**Use this document** after MVP is working and you're ready to build comprehensive test coverage (Phase 6 in VISION.md).

---

---

## Testing Pyramid

```
         ┌─────────────┐
         │  Manual E2E │  10% - Full user scenarios
         └─────────────┘
       ┌───────────────────┐
       │   Integration     │  30% - Module interactions
       └───────────────────┘
     ┌───────────────────────┐
     │      Unit Tests       │  60% - Individual components
     └───────────────────────┘
```

---

## Unit Tests (60%)

### Test Suite 1: content_models.py

**File**: `amplifier-core/tests/test_content_models.py`

**Test Cases**:

```python
import pytest
from amplifier_core.content_models import (
    ContentBlockType,
    TextContent,
    ThinkingContent,
    ToolCallContent,
    ToolResultContent
)

def test_text_content_creation():
    """Test TextContent instantiation and serialization."""
    block = TextContent(text="Hello world")
    assert block.type == ContentBlockType.TEXT
    assert block.text == "Hello world"

    # Test serialization
    data = block.to_dict()
    assert data["type"] == "text"
    assert data["text"] == "Hello world"

def test_thinking_content_creation():
    """Test ThinkingContent instantiation and serialization."""
    block = ThinkingContent(text="Let me think about this...")
    assert block.type == ContentBlockType.THINKING
    assert block.text == "Let me think about this..."

    # Test serialization
    data = block.to_dict()
    assert data["type"] == "thinking"
    assert data["text"] == "Let me think about this..."

def test_tool_call_content_creation():
    """Test ToolCallContent instantiation and serialization."""
    block = ToolCallContent(
        id="call_123",
        name="search",
        arguments={"query": "test"}
    )
    assert block.type == ContentBlockType.TOOL_CALL
    assert block.id == "call_123"
    assert block.name == "search"
    assert block.arguments == {"query": "test"}

    # Test serialization
    data = block.to_dict()
    assert data["type"] == "tool_call"
    assert data["id"] == "call_123"
    assert data["name"] == "search"
    assert data["arguments"] == {"query": "test"}

def test_tool_result_content_creation():
    """Test ToolResultContent instantiation and serialization."""
    block = ToolResultContent(
        tool_call_id="call_123",
        output="Search results here",
        error=None
    )
    assert block.type == ContentBlockType.TOOL_RESULT
    assert block.tool_call_id == "call_123"
    assert block.output == "Search results here"
    assert block.error is None

def test_tool_result_with_error():
    """Test ToolResultContent with error."""
    block = ToolResultContent(
        tool_call_id="call_123",
        output=None,
        error="Connection timeout"
    )
    assert block.error == "Connection timeout"

    data = block.to_dict()
    assert data["error"] == "Connection timeout"

def test_raw_data_preservation():
    """Test that raw provider data is preserved."""
    raw = {"provider_specific": "data"}
    block = TextContent(text="test", raw=raw)
    assert block.raw == raw

    data = block.to_dict()
    assert data["raw"] == raw
```

**Run Tests**:

```bash
cd amplifier-core
pytest tests/test_content_models.py -v
```

### Test Suite 2: ProviderResponse Update

**File**: `amplifier-core/tests/test_models.py` (update existing)

**Test Cases**:

```python
def test_provider_response_content_blocks_field():
    """Test that ProviderResponse has content_blocks field."""
    from amplifier_core.models import ProviderResponse
    from amplifier_core.content_models import TextContent

    # Test with content_blocks
    response = ProviderResponse(
        content="Hello",
        content_blocks=[TextContent(text="Hello")]
    )
    assert response.content_blocks is not None
    assert len(response.content_blocks) == 1

def test_provider_response_backward_compatibility():
    """Test that old code still works without content_blocks."""
    from amplifier_core.models import ProviderResponse

    # Old style - no content_blocks
    response = ProviderResponse(content="Hello")
    assert response.content is not None
    assert response.content_blocks is None  # Defaults to None

def test_provider_response_both_fields():
    """Test that both old and new fields can coexist."""
    from amplifier_core.models import ProviderResponse
    from amplifier_core.content_models import TextContent

    response = ProviderResponse(
        content="Hello world",  # Old field
        content_blocks=[TextContent(text="Hello world")]  # New field
    )
    assert response.content == "Hello world"
    assert len(response.content_blocks) == 1
    assert response.content_blocks[0].text == "Hello world"
```

**Run Tests**:

```bash
cd amplifier-core
pytest tests/test_models.py::test_provider_response_content_blocks_field -v
pytest tests/test_models.py::test_provider_response_backward_compatibility -v
pytest tests/test_models.py::test_provider_response_both_fields -v
```

---

## Integration Tests (30%)

### Test Suite 3: Anthropic Provider with Extended Thinking

**File**: `amplifier-module-provider-anthropic/tests/test_extended_thinking.py`

**Test Cases**:

```python
import pytest
from amplifier_mod_provider_anthropic import AnthropicProvider
from amplifier_core.content_models import ThinkingContent, TextContent

@pytest.mark.asyncio
@pytest.mark.integration
async def test_anthropic_extended_thinking():
    """Test Anthropic provider with extended thinking enabled."""
    provider = AnthropicProvider(
        api_key=os.environ["ANTHROPIC_API_KEY"],
        config={"default_model": "claude-opus-4-20250514"}
    )

    messages = [{"role": "user", "content": "Explain how binary search works"}]

    response = await provider.complete(
        messages,
        extended_thinking=True  # Enable thinking blocks
    )

    # Verify content_blocks exist
    assert response.content_blocks is not None
    assert len(response.content_blocks) > 0

    # Find thinking blocks
    thinking_blocks = [b for b in response.content_blocks if isinstance(b, ThinkingContent)]
    assert len(thinking_blocks) > 0, "Should have at least one thinking block"

    # Verify thinking has content
    assert len(thinking_blocks[0].text) > 0

    # Verify backward compatibility
    assert response.content is not None
    assert len(response.content) > 0
```

**Run Tests**:

```bash
cd amplifier-module-provider-anthropic
pytest tests/test_extended_thinking.py -v -m integration
```

### Test Suite 4: OpenAI Provider with Reasoning

**File**: `amplifier-module-provider-openai/tests/test_reasoning.py`

**Test Cases**:

```python
import pytest
from amplifier_mod_provider_openai import OpenAIProvider
from amplifier_core.content_models import ThinkingContent, TextContent

@pytest.mark.asyncio
@pytest.mark.integration
async def test_openai_reasoning_blocks():
    """Test OpenAI provider extracts reasoning blocks from o1/o3 models."""
    provider = OpenAIProvider(
        api_key=os.environ["OPENAI_API_KEY"],
        config={"default_model": "o3-mini"}
    )

    messages = [{"role": "user", "content": "If x + 7 = 15, what is x?"}]

    response = await provider.complete(
        messages,
        reasoning="medium"  # Enable reasoning
    )

    # Verify content_blocks exist
    assert response.content_blocks is not None

    # Find reasoning blocks (as ThinkingContent)
    thinking_blocks = [b for b in response.content_blocks if isinstance(b, ThinkingContent)]

    # Note: May not have thinking blocks depending on model/query
    # But should have at least text blocks
    text_blocks = [b for b in response.content_blocks if isinstance(b, TextContent)]
    assert len(text_blocks) > 0
```

**Run Tests**:

```bash
cd amplifier-module-provider-openai
pytest tests/test_reasoning.py -v -m integration
```

### Test Suite 5: Loop Orchestrator Event Emission

**File**: `amplifier-module-loop-basic/tests/test_content_block_events.py`

**Test Cases**:

```python
import pytest
from unittest.mock import AsyncMock, MagicMock
from amplifier_mod_loop_basic import BasicOrchestrator
from amplifier_core.models import ProviderResponse
from amplifier_core.content_models import TextContent, ThinkingContent
from amplifier_core.events import CONTENT_BLOCK_START, CONTENT_BLOCK_END

@pytest.mark.asyncio
async def test_loop_emits_content_block_events():
    """Test that loop orchestrator emits content block events."""
    # Create mock components
    hooks = MagicMock()
    hooks.emit = AsyncMock()

    provider = MagicMock()
    provider.complete = AsyncMock(return_value=ProviderResponse(
        content="Hello world",
        content_blocks=[
            ThinkingContent(text="Let me think..."),
            TextContent(text="Hello world")
        ]
    ))

    context = MagicMock()
    context.add_message = AsyncMock()
    context.messages = []

    orchestrator = BasicOrchestrator(config={})

    # Execute
    await orchestrator.execute(
        prompt="Test",
        context=context,
        providers={"test": provider},
        tools={},
        hooks=hooks
    )

    # Verify events were emitted
    emit_calls = hooks.emit.call_args_list

    # Should have start and end events for each block
    start_events = [c for c in emit_calls if c[0][0] == CONTENT_BLOCK_START]
    end_events = [c for c in emit_calls if c[0][0] == CONTENT_BLOCK_END]

    assert len(start_events) == 2  # One for thinking, one for text
    assert len(end_events) == 2

    # Verify event data
    first_start = start_events[0][0][1]["data"]
    assert first_start["block_type"] == "thinking"
    assert first_start["block_index"] == 0

    second_start = start_events[1][0][1]["data"]
    assert second_start["block_type"] == "text"
    assert second_start["block_index"] == 1
```

**Run Tests**:

```bash
cd amplifier-module-loop-basic
pytest tests/test_content_block_events.py -v
```

---

## Manual End-to-End Tests (10%)

### E2E Test 1: Anthropic Extended Thinking

**Setup**:

```toml
# test_configs/anthropic_thinking.toml
[provider]
name = "anthropic"
api_key = "${ANTHROPIC_API_KEY}"
default_model = "claude-opus-4-20250514"

[provider.config]
extended_thinking = true
max_tokens = 4096

[loop]
name = "basic"
default_provider = "anthropic"
```

**Test Steps**:

1. Start CLI: `amplifier run --config test_configs/anthropic_thinking.toml --mode chat`
2. Enter prompt: "Explain the difference between quicksort and mergesort"
3. **Expected**: See thinking block displayed before response
4. **Verify**: Thinking text is complete (not truncated)
5. **Verify**: Response text appears after thinking

**Success Criteria**:

- Thinking block appears in display
- Thinking is complete
- Response follows thinking
- No errors in logs

### E2E Test 2: OpenAI Reasoning

**Setup**:

```toml
# test_configs/openai_reasoning.toml
[provider]
name = "openai"
api_key = "${OPENAI_API_KEY}"
default_model = "o3-mini"

[provider.config]
reasoning = "medium"
max_output_tokens = 4096

[loop]
name = "basic"
default_provider = "openai"
```

**Test Steps**:

1. Start CLI: `amplifier run --config test_configs/openai_reasoning.toml --mode chat`
2. Enter prompt: "Solve: 2x + 5 = 17"
3. **Expected**: See reasoning block (if model provides one)
4. **Expected**: See final answer
5. **Verify**: Both backward compatible fields and content_blocks populated

**Success Criteria**:

- Model reasoning visible (if provided)
- Final answer clear
- No errors in logs

### E2E Test 3: Tool Calls with Content Blocks

**Test Steps**:

1. Start CLI with tool-enabled config
2. Enter prompt that requires tool use: "What's the weather in Paris?"
3. **Expected**: See tool call block displayed
4. **Expected**: See tool execution (existing behavior)
5. **Expected**: See tool result content block
6. **Expected**: See final response

**Success Criteria**:

- Tool call appears as content block
- Tool execution completes
- Tool result appears
- Final response incorporates tool result

### E2E Test 4: Backward Compatibility

**Test Steps**:

1. Use old-style config (no content_blocks features)
2. Run existing test cases
3. **Expected**: All existing tests pass
4. **Expected**: No new warnings or errors
5. **Verify**: Old code paths still work

**Success Criteria**:

- All existing tests pass
- No regression in functionality
- No performance degradation

---

## Performance Tests

### Test: Content Block Processing Overhead

**Measure**:

- Response time with content_blocks vs. without
- Memory usage with content_blocks
- Event emission overhead

**Acceptance Criteria**:

- < 5ms overhead for content block processing
- < 1MB additional memory per response
- < 1ms overhead for event emission

**Test Code**:

```python
import time
from amplifier_core.models import ProviderResponse
from amplifier_core.content_models import TextContent

# Benchmark without content_blocks
start = time.perf_counter()
for _ in range(1000):
    response = ProviderResponse(content="Test")
without_blocks = time.perf_counter() - start

# Benchmark with content_blocks
start = time.perf_counter()
for _ in range(1000):
    response = ProviderResponse(
        content="Test",
        content_blocks=[TextContent(text="Test")]
    )
with_blocks = time.perf_counter() - start

overhead_ms = (with_blocks - without_blocks) * 1000 / 1000
print(f"Average overhead: {overhead_ms:.2f}ms")
assert overhead_ms < 5, f"Overhead too high: {overhead_ms}ms"
```

---

## Test Execution Order

Run tests in this order:

1. **Unit tests** - Fast, no dependencies

   ```bash
   make test-unit
   ```

2. **Integration tests** - Requires API keys

   ```bash
   make test-integration
   ```

3. **Manual E2E** - Human verification

   ```bash
   make test-e2e
   ```

4. **Performance tests** - After functionality verified
   ```bash
   make test-performance
   ```

---

## CI/CD Integration

### GitHub Actions Workflow

```yaml
name: Content Models Tests

on: [push, pull_request]

jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run unit tests
        run: |
          cd amplifier-core
          pytest tests/test_content_models.py -v

  integration-tests:
    runs-on: ubuntu-latest
    needs: unit-tests
    steps:
      - uses: actions/checkout@v3
      - name: Run integration tests
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        run: |
          pytest -v -m integration
```

---

## Regression Test Suite

Ensure these existing tests still pass:

- [ ] All provider tests (existing)
- [ ] All loop orchestrator tests (existing)
- [ ] All CLI tests (existing)
- [ ] All tool tests (existing)
- [ ] Performance benchmarks (existing)

---

## Test Coverage Goals

- **content_models.py**: 100% (simple dataclasses)
- **Provider updates**: 90%+ (mock API responses)
- **Loop orchestrator**: 85%+ (event emission)
- **CLI display**: 70%+ (UI layer, harder to test)

**Overall Target**: 85%+ code coverage

---

## Success Metrics

- All unit tests pass
- All integration tests pass (with API keys)
- Manual E2E tests verify user experience
- No performance regression
- Backward compatibility maintained
- Coverage goals met
