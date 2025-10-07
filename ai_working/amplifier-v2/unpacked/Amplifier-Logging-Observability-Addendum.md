# Amplifier Logging & Observability — Adoption Addendum and Critique
_Last updated: 2025-10-07T16:39:21Z_

**Purpose.** This addendum distills, critiques, and operationalizes the “Amplifier Logging & Observability System Design” so we can fold it cleanly into the modular kernel architecture (ultra-thin core + mount-point hooks). It highlights what we should adopt unchanged, what to tighten, and a concrete MVP → hardening plan with tests, schemas, and guardrails. fileciteturn1file0

---

## 1) Executive summary

**What’s strong and aligns well (adopt largely as-is):**

- **Ultra-minimal core, event-driven logging via hooks.** Keep core logging as mechanism (singleton JSONL writer), policy in a **Logging Hook module** that subscribes to lifecycle events. This matches our kernel + plugins model and keeps the core boring/stable. fileciteturn1file0
- **Unified JSONL pipeline as source of truth.** One canonical stream for core + modules enables replay, audits, and external transforms without fragmenting outputs. fileciteturn1file0
- **Early bootstrap visibility.** Core logger must be alive before plugin load; events take over once hooks mount. fileciteturn1file0
- **Non-interference guarantees.** Hook isolation + defensive handlers so logging can’t break the agent loop. fileciteturn1file0

**Where to tighten/extend before we ship:**
- **Privacy & secrets controls.** Add first-class redaction, opt-in model I/O capture, and field-level classification (never log env secrets, API keys, access tokens). 
- **Correlation beyond sessions.** Add `request_id`, `span_id`/`parent_span_id` so tool calls and provider calls nest under a prompt for precise causal traces.
- **Volume/safety.** Introduce sampling, size limits, rotation/retention, and a ring-buffer “flight recorder” mode.
- **Portable telemetry.** Keep JSONL canonical, but add an optional **OTel Exporter plugin** to map logs→OTLP and (later) lightweight metrics/traces—without polluting core.
- **Schema versioning.** Version the JSON schema so downstream consumers don’t break when we add fields.

---

## 2) Target architecture (concrete)

### 2.1 Modules and mount points
- **Core:** bootstrap logger (JSONL writer + handlers); hook dispatcher (already in core). No policy/formatting beyond JSON envelope. fileciteturn1file0
- **Hooks (plugins):**
  - **hooks-logging** _(default, enabled)_: subscribes to lifecycle + tool/provider events; builds structured log bodies; calls core logger. fileciteturn1file0
  - **hooks-redaction** _(default, enabled)_: scrub/transform event payloads (secrets, PII) before hooks-logging sees them.
  - **hooks-stats** _(optional)_: derive lightweight counters (tokens, tool counts) for dashboards (still write as JSONL “metrics” records).
  - **hooks-otel-exporter** _(optional)_: tail JSONL or consume events to emit OTLP logs/metrics to backends.

### 2.2 Event taxonomy (minimum viable)
We’ll emit these consistently from orchestrator, providers, tools, and context managers (names are stable surface area): fileciteturn1file0

- **session:start / session:end**
- **prompt:submit / prompt:complete** (top-level turn boundaries)
- **plan:start / plan:end** (if the loop plans)
- **provider:request / provider:response / provider:error**
- **tool:pre / tool:post / tool:error**
- **context:pre_compact / context:post_compact**
- **artifact:write** (e.g., file diff committed), **artifact:read**
- **policy:violation** (security/sandbox flags), **approval:required/granted/denied**

> _Note:_ The original doc already covers session, prompt, tool, and compaction events; we add provider, artifact, and policy events to close observability gaps. fileciteturn1file0

---

## 3) JSONL schema (v1)

All logs are one-object-per-line JSON. Keep it stable; only additive changes between minor versions.

```json
{
  "ts": "2025-10-07T12:34:56.789Z",
  "lvl": "INFO",                        // DEBUG|INFO|WARN|ERROR
  "schema": {"name":"amplifier.log","ver":"1.0.0"},
  "session_id": "s-9e8f…",
  "request_id": "r-12ab…",              // new per top-level prompt/turn
  "span_id": "sp-001",                  // per nested op (tool/provider); string
  "parent_span_id": "sp-000",           // null at roots
  "event": "tool:post",
  "component": "tool",                  // core|hook|tool|provider|context|agent
  "module": "filesystem",               // module/package name if applicable
  "message": "Wrote file with diff",
  "duration_ms": 1432,                  // when applicable
  "status": "ok",                       // ok|error|denied|skipped
  "redaction": {"applied": true, "rules":["secrets","pii-basic"]},
  "data": {
    "tool": "write_file",
    "path": "src/app.py",
    "lines_changed": 32,
    "diff_sha256": "…",                 // never inline huge diffs; point to artifact store
    "result_bytes": 0
  },
  "error": null                         // or { "type": "...", "msg": "...", "stack": "…" }
}
```

**Design notes**
- **`data` is the extensible payload** for each event; keep top-level stable & analytics-friendly.
- **Large bodies (model responses, big diffs)** are never inlined; store to an **artifact store** (local file path or blob store) and reference by content hash.
- **`redaction`** records what rules fired for transparency and audit.

---

## 4) Privacy, security, and governance

### 4.1 Field classification & defaults
- **Category A (safe operational):** timestamps, ids, durations, module names → always log.
- **Category B (potentially sensitive text):** prompts, model outputs, tool inputs/outputs → _**off by default**_; developers can **opt in** at `log.capture.model_io=true` or per-session.
- **Category C (secrets & credentials):** env vars, tokens, keys → **never log** (blocked at source).

### 4.2 Redaction pipeline (hooks-redaction)
- **Detectors:** regex for common secrets (AWS, Azure, GCP keys), JWTs, emails/phones; optional ML PII detector.
- **Actions:** replace with `"[REDACTED:TYPE]"`, or partial-hash (`"sk_live_…abcd"`). 
- **Config:** allowlist for domains/paths, max captured chars for context windows.
- **Proof of scrubbing:** include `redaction.applied` in each record.

### 4.3 Storage & retention
- **Rotation:** size/time-based rotation via core logger handlers.
- **Retention:** default 7–14 days in dev; org policy for prod. 
- **At-rest protection:** optional file encryption (fs-level or plugin). 
- **Access controls:** OS perms; optional integration with enterprise key management via exporter plugin.

---

## 5) Volume & safety levers

- **Log levels** (global + per-category overrides).
- **Sampling** (e.g., sample DEBUG at 10% or first N per minute).
- **Size limits** per field and per-record; truncate with indicator flags.
- **Flight recorder mode:** ring buffer in memory; on error, flush to disk for forensic capture.
- **Backpressure:** non-blocking writes with bounded queue; drop-policy only for DEBUG and mark drops in a heartbeat record.

---

## 6) Portable telemetry (optional, modular)

- Keep **JSONL canonical**.
- Add **hooks-otel-exporter** to map selected records to OTLP:
  - **Logs:** event→log; preserve `session_id` as trace id seed if tracing is enabled.
  - **Traces:** represent `request_id` as trace, `span_id`/`parent_span_id` as spans for tool/provider calls.
  - **Metrics:** counters (tokens, tool_invocations, errors) from hooks-stats.

> This stays out of core; exporter can be swapped (OTel, Splunk HEC, ELK) without changing logging policy. fileciteturn1file0

---

## 7) Developer experience (plugin authors)

- Use **`context.log`** for all plugin logs; no stdout prints; no separate files. fileciteturn1file0
- Prefer **structured logs**: `context.log.info("...", extra={"key": "val"})` → ends up in `data`.
- Emit **custom events** only if other plugins could benefit; otherwise log directly.
- Respect **size caps** and avoid emitting raw large payloads; write artifacts and reference by hash/path.

---

## 8) MVP → Hardening plan

### Phase A — MVP (ship fast)
- **Core:** JSONL logger init, rotation, level config; hook safety wrappers.
- **hooks-logging:** handle `session`, `prompt`, `tool`, `context` events; JSON schema v1; `session_id` & `request_id`; basic duration timing.
- **hooks-redaction:** baseline secrets + PII detectors; apply before logging.
- **CLI:** `amplifier logs tail --filter 'session_id=… level>=INFO'`

**Exit criteria**
- End-to-end dev session produces a coherent JSONL narrative.
- Secrets never appear in logs (unit + fuzz tests).

### Phase B — Hardening
- Add `provider:*` and `artifact:*` coverage; add `span_id`/nesting.
- Flight recorder mode; sampling; size caps; error budget tests.
- Optional **hooks-otel-exporter** and **hooks-stats**.

---

## 9) Test matrix (core + modules)

### Correctness
- **Event coverage:** every lifecycle point emits exactly one event with required fields.
- **Redaction:** seed with known secrets → confirm masked; false-positive/negative bounds.
- **Schema stability:** unknown fields ignored by consumers; version bump on breaking change.

### Reliability
- **Hook isolation:** inject exceptions into hooks-logging; agent loop continues; error is logged.
- **I/O failures:** simulate disk full; fallback path works; error surfaced once.
- **Load:** 10k events/min (synthetic); ensure no unbounded memory growth; backpressure policy respected.

### Privacy
- **No secrets regression:** snapshot-based test ensures keys never present even at DEBUG.
- **Opt-in model I/O:** when enabled, payloads present but scrubbed; when disabled, absent.

---

## 10) Implementation sketches

**Core bootstrap (pseudocode)**
```python
logger = JsonlLogger(path="~/.amplifier/logs/current.jsonl", rotation="100MB", level="INFO")
hooks = HookRegistry(on_error=lambda e: logger.error("hook_failed", { "err": str(e) }))
```

**Logging hook (pseudocode)**
```python
@hooks.on("tool:pre")
def on_tool_pre(evt, ctx):
    data = redact(evt.data)  # hooks-redaction
    logger.info("tool:pre", extra=build_record(evt, ctx, data))
```

**ID propagation**
```python
session_id = new_id("s-")
logger.set_context(session_id=session_id)
request_id = new_id("r-")  # per prompt
```

---

## 11) Open questions (pre-code review)

1) **Default model I/O capture:** off (privacy) or dev-only on?  
2) **Artifact store abstraction:** local-only initially or pluggable (fs/s3/blob)?  
3) **Span model:** keep simple IDs or adopt W3C traceparent/trace-id format to ease OTel export?  
4) **Config surface:** file (TOML/YAML) vs env vars; precedence and hot-reload?  
5) **User approvals:** Should approval flows also emit structured policy/decision entries? (recommended)

---

## 12) Final stance

Adopt the doc’s core: **core-minimal + hook-driven logging to unified JSONL**. Ship quickly with a **redaction-first** posture, strong **correlation IDs**, and **non-interference** guarantees. Keep OTel/export **modular**. This gives us durable auditability today and a clean runway to richer observability tomorrow—without compromising the kernel’s simplicity. fileciteturn1file0
