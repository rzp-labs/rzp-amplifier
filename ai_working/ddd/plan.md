# DDD Phase 1: Plan - Intelligent Issue Analysis System

## Feature Overview

**Goal**: System that researches available context, synthesizes findings, and makes recommendations on what issues are. If insufficient information, explicitly lists what additional data is needed. System learns from outcomes to improve recommendations over time.

**User Value**: Reduce time teams spend on issues (not auto-resolve them) by doing the heavy lifting of research and synthesis.

---

## Architectural Recommendation

**Recommendation: Approach 2 (Standalone Investigation Workflow) with specific modifications**

### Why This Approach Wins

1. **Single source initially** ✅ - Start with Linear issue history (simplest valuable source)
2. **Citations mandatory** ✅ - Pydantic models enforce source tracking at every level
3. **Philosophy aligned** ✅ - ~100-150 lines per module, modular design, ruthless simplicity
4. **Grows incrementally** ✅ - Can add Git, codebase analysis later without refactoring
5. **Learning store** ✅ - File-based pattern tracking fits orchestrator patterns

### Architecture: Investigation Workflow

**Module Breakdown** (~500 lines total across 5 modules):

```
orchestrator/
├── investigation.py          # Main workflow (~150 lines)
├── models.py                 # Add investigation models (~50 lines)
├── linear_history.py         # Linear research module (~120 lines)
├── citation_tracker.py       # Citation management (~80 lines)
└── learning_store.py         # Pattern learning (~100 lines)
```

---

## Single Source to Start With

**Recommendation: Linear Issue History**

**Why Linear history wins:**
- Already have Linear GraphQL API client
- Rich context: issue patterns, resolution paths, team discussions
- Minimal additional infrastructure needed
- High value: "Similar issues resolved as X"

**What to research from Linear:**
- Issues with same labels/components
- Recent resolutions in same area
- Team member expertise patterns (who solved similar issues)
- Common resolution paths

**Alternatives considered:**
- **Git history**: More complex, requires git analysis agent
- **Codebase analysis**: Complex, need static analysis
- **Logs**: Requires log aggregation infrastructure

Start simple, add complexity only when proven valuable.

---

## Mandatory Citations Pattern

**Citation Structure** (Pydantic models):

```python
# models.py additions

class Citation(BaseModel):
    """Single source citation for a finding."""

    source_type: Literal["linear_issue", "git_commit", "codebase", "logs"]
    source_id: str = Field(..., description="e.g., 'ABC-123', 'commit-sha'")
    source_url: str = Field(..., description="Direct link to source")
    excerpt: str = Field(..., description="Relevant text from source")
    retrieved_at: str = Field(..., description="ISO timestamp")


class Finding(BaseModel):
    """Investigation finding with mandatory citations."""

    finding: str = Field(..., description="What was discovered")
    confidence: Literal["low", "medium", "high"]
    citations: list[Citation] = Field(
        ...,
        min_length=1,  # MANDATORY: At least one citation
        description="Sources supporting this finding"
    )


class Recommendation(BaseModel):
    """Investigation recommendation with evidence."""

    recommendation: str
    reasoning: str
    citations: list[Citation] = Field(
        ...,
        min_length=1,  # MANDATORY
        description="Evidence supporting recommendation"
    )
    confidence: Literal["low", "medium", "high"]


class InvestigationResult(BaseModel):
    """Complete investigation result."""

    issue_id: str
    research_sources: list[str] = Field(
        ...,
        description="What sources were researched"
    )
    findings: list[Finding]
    recommendations: list[Recommendation]
    missing_data: list[str] = Field(
        default_factory=list,
        description="What additional data would improve analysis"
    )
    success: bool
    duration: float
```

**Output Format** (Markdown with citations):

```markdown
## Investigation: ABC-123

### Research Sources
- Linear issue history (123 similar issues)
- Team expertise patterns (5 related resolvers)

### Findings

**Finding 1: Similar issue resolved 3 times in past month**
Confidence: High

*Sources:*
- [ABC-100](https://linear.app/issue/ABC-100): "Same error pattern, resolved by adding timeout"
- [ABC-105](https://linear.app/issue/ABC-105): "Duplicate root cause identified"
- [ABC-110](https://linear.app/issue/ABC-110): "Third occurrence, permanent fix deployed"

**Finding 2: Team member @alice has resolved 4 similar issues**
Confidence: High

*Sources:*
- [ABC-100](https://linear.app/issue/ABC-100): Resolved by @alice
- [ABC-105](https://linear.app/issue/ABC-105): Resolved by @alice
- ...

### Recommendations

**Recommendation: Investigate database connection pooling**
Confidence: High
Reasoning: All 3 similar issues were resolved by adjusting connection pool settings

*Supporting Evidence:*
- [ABC-100](https://linear.app/issue/ABC-100): "Increased max_connections from 50 to 100"
- [ABC-105](https://linear.app/issue/ABC-105): "Added connection pool timeout"

### Missing Data
- Database connection metrics from last 7 days
- Error logs matching this pattern
```

---

## Module Specifications

### Module 1: `investigation.py` (~150 lines)

**Purpose**: Orchestrate investigation workflow

**Contract**:
```python
def execute_investigation(issue_id: str) -> InvestigationResult:
    """Execute full investigation workflow.

    Steps:
    1. Fetch issue from Linear
    2. Research Linear history for patterns
    3. Synthesize findings with citations
    4. Generate recommendations
    5. Identify missing data

    Returns InvestigationResult with all citations
    """
```

**Dependencies**: `linear_client`, `linear_history`, `citation_tracker`, `learning_store`

**Key Patterns**:
- Use defensive utilities (`call_agent_with_retry`, `parse_llm_json`)
- File-based result saving (like triage)
- Optional Linear writes via `LINEAR_ENABLE_WRITES`

---

### Module 2: `linear_history.py` (~120 lines)

**Purpose**: Research Linear for similar issues and patterns

**Contract**:
```python
class LinearHistoryResearcher:
    """Research Linear issue history for patterns."""

    def find_similar_issues(
        self,
        issue: dict,
        max_results: int = 50
    ) -> list[dict]:
        """Find issues with similar labels/components/text."""

    def find_resolution_patterns(
        self,
        issues: list[dict]
    ) -> list[ResolutionPattern]:
        """Identify common resolution paths."""

    def find_team_expertise(
        self,
        issues: list[dict]
    ) -> list[TeamExpertise]:
        """Track who resolves which types of issues."""
```

**Implementation Notes**:
- Use Linear GraphQL API with search filters
- Extract: labels, components, assignees, state transitions
- Return with full citation data (issue ID, URL, excerpt)

---

### Module 3: `citation_tracker.py` (~80 lines)

**Purpose**: Manage citation collection and validation

**Contract**:
```python
class CitationTracker:
    """Track and validate citations for findings."""

    def create_citation(
        self,
        source_type: str,
        source_id: str,
        source_url: str,
        excerpt: str
    ) -> Citation:
        """Create citation with timestamp."""

    def validate_citations(
        self,
        findings: list[Finding]
    ) -> bool:
        """Ensure all findings have citations."""

    def format_citations_markdown(
        self,
        citations: list[Citation]
    ) -> str:
        """Format citations for display."""
```

**Key Validation**:
- Every Finding MUST have ≥1 citation
- Every Recommendation MUST have ≥1 citation
- Citations include direct links (traceable)

---

### Module 4: `learning_store.py` (~100 lines)

**Purpose**: File-based pattern learning store

**Contract**:
```python
class PatternStore:
    """Store and retrieve issue patterns for learning."""

    def __init__(self, store_path: Path = Path("data/patterns.jsonl")):
        """Initialize with file path."""

    def record_pattern(
        self,
        issue_pattern: str,
        recommendation: str,
        outcome: Optional[str] = None,
        citations: list[Citation]
    ):
        """Record issue pattern → recommendation → outcome."""

    def find_matching_patterns(
        self,
        issue_description: str,
        min_confidence: float = 0.7
    ) -> list[PatternMatch]:
        """Find patterns similar to current issue."""

    def update_outcome(
        self,
        pattern_id: str,
        outcome: str
    ):
        """Update pattern with resolution outcome."""
```

**File Format** (JSONL):
```json
{
  "pattern_id": "uuid",
  "issue_pattern": "Database connection timeout",
  "recommendation": "Increase connection pool size",
  "outcome": "resolved",
  "confidence": 0.85,
  "citations": [...],
  "recorded_at": "2025-11-03T10:00:00Z",
  "updated_at": "2025-11-03T12:00:00Z"
}
```

**Learning Mechanism**:
- New issue → Check pattern store for similar patterns
- If match found → Include in recommendations with citation
- After resolution → Update pattern with outcome
- High-success patterns gain confidence over time

---

## Philosophy Alignment Check

✅ **Ruthless Simplicity**
- Start with ONE source (Linear history)
- File-based pattern store (no database)
- ~100-150 lines per module
- Reuses proven patterns (defensive utilities, agent delegation)

✅ **Modular Design**
- Each module self-contained
- Clear Pydantic contracts
- Can regenerate modules independently
- Easy to test in isolation

✅ **Citations Mandatory**
- Pydantic enforces `min_length=1` on citations
- Every finding/recommendation must cite source
- Direct links enable verification

✅ **Incremental Growth**
- Start with Linear history
- Add Git analysis later (new module: `git_history.py`)
- Add codebase analysis later (new module: `codebase_analyzer.py`)
- No refactoring needed—just add modules

---

## Implementation Plan

**Phase 1: Core Investigation** (~500 lines)
1. Add models to `models.py` (Citation, Finding, Recommendation, InvestigationResult)
2. Create `linear_history.py` (research Linear for patterns)
3. Create `citation_tracker.py` (manage citations)
4. Create `learning_store.py` (file-based pattern tracking)
5. Create `investigation.py` (orchestrate workflow)

**Phase 2: CLI & Testing** (~200 lines)
6. Add CLI command `orchestrator investigate <issue-id>`
7. Add tests for each module
8. Add integration test for full workflow

**Phase 3: Learning Loop** (Manual initially)
9. After resolution, manually update pattern store with outcome
10. Future: Hook to auto-update patterns when issues close

---

## Key Differentiators from Triage

**Triage**:
- Analyzes SINGLE issue in isolation
- Determines validity & severity
- No research, no citations
- No learning

**Investigation**:
- Researches CONTEXT across many issues
- Synthesizes patterns with evidence
- MANDATORY citations for every finding
- Learns from outcomes over time

**Why separate workflows**:
- Different purposes (quick triage vs deep research)
- Different timescales (20s vs 60s+)
- Different data sources (single issue vs historical patterns)
- Different outputs (priority vs recommendations)

---

## Next Steps

1. **User approval** of this plan
2. **Create spec for each module** (use this as blueprint)
3. **Delegate to modular-builder** to implement modules
4. **Test with real Linear issues** to validate research quality
5. **Iterate on pattern matching** to improve recommendations
6. **Add more sources** (Git, codebase) when Linear proves valuable

**Start small, prove value, grow incrementally.** This is the orchestrator way.

---

*Plan created by: zen-architect agent*
*Date: 2025-11-03*
