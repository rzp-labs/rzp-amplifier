---
description: Orchestrates parallel investigation of beads issues, identifies relationships and meta-patterns, proposes meta-issues when one solution solves multiple problems, and updates all findings
category: project-management
allowed-tools: Bash, Read, Glob, Grep, Task, TodoWrite
---

# Claude Command: Investigate Beads Issues

This command orchestrates comprehensive investigation of beads issue tracker tasks, launching multiple beads-investigator agents in parallel, synthesizing findings, identifying meta-patterns, and proposing meta-issues when one solution addresses multiple problems.

## Usage

```
/investigate-beads
```

Or with arguments:

```
/investigate-beads --max-issues 5 --priority 1
/investigate-beads --labels repl,agent
/investigate-beads --status open
```

## What This Command Does

1. **Project Discovery**: Locates project root, AGENTS.md, and .beads/ directory
2. **Issue Retrieval**: Lists open uninvestigated issues from beads database
3. **Parallel Investigation**: Launches beads-investigator agents for each issue
4. **Meta-Analysis**: Synthesizes findings to identify patterns and relationships
5. **Meta-Issue Creation**: Proposes new issues when one solution solves multiple problems
6. **Beads Updates**: Updates all investigated issues with findings and links
7. **Comprehensive Report**: Delivers synthesis of all investigations with recommendations

## Phase 1: Discovery and Planning

### 1.1 Project Context Discovery

```
IMPORTANT: This command is general-purpose and works with any project that has:
- An AGENTS.md file in the project root
- A .beads/ directory with issue database

Discovery sequence:
1. Find project root (look for AGENTS.md)
2. Identify .beads/ directory and database file
3. Read AGENTS.md to understand project context
4. Verify bd CLI availability
```

### 1.2 Issue Selection

```
Query uninvestigated issues:
- Status: open (by default, or as specified)
- Priority: All (or filtered by --priority)
- Labels: All (or filtered by --labels)
- Investigation status: Not marked with "🔍 INVESTIGATION COMPLETE"

Filtering:
- Use grep to find issues without investigation markers
- Respect --max-issues limit (default: 10)
- Prioritize by priority level (P0 > P1 > P2 > P3)
- Group related issues for context sharing
```

### 1.3 Task Planning

Use **TodoWrite** to create investigation plan:

```
Tasks:
[ ] Discover project structure
[ ] Retrieve open uninvestigated issues
[ ] Launch parallel investigations (one per issue)
[ ] Collect investigation reports
[ ] Perform meta-analysis
[ ] Identify meta-patterns
[ ] Propose meta-issues
[ ] Update beads with findings
[ ] Link related issues
[ ] Generate comprehensive report
```

## Phase 2: Parallel Investigation

### 2.1 Agent Launch Strategy

**CRITICAL: Launch ALL agents in SINGLE message with multiple Task calls**

```python
# For N issues, create N Task tool calls in ONE message:
Task beads-investigator: "Investigate bd-7: [title]
Project root: /path/to/project
Read @/path/to/project/AGENTS.md for context
Issue details: [from bd show bd-7]
Related context: [any known relationships]"

Task beads-investigator: "Investigate bd-8: [title]
Project root: /path/to/project
Read @/path/to/project/AGENTS.md for context
Issue details: [from bd show bd-8]
Related context: bd-7 also involves REPL issues"

Task beads-investigator: "Investigate bd-9: [title]
..."
```

**Context Sharing Across Agents**:

When you detect related issues (same labels, similar titles, same component):
- Inform each agent about related investigations
- Example: "Note: bd-7, bd-8, bd-9 all involve REPL issues. Consider if root causes are shared."

### 2.2 Context Efficiency

```
Per-agent context loading:
- Project AGENTS.md: Shared (referenced, not duplicated)
- Issue details: Unique per agent
- Related context: Minimal (just issue IDs and brief notes)

Expected: Each agent returns focused investigation report
Result: Main context preserved, agents return only essentials
```

## Phase 3: Meta-Analysis and Pattern Recognition

### 3.1 Collect All Investigation Reports

```
After all agents complete:
- Gather N investigation reports
- Parse each for:
  * Root causes
  * Proposed solutions
  * Related issues identified
  * File paths affected
  * Philosophy alignment notes
```

### 3.2 Pattern Detection

**Analyze across all investigations for:**

**Shared Root Causes**:
```
Pattern: Multiple issues stem from same underlying problem
Example:
- bd-7: Poor REPL editing → Root: Rich console.input() limitations
- bd-8: Ctrl-C exits → Root: Rich console.input() limitations
- bd-9: Paste breaks → Root: Rich console.input() limitations
→ PATTERN DETECTED: Same root cause across 3 issues
```

**Shared Solutions**:
```
Pattern: One solution addresses multiple issues
Example:
- bd-7 proposes: Adopt prompt_toolkit
- bd-8 proposes: Adopt prompt_toolkit
- bd-9 proposes: Adopt prompt_toolkit
- bd-10 proposes: Adopt prompt_toolkit
→ PATTERN DETECTED: Single solution (prompt_toolkit) solves 4 issues
```

**Shared File Paths**:
```
Pattern: Multiple issues affect same code locations
Example:
- bd-7 affects: main.py:1413
- bd-8 affects: main.py:1458-1464
- bd-9 affects: main.py:1413
→ PATTERN DETECTED: Clustered in same file/module
```

**Philosophy Alignments**:
```
Pattern: Multiple issues violate same principle
Example:
- bd-7 violates: Library vs Custom principle
- bd-8 violates: Error visibility principle
→ PATTERN DETECTED: Philosophy violations in same area
```

### 3.3 Relationship Discovery

**Build relationship graph:**

```
For each investigation:
  Related issues mentioned → Create relationship edges
  Files affected → Group by file
  Solutions proposed → Group by approach
  Philosophy violations → Group by principle

Output: Graph showing:
- Issue clusters (related by cause, solution, or file)
- Solution groups (issues solvable together)
- Dependency chains (issue A enables issue B)
```

## Phase 4: Meta-Issue Proposal

### 4.1 Meta-Issue Detection Criteria

**Create meta-issue when:**

1. **Unified Solution Pattern**:
   - ≥3 issues share identical/similar solution
   - Single implementation addresses all
   - Combined effort < sum of individual efforts

2. **Shared Root Cause Pattern**:
   - ≥2 issues stem from same underlying problem
   - Fixing root cause resolves all symptoms

3. **Enabling Pattern**:
   - Implementing solution X enables solutions Y, Z
   - Example: Adding capability makes other features possible

4. **Philosophy Alignment Pattern**:
   - Multiple issues fixed by same philosophy-driven refactor
   - Example: Adopting proper library solves multiple workaround issues

### 4.2 Meta-Issue Creation

**When meta-pattern detected:**

```markdown
META-ISSUE PROPOSAL:

Title: [Concise description of unified solution]
Example: "Modernize REPL with prompt_toolkit (solves bd-7, bd-8, bd-9, bd-10)"

Type: task (usually, since it's an implementation)
Priority: [Highest priority among solved issues]

Description:
[Comprehensive plan synthesized from individual investigations]

ISSUES SOLVED:
- bd-X: [Brief description]
- bd-Y: [Brief description]
- bd-Z: [Brief description]

UNIFIED APPROACH:
[Synthesized solution that addresses all issues]

BENEFITS OF UNIFIED SOLUTION:
- Efficiency: [Single implementation vs multiple]
- Coherence: [Addresses root cause vs symptoms]
- Philosophy: [Better alignment with principles]

IMPLEMENTATION PLAN:
[Merged from individual proposals]

FILES AFFECTED:
[Merged list from all issues]

ESTIMATED EFFORT:
- Combined approach: [X hours]
- Individual approaches: [Y hours]
- Savings: [Y-X hours]

ACCEPTANCE CRITERIA:
[Merged criteria from all issues]
✓ [Criterion from issue 1]
✓ [Criterion from issue 2]
✓ [Criterion from issue 3]
```

### 4.3 Meta-Issue Implementation

**Create the meta-issue:**

```bash
# Create new issue
bd --db .beads/<project>.db create "[Meta-issue title]" \
  --type task \
  --priority [P0-P3] \
  --design "[Full design from investigation synthesis]"

# Link all solved issues
for issue in bd-X bd-Y bd-Z; do
  bd --db .beads/<project>.db dep add [new-meta-issue] $issue --type blocks
done
```

## Phase 5: Update Beads with Findings

### 5.1 Update Investigation Status

**For each investigated issue:**

```bash
# Update with investigation marker and findings
bd --db .beads/<project>.db update bd-X --notes "🔍 INVESTIGATION COMPLETE - See bd-META for implementation

[Full investigation report from beads-investigator agent]"
```

**Investigation marker patterns:**
- `🔍 INVESTIGATION COMPLETE - See bd-X for implementation` (if meta-issue created)
- `🔍 INVESTIGATION COMPLETE - Awaiting implementation decision` (standalone)
- `🔍 INVESTIGATION COMPLETE - Needs [context]` (blocked on info)

### 5.2 Link Related Issues

**Create dependency relationships:**

```bash
# When investigation identifies dependencies
bd --db .beads/<project>.db dep add bd-X bd-Y --type blocks
bd --db .beads/<project>.db dep add bd-X bd-Z --type enables
```

**Relationship types:**
- `blocks`: Issue A must be solved before B
- `depends-on`: Issue A needs B completed
- `related`: Issues are related but not blocking

### 5.3 Export to JSONL

```bash
# Always export after updates
bd --db .beads/<project>.db export -o .beads/<project>.jsonl
```

## Phase 6: Comprehensive Report

### 6.1 Report Structure

```markdown
# 🔍 BEADS INVESTIGATION REPORT

**Date**: [ISO timestamp]
**Issues Investigated**: [count]
**Meta-Issues Created**: [count]
**Project**: [name from AGENTS.md]

## Summary

[High-level overview of findings]

## Individual Investigations

### bd-X: [Title]
**Root Cause**: [Brief summary]
**Solution**: [Brief summary]
**Status**: [Investigation status]
**Related**: [Related issue IDs]

[Repeat for each issue...]

## Meta-Pattern Analysis

### Pattern 1: [Pattern Name]
**Issues**: bd-A, bd-B, bd-C
**Shared Element**: [Root cause / solution / file / principle]
**Significance**: [Why this matters]

[Repeat for each pattern...]

## Meta-Issues Created

### bd-META-1: [Title]
**Solves**: bd-X, bd-Y, bd-Z
**Approach**: [Brief description]
**Benefits**: [Why unified solution is better]
**Priority**: [P0-P3]
**Estimated Effort**: [X hours]

[Repeat for each meta-issue...]

## Relationship Graph

```
[Text-based visualization of issue relationships]

bd-7 (REPL editing)     \
bd-8 (REPL Ctrl-C)       } → bd-19 (prompt_toolkit) [BLOCKS ALL]
bd-9 (REPL paste)        /
bd-10 (REPL length)     /

bd-14 (validation) → bd-15 (contracts) [RELATED]
```

## Updated Issues

**Investigation markers added to:**
- bd-X: "🔍 INVESTIGATION COMPLETE - See bd-META-1 for implementation"
- bd-Y: "🔍 INVESTIGATION COMPLETE - Awaiting decision"
- bd-Z: "🔍 INVESTIGATION COMPLETE - Needs user input"

**Dependencies created:**
- bd-META-1 blocks: bd-X, bd-Y, bd-Z
- bd-A enables: bd-B

## Recommendations

### Immediate Actions
1. [Action 1 with justification]
2. [Action 2 with justification]

### Implementation Priority
1. **High**: [bd-IDs] - [Why urgent]
2. **Medium**: [bd-IDs] - [Why important]
3. **Low**: [bd-IDs] - [Why can wait]

### Philosophy Observations
- [Insight 1]: [What investigations revealed about project health]
- [Insight 2]: [Alignment opportunities]

## Next Steps

1. **Review**: User reviews findings and approves meta-issues
2. **Decide**: User chooses which investigations to implement
3. **Implement**: Use relevant agents (modular-builder, zen-architect, etc.)
4. **Close**: Close resolved issues after implementation verified

---

**All findings exported to**: .beads/<project>.jsonl
**Database updated**: .beads/<project>.db

**Search for investigations**:
```bash
bd --db .beads/<project>.db list --status open | grep "🔍 INVESTIGATION COMPLETE"
```
```

### 6.2 Report Delivery

**Present to user**:
- Complete report (above structure)
- Clear next steps
- Ask for guidance on priorities
- Offer to implement via other agents

## Special Considerations

### Working in Any Project

**Adaptability Requirements**:
```
✓ Find AGENTS.md (may be in root, may be elsewhere)
✓ Find .beads/ directory (may have any project name)
✓ Determine database filename (*.db in .beads/)
✓ Read project-specific philosophy from AGENTS.md
✓ Respect project-specific conventions
```

**Generic Patterns**:
```
❌ Don't assume "amplifier-dev" as project name
❌ Don't assume specific file paths
❌ Don't assume specific philosophies
✅ DO discover project structure
✅ DO read project AGENTS.md
✅ DO adapt to project conventions
```

### Error Handling

**When issues occur:**

```
Beads DB not found:
→ Report clearly: "No .beads/ directory found in [path]"
→ Suggest: User needs to initialize beads tracker

AGENTS.md not found:
→ Report: "No AGENTS.md found, using general investigation approach"
→ Proceed without project-specific context

Agent failures:
→ Continue with other investigations
→ Report failed investigations separately
→ Don't block on single failure

No investigation markers found:
→ Report: "All open issues already investigated"
→ Offer to re-investigate or update existing investigations
```

### Efficiency Patterns

**Context Management**:
```
✓ Reference @AGENTS.md (don't duplicate)
✓ Launch all agents in SINGLE message
✓ Agents return focused reports (not full context)
✓ Main thread synthesizes (doesn't duplicate agent work)
```

**Parallel Execution**:
```
For 5 issues:
  Sequential (bad): 5 separate Task calls = 5 messages = slow
  Parallel (good): 1 message with 5 Task calls = fast + preserved context
```

## Philosophy Alignment

This command embodies the Amplifier philosophy:

**Specialization**: One agent per issue investigation
**Orchestration**: Command coordinates, doesn't duplicate work
**Context Management**: Fork for investigation, return only essentials
**Pattern Recognition**: Meta-analysis finds emergent insights
**Automation**: Reduces manual work through systematic process
**Quality**: Thorough investigation before implementation

## Success Criteria

Investigation session is successful when:

✓ All selected issues have investigation markers
✓ Meta-patterns identified and documented
✓ Meta-issues created where appropriate
✓ All related issues linked via dependencies
✓ Comprehensive report delivered
✓ User has clear next steps

## Additional Guidance

$ARGUMENTS
