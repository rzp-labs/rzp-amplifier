# Content Models System: Long-Term Vision

**Document Date**: 2025-10-12
**Type**: Future Guidance
**Purpose**: Guide future developers on when and how to enhance the content models system

---

## Philosophy

This document describes the **complete vision** for the content models system. The immediate implementation (see `04_IMPLEMENTATION_PLAN.md`) focuses on **ruthless simplicity** - building only what's needed NOW.

**When to build these features:**
- When there's proven user need (not hypothetical)
- When current implementation becomes a bottleneck
- When at least 2 independent use cases converge on the need

**How to decide:**
- Follow the kernel philosophy (mechanism vs. policy)
- Measure before optimizing
- Preserve the small, stable kernel

---

## Phase 1: Minimum Viable ✅ (Current Implementation)

**Goal**: Fix import errors, enable basic thinking display

**What's included:**
- Content models (TextContent, ThinkingContent, ToolCallContent, ToolResultContent)
- ProviderResponse.content_blocks field
- Basic event types (CONTENT_BLOCK_START, CONTENT_BLOCK_END)
- Anthropic extended_thinking support
- OpenAI reasoning support
- Loop orchestrator event emission

**Success criteria:**
- No import errors
- Thinking/reasoning blocks accessible in logs
- Events emitted when blocks exist

---

## Phase 2: User Experience 🎯 (Next Priority)

**When to build**: After Phase 1 is validated and users need visual display

### CLI Display Layer

**Location**: `amplifier-app-cli/amplifier_cli/display.py` (NOT in kernel)

**Purpose**: Render content blocks for user display (policy decision)

**Features:**
- Display thinking blocks in visual panels
- Format text blocks cleanly
- Show tool calls with context
- Display tool results

**Implementation:**
```python
from rich.console import Console
from rich.panel import Panel

class ContentBlockRenderer:
    """Renders content blocks for CLI display."""

    def render_thinking(self, block: ThinkingContent):
        """Display thinking block without truncation."""
        console.print(Panel(
            block.text,
            title="🤔 Thinking",
            border_style="dim",
            expand=False
        ))

    def render_text(self, block: TextContent):
        """Display text block."""
        console.print(block.text)

    def render_tool_call(self, block: ToolCallContent):
        """Display tool call with argument preview."""
        args_preview = str(block.arguments)[:200]
        console.print(f"🔧 Calling {block.name}({args_preview}...)")
```

**Hook Integration:**
```python
# In CLI startup
from amplifier_core.events import CONTENT_BLOCK_END

@hooks.on(CONTENT_BLOCK_END)
async def handle_content_block(event_data):
    block_dict = event_data["data"]["block"]
    block_type = block_dict["type"]

    if block_type == "thinking":
        renderer.render_thinking(ThinkingContent(**block_dict))
    elif block_type == "text":
        renderer.render_text(TextContent(**block_dict))
    # ... etc
```

**Why later**: Need to validate that events work before building display layer. Display is pure policy - can iterate rapidly without touching kernel.

---

## Phase 3: Streaming Support 🌊 (Future Enhancement)

**When to build**: When providers start returning streaming responses and users want progressive display

### Streaming Delta Events

**Changes needed:**
1. Providers emit deltas as they arrive
2. Loop orchestrator forwards delta events
3. Display layer accumulates and renders progressively

**Provider changes:**
```python
async for chunk in stream:
    if chunk.content_blocks_delta:
        # Emit delta event
        await hooks.emit(CONTENT_BLOCK_DELTA, {
            "data": {
                "block_index": chunk.index,
                "delta": chunk.delta_text,
                "partial_json": chunk.partial_json
            }
        })
```

**Loop orchestrator changes:**
```python
# Forward streaming events from provider
async for event in provider.stream(messages):
    if event["type"] == "content_block_delta":
        await hooks.emit(CONTENT_BLOCK_DELTA, event["data"])
```

**Display layer changes:**
```python
@hooks.on(CONTENT_BLOCK_DELTA)
async def handle_delta(event_data):
    # Accumulate and display progressively
    delta = event_data["data"]["delta"]
    console.print(delta, end="", flush=True)
```

**Why later**: Streaming adds complexity. Need to validate basic implementation works first. Most models don't stream thinking blocks yet.

---

## Phase 4: Full Provider Parity 🔄 (As Needed)

**When to build**: When Azure/Ollama get reasoning/thinking support in their models

### Azure OpenAI Reasoning Support

Currently Azure OpenAI already builds content_blocks for text and tools. When gpt-5 series with reasoning is available on Azure:

**Changes needed:**
- Same as OpenAI provider
- Extract reasoning blocks from response.output
- Build ThinkingContent for reasoning blocks

### Ollama Reasoning Support

Currently Ollama already builds content_blocks for text and tools. When underlying models support reasoning:

**Changes needed:**
- Depends on model's OpenAI compatibility
- May work automatically if model follows OpenAI format
- May need custom extraction logic

**Why later**: Don't build for models that don't exist yet. Wait for proven need.

---

## Phase 5: Advanced Content Types 🚀 (Future Vision)

**When to build**: When use cases emerge requiring these types

### Image Content Blocks

**Use case**: Models that return images (DALL-E, image generation)

**Implementation:**
```python
class ContentBlockType(str, Enum):
    # ... existing types ...
    IMAGE = "image"

@dataclass
class ImageContent(ContentBlock):
    type: ContentBlockType = ContentBlockType.IMAGE
    url: str = ""
    alt_text: str = ""
    dimensions: dict[str, int] | None = None
```

### Audio Content Blocks

**Use case**: Models that return audio (TTS, audio generation)

**Implementation:**
```python
class ContentBlockType(str, Enum):
    # ... existing types ...
    AUDIO = "audio"

@dataclass
class AudioContent(ContentBlock):
    type: ContentBlockType = ContentBlockType.AUDIO
    url: str = ""
    duration: float = 0.0
    transcript: str | None = None
```

### Video Content Blocks

**Use case**: Models that return video

**Implementation:**
```python
class ContentBlockType(str, Enum):
    # ... existing types ...
    VIDEO = "video"

@dataclass
class VideoContent(ContentBlock):
    type: ContentBlockType = ContentBlockType.VIDEO
    url: str = ""
    duration: float = 0.0
    thumbnail: str | None = None
```

**Why later**: No immediate need. Current models don't return these types. Follow "rough consensus & running code—then abstraction" principle.

---

## Phase 6: Performance Optimization ⚡ (If Needed)

**When to build**: When performance becomes a bottleneck (measure first!)

### Potential Optimizations

1. **Event Batching**
   - Batch multiple CONTENT_BLOCK_END events
   - Reduce event emission overhead
   - Only if profiling shows event emission is slow

2. **Content Block Pooling**
   - Reuse content block instances
   - Reduce allocation overhead
   - Only if profiling shows allocation is slow

3. **Lazy Serialization**
   - Only serialize blocks when needed
   - Skip serialization for blocks not displayed
   - Only if profiling shows serialization is slow

4. **Selective Event Emission**
   - Allow display layer to subscribe to specific block types
   - Skip emitting events for unwanted types
   - Only if profiling shows excess events

**Why later**: "Measure before tuning" - avoid speculative complexity. Current implementation is simple and predictable. Optimize only if proven bottleneck.

---

## Phase 7: Testing Infrastructure 🧪 (As System Matures)

**When to build**: After core implementation is stable and being used

See `TESTING.md` for complete testing strategy. Build tests incrementally:

1. **Unit tests** (Phase 1): content_models.py serialization
2. **Provider integration tests** (Phase 2): Real API calls with thinking enabled
3. **Event emission tests** (Phase 3): Verify orchestrator emits correct events
4. **Display tests** (Phase 4): Verify rendering works correctly
5. **E2E tests** (Phase 5): Complete user scenarios

**Why later**: Following "working code first, then tests" philosophy. Build minimal tests alongside implementation, comprehensive tests after system proves itself.

---

## Decision Framework

### When to Add a Feature

Ask these questions:

1. **Necessity**: "Do we actually need this right now?" (Not hypothetical)
2. **Evidence**: "Do we have ≥2 independent use cases that need it?"
3. **Kernel impact**: "Does this change the kernel or just the edges?"
4. **Complexity budget**: "What complexity are we retiring to afford this?"
5. **Measurement**: "Have we measured that current approach is insufficient?"

If any answer is "no", wait until circumstances change.

### Kernel vs. Edge Decision

- **Kernel** (mechanism): Data structures, event types, stable contracts
- **Edge** (policy): Provider extraction, display rendering, formatting

Default to edge. Only add to kernel if:
- Multiple modules need the capability
- It's truly a mechanism (not a policy)
- It maintains invariants (backward compatibility, non-interference)

### Backward Compatibility

Since this is a new system, we're not constrained by backward compatibility YET. However, once this ships:

- **Kernel changes**: Must maintain backward compatibility
- **Edge changes**: Can evolve rapidly without touching kernel
- **Deprecation**: Follow kernel philosophy deprecation discipline

---

## Anti-Patterns to Avoid

1. **Building for hypothetical futures**
   - "We might need X someday" → Wait until you do

2. **Optimizing before measuring**
   - "This might be slow" → Measure first

3. **Adding flags to kernel**
   - "Add a flag to enable Y" → Make it a module instead

4. **Breaking kernel contracts**
   - "Let's change the event format" → Add new event type instead

5. **Mixing mechanism and policy**
   - "Display logic in loop orchestrator" → Keep display in app layer

---

## Success Metrics

### Phase 1 Success
- Import errors fixed
- Thinking blocks accessible
- Events emitted

### Phase 2 Success
- Users can see thinking blocks
- Display is clear and useful
- No complaints about missing info

### Phase 3 Success
- Streaming feels responsive
- No perceived lag in display
- Users prefer streaming over batch

### Phase 4+ Success
- Each phase solves a real user problem
- Kernel remains small and stable
- Features can be added without touching kernel

---

## Conclusion

This vision document provides guidance for future development. The key principle: **build what's needed NOW, not what might be needed SOMEDAY**.

Follow the kernel philosophy:
- Small, stable center
- Explosive innovation at edges
- Measure before optimizing
- Preserve simplicity

When in doubt, reference:
- `@amplifier-dev/docs/KERNEL_PHILOSOPHY.md`
- `@ai_context/IMPLEMENTATION_PHILOSOPHY.md`
- `@ai_context/MODULAR_DESIGN_PHILOSOPHY.md`
