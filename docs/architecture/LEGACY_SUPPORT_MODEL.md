# Legacy Support Model (OPS1)

Status: FROZEN.  
Scope: honest behavior for legacy binaries and mixed-version artifacts.

## What Legacy Binaries Can Do

- Inspect data, packs, and manifests.
- Replay and export when compatibility_mode permits.
- Produce compat_report for every load/join/run/update/migrate operation.

## What Legacy Binaries Cannot Do

- Simulate mechanics they do not implement.
- Mutate authoritative state when compatibility is degraded or frozen.
- Proceed without explicit compat_report disclosure.

## Mode Selection Rules

- Missing required capabilities ⇒ `refuse`.
- Missing non-critical capabilities ⇒ `degraded` or `inspect-only`.
- Unknown or future-only artifacts ⇒ `frozen` or `inspect-only`, never `full`.

## Honesty Requirements

- No silent compatibility hacks or auto-upgrades.
- Explicit refusal semantics must be surfaced in all interfaces.
