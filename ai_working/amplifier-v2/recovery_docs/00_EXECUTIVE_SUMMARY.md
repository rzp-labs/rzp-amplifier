# Content Models & Real-Time Display Recovery

**Date**: 2025-10-12
**Status**: Architecture Complete, Ready for Implementation
**Type**: Feature Recovery & Reconstruction
**Supported Models**: OpenAI gpt-5 series, Anthropic 4 series, Azure OpenAI gpt-5 series, Ollama OpenAI-compatible

---

## Executive Summary

The thinking and tool display feature was lost due to phantom commits (local-only code destroyed during monorepo restructure). Through archaeological investigation and fresh API research, we have reconstructed the complete architecture following kernel philosophy principles.

### Critical Discovery

**Azure OpenAI and Ollama providers are already trying to use the content models system!**

```python
# Lines 13-14 in both providers
from amplifier_core.content_models import TextContent, ToolCallContent
```

Both providers have code to build `content_blocks`, but the module doesn't exist yet. This caused immediate import errors.

### What Needs to Be Built (Minimum Viable)

1. **amplifier-core/amplifier_core/content_models.py** - New file with all content block types
2. **amplifier-core/amplifier_core/models.py** - Add `content_blocks` field to ProviderResponse
3. **amplifier-core/amplifier_core/events.py** - Add content block event types
4. **amplifier-module-provider-anthropic** - Basic extended_thinking support
5. **amplifier-module-provider-openai** - Basic reasoning block extraction
6. **amplifier-module-loop-basic** - Simple content block event emission

### Kernel Philosophy Alignment

This design perfectly follows the kernel philosophy:
- **Mechanism (kernel)**: Content models are pure data structures, events are constants
- **Policy (edges)**: Providers extract blocks, orchestrators emit events, display layer renders
- **Small and stable**: Only one new module, one field, three event types in kernel
- **Text-first**: Dataclasses with clear structure and serialization
- **Separation of concerns**: Clear boundaries between kernel and edges

### Implementation Priority

**Critical Path** (2-3 hours):
1. Create content_models.py (fixes import errors in 2 providers) ⚡
2. Update ProviderResponse (enables providers to populate content_blocks)
3. Add event types (enables orchestrator to emit events)
4. Update Anthropic provider (basic thinking support)
5. Update OpenAI provider (basic reasoning support)
6. Update loop orchestrator (simple event emission)

### Real-Time Display Requirements

From Saturday session work, content needs to appear **as it occurs**, not at the end:
- Thinking blocks should be accessible in real-time
- Tool calls should appear when invoked
- Tool results should show immediately after execution

This is enabled by event-based architecture that the loop orchestrator will emit.

---

## Documentation Structure

- `01_ARCHAEOLOGICAL_FINDINGS.md` - What was lost and how we discovered it (historical record)
- `02_API_RESEARCH.md` - Latest provider API capabilities (gpt-5, Claude 4 series)
- `03_ARCHITECTURE_DESIGN.md` - Complete technical specification aligned with kernel philosophy
- `04_IMPLEMENTATION_PLAN.md` - Minimal viable implementation (immediate needs only)
- `VISION.md` - Future enhancements and long-term guidance
- `TESTING.md` - Testing strategy (can be used when ready)

---

## Next Steps

1. Review architecture documentation (especially 03 and 04)
2. Implement in order: content_models → ProviderResponse → events → providers → loop
3. Test with basic verification (import tests, manual provider tests)
4. See VISION.md for future enhancements after MVP is working

---

## Supported Models

**Anthropic**:
- Claude Opus 4
- Claude Sonnet 4.5
- Claude Haiku 4

**OpenAI**:
- gpt-5 series (with Responses API)

**Azure OpenAI**:
- gpt-5 series deployments (with Responses API)

**Ollama**:
- OpenAI-compatible models

---

## Key Terminology

- **Anthropic**: "thinking" blocks (via `extended_thinking` parameter)
- **OpenAI**: "reasoning" blocks (via `reasoning` parameter)
- **Unified**: Both map to `ThinkingContent` in our content models
