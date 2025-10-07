# PR_PLAN.md

This plan lands kernel-alignment in **two PRs** for clarity and bisectability.

## PR 1 — Kernel boundary & loader parameterization
**Repos:** `amplifier-core`, `amplifier-cli`  
**Changes:**
- `amplifier-core`: `AmplifierSession(config, loader=None)`; remove internal defaults & file I/O.
- `amplifier-core`: `ModuleLoader(search_paths=None)`; discovery uses entry points → `search_paths` → env var.
- Update core tests to pass configs directly; adjust mocks.
- No functional change to orchestrator/providers/tools behavior.

**Acceptance:**
- Unit tests green; new tests cover missing-config error and loader search_paths precedence.

## PR 2 — App-layer config resolution & docs
**Repos:** `amplifier-cli`, `docs`  
**Changes:**
- Implement `resolve_app_config()` (default < user < project < --config < inline).
- Build and pass **Mount Plan** + `search_paths` to kernel.
- Add docs: `KERNEL_PHILOSOPHY.md`, `config_resolution.md`, `event_taxonomy.md`.
- Wire `amplifier logs tail` (optional) if not present.

**Acceptance:**
- CLI e2e tests for precedence.
- Developer docs updated; CHANGELOG notes kernel boundary change.

## Fast follow (separate PRs)
- `hooks-logging` + `hooks-redaction` (default-on).
- Optional `hooks-otel-exporter`, `hooks-stats`.
