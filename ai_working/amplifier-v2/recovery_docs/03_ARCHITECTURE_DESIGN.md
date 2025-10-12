# Architecture Design: Content Models & Real-Time Display

**Design Date**: 2025-10-12
**Architect**: zen-architect
**Philosophy**: Mechanism not policy, ruthless simplicity
**Supported Models**: OpenAI gpt-5 series, Anthropic 4 series, Azure OpenAI gpt-5 series, Ollama OpenAI-compatible

---

## Design Principles

### Kernel Philosophy Alignment

1. **Mechanism, not policy** - Content models are pure data structures (mechanism). Display decisions live in application layer (policy).
2. **Small, stable kernel** - Minimal changes to core: one new module, one field addition, three event types.
3. **Separation of concerns** - Clear boundaries between kernel (models/events) and edges (providers/display).
4. **Extensibility through composition** - New content block types can be added without changing existing code.
5. **Text-first, inspectable** - All content blocks are dataclasses with clear structure.

---

## Module 1: Content Models (amplifier-core)

**File**: `amplifier-core/amplifier_core/content_models.py`

### Purpose
Define standardized content block types for unified content handling across all providers.

### Contract
- **Inputs**: None (pure data structures)
- **Outputs**: ContentBlock types for use by providers and consumers
- **Side Effects**: None
- **Dependencies**: Only Python standard library (dataclasses, enum)

### Implementation

```python
"""Content models for unified content handling across providers."""

from dataclasses import dataclass
from typing import Any
from enum import Enum


class ContentBlockType(str, Enum):
    """Types of content blocks."""
    TEXT = "text"
    THINKING = "thinking"  # Reasoning/thinking blocks (Claude thinking, OpenAI reasoning)
    TOOL_CALL = "tool_call"
    TOOL_RESULT = "tool_result"
    # Future: IMAGE, AUDIO, etc.


@dataclass
class ContentBlock:
    """Base class for all content blocks.

    Provides common structure and raw data preservation.
    """
    type: ContentBlockType
    raw: dict[str, Any] | None = None  # Original provider-specific data

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        result = {"type": self.type.value}
        if self.raw:
            result["raw"] = self.raw
        return result


@dataclass
class TextContent(ContentBlock):
    """Regular text content from the model."""
    type: ContentBlockType = ContentBlockType.TEXT
    text: str = ""

    def to_dict(self) -> dict[str, Any]:
        result = super().to_dict()
        result["text"] = self.text
        return result


@dataclass
class ThinkingContent(ContentBlock):
    """Model reasoning/thinking content.

    This represents the model's internal reasoning process.
    Should be displayed without truncation to preserve full context.
    """
    type: ContentBlockType = ContentBlockType.THINKING
    text: str = ""

    def to_dict(self) -> dict[str, Any]:
        result = super().to_dict()
        result["text"] = self.text
        return result


@dataclass
class ToolCallContent(ContentBlock):
    """Tool call request from the model."""
    type: ContentBlockType = ContentBlockType.TOOL_CALL
    id: str = ""
    name: str = ""
    arguments: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        result = super().to_dict()
        result.update({
            "id": self.id,
            "name": self.name,
            "arguments": self.arguments
        })
        return result


@dataclass
class ToolResultContent(ContentBlock):
    """Result from tool execution."""
    type: ContentBlockType = ContentBlockType.TOOL_RESULT
    tool_call_id: str = ""
    output: Any = None
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        result = super().to_dict()
        result.update({
            "tool_call_id": self.tool_call_id,
            "output": self.output
        })
        if self.error:
            result["error"] = self.error
        return result
```

### Design Notes

- **Dataclasses**: Simple, immutable-by-convention, easy to serialize
- **Base class**: Common structure for all blocks
- **Type safety**: Enum for block types prevents typos
- **Raw data preservation**: Keep original provider data for debugging
- **to_dict()**: Enable easy serialization for logging/storage

---

## Module 2: Provider Response Update (amplifier-core)

**File**: `amplifier-core/amplifier_core/models.py`

### Changes Required

Add `content_blocks` field to `ProviderResponse`:

```python
from typing import Any
from pydantic import BaseModel, Field


class ProviderResponse(BaseModel):
    """Response from LLM provider."""

    content: str = Field(..., description="Response text content")
    raw: Any | None = Field(default=None, description="Raw provider response object")
    usage: dict[str, int] | None = Field(default=None, description="Token usage statistics")
    tool_calls: list[ToolCall] | None = Field(default=None, description="Parsed tool calls from response")

    # NEW: Structured content blocks
    content_blocks: list[Any] | None = Field(
        default=None,
        description="Structured content blocks (TextContent, ThinkingContent, ToolCallContent, etc.)"
    )
```

### Design Notes

- **Optional field**: `content_blocks` defaults to `None` for providers that don't populate it yet
- **Flexible typing**: `list[Any]` allows any content block type
- **Coexists with old fields**: `content` and `tool_calls` still used for basic functionality
- **No validation**: Kernel doesn't enforce block structure (policy belongs elsewhere)

---

## Module 3: Event Types (amplifier-core)

**File**: `amplifier-core/amplifier_core/events.py`

### New Event Types

```python
# Content Block Events (for real-time display)
CONTENT_BLOCK_START = "content_block:start"
CONTENT_BLOCK_DELTA = "content_block:delta"
CONTENT_BLOCK_END = "content_block:end"
```

### Event Data Structures

```python
# Event emitted when content block starts
{
    "event": "content_block:start",
    "data": {
        "block_type": "thinking",  # or "text", "tool_call"
        "block_index": 0,
        "timestamp": "2025-10-12T...",
        "metadata": {...}  # Provider-specific
    }
}

# Event emitted for streaming updates
{
    "event": "content_block:delta",
    "data": {
        "block_index": 0,
        "delta": "partial text...",  # For text/thinking blocks
        "partial_json": "{\"loc",    # For tool call arguments
        "timestamp": "2025-10-12T..."
    }
}

# Event emitted when content block completes
{
    "event": "content_block:end",
    "data": {
        "block_index": 0,
        "block": {  # Complete ContentBlock serialized
            "type": "thinking",
            "text": "complete thinking text...",
            "raw": {...}
        },
        "timestamp": "2025-10-12T..."
    }
}
```

### Design Notes

- **Three event lifecycle**: start → delta (optional, streaming) → end
- **Minimal data**: Just what's needed for display
- **Block serialization**: Complete blocks in end events
- **Timestamp tracking**: For debugging and latency analysis

---

## Module 4: Provider Implementations

### Anthropic Provider Update

**File**: `amplifier-module-provider-anthropic/amplifier_mod_provider_anthropic/__init__.py`

**Changes Required**:

1. **Add extended_thinking parameter support**:
```python
async def complete(self, messages: list[dict[str, Any]], **kwargs) -> ProviderResponse:
    params = {
        "model": kwargs.get("model", self.default_model),
        "messages": anthropic_messages,
        "max_tokens": kwargs.get("max_tokens", self.max_tokens),
        "temperature": kwargs.get("temperature", self.temperature),
    }

    # NEW: Support extended thinking
    if kwargs.get("extended_thinking"):
        params["extended_thinking"] = kwargs["extended_thinking"]

    # ... rest of implementation
```

2. **Parse thinking blocks from response**:
```python
content = ""
tool_calls = []
content_blocks = []  # NEW

for block in response.content:
    if block.type == "text":
        content = block.text
        content_blocks.append(TextContent(text=block.text, raw=block))
    elif block.type == "thinking":  # NEW
        content_blocks.append(ThinkingContent(text=block.text, raw=block))
    elif block.type == "tool_use":
        tool_calls.append(ToolCall(tool=block.name, arguments=block.input, id=block.id))
        content_blocks.append(ToolCallContent(id=block.id, name=block.name, arguments=block.input, raw=block))

return ProviderResponse(
    content=content,
    raw=response,
    usage={"input": response.usage.input_tokens, "output": response.usage.output_tokens},
    tool_calls=tool_calls if tool_calls else None,
    content_blocks=content_blocks if content_blocks else None,  # NEW
)
```

### OpenAI Provider Update

**File**: `amplifier-module-provider-openai/amplifier_mod_provider_openai/__init__.py`

**Changes Required**:

1. **Add reasoning parameter support** (for gpt-5 series):
```python
# Add reasoning control
if reasoning := kwargs.get("reasoning", self.reasoning):
    params["reasoning"] = {"effort": reasoning}
```

2. **Extract reasoning blocks from response.output**:
```python
content_parts = []
tool_calls = []
content_blocks = []  # NEW

for block in response.output:
    if hasattr(block, "type"):
        block_type = block.type

        if block_type == "reasoning":  # NEW
            reasoning_text = getattr(block, "text", "")
            content_blocks.append(ThinkingContent(text=reasoning_text, raw=block))

        elif block_type == "message":
            # ... existing text extraction ...
            content_blocks.append(TextContent(text=text, raw=block))

        elif block_type == "tool_call":
            # ... existing tool call extraction ...
            content_blocks.append(ToolCallContent(id=id, name=name, arguments=args, raw=block))

return ProviderResponse(
    content=content,
    raw=response,
    usage={...},
    tool_calls=tool_calls if tool_calls else None,
    content_blocks=content_blocks if content_blocks else None,  # NEW
)
```

### Azure OpenAI Provider

**Status**: Already building `content_blocks` (lines 257-276)

**Required Changes**: Same as OpenAI provider for reasoning block support.

### Ollama Provider

**Status**: Already building `content_blocks` (lines 205-221)

**Required Changes**: None immediately (depends on underlying model OpenAI compatibility).

---

## Module 5: Loop Orchestrator Update

**File**: `amplifier-module-loop-basic/amplifier_mod_loop_basic/__init__.py`

### Changes Required

**Add content block event emission**:

```python
async def execute(self, prompt: str, context, providers: dict[str, Any], tools: dict[str, Any], hooks: HookRegistry) -> str:
    # ... existing code ...

    response = await provider.complete(messages)

    # NEW: Emit content block events if present
    if hasattr(response, 'content_blocks') and response.content_blocks:
        for idx, block in enumerate(response.content_blocks):
            # Emit block start
            await hooks.emit(CONTENT_BLOCK_START, {
                "data": {
                    "block_type": block.type.value,
                    "block_index": idx,
                    "metadata": getattr(block, 'raw', None)
                }
            })

            # Emit block end with complete block
            await hooks.emit(CONTENT_BLOCK_END, {
                "data": {
                    "block_index": idx,
                    "block": block.to_dict()
                }
            })

    # Existing tool call handling
    if tool_calls:
        # ... existing code ...
```

### Streaming Support (Future Enhancement)

For streaming responses, emit delta events:

```python
async for chunk in stream:
    if chunk.content_blocks_delta:
        await hooks.emit(CONTENT_BLOCK_DELTA, {
            "data": {
                "block_index": chunk.index,
                "delta": chunk.delta_text,
                "partial_json": chunk.partial_json
            }
        })
```

---

## Module 6: Display Layer (Application Level)

**Location**: NOT in kernel - in CLI or application layer

**Purpose**: Render content blocks for user display (policy decision)

### Example Display Handler

```python
# In amplifier-app-cli or similar application layer
from rich.console import Console
from rich.panel import Panel
from amplifier_core.content_models import ContentBlockType

console = Console()

class ContentBlockRenderer:
    """Renders content blocks for CLI display."""

    def render_thinking(self, block: ThinkingContent) -> None:
        """Display thinking block - POLICY DECISION."""
        # Show full thinking without truncation
        console.print(Panel(
            block.text,
            title="🤔 Thinking",
            border_style="dim",
            expand=False
        ))

    def render_text(self, block: TextContent) -> None:
        """Display text block - POLICY DECISION."""
        console.print(block.text)

    def render_tool_call(self, block: ToolCallContent) -> None:
        """Display tool call - POLICY DECISION."""
        # Show with argument preview
        args_preview = str(block.arguments)[:200]
        console.print(f"🔧 Calling {block.name}({args_preview}...)")
```

---

## Summary: Separation of Concerns

### Kernel (Mechanism)
- **content_models.py**: Data structures only
- **models.py**: Optional content_blocks field
- **events.py**: Event type constants
- **No display logic**: No decisions about what to show or how

### Providers (Policy at edges)
- **Extract blocks**: Parse provider-specific responses
- **Build content_blocks**: Create appropriate ContentBlock instances
- **Transform to unified format**: Convert provider-native types to content models

### Loop Orchestrator (Mechanism)
- **Emit events**: Fire content block events when blocks exist
- **No display decisions**: Just make data available
- **Hook integration**: Use existing hook system

### Application Layer (Policy at edges)
- **Display rendering**: Decide how to show each block type
- **Formatting decisions**: Colors, truncation, layout
- **User experience**: Interactive vs. batch mode handling

This clean separation ensures the kernel remains small and stable while policy can evolve rapidly at the edges.
