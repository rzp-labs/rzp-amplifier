# Archaeological Findings: The Phantom Commits

**Investigation Date**: 2025-10-12
**Lead**: knowledge-archaeologist + independent discovery

---

## The Mystery

User reported that thinking and tool display was working Friday, but disappeared by Sunday. No obvious changes in the visible codebase explained the loss.

---

## Root Cause: Phantom Commits

The feature existed only in **orphaned local commits** that were:

1. Never pushed to the remote repository
2. Referenced by submodule pointers in parent repo commits
3. Destroyed when the monorepo was restructured into separate module repositories
4. The commits existed in git history of parent repo but the actual code in the submodule was lost

### The Missing Commits

Parent repository commits referenced these submodule states:

- `de434f31a8bef2a66e073398e8bb64d2406b86b4` (from commit 5c97035)
- `85718c5b173db2d5d688c6d03afe260ce7e9a4b1` (from commit 1aa202c)

When checked, **these commits do not exist** in any remote branch.

---

## Commit Message Evidence

### Commit 5c970350 (Oct 10, 2025)

```
feat: update amplifier-dev for real-time thinking and tool display

Update amplifier-dev submodule to include real-time display functionality
for AI thinking and tool execution across CLI tools.

This update brings comprehensive real-time feedback to the CLI, showing:
- Complete AI thinking without truncation
- Tool calls as they occur (with 5 lines of argument context)
- Tool results immediately (with 5 lines of output context)

Implementation spans multiple modules with hook-based architecture for
extensibility. Tested successfully in both interactive chat and single-shot
execution modes.
```

### Commit 1aa202c66e (Oct 10, 2025)

```
feat: update amplifier-dev for content models and extended thinking

Update amplifier-dev submodule to include comprehensive content model
architecture and extended thinking support across all providers.

This update includes:
- Content model foundation (TextContent, ThinkingContent, ToolCallContent, etc.)
- Extended thinking support for Anthropic Claude
- Content blocks support for OpenAI Responses API
- Enhanced logging for thinking and tool execution
- Comprehensive documentation and implementation guides
- Updated test configuration with thinking enabled

All changes maintain backward compatibility while enabling new
structured content capabilities for real-time display.
```

---

## Evidence of Partial Implementation

### Azure OpenAI Provider (amplifier-module-provider-azure-openai)

**Lines 13-14**: Already importing content models
```python
from amplifier_core.content_models import TextContent
from amplifier_core.content_models import ToolCallContent
```

**Lines 257-276**: Already building content_blocks
```python
# Build content_blocks for structured content
content_blocks = []

# Add text content if present
if content:
    content_blocks.append(TextContent(text=content))

# Add tool call content blocks
if tool_calls:
    import json
    for tc in tool_calls:
        # Parse arguments from JSON string to dict
        try:
            input_dict = json.loads(tc.arguments) if isinstance(tc.arguments, str) else tc.arguments
        except json.JSONDecodeError:
            input_dict = {"raw": tc.arguments}

        content_blocks.append(ToolCallContent(id=tc.id, name=tc.tool, input=input_dict))
```

### Ollama Provider (amplifier-module-provider-ollama)

**Lines 14-15**: Already importing content models
```python
from amplifier_core.content_models import TextContent
from amplifier_core.content_models import ToolCallContent
```

**Lines 169-227**: Already building content_blocks (in both streaming and non-streaming paths)

---

## What Was Lost

From commit messages and provider evidence, we can reconstruct what was lost:

1. **content_models.py** - Complete module with all content block types
2. **ProviderResponse.content_blocks** - Field for structured content
3. **Extended thinking support** - Anthropic provider parameter for reasoning blocks
4. **OpenAI reasoning extraction** - For o1/o3 models' thinking blocks
5. **Loop orchestrator events** - Emitting content block events for display
6. **Display logic** - Rendering thinking, tool calls, and results in real-time

---

## What Survived

1. **Provider imports** - Azure OpenAI and Ollama still reference content_models
2. **content_blocks building** - Both providers have code to populate the field
3. **Architectural vision** - Commit messages preserved the design intent
4. **Kernel philosophy alignment** - Mechanism/policy separation was clear

---

## Lessons Learned

### What Went Wrong

1. **Local work not pushed** - Critical features existed only in local commits
2. **Submodule management** - Monorepo restructure destroyed orphaned commits
3. **No CI/CD validation** - No automated check that submodule commits exist remotely
4. **Lack of integration tests** - Feature breakage not caught automatically

### Process Improvements

1. **Always push feature branches** - Even WIP code should be on remote
2. **Validate submodule pointers** - Check that referenced commits exist remotely before merging
3. **Document architecture** - Commit messages preserved the vision even when code was lost
4. **Add CI checks** - Validate submodule commits exist and are accessible
5. **Integration tests** - Test critical features end-to-end

### What Worked Well

1. **Git archaeology** - Commit messages revealed what was lost
2. **Modular architecture** - Easy to reimplement in isolated pieces
3. **Provider consistency** - Some providers retained partial implementations locally
4. **Ruthless simplicity** - Clean design makes reimplementation straightforward

---

## Current Status

**Import Errors**: Azure OpenAI and Ollama providers will fail on import until content_models.py exists.

**Next Step**: Create content_models.py to fix the immediate import errors, then rebuild the complete feature.
