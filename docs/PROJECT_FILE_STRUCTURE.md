# Project File Structure: The Three-File Pattern

**Standardized documentation pattern for Amplifier workspace and submodule projects**

---

## Overview

The Amplifier workspace uses a three-file documentation pattern to provide clear separation of concerns while maintaining comprehensive guidance for different audiences:

1. **README.md** - User-facing documentation (discovery and quick start)
2. **AGENTS.md** - Comprehensive AI assistant guidance (technical implementation)
3. **CLAUDE.md** - Claude Code-specific orchestration (strategic coordination)

**Why three files instead of one?**

- **Audience separation** - External users vs AI assistants vs Claude Code
- **Scope clarity** - What to use vs how to build vs how to orchestrate
- **Maintainability** - Changes to one audience don't clutter others
- **Reference hierarchy** - CLAUDE.md imports AGENTS.md, avoiding duplication

---

## The Three Files Explained

### README.md (User-Facing Documentation)

**Primary audience**: Human users discovering or setting up the project

**Purpose**: Get someone from "never heard of this" to "successfully running it"

**Core questions answered**:
- What is this project?
- Why would I use it?
- How do I install it?
- How do I run basic workflows?
- Where can I learn more?

**Tone**: Welcoming, tutorial-style, assumes no prior knowledge

**Structure pattern**:
```markdown
# Project Name: One-Line Hook

> Brief description or tagline

## QuickStart
- Prerequisites
- Installation
- First command

## Features To Try
- Feature demonstrations
- Example commands
- Links to detailed docs

## Documentation
- Links to deeper guides

## License/Contributing
```

**What to include**:
- ✅ Installation instructions
- ✅ Quick start examples
- ✅ Feature showcase
- ✅ Links to detailed documentation
- ✅ Prerequisites and requirements

**What NOT to include**:
- ❌ Code style guidelines (belongs in AGENTS.md)
- ❌ Internal implementation details
- ❌ AI-specific orchestration patterns
- ❌ Philosophy deep dives (link to them instead)

**Real example**: `@README.md` (438 lines) - Amplifier's feature-rich showcase

---

### AGENTS.md (AI-Comprehensive Guidance)

**Primary audience**: All AI assistants (Claude, GPT, Codex, etc.)

**Purpose**: Provide complete technical context for implementation work

**Core questions answered**:
- How do I build/test/deploy this project?
- What are the code style conventions?
- What patterns should I follow?
- What anti-patterns should I avoid?
- What tools and commands are available?

**Tone**: Authoritative, comprehensive, assumes AI assistant context

**Structure pattern**:
```markdown
# AI Assistant Guidance

## CRITICAL: [Top-priority guidance]

## Important: [Key context like git submodule status]

## Build/Test/Lint Commands

## Code Style Guidelines

## File Organization Guidelines

## Implementation Philosophy
[Either inline or reference to detailed docs]

## Modular Design Philosophy
[Either inline or reference to detailed docs]
```

**What to include**:
- ✅ Build, test, lint commands
- ✅ Code style and formatting rules
- ✅ File organization patterns
- ✅ Implementation philosophy (inline or referenced)
- ✅ Dependency management instructions
- ✅ Testing strategies
- ✅ Common patterns and anti-patterns
- ✅ Configuration management
- ✅ Development workflow

**What NOT to include**:
- ❌ User-facing installation guides (belongs in README.md)
- ❌ Claude Code-specific orchestration (belongs in CLAUDE.md)
- ❌ Marketing content or feature showcases

**Real examples**:
- `@AGENTS.md` (758 lines) - Comprehensive workspace guidance
- `@infrastructure/AGENTS.md` (322 lines) - IaC-specific guidance
- `@orchestrator/AGENTS.md` (283 lines) - Orchestrator-specific guidance

---

### CLAUDE.md (Claude Code Orchestration)

**Primary audience**: Claude Code specifically

**Purpose**: Strategic coordination and context management for Claude Code sessions

**Core questions answered**:
- What files should I import for context?
- How should I orchestrate this work?
- What sub-agents are available?
- How should I manage context window?
- What parallel execution strategies should I use?

**Tone**: Directive, strategic, assumes Claude Code capabilities

**Structure pattern**:
```markdown
# CLAUDE.md

## Important: Consult [parent/shared] Context

## Import Key Context Files
- @AGENTS.md
- @../AGENTS.md (for submodules)
- @ai_context/PHILOSOPHY.md

## Critical Operating Principles
- Planning with TodoWrite
- Sub-agent delegation
- Parallel execution
- Clarifying questions

## [Project-specific] Patterns
- Context management
- Sub-agent strategies
- Code-based utilities

## Key Metrics for Success

## Philosophical Anchors

## Document Reference Protocol
```

**What to include**:
- ✅ Import statements (`@AGENTS.md`, `@../AGENTS.md` for submodules)
- ✅ Claude Code-specific operating principles
- ✅ Parallel execution strategies
- ✅ Sub-agent delegation patterns
- ✅ Context window management
- ✅ TodoWrite usage guidelines
- ✅ Reference to parent workspace context (for submodules)

**What NOT to include**:
- ❌ Duplicate content from AGENTS.md (import it instead)
- ❌ Generic AI guidance (belongs in AGENTS.md)
- ❌ User-facing documentation

**Real examples**:
- `@CLAUDE.md` (232 lines) - Workspace orchestration
- `@infrastructure/CLAUDE.md` (151 lines) - IaC orchestration (minimal, references parent)
- `@orchestrator/CLAUDE.md` (432 lines) - Orchestrator orchestration (comprehensive due to complexity)

---

## Decision Trees

### Where Does This Content Belong?

```
Is this content about...

┌─ How users discover/install? ────────────────────────► README.md
│
├─ How AI assistants implement? ──────────────────────► AGENTS.md
│
├─ How Claude Code orchestrates? ─────────────────────► CLAUDE.md
│
└─ Detailed philosophy/design? ───────────────────────► ai_context/ or docs/
                                                         (referenced by AGENTS.md)
```

### Is This Content Duplicated?

```
Before adding content, ask:

1. Is this already in another file?
   ├─ Yes → Reference it, don't duplicate
   └─ No → Continue

2. Could this fit in a parent/imported file?
   ├─ Yes → Add there, reference here
   └─ No → Continue

3. Is this specific to this audience?
   ├─ Yes → Add here
   └─ No → Belongs in shared location
```

### When to Reference vs Duplicate

**Reference when**:
- Content is maintained in one canonical location
- Content might change and needs single source of truth
- Content applies to multiple contexts

**Duplicate when**:
- Content is truly context-specific
- Duplication improves readability significantly
- Content is unlikely to diverge

**Example patterns**:

```markdown
<!-- Good: Reference -->
For implementation philosophy, see `@ai_context/IMPLEMENTATION_PHILOSOPHY.md`

<!-- Good: Import (CLAUDE.md) -->
# import the following files (using the `@` syntax):
- @AGENTS.md
- @../AGENTS.md  # For submodules

<!-- Bad: Duplicate 700 lines of philosophy in multiple files -->
```

---

## Templates

### README.md Template

```markdown
# Project Name: One-Line Value Proposition

> Brief description explaining what this project does

[Optional: Warning/Disclaimer callout for experimental projects]

Project overview - 2-3 sentences about what this is and who it's for.

## 🚀 QuickStart

### Prerequisites Guide

<details>
<summary>Click to expand prerequisite instructions</summary>

List prerequisites with installation commands per platform.

</details>

### Setup

```bash
# Clone and install
git clone [url] [name]
cd [name]
make install
```

### Get Started

```bash
# First command to run
[command]
```

**Create your first [thing] in N steps:**

1. Step one
2. Step two
...

**Learn more** with [Link to detailed guide]

---

## 📖 How to Use [Project]

### [Major Feature 1]

Description and code example

### [Major Feature 2]

Description and code example

---

## ✨ Features To Try

### 🔧 [Feature Category 1]

- _Tell Claude Code:_ `[example command]`
- _View the documentation:_ [Link]

### 🎨 [Feature Category 2]

- _Tell Claude Code:_ `[example command]`
- _Available specialists:_ List
- _View the documentation:_ [Link]

---

## Disclaimer

[If experimental]

## Contributing

[Contribution guidelines]

## Trademarks

[Legal notices if applicable]
```

---

### AGENTS.md Template

```markdown
# AI Assistant Guidance

This file provides guidance to AI assistants when working with code in this repository.

---

## 💎 CRITICAL: [Most Important Principle]

**[Critical guidance]** - Explanation

**User's role**: [What user decides]
**Your role**: [What AI implements]

**Anti-pattern**: [What not to do]
**Correct pattern**: [What to do instead]

**Remember**: [Key reminder]

---

## Important: [Second-Priority Context]

[Important context like git submodule status, decision tracking, etc.]

## Build/Test/Lint Commands

- Install dependencies: `[command]`
- Run all checks: `[command]`
- Run tests: `[command]`

## Dependency Management

- **ALWAYS use `[tool]`** for dependency management
- To add dependencies: `[command]`

## Code Style Guidelines

- [Style rule 1]
- [Style rule 2]
...

## Formatting Guidelines

- Line length: [number] characters
- [Formatting rule 1]
- [Formatting rule 2]
...

## File Organization Guidelines

- [Organization rule 1]
- [Organization rule 2]
...

## Testing Instructions

- [Testing approach]
- [How to run tests]
- [Test patterns to follow]

## Implementation Philosophy

[Either inline the philosophy OR reference it]

### Core Philosophy

[Key principles if inline]

### Core Design Principles

[Design principles if inline]

**OR**

For complete implementation philosophy, see `@ai_context/IMPLEMENTATION_PHILOSOPHY.md`

## Modular Design Philosophy

[Either inline OR reference]

**OR**

For complete modular design philosophy, see `@ai_context/MODULAR_DESIGN_PHILOSOPHY.md`

## [Project-Specific Sections]

[Add sections specific to this project's needs]
```

---

### CLAUDE.md Template

```markdown
# CLAUDE.md

This file provides guidance to Claude Code when working with code in this repository.

[For submodules: "This project is a git submodule within the Amplifier workspace."]

This project uses a shared context file (`AGENTS.md`) for common project guidelines. Please refer to it for information on build commands, code style, and design philosophy.

This file is reserved for Claude Code-specific instructions.

# import the following files (using the `@` syntax):

- @AGENTS.md
[- @../AGENTS.md  # For submodules]
[- @../CLAUDE.md  # For submodules]
- @DISCOVERIES.md
- @ai_context/IMPLEMENTATION_PHILOSOPHY.md
- @ai_context/MODULAR_DESIGN_PHILOSOPHY.md
[- Other philosophy files]

# Claude's Working Philosophy and Memory System

## Critical Operating Principles

- VERY IMPORTANT: Always think through a plan for every ask, and if it is more than a simple request, break it down and use TodoWrite tool to manage a todo list.
- VERY IMPORTANT: Always consider if there is an agent available that can help with any given sub-task.

<example>
[Examples of good patterns]
</example>

- VERY IMPORTANT: If user has not provided enough clarity to CONFIDENTLY proceed, ask clarifying questions.

## Parallel Execution Strategy

**CRITICAL**: Always ask yourself: "What can I do in parallel here?"

### When to Parallelize

[Guidelines]

### Common Patterns

[Examples]

### Anti-Patterns to Avoid

[Examples]

### Remember

[Key points]

### 1. Context Window Management

[Strategies]

### 2. Sub-Agent Delegation Strategy

[Guidance]

### 3. Creating New Sub-Agents

[Process]

### 4. My Role as Orchestrator

[Principles]

### 5. Code-Based Utilities Strategy

[Approach]

### 6. Human Engagement Points

[When to involve user]

### 7. Learning and Memory System

[Memory architecture]

### 8. Continuous Improvement Rhythm

[Improvement process]

## Key Metrics for Success

[Success criteria]

## Philosophical Anchors

[Core references]

## Document Reference Protocol

[How to work with referenced documents]
```

---

## Real-World Examples

### Workspace Level Pattern

**README.md** (438 lines):
- ✅ Feature showcase with extensive examples
- ✅ QuickStart with multiple entry points
- ✅ "Features To Try" sections with commands
- ✅ Links to deeper documentation
- ✅ Disclaimer and contribution info

**AGENTS.md** (758 lines):
- ✅ CRITICAL section on respecting user time
- ✅ Comprehensive build/test/lint commands
- ✅ Code style and formatting guidelines
- ✅ Inline philosophy sections (fully embedded)
- ✅ Decision tracking system
- ✅ Configuration management patterns

**CLAUDE.md** (232 lines):
- ✅ Imports AGENTS.md and philosophy files
- ✅ Parallel execution strategies with examples
- ✅ Sub-agent delegation patterns
- ✅ Context window management
- ✅ Document reference protocol

---

### Submodule Pattern: Infrastructure

**README.md** (232 lines):
- ✅ Focused on IaC quick start
- ✅ Stack overview
- ✅ Step-by-step deployment guide
- ✅ Structure explanation
- ✅ Common commands reference

**AGENTS.md** (322 lines):
- ✅ References parent workspace: `@../AGENTS.md`
- ✅ Project overview (IaC-specific)
- ✅ Git submodule awareness section
- ✅ IaC build/test commands
- ✅ Architecture overview (root orchestrator pattern)
- ✅ Philosophy alignment section (references parent)

**CLAUDE.md** (151 lines):
- ✅ Minimal - references parent heavily
- ✅ Imports parent CLAUDE.md: `@../CLAUDE.md`
- ✅ IaC-specific patterns (deployment flow, security)
- ✅ File organization
- ✅ Linting configuration

**What this shows**: Submodules can be lean by referencing parent context.

---

### Submodule Pattern: Orchestrator

**README.md** (154 lines):
- ✅ Overview of orchestrator purpose
- ✅ Quick start with prerequisites
- ✅ Core workflows explanation
- ✅ Architecture diagram
- ✅ Links to detailed documentation

**AGENTS.md** (283 lines):
- ✅ References parent workspace
- ✅ Git submodule awareness
- ✅ Write mode control (project-specific feature)
- ✅ Defensive utilities pattern (project-specific)
- ✅ Philosophy alignment section

**CLAUDE.md** (432 lines):
- ✅ Comprehensive due to project complexity
- ✅ Imports parent context files
- ✅ Write mode control emphasis (critical for this project)
- ✅ Module size discipline
- ✅ Workflow-specific guidance

**What this shows**: More complex projects have more comprehensive CLAUDE.md files.

---

## Common Patterns Across Files

### How CLAUDE.md Imports AGENTS.md

**Pattern**:
```markdown
# import the following files (using the `@` syntax):

- @AGENTS.md
- @DISCOVERIES.md
- @ai_context/IMPLEMENTATION_PHILOSOPHY.md
- @ai_context/MODULAR_DESIGN_PHILOSOPHY.md
```

**For submodules**:
```markdown
# import the following files (using the `@` syntax):

- @AGENTS.md
- @../AGENTS.md  # Parent workspace guidance
- @../CLAUDE.md  # Parent workspace Claude guidance
- @../DISCOVERIES.md
- @../ai_context/IMPLEMENTATION_PHILOSOPHY.md
```

**Why this works**: Claude Code's `@` syntax loads file content as context.

---

### How README.md Links to Other Docs

**Pattern**:
```markdown
- _Tell Claude Code:_ `[example command]`
- _View the documentation:_ [Link to detailed guide](docs/GUIDE.md)
```

**Benefits**:
- Keeps README.md concise
- Points users to detailed information
- Separates discovery from deep learning

---

### How to Reference Parent Workspace Context

**For submodules**:

```markdown
## Important: This is a Git Submodule

[Project] is a **standalone project** that lives as a git submodule within the Amplifier workspace. This means:

- **Independent version control** - Has its own git repository and history
- **Own dependencies** - Has its own `pyproject.toml` managed with `uv`
- **Own virtual environment** - Uses local `.venv/` (NOT parent workspace's `.venv`)
- **Clean separation** - No code imports from Amplifier (only follows its patterns)

**For general Amplifier workspace guidance, see `@../AGENTS.md` and `@../CLAUDE.md`.**
```

**Where this appears**:
- Top of AGENTS.md (submodules only)
- Top of CLAUDE.md (submodules only)
- Reminds AI of the submodule relationship

---

### Philosophical Content: Inline vs Referenced

**Workspace level** (typically inline):
```markdown
## Implementation Philosophy

[700+ lines of complete philosophy embedded in AGENTS.md]
```

**Submodule level** (typically referenced):
```markdown
## Philosophy Alignment

### Ruthless Simplicity

- [Key principles specific to this project]

### Infrastructure as Code Best Practices

- [Principles specific to this project]

**For complete philosophy**: See parent workspace `@../ai_context/IMPLEMENTATION_PHILOSOPHY.md`
```

**Decision factors**:
- Workspace: Inline (canonical location)
- Submodule: Reference parent OR inline if project-specific philosophy diverges

---

## Anti-Patterns to Avoid

### 1. Content Duplication

**❌ Bad**:
```markdown
<!-- In AGENTS.md -->
## Implementation Philosophy
[700 lines of philosophy]

<!-- In CLAUDE.md -->
## Implementation Philosophy
[Same 700 lines duplicated]
```

**✅ Good**:
```markdown
<!-- In AGENTS.md -->
## Implementation Philosophy
[700 lines of philosophy]

<!-- In CLAUDE.md -->
# import the following files (using the `@` syntax):
- @AGENTS.md
```

---

### 2. Audience Confusion

**❌ Bad**:
```markdown
<!-- In README.md -->
## Code Style Guidelines

- Line length: 120 characters
- Use Python type hints consistently
- Import statements at top of files
[Continues for 200 lines...]
```

**✅ Good**:
```markdown
<!-- In README.md -->
## Development

See [AGENTS.md](AGENTS.md) for code style and development guidelines.

<!-- In AGENTS.md -->
## Code Style Guidelines
[Complete guidelines here]
```

---

### 3. Missing Submodule Context

**❌ Bad** (in submodule AGENTS.md):
```markdown
# AI Assistant Guidance

## Build/Test/Lint Commands

- Install dependencies: `make install`
[No mention that this is a submodule]
```

**✅ Good**:
```markdown
# AI Assistant Guidance

**For general Amplifier workspace guidance, see `@../AGENTS.md` and `@../CLAUDE.md`.**

## Important: This is a Git Submodule

[Explanation of submodule relationship and implications]

## Build/Test/Lint Commands
[...]
```

---

### 4. Orphaned Philosophy

**❌ Bad**:
```markdown
<!-- README.md with extensive philosophy -->
## Our Design Philosophy

[5000 lines of philosophy in user-facing doc]
```

**✅ Good**:
```markdown
<!-- README.md -->
## Philosophy

We follow ruthless simplicity and modular design principles. See [DESIGN_PHILOSOPHY.md](docs/DESIGN_PHILOSOPHY.md) for details.

<!-- docs/DESIGN_PHILOSOPHY.md -->
[Complete philosophy document]

<!-- AGENTS.md references it -->
For implementation philosophy, see `@ai_context/DESIGN_PHILOSOPHY.md`
```

---

### 5. CLAUDE.md Without Imports

**❌ Bad**:
```markdown
# CLAUDE.md

## Operating Principles

[Duplicates everything from AGENTS.md]
```

**✅ Good**:
```markdown
# CLAUDE.md

# import the following files (using the `@` syntax):

- @AGENTS.md
- @DISCOVERIES.md

## Claude Code-Specific Guidance

[Only Claude-specific orchestration patterns]
```

---

### 6. Unclear File Boundaries

**❌ Bad**:
```markdown
<!-- Mixed concerns in README.md -->
# Project

## Installation
## Features
## Code Style for AI Assistants
## Claude Code Orchestration Strategies
## Build Commands
## User Guide
```

**✅ Good**:
```markdown
<!-- README.md: User-facing only -->
# Project

## Installation
## Features
## User Guide
## Documentation Links

<!-- AGENTS.md: AI implementation -->
## Build Commands
## Code Style
## Testing

<!-- CLAUDE.md: Orchestration -->
## Orchestration Strategies
## Context Management
```

---

## For New Projects

### Quick Start Checklist

When creating a new project (workspace or submodule):

- [ ] **Create README.md**
  - [ ] Add project overview and value proposition
  - [ ] Add QuickStart with prerequisites
  - [ ] Add feature showcase
  - [ ] Link to detailed documentation

- [ ] **Create AGENTS.md**
  - [ ] Add critical guidance section
  - [ ] Add build/test/lint commands
  - [ ] Add code style guidelines
  - [ ] Reference or inline philosophy
  - [ ] Add project-specific patterns

- [ ] **Create CLAUDE.md**
  - [ ] Import AGENTS.md
  - [ ] Add Claude Code operating principles
  - [ ] Add parallel execution strategies
  - [ ] Add sub-agent delegation patterns
  - [ ] Reference parent context (if submodule)

- [ ] **For Submodules Additionally**
  - [ ] Add git submodule awareness section to AGENTS.md
  - [ ] Reference parent workspace context in both AGENTS.md and CLAUDE.md
  - [ ] Import parent files in CLAUDE.md (`@../AGENTS.md`, `@../CLAUDE.md`)

---

### File Creation Order

**Recommended sequence**:

1. **README.md** (creates public face)
   - Defines what the project is
   - Establishes user-facing narrative

2. **AGENTS.md** (defines implementation approach)
   - Documents build/test/deploy
   - Establishes technical standards
   - Embeds or references philosophy

3. **CLAUDE.md** (adds orchestration layer)
   - Imports AGENTS.md
   - Adds Claude-specific strategies
   - References parent context (for submodules)

**Why this order?**
- Each file builds on the previous
- README.md forces clarity about project purpose
- AGENTS.md can reference README.md for context
- CLAUDE.md imports AGENTS.md, so AGENTS.md should exist first

---

### Validation Criteria

**Before considering the file set complete, verify**:

#### README.md
- [ ] Can a new user install and run the project from these instructions alone?
- [ ] Are features demonstrated with actual commands?
- [ ] Are links to detailed documentation provided?
- [ ] Is the value proposition clear in the first paragraph?

#### AGENTS.md
- [ ] Are all build/test/lint commands documented?
- [ ] Are code style guidelines comprehensive?
- [ ] Is philosophy either inlined or clearly referenced?
- [ ] For submodules: Is git submodule status explained?
- [ ] For submodules: Are parent workspace references included?

#### CLAUDE.md
- [ ] Does it import AGENTS.md (and parent files for submodules)?
- [ ] Are Claude Code-specific patterns documented?
- [ ] Is parallel execution strategy explained?
- [ ] Is sub-agent delegation covered?
- [ ] For submodules: Are parent context references clear?

#### Cross-File Validation
- [ ] Is there significant content duplication? (There shouldn't be)
- [ ] Are audiences clearly separated?
- [ ] Do links between files work?
- [ ] Can each file be read independently but together provide complete picture?

---

## Rationale for Key Decisions

### Why Three Files Instead of One?

**Decision**: Separate README.md (users), AGENTS.md (AI implementation), CLAUDE.md (orchestration)

**Rationale**:
- **Audience separation** - Users don't need AI orchestration strategies; AI doesn't need marketing content
- **Maintenance** - Changes to user instructions don't clutter AI guidance
- **Clarity** - Each file has a clear, single purpose
- **Scalability** - Easy to expand guidance for each audience independently

**Alternative considered**: Single README.md with all content
**Why rejected**: 2000+ line README.md with mixed audiences is difficult to navigate and maintain

---

### Why CLAUDE.md Imports AGENTS.md Instead of Duplicating?

**Decision**: CLAUDE.md uses `@` syntax to import AGENTS.md content

**Rationale**:
- **Single source of truth** - Build commands, code style documented once
- **Maintenance** - Changes to commands don't require updating multiple files
- **Clarity** - CLAUDE.md focuses on what's unique to Claude Code

**Alternative considered**: Duplicate content in both files
**Why rejected**: Maintenance burden, risk of divergence, unclear which file is authoritative

---

### Why Submodules Reference Parent Workspace?

**Decision**: Submodule AGENTS.md and CLAUDE.md explicitly reference parent workspace files

**Rationale**:
- **Context preservation** - AI understands relationship between submodule and workspace
- **Shared patterns** - Philosophy and patterns established at workspace level apply
- **Avoiding duplication** - Parent philosophy doesn't need to be repeated
- **Independence** - Submodule can still be used standalone (references are clear)

**Alternative considered**: Duplicate all parent content in submodule
**Why rejected**: Massive duplication, maintenance nightmare, unclear which version is canonical

---

### Why Inline Philosophy in Workspace but Reference in Submodules?

**Decision**: Workspace AGENTS.md contains full philosophy inline; submodules reference parent

**Rationale**:
- **Canonical location** - Workspace is the authoritative source
- **Submodule independence** - Submodules can override/extend if needed
- **Efficiency** - Most submodules share workspace philosophy
- **Clarity** - AI can find philosophy in one canonical place

**Alternative considered**: Philosophy always in separate files
**Why rejected**: Works for workspace but creates file sprawl; embedding in workspace AGENTS.md is more accessible

---

### Why Different README.md Lengths?

**Decision**: README.md length varies by project complexity (workspace: 438 lines, infrastructure: 232 lines)

**Rationale**:
- **Scope reflects complexity** - Workspace has many features; infrastructure is focused
- **User needs** - More features require more examples and documentation
- **Discovery** - Feature-rich projects need showcase; focused projects need clarity

**Alternative considered**: Standardize all README.md files to same length
**Why rejected**: Artificial constraint that doesn't match actual user needs

---

## Summary

The three-file pattern provides:

1. **Clear audience separation** - Users, AI implementers, Claude Code orchestrator
2. **Reduced duplication** - CLAUDE.md imports AGENTS.md; submodules reference parent
3. **Maintainability** - Single source of truth for each type of content
4. **Scalability** - Pattern works for workspace and submodules
5. **Flexibility** - Files can be expanded independently based on needs

**When to use this pattern**:
- All Amplifier workspace projects
- All git submodule projects
- Any project with AI-assisted development

**When to adapt it**:
- Very simple projects (README.md + AGENTS.md may be sufficient)
- Non-AI projects (README.md alone may be sufficient)

**Core principle**: Each file serves a distinct audience with minimal overlap.
