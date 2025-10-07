# kernel_boundary_checklist.md

Use this checklist for any change that touches `amplifier-core`:

- [ ] Is this **mechanism** (coordination, lifecycle, contracts) and **not policy** (defaults, selection, formatting)?
- [ ] Could this live cleanly as a module instead? If yes, **move it**.
- [ ] Is the **interface narrow** and **additive**? (Avoid breaking changes.)
- [ ] Are **failure modes isolated**? (Hook errors do not crash core.)
- [ ] Are **events emitted** at meaningful lifecycle points?
- [ ] No file I/O, env lookups, or path defaults in core.
- [ ] No provider/tool specific logic or data formats in core.
- [ ] Tests: golden compatibility, deterministic failure behavior.
