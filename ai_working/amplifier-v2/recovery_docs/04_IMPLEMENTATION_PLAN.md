# Implementation Plan: Immediate Needs Only

**Plan Date**: 2025-10-12
**Estimated Effort**: 2-3 hours for minimum viable implementation
**Priority**: **CRITICAL** - Two providers are broken (import errors)
**Supported Models**: OpenAI gpt-5 series, Anthropic 4 series, Azure OpenAI gpt-5 series, Ollama OpenAI-compatible

---

## Implementation Strategy

**Ruthless Simplicity**: Build only what's needed NOW. The VISION.md document describes future enhancements.

**Immediate Goal**: Fix import errors and enable basic thinking/reasoning display.

---

## Critical Path (What We Need NOW)

1. **content_models.py** ⚡ Fixes import errors immediately
2. **models.py update** - Enables providers to use content_blocks
3. **events.py update** - Add event types for orchestrator
4. **Anthropic provider** - Basic extended_thinking support
5. **OpenAI provider** - Basic reasoning block extraction
6. **Loop orchestrator** - Simple event emission

**NOT included in immediate implementation**:
- Advanced streaming (VISION.md)
- CLI display layer (can be added after core works)
- Full test suite (start with basic verification)
- Azure/Ollama reasoning support (they already build basic content_blocks)

---

## Step 1: Create content_models.py ⚡ CRITICAL

**File**: `amplifier-core/amplifier_core/content_models.py`

**Why First**: Azure OpenAI and Ollama providers have import errors until this exists.

**Estimated Time**: 15 minutes

### Implementation

```bash
cd /workspaces/amplifier/amplifier-dev/amplifier-core
```

Create the file with content from `03_ARCHITECTURE_DESIGN.md` Section "Module 1: Content Models".

### Verification

```bash
# Test imports work
cd /workspaces/amplifier/amplifier-dev
python3 -c "from amplifier_core.content_models import TextContent, ThinkingContent, ToolCallContent, ToolResultContent; print('✓ Imports successful')"

# Test Azure OpenAI provider imports
python3 -c "import amplifier_mod_provider_azure_openai; print('✓ Azure OpenAI provider imports')"

# Test Ollama provider imports
python3 -c "import amplifier_mod_provider_ollama; print('✓ Ollama provider imports')"
```

### Git Workflow

```bash
cd amplifier-core
git add amplifier_core/content_models.py
git commit -m "feat: add content models for unified content handling

Add ContentBlock types (TextContent, ThinkingContent, ToolCallContent,
ToolResultContent) to support structured content from providers.

Fixes import errors in Azure OpenAI and Ollama providers that
were already trying to use these models."
git push origin main
```

---

## Step 2: Update ProviderResponse

**File**: `amplifier-core/amplifier_core/models.py`

**Estimated Time**: 10 minutes

### Implementation

Add `content_blocks` field to `ProviderResponse` class:

```python
content_blocks: list[Any] | None = Field(
    default=None,
    description="Structured content blocks (TextContent, ThinkingContent, ToolCallContent, etc.)"
)
```

See `03_ARCHITECTURE_DESIGN.md` Section "Module 2: Provider Response Update" for complete code.

### Verification

```bash
python3 -c "from amplifier_core.models import ProviderResponse; r = ProviderResponse(content='test'); print('content_blocks' in r.model_fields); print('✓ ProviderResponse updated')"
```

### Git Workflow

```bash
cd amplifier-core
git add amplifier_core/models.py
git commit -m "feat: add content_blocks field to ProviderResponse

Add optional content_blocks field to ProviderResponse to support
structured content from providers."
git push origin main
```

---

## Step 3: Add Event Types

**File**: `amplifier-core/amplifier_core/events.py`

**Estimated Time**: 5 minutes

### Implementation

Add event constants:

```python
# Content Block Events
CONTENT_BLOCK_START = "content_block:start"
CONTENT_BLOCK_DELTA = "content_block:delta"  # For future streaming support
CONTENT_BLOCK_END = "content_block:end"
```

### Git Workflow

```bash
cd amplifier-core
git add amplifier_core/events.py
git commit -m "feat: add content block event constants

Add CONTENT_BLOCK_START, CONTENT_BLOCK_DELTA, and CONTENT_BLOCK_END
event constants for content block lifecycle events."
git push origin main
```

---

## Step 4: Update Anthropic Provider (Minimal)

**File**: `amplifier-module-provider-anthropic/amplifier_mod_provider_anthropic/__init__.py`

**Estimated Time**: 20 minutes

### Implementation

1. **Add import**:
```python
from amplifier_core.content_models import TextContent, ThinkingContent, ToolCallContent
```

2. **Add extended_thinking parameter support** (in `complete` method)
3. **Parse thinking blocks** from response.content (see 03_ARCHITECTURE_DESIGN.md)

### Test Configuration

Create test config:

```toml
# test_extended_thinking.toml
[provider]
name = "anthropic"
api_key = "${ANTHROPIC_API_KEY}"
default_model = "claude-4-opus"

[provider.config]
extended_thinking = true
max_tokens = 4096
```

### Manual Test

```bash
amplifier run --config test_extended_thinking.toml --mode chat
# Ask: "Explain how quicksort works"
```

### Git Workflow

```bash
cd amplifier-module-provider-anthropic
git add amplifier_mod_provider_anthropic/__init__.py
git commit -m "feat: add basic extended thinking support

Add extended_thinking parameter support and parse thinking blocks
from Anthropic responses. Build content_blocks with ThinkingContent,
TextContent, and ToolCallContent types."
git push origin main
```

---

## Step 5: Update OpenAI Provider (Minimal)

**File**: `amplifier-module-provider-openai/amplifier_mod_provider_openai/__init__.py`

**Estimated Time**: 20 minutes

### Implementation

1. **Add import**:
```python
from amplifier_core.content_models import TextContent, ThinkingContent, ToolCallContent
```

2. **Add reasoning parameter support** (see 03_ARCHITECTURE_DESIGN.md)
3. **Extract reasoning blocks** from response.output

### Test Configuration

```toml
# test_reasoning.toml
[provider]
name = "openai"
api_key = "${OPENAI_API_KEY}"
default_model = "gpt-5"

[provider.config]
reasoning = "medium"
max_output_tokens = 4096
```

### Git Workflow

```bash
cd amplifier-module-provider-openai
git add amplifier_mod_provider_openai/__init__.py
git commit -m "feat: add basic reasoning block support for gpt-5 series

Add reasoning parameter support and extract reasoning blocks from
OpenAI Responses API output. Build content_blocks with ThinkingContent,
TextContent, and ToolCallContent types."
git push origin main
```

---

## Step 6: Update Loop Orchestrator

**File**: `amplifier-module-loop-basic/amplifier_mod_loop_basic/__init__.py`

**Estimated Time**: 15 minutes

### Implementation

1. **Import event constants**:
```python
from amplifier_core.events import CONTENT_BLOCK_START, CONTENT_BLOCK_END
```

2. **Add content block event emission** (see 03_ARCHITECTURE_DESIGN.md for code)

### Verification

Check event logs after provider calls to verify events are emitted.

### Git Workflow

```bash
cd amplifier-module-loop-basic
git add amplifier_mod_loop_basic/__init__.py
git commit -m "feat: emit content block events for real-time display

Emit CONTENT_BLOCK_START and CONTENT_BLOCK_END events when providers
return content_blocks. Enables real-time display of thinking, text,
and tool call blocks as they occur."
git push origin main
```

---

## Step 7: Update Parent Repository

After all submodules are updated and pushed:

```bash
cd /workspaces/amplifier/amplifier-dev

# Update submodule references
git add amplifier-core
git add amplifier-module-provider-anthropic
git add amplifier-module-provider-openai
git add amplifier-module-loop-basic

git commit -m "feat: add content models and basic real-time display

Minimal implementation of content models for unified content handling:

- Content models: TextContent, ThinkingContent, ToolCallContent, ToolResultContent
- Provider updates: Extract thinking/reasoning blocks from responses
- Loop orchestrator: Emit content block events
- Event types: CONTENT_BLOCK_START, CONTENT_BLOCK_END

Fixes import errors in Azure OpenAI and Ollama providers.
Enables basic real-time display of model thinking and tool execution."

git push origin main
```

---

## Verification Checklist (Minimum Viable)

After all steps complete:

- [ ] No import errors in any provider
- [ ] Anthropic provider supports extended_thinking parameter
- [ ] OpenAI provider extracts reasoning blocks
- [ ] Azure OpenAI provider still works (already has content_blocks code)
- [ ] Ollama provider still works (already has content_blocks code)
- [ ] Loop orchestrator emits content block events
- [ ] Events appear in logs when using thinking-enabled models

---

## What's NOT in This Implementation

See `VISION.md` for future enhancements:
- CLI display layer (renderer for thinking blocks)
- Advanced streaming with CONTENT_BLOCK_DELTA events
- Full test suite
- Azure/Ollama reasoning support
- Tool result content blocks
- Performance optimization

**Why not included**: Following ruthless simplicity - build minimal working version first, validate it works, then enhance.

---

## Success Criteria

**Immediate Success** (This Implementation):
- ✅ Import errors fixed
- ✅ Content blocks populated by providers
- ✅ Events emitted by orchestrator
- ✅ Thinking/reasoning blocks accessible in logs

**Future Success** (See VISION.md):
- Real-time CLI display rendering
- Streaming support
- Full provider parity
- Comprehensive test coverage
