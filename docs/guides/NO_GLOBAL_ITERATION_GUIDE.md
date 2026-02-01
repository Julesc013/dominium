Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# No-Global-Iteration Guide (PERF2)

This guide defines the only acceptable patterns for macro stepping and the
forbidden patterns that CI will reject. It is enforceable law, not guidance.

## Allowed patterns

- Event-driven scheduling via `dg_due_sched` (next_due_tick + process_until).
- Interest-set bounded iteration over a precomputed, deterministic list.
- Bounded queues (priority queues or ring buffers) scoped to active objects.
- Explicit stable ordering by (due_tick, stable_key).

## Forbidden patterns

- Any “update all” or “tick all” loops over global registries.
- Iterating over every entity/region/market/city each tick.
- Unbounded scans over MAX-capacity arrays in tick entrypoints.
- Background catch-up threads used to hide global sweeps.

## CI enforcement

CI check: `PERF-GLOBAL-002`
- Mechanism: static scan for global-iteration patterns in authoritative paths.
- Failure: merge is blocked until the loop is replaced with a due-event schedule.

## Migration allowlist (timeboxed)

No allowlisted global sweeps are approved. Any temporary exception MUST be
documented here with a removal deadline and a CI matrix update.