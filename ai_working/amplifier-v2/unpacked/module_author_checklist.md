# module_author_checklist.md

For new or updated modules (orchestrator, provider, tool, agent, context, hooks):

- [ ] Implements only the **stable Protocol**; no reliance on core internals.
- [ ] Uses `context.log` for structured logs; avoids stdout prints and separate files.
- [ ] Emits or consumes **standard events** when appropriate.
- [ ] Handles its own failures; returns errors through the interface; never crashes the kernel.
- [ ] Configuration is explicit and documented; supports sane defaults within the module.
- [ ] Avoids long-running blocking I/O on the main loop; consider batching or async if needed.
- [ ] Includes tests (unit + integration where applicable).