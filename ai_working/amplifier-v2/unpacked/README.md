# Amplifier Kernel Alignment — Handoff Packet
_Last updated: 2025-10-07T18:01:58Z_

This packet provides everything a developer needs to **align the current WIP codebase with the Kernel Philosophy** and to adopt the **logging/observability** posture without prior context.

## Contents
- `KERNEL_PHILOSOPHY.md` — Kernel mindset (mechanism not policy, tiny/stable core, open edges/closed center).
- `MIGRATION_KERNEL_ALIGNMENT.md` — Concrete actions to move policy out of core and keep the kernel minimal.
- `config_resolution.md` — App-layer config precedence (default < user < project < --config < inline).
- `event_taxonomy.md` — Canonical lifecycle events to emit across orchestrator/providers/tools/context.
- `logging_schema_v1.json` — JSON schema for unified JSONL logs (stable, additive).
- `Amplifier-Logging-Observability-Addendum.md` — Detailed critique + adoption plan for logging hooks and IDs.
- `PR_PLAN.md` — Step-by-step commit plan to implement changes safely.
- `CODEBASE_LAYOUT.txt` — Snapshot of current repo structure for orientation.

## TL;DR
- **Core stops doing policy & file I/O.** Core accepts a *resolved plan*; app/CLI resolves config and search paths.
- **Loader is parameterized.** App passes search paths; core does not hard-code discovery locations.
- **Loop remains a module.** Competing orchestrators are welcome; core only defines the Protocol.
- **Observability via hooks.** Logging is a plugin; JSONL is canonical; redaction/correlation IDs are policy outside core.

For rationale and philosophy, see `KERNEL_PHILOSOPHY.md`.
