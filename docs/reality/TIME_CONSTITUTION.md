Status: DERIVED
Last Reviewed: 2026-02-26
Supersedes: none
Superseded By: none
Version: 1.0.0
Compatibility: Bound to `docs/canon/constitution_v1.md` and `docs/canon/glossary_v1.md`.

# Time Constitution

## Purpose
Define deterministic simulation-time governance where canonical ordering is tick-index based, variable simulation delta is policy-driven, and time travel is lineage branching only.

## A) Canonical Tick
- `tick_index` is the authoritative simulation time coordinate (`u64`).
- Deterministic scheduling, ordering, replay, and hash anchors use tick index only.
- Wall-clock is never an authoritative input.

## B) Simulation Time
Simulation time is derived from deterministic per-tick deltas:

`sim_time_seconds = Σ dt_sim_seconds(tick_i)`

Rules:
- `dt_sim` may vary per tick.
- Every applied `dt_sim` value must be deterministic and recorded in canonical tick metadata.
- `sim_time_seconds` is derived state and replay-computable from tick metadata.

## C) Variable UPS
- UPS (updates per real second) is runtime scheduling only.
- UPS variance may change render/host cadence but must not change authoritative outcomes.
- Authoritative truth evolution depends only on deterministic intents/processes, `tick_index`, and recorded `dt_sim` values.

## D) Time Control Processes
Time-rate control is process-driven and law-gated.

Canonical process surface:
- `process.time_set_rate`
- `process.time_pause`
- `process.time_resume`

Implementation compatibility note:
- Existing process id `process.time_control_set_rate` is retained as the canonical RS-3 rate-control implementation path.

Rules:
- Rate/pause changes are deterministic state transitions.
- No direct state mutation outside process execution.
- `dt_sim` selection uses deterministic quantization rules only.

## E) Time Travel
Time travel is branch creation from a committed checkpoint, never retroactive mutation.

Canonical model:
- `new_save_lineage(parent_save_id, checkpoint_tick) -> new_save_id`
- Parent lineage remains immutable.
- Branching creates explicit branch artifacts and divergence metadata.
- Ranked policy may forbid branching by deterministic refusal.

## F) Save Size and Compaction
Canonical persistence model:
- deterministic checkpoints
- deterministic intent/envelope logs
- deterministic hash anchors (including conservation ledger hashes)

Compaction doctrine:
- compaction is deterministic and policy-driven
- compaction never rewrites truth history semantics
- retained canonical artifacts must preserve replayability from earliest retained checkpoint
- derived artifacts remain regenerable

## Multiplayer Constitution
- Tick index is authoritative across lockstep, authoritative server, and hybrid SRZ policies.
- Deterministic `dt_sim` policy state must be compatible at handshake.
- Mid-session branch mutation is forbidden by default; branching is a lineage/session boundary operation.
