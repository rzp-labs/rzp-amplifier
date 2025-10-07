# MIGRATION_KERNEL_ALIGNMENT.md

Goal: **Lock in the kernel boundary** now so policy lives in the app layer and the **core stays tiny & stable.**

## 1) Core session owns *mechanism*, not *policy*
**Before:** `AmplifierSession` selected defaults and read config files.  
**After:** `AmplifierSession(config: dict, loader: ModuleLoader|None)`
- Remove: internal `_get_default_config()` / file I/O.
- Require: orchestrator + context in `config` (error if missing).
- Keep: mechanism-only helpers (plan validation, dict merge).

### Actions
- Move TOML parsing & precedence out of `amplifier-core` into CLI/app.
- Keep core free of user/project path knowledge.

## 2) ModuleLoader is parameterized
- API: `ModuleLoader(search_paths: list[Path]|None = None)`
- Discovery order: entry points → explicit `search_paths` → `AMPLIFIER_MODULES` env (if provided).
- No baked-in defaults for filesystem discovery inside core.

## 3) App/CLI resolves configuration
- Precedence: **default < user < project < --config < inline**.
- Build a **Mount Plan**: orchestrator, context, providers, tools, hooks (+ per-module config).
- Instantiate: `AmplifierSession(plan, ModuleLoader(search_paths))`.

## 4) Tests
- Update core tests to pass dicts and mount mocks directly.
- Add app-layer tests for config precedence.

## 5) Observability (fast follow)
- Implement `hooks-logging` with `session_id`, `request_id`, `span_id`/`parent_span_id` and JSONL schema v1.
- Implement `hooks-redaction` (secrets/PII) and enable by default.
- Ensure core emits lifecycle events: session/prompt/tool/provider/context/artifact/policy.

## Non-goals in this migration
- Changing orchestrator logic, provider behavior, or tool semantics.
- Implementing exporters (OTel) in core—those remain plugins.
