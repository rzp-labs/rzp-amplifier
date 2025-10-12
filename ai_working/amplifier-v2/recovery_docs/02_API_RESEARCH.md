# API Research: Provider Capabilities Summary

**Research Date**: 2025-10-12
**Sources**: Context7 MCP with latest provider documentation
**Supported Models**: OpenAI gpt-5 series, Anthropic 4 series, Azure OpenAI gpt-5 series, Ollama OpenAI-compatible

---

## OpenAI Responses API (gpt-5 series)

### Key Features

**Reasoning Blocks** (gpt-5 series models):
- Models can output internal reasoning
- Exposed via `reasoning` parameter
- Streaming provides reasoning deltas
- Separate from regular output text

**Content Structure**:
```python
response.output = [
    {"type": "reasoning", "text": "Let me analyze this..."},
    {"type": "message", "content": [{"type": "output_text", "text": "The answer is..."}]},
    {"type": "tool_call", "name": "search", "input": {...}}
]
```

**Streaming Pattern**:
- Events for each block type
- Delta updates for text content
- Progressive JSON building for tool arguments

### Relevant Capabilities

- Native reasoning blocks
- Tool calls as first-class output blocks
- Structured output with multiple content types
- Streaming support for all block types

---

## Anthropic API (4 series models)

### Key Features

**Extended Thinking** (Claude 4 series):
- `extended_thinking` parameter enables thinking blocks
- Thinking blocks separate from text blocks
- Never truncated (full reasoning preserved)
- Available in Claude Opus 4, Sonnet 4.5, Haiku 4

**Content Block Structure**:
```python
response.content = [
    {"type": "thinking", "text": "I need to consider..."},
    {"type": "text", "text": "Here's my response..."},
    {"type": "tool_use", "id": "...", "name": "search", "input": {...}}
]
```

**Streaming Events**:
- `content_block_start` - Block begins
- `content_block_delta` - Incremental updates
  - `text_delta` for text/thinking
  - `input_json_delta` for tool arguments
- `content_block_stop` - Block complete

### Code Example from Docs

```python
async with client.messages.stream(
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello!"}],
    model="claude-3-5-sonnet-latest",
) as stream:
    async for event in stream:
        if event.type == "text":
            print(event.text, end="", flush=True)
        elif event.type == "content_block_stop":
            print('\n\nBlock finished:', event.content_block)
```

### Relevant Capabilities

- Explicit thinking block type
- Tool use as content blocks
- Rich streaming with delta events
- Snapshot accumulation for complete blocks

---

## Azure OpenAI (gpt-5 series)

### Key Features

**Same as OpenAI** (uses Responses API on Azure infrastructure):
- Same response structure
- Same reasoning capabilities
- Deployment name mapping instead of direct model names
- Authentication differences (API key, Managed Identity, Azure AD)

### Differences from OpenAI

- Uses `azure_endpoint` instead of base URL
- Requires `deployment` name (maps to model)
- API version parameter
- Azure-specific authentication methods

### Current Status in Codebase

**Already building content_blocks** (lines 257-276):
```python
content_blocks = []
if content:
    content_blocks.append(TextContent(text=content))
if tool_calls:
    for tc in tool_calls:
        input_dict = json.loads(tc.arguments) if isinstance(tc.arguments, str) else tc.arguments
        content_blocks.append(ToolCallContent(id=tc.id, name=tc.tool, input=input_dict))

return ProviderResponse(
    content=content,
    content_blocks=content_blocks,
    raw=response,
    usage={...},
    tool_calls=tool_calls,
)
```

---

## Ollama (OpenAI-compatible)

### Key Features

**OpenAI-Compatible API**:
- Uses OpenAI's Chat Completions format
- Supports tools in OpenAI format
- Message structure matches OpenAI
- Streaming follows OpenAI patterns

**Local Execution**:
- Runs locally (http://localhost:11434 default)
- No API key required
- Models pulled locally via `ollama pull`
- Self-hosted, privacy-preserving

### Current Status in Codebase

**Already building content_blocks** (lines 205-221):
```python
content_blocks = []
if content:
    content_blocks.append(TextContent(text=content))
if tool_calls:
    for tc in tool_calls:
        input_dict = tc.arguments if isinstance(tc.arguments, dict) else {}
        content_blocks.append(ToolCallContent(id=tc.id, name=tc.tool, input=input_dict))

return ProviderResponse(
    content=content,
    content_blocks=content_blocks,
    raw=response,
    usage=usage,
    tool_calls=tool_calls if tool_calls else None,
)
```

---

## Unified Content Model Design

### Common Patterns Across Providers

1. **Multiple content types** - All providers separate text, thinking/reasoning, and tool calls
2. **Streaming support** - All providers stream content progressively
3. **Block-based structure** - Content organized as discrete blocks
4. **Tool calls as blocks** - Tool invocations are first-class content

### Provider-Specific Differences

| Feature | OpenAI | Anthropic | Azure OpenAI | Ollama |
|---------|--------|-----------|--------------|--------|
| Thinking blocks | "reasoning" | "thinking" | Same as OpenAI | Via OpenAI compat |
| Text blocks | "message.output_text" | "text" | Same as OpenAI | Same as OpenAI |
| Tool blocks | "tool_call" | "tool_use" | Same as OpenAI | Same as OpenAI |
| Parameter | `reasoning` | `extended_thinking` | Same as OpenAI | Same as OpenAI |
| Models | gpt-5 series | Opus 4, Sonnet 4.5, Haiku 4 | gpt-5 series | OpenAI-compatible |

### Recommended Unified Model

```python
class ContentBlockType(Enum):
    TEXT = "text"              # Regular text output
    THINKING = "thinking"      # Reasoning/thinking blocks
    TOOL_CALL = "tool_call"    # Tool invocation
    TOOL_RESULT = "tool_result" # Tool execution result

@dataclass
class ContentBlock:
    type: ContentBlockType
    raw: dict | None = None  # Original provider data

@dataclass
class TextContent(ContentBlock):
    type = ContentBlockType.TEXT
    text: str = ""

@dataclass
class ThinkingContent(ContentBlock):
    type = ContentBlockType.THINKING
    text: str = ""

@dataclass
class ToolCallContent(ContentBlock):
    type = ContentBlockType.TOOL_CALL
    id: str = ""
    name: str = ""
    arguments: dict[str, Any] | None = None

@dataclass
class ToolResultContent(ContentBlock):
    type = ContentBlockType.TOOL_RESULT
    tool_call_id: str = ""
    output: Any = None
    error: str | None = None
```

---

## Implementation Requirements

### Per-Provider Requirements

**Anthropic**:
- Add `extended_thinking` parameter support to request
- Parse "thinking" blocks from response.content
- Build ThinkingContent for each thinking block

**OpenAI (gpt-5 series)**:
- Add `reasoning` parameter support
- Parse "reasoning" blocks from response.output
- Build ThinkingContent for each reasoning block

**Azure OpenAI**:
- Same as OpenAI (inherits reasoning support)
- Already building content_blocks for text and tools

**Ollama**:
- Depends on underlying model's OpenAI compatibility
- Already building content_blocks for text and tools
- May not support reasoning blocks depending on model

---

## Streaming Considerations

### Event Flow Pattern

```
1. message_start / response_start
2. content_block_start (thinking)
3. content_block_delta (thinking text chunk)
4. content_block_delta (thinking text chunk)
5. content_block_stop (thinking)
6. content_block_start (text)
7. content_block_delta (text chunk)
8. content_block_stop (text)
9. content_block_start (tool_call)
10. content_block_delta (tool arguments partial JSON)
11. content_block_stop (tool_call)
12. message_stop / response_stop
```

### Real-Time Display Requirements

For real-time display (content as events occur):
- Emit events as blocks are discovered
- Allow streaming text/thinking to display progressively
- Show tool calls when block starts
- Show tool results after execution

This requires the loop orchestrator to emit events, not just collect responses.

---

## Kernel Philosophy Alignment

### Mechanism (Kernel)
- **Content models**: Pure data structures representing provider output
- **Event types**: CONTENT_BLOCK_START, CONTENT_BLOCK_DELTA, CONTENT_BLOCK_END
- **ProviderResponse**: Optional content_blocks field

### Policy (Edges)
- **Providers**: Extract and build appropriate content blocks for their API
- **Loop orchestrator**: Emit events when blocks exist
- **Display layer**: Decide how to render each block type

This clean separation keeps the kernel minimal and stable while allowing innovation at the edges.

---

## Next Steps

1. Implement content_models.py with unified structure
2. Update each provider to build appropriate content blocks
3. Test with real API calls to verify block extraction
4. Add streaming support where missing
