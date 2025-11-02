# Memory Extraction Enhancements

**Status**: Planned (pending observation of actual error patterns)
**Created**: 2025-11-02
**Context**: Error visibility improvements implemented (Fixes 1 & 3). These enhancements address remaining failure modes.

---

## Enhancement 1: Memory CLI Retry Capability

**What**: Add retry command to `memory_cli.py` for batch transcript processing

**Why**: Manual recovery when automatic extraction fails during session shutdown

**Implementation Sketch**:
```bash
# Retry failed extractions from last N sessions
amplifier memory retry --last 5

# Retry specific transcript files
amplifier memory retry --files transcript1.jsonl transcript2.jsonl

# Skip already-processed transcripts
amplifier memory retry --skip-processed
```

**Key Features**:
- Batch processing of transcript files
- Automatic skip of already-extracted transcripts (check memory store)
- Progress reporting
- Error summary

**When to Implement**: After observing actual extraction failures in production use

---

## Enhancement 2: Checkpoint Saving During Extraction

**What**: Save partial results during long memory extractions

**Why**: Prevent total work loss on timeout or crash near completion

**Implementation Sketch**:
- Save checkpoint after each memory item extracted
- Store checkpoint in temp file: `.memory_extraction_checkpoint_{session_id}.json`
- Resume from checkpoint on retry
- Clean up checkpoint on successful completion

**Data to Checkpoint**:
```json
{
  "session_id": "...",
  "last_processed_index": 42,
  "extracted_count": 15,
  "memories_extracted": ["mem1", "mem2", ...],
  "timestamp": "2025-11-02T..."
}
```

**When to Implement**: After seeing timeouts or crashes during extraction

---

## Enhancement 3: On-Demand Extraction Testing

**What**: Test memory extraction without full session lifecycle

**Why**: Development, debugging, and validation

**Implementation Sketch**:
```bash
# Test extraction on sample transcript
amplifier memory test-extract --transcript test_data.jsonl

# Validate extraction quality
amplifier memory validate --transcript recent_session.jsonl --show-memories

# Debug extraction issues
amplifier memory debug-extract --transcript problem_session.jsonl --verbose
```

**Use Cases**:
- Development: Test extraction logic changes
- Debugging: Understand why extraction failed
- Validation: Verify extraction quality before deployment
- Documentation: Generate examples for docs

**When to Implement**: When actively developing/debugging extraction logic

---

## Implementation Priority

**Do NOT implement yet**. Wait for:

1. **Actual error patterns** - What failures occur in real use?
2. **Usage data** - How often do extractions fail?
3. **User feedback** - What recovery workflows are needed?

**Current Focus**: Monitor error logs from Fixes 1 & 3, understand failure modes

---

## Success Criteria

These enhancements are ready to implement when:

- [ ] We've seen 5+ extraction failures in production
- [ ] We understand common failure patterns
- [ ] Users request recovery mechanisms
- [ ] Error logs show timeouts or crashes during extraction

Until then: observe, learn, prioritize based on actual needs.
