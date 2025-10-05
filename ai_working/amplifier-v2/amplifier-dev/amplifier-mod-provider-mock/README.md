# Amplifier Mock Provider Module

Mock LLM provider for testing Amplifier without API calls.

## Purpose

Provides pre-configured responses for testing and development without calling real LLM APIs.

## Contract

**Module Type:** Provider
**Mount Point:** `providers`
**Entry Point:** `amplifier_mod_provider_mock:mount`

## Configuration

```toml
[[providers]]
module = "provider-mock"
name = "mock"
config = {
    responses = [
        "Response 1",
        "Response 2",
        "Response 3"
    ]
}
```

## Behavior

- Returns responses from configured list in rotation
- Can simulate tool calls when prompt contains "read"
- No external API calls
- No authentication required

## Dependencies

- `amplifier-core>=1.0.0`
