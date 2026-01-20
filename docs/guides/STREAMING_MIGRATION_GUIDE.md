# Streaming Migration Guide (ADOPT1)

This guide defines the first Work IR migration for world streaming, paging, and
data access. It is **derived work** and must be schedulable, budgeted, and
law-gated.

## Migration State
- **MIGRATION_STATE = DUAL**
- Legacy streaming remains available but is compared to Work IR output.
- Mismatches are recorded deterministically; no silent fallback.

## System Overview
`WorldStreamingSystem` implements `ISimSystem` and emits Work IR tasks only.

Required identity:
- `system_id = "WORLD_STREAMING"` (stable hash)
- `category = DERIVED`
- `determinism_class = DERIVED`
- `law_targets = [EXEC.DERIVED_TASK, WORLD.DATA_ACCESS]`

## Task Emission
Tasks represent **requests**, not IO:
- `OP_STREAM_LOAD_CHUNK`
- `OP_STREAM_UNLOAD_CHUNK`

Each task must declare:
- AccessSet reads:
  - interest set inputs
  - streaming cache metadata (read-only)
- AccessSet writes:
  - streaming cache metadata for the target chunk
- CostModel:
  - IO-heavy, degradable priority

All task IDs, AccessSet IDs, and CostModel IDs must be stable and derived from
the system ID + local ID using `dom_work_graph_builder_make_id(...)`.

## Budgeting & Degradation
Fidelity tiers control work volume:
- `focus` / `micro`: emit more tasks
- `meso`: moderate
- `macro`: minimal
- `latent`: no tasks

Budget hints clamp total emitted tasks per tick. When budgets are tight:
- load requests are prioritized
- unload requests are delayed
- stale cached data is tolerated

## DUAL-Path Validation
While DUAL:
- legacy plan and IR plan both run
- plans are compared deterministically
- mismatches increment a counter (no silent accept)

## Prohibitions
- No direct IO or background streaming in gameplay code.
- No blocking the main loop for streaming.
- No implicit access without Work IR tasks.

## Tests
`engine/tests/streaming_work_ir_tests.cpp` validates:
- deterministic emission
- budget enforcement
- degradation behavior
- law refusal handling
- legacy vs IR parity
