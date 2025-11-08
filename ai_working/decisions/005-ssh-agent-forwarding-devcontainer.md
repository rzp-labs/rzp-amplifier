# ADR 005: SSH Agent Forwarding for Devcontainer Ansible Access

**Date**: 2025-11-07
**Status**: Proposed
**Context**: Infrastructure automation with Ansible

## Problem

Need to run Ansible from devcontainer to target hosts with:
- SSH keys managed by 1Password SSH agent
- Two macOS development hosts
- Devcontainer required for dependency isolation
- Current workflow: SSH into devpod from host

## Decision

Use SSH agent forwarding to provide devcontainer access to 1Password SSH agent.

### Configuration

**On each macOS host** (`~/.ssh/config`):
```ssh-config
Host *.devpod
  ForwardAgent yes
  IdentityAgent "~/Library/Group Containers/2BUA8C4S2C.com.1password/t/agent.sock"
```

**No devcontainer changes needed** - agent forwarding happens automatically when SSHing into devpod.

## Rationale

### Philosophy Alignment

**Ruthless Simplicity**:
- 2-line config change per host
- Zero custom code
- Uses SSH agent forwarding as designed

**Present-Moment Focus**:
- Solves actual current need (SSH to targets)
- Doesn't build infrastructure for hypothetical problems
- Works with existing workflow

**Trust in Standard Tools**:
- SSH agent forwarding is battle-tested
- 1Password agent integration is documented
- DevPod handles forwarding automatically

### Alternatives Considered

**1. Git-Pull-Per-Host** (each host pulls repo, runs locally):
- ✅ Simple, works with current setup
- ❌ Perceived "WIP not centralized" issue (actually fine!)
- **Rejected**: Agent forwarding is simpler

**2. Centralized Docker-Host** (devcontainer on target machine):
- ✅ WIP centralized
- ❌ Loses local development experience
- ❌ Adds network latency
- ❌ Single point of failure
- **Rejected**: Over-engineering, violates simplicity

**3. ProxyJump from Host** (run Ansible from host, jump through devpod):
- ✅ Zero devcontainer config
- ❌ Defeats devcontainer dependency isolation purpose
- **Rejected**: Not solving the right problem

## Consequences

### Positive

- Minimal configuration (2 lines per host)
- No devcontainer code changes
- Works with existing SSH workflow
- Each host independent (clear failure isolation)
- 1Password keys available inside devcontainer
- Standard SSH agent forwarding (well-understood)

### Negative

- Each host must configure `~/.ssh/config` independently
- WIP stays local (must commit/push to sync between hosts)
- **Both are normal** - not actual problems

### Neutral

- Each developer pulls independently
- Git handles coordination (as designed)
- No centralized infrastructure needed

## Implementation

**Step 1**: Add to `~/.ssh/config` on each macOS host
**Step 2**: Verify with `ssh rzp-amplifier.devpod && ssh-add -l`
**Step 3**: Document in `infrastructure/docs/DEVELOPMENT.md`
**Step 4**: Update infrastructure README

## Review Triggers

- If agent forwarding proves unreliable
- If we add >2 development hosts and coordination becomes painful
- If 1Password agent changes socket location
- If devpod changes forwarding behavior

## Notes

**Multi-host WIP "problem"**: This isn't actually a problem requiring solution. Git is designed for this workflow. Commit when ready, push when sharing. Standard practice.

**Why this wins**: Solves exact current need with minimal complexity. Doesn't build infrastructure for hypothetical futures.
