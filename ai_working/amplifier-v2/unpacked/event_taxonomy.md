# event_taxonomy.md

Canonical lifecycle events emitted by the kernel and orchestrator. Names are **stable**; payloads can **add fields** over time (additive evolution).

- `session:start` / `session:end` — session lifecycle (includes `session_id`).
- `prompt:submit` / `prompt:complete` — top-level prompt boundaries (`request_id`).
- `plan:start` / `plan:end` — orchestration planning (if used).
- `provider:request` / `provider:response` / `provider:error` — model calls.
- `tool:pre` / `tool:post` / `tool:error` — tool invocation lifecycle.
- `context:pre_compact` / `context:post_compact` — context management.
- `artifact:write` / `artifact:read` — files, diffs, external artifacts.
- `policy:violation` — sandbox/safety checks; `approval:required/granted/denied` if applicable.

**Fields (common):**
- `ts`, `level`, `session_id`, `request_id?`, `span_id?`, `parent_span_id?`  
- `component` (`core|hook|tool|provider|context|agent`), `module?`  
- `event`, `message`, `status` (`ok|error|denied|skipped`), `duration_ms?`  
- `data` (event-specific, JSON object)
