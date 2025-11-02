# [DECISION-002] Pure Delegation Architecture for Recursive Workspace

**Date**: 2025-11-01
**Status**: Active
**Superseded by**: N/A

## Context

The amplifier workspace uses git submodules (orchestrator, infrastructure) to organize projects. Developers work from the parent workspace directory, never navigating into submodules directly. The existing recursive Makefile system (`recursive.mk`) delegates operations to submodules, which was 90% working.

**Problem discovered**: Running `make test` from parent workspace caused 6 ModuleNotFoundError failures. Root cause was parent pytest discovering submodule test files before Makefile delegation occurred, attempting to import from packages (orchestrator.config, orchestrator.models, etc.) that aren't installed in the parent's virtual environment.

**User requirements**:
- Work always occurs from parent workspace
- Recursive operations (formatting, linting, typechecking, testing) must work across all projects
- All amplifier features (hooks, checks, tests) must function regardless of which project is being modified
- Example: "if commands are run when working on @infrastructure/ all claude code hooks should fire off as they would if we were modifying the workspace directory"

## Decision

Implement **Pure Delegation Architecture** where the parent workspace delegates ALL operations to submodules via Makefile without importing their code.

### Three-Part Implementation

1. **pytest.ini exclusion**: Configure parent pytest to discover only `testpaths = tests`, excluding submodule directories from discovery
2. **Makefile clarity**: Separate parent-only (`check`, `test`) from recursive (`check-all`, `test-all`) operations with explicit naming
3. **Path-based hooks**: Claude Code hooks detect file paths to determine which project was modified and delegate checks appropriately

## Rationale

**zen-architect consultation recommended Pure Delegation** after evaluating three approaches:

### Why Pure Delegation Wins

- **Aligns with project philosophy**: Embodies ruthless simplicity and modular design principles
- **Leverages existing system**: Current recursive.mk system already 90% working
- **True independence**: Submodules remain standalone "bricks" with own venvs, dependencies, and build systems
- **Scalable**: Can add any number of submodules with different tech stacks without coupling
- **Clear boundaries**: No ambiguity about when to import vs delegate
- **Minimal implementation**: pytest.ini is 15 lines, Makefile changes are renaming, hook is straightforward bash

## Alternatives Considered

### Option A: Pure Delegation ✅ (CHOSEN)

**Description**: Parent delegates ALL operations to submodules via Makefile without importing their code.

**Pros**:
- True submodule independence
- Philosophy aligned (ruthless simplicity, modular design)
- Current system 90% working
- Scalable to multiple submodules with different tech stacks

**Cons**:
- Cannot write integration tests in parent that import from multiple submodules

### Option B: Editable Installs ❌ (REJECTED)

**Description**: Install submodules as editable packages (`pip install -e`) in parent venv.

**Pros**:
- Allows cross-submodule imports
- Single pytest invocation discovers all tests
- IDE import resolution works automatically

**Cons**:
- **Violates standalone principle**: Submodules no longer independent
- **Dependency conflicts**: Parent and submodule dependencies can conflict in shared venv
- **Blurs boundaries**: Unclear architectural separation
- **Against modular design philosophy**: Tight coupling between modules

**zen-architect assessment**: "Goes against architectural principles"

### Option C: Hybrid Approach ❌ (REJECTED)

**Description**: Mix editable installs for some submodules with delegation for others.

**Pros**:
- Flexibility in some scenarios

**Cons**:
- **Complexity**: Mixing patterns creates cognitive overhead
- **Unclear rules**: When to import vs delegate becomes ambiguous
- **Harder maintenance**: Two patterns to understand and maintain
- **Worst of both worlds**: Gets neither the simplicity of delegation nor the convenience of imports

**zen-architect assessment**: "Adds unnecessary complexity"

## Consequences

### Positive

- **Submodules remain truly standalone**: Can be cloned and used independently
- **No dependency conflicts**: Each submodule has isolated virtual environment
- **Clear developer workflow**: Always work from parent, explicit commands for scope
- **Philosophy compliance**: Embodies ruthless simplicity and modular design
- **Scalable**: Adding new submodules requires only 4 file updates

### Negative (Trade-offs Accepted)

- **No cross-submodule imports in tests**: Cannot write `import orchestrator; import infrastructure` in parent tests
  - **Mitigation**: Use API-level integration tests (MCP/HTTP calls) instead of import-based tests
  - **Why acceptable**: Aligns with service architecture where modules communicate via APIs

### Risks

- **Hook path detection uncertainty**: Claude Code hook protocol may require refinement based on actual INPUT_JSON structure
  - **Mitigation**: Hook includes logging to `/tmp/claude-hook-post-tool-use.log` for debugging
  - **Fallback**: Can use git diff to detect recent changes if hook data insufficient

- **Developer confusion**: Team might expect `make check` to recursively check all projects
  - **Mitigation**: Clear naming (`check` vs `check-all`), comprehensive documentation, help text in Makefile

## Review Triggers

This decision should be reconsidered if:

- [ ] **Adding 5+ submodules**: Delegation pattern may become unwieldy at scale
- [ ] **Cross-submodule integration tests needed**: If API-level tests prove insufficient
- [ ] **Performance issues**: If recursive delegation becomes measurably slow
- [ ] **Team feedback**: If developers consistently find the model confusing after 3 months
- [ ] **Hook reliability problems**: If path-based detection proves unreliable

## Implementation Details

### Files Changed

- `pytest.ini` (new): Excludes submodules from parent pytest discovery
- `Makefile` (modified): Renamed recursive targets with `-all` suffix
- `.claude/hooks/post-tool-use.sh` (new): Path-based project detection and delegation
- `docs/architecture/recursive_workspace.md` (new): Comprehensive architecture documentation
- This decision record

### Success Criteria

- ✅ `make test` from parent runs ONLY parent tests (no ModuleNotFoundError)
- ✅ `make test-all` from parent runs parent + all submodule tests
- ✅ Each submodule uses own isolated .venv during operations
- ✅ Hooks detect file modifications and run appropriate project checks
- ✅ All existing tests pass
- ✅ Philosophy requirements met (ruthless simplicity, modular design)

## References

- **DDD Phase 1 Plan**: [ai_working/ddd/plan.md](../ddd/plan.md)
- **zen-architect Analysis**: Comprehensive evaluation of architectural approaches (2025-11-01)
- **Implementation Philosophy**: [ai_context/IMPLEMENTATION_PHILOSOPHY.md](../../ai_context/IMPLEMENTATION_PHILOSOPHY.md)
- **Modular Design Philosophy**: [ai_context/MODULAR_DESIGN_PHILOSOPHY.md](../../ai_context/MODULAR_DESIGN_PHILOSOPHY.md)
- **Architecture Documentation**: [docs/architecture/recursive_workspace.md](../../docs/architecture/recursive_workspace.md)
- **User Requirements**: Original conversation identifying recursive testing issue and constraints

## Notes

This decision was made through Document-Driven Development (DDD) process with explicit approval gate. The Pure Delegation pattern was unanimously recommended by zen-architect after systematic analysis and aligns perfectly with the project's core philosophy of ruthless simplicity and modular design.

The 6 ModuleNotFoundError failures were the symptom that prompted this architectural decision, but the solution addresses the broader question of how parent and submodules should interact in a recursive workspace structure.
