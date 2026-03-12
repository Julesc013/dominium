Status: DERIVED
Last Reviewed: unknown
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# TIME-ANCHOR-0 Retro Audit

## Purpose

This audit identifies the authoritative tick surfaces, existing proof-anchor behavior, current compaction boundaries, and the remaining risks around mixed-width tick handling before TIME-ANCHOR-0 enforcement is added.

The audit is intentionally conservative. The implementation goal is to add canonical epoch anchors and 64-bit tick discipline without changing simulation semantics.

## Authoritative Tick Surfaces

The current project already treats simulation time as integer tick progression, but the authoritative paths rely on Python `int` rather than an explicit canonical tick helper.

Primary truth-path files located during the audit:

- `src/time/time_engine.py`
  - `simulation_time.tick` is the canonical process-facing time counter
  - `advance_time(...)` increments tick deterministically and never consults wall-clock time
- `tools/xstack/sessionx/process_runtime.py`
  - `_advance_time(...)` delegates to `src.time.time_engine.advance_time`
  - this is the main mutation path used by Process execution
- `src/net/policies/policy_server_authoritative.py`
  - `advance_authoritative_tick(...)` increments authoritative server tick
  - `_build_anchor_frame(...)` emits canonical per-tick hash-anchor frames
- `src/net/srz/shard_coordinator.py`
  - `advance_hybrid_tick(...)` increments hybrid shard-runtime tick
  - `_build_anchor_frame(...)` emits canonical per-tick shard hash-anchor frames
- `src/server/runtime/tick_loop.py`
  - wraps authoritative tick advancement and writes MVP proof-anchor artifacts

Observed result:

- no truth-path audit target used wall-clock APIs to advance simulation
- the remaining risk is not wall-clock coupling, but lack of an explicit bounded `tick_t` helper and the continued use of plain `int(...)` conversion in truth paths

## Mixed-Width Risk Review

Searches found many tick annotations such as `tick: int`, `current_tick: int`, and `canonical_tick: int` across Python code. In CPython this does not create an immediate overflow bug, but it is not an explicit canonical-width contract.

Separate searches also found `u32` and `i32` usage in several native utilities. The audited examples were:

- `tools/history/history_cli.cpp`
- `tools/replay_analyzer/ra_parser.h`
- `tools/universe_editor/ue_queries.h`
- `tools/coredata_compile/*`

These are not the authoritative truth mutation paths used by MVP server/process time advancement. They remain loadable and unchanged for TIME-ANCHOR-0, but they justify adding an explicit static check for mixed-width tick declarations in scoped truth/time paths.

## Existing Proof Anchors

Existing deterministic anchor-like artifacts already present:

- per-tick network hash-anchor frames
  - `src/net/policies/policy_server_authoritative.py`
  - `src/net/srz/shard_coordinator.py`
- per-tick control proof bundles
  - same authoritative and hybrid paths
- MVP proof-anchor artifacts
  - `src/server/runtime/tick_loop.py`
  - written under `build/server/<save_id>/proof_anchors/anchor.tick.<tick>.json`

Current cadence behavior:

- `server_config_registry.json` already defines `proof_anchor_interval_ticks`
- the default MVP server config uses `proof_anchor_interval_ticks = 4`
- hash-anchor frames are emitted every authoritative tick
- MVP proof-anchor artifacts are emitted on the configured interval only

Conclusion:

- the repository already has deterministic proof artifacts
- TIME-ANCHOR-0 should add canonical epoch anchors as a distinct artifact layer, not replace existing proof anchors

## Existing Compaction Boundaries

Two compaction surfaces are relevant:

- save/session compaction
  - `tools/xstack/sessionx/time_lineage.py`
  - currently retains or merges artifacts by policy and checkpoint cadence
  - it does not currently require epoch-anchor-aligned cut points
- provenance compaction
  - `src/meta/provenance/compaction_engine.py`
  - already maintains:
    - `compaction_marker_hash_chain`
    - `compaction_pre_anchor_hash`
    - `compaction_post_anchor_hash`
  - currently validates replay equivalence and open-branch safety, but not epoch-anchor boundaries

Conclusion:

- the safest insertion point is to enforce epoch-anchor boundaries in both the provenance compaction engine and the session save compactor
- compaction marker extensions can record the bounding epoch-anchor IDs without changing replay semantics

## Existing Time Warp / Batching

Time warp is already tick-based and deterministic:

- `src/time/time_engine.py`
  - `advance_time(..., steps=N)` batches canonical tick advancement
- `tools/earth/earth9_stress_common.py`
  - time-warp scripts express days and years as deterministic tick counts
- `tools/system/tool_generate_sys_stress.py`
  - uses deterministic `time_warp_batch_size`
- `tools/mvp/mvp_smoke_common.py`
  - advances `1 day`, `30 days`, and `365 days` through server ticks, not wall-clock time

Conclusion:

- batching already exists in the correct semantic form
- TIME-ANCHOR-0 only needs to ensure:
  - batching respects explicit tick overflow bounds
  - epoch anchor emission remains aligned to absolute tick, not batch size

## Safest Insertion Points

The lowest-risk insertion points identified by the audit are:

1. add a canonical tick helper under `src/time/`
   - explicit `uint64` contract
   - normalization and overflow/refusal helpers
2. add an epoch anchor engine under `src/time/`
   - load deterministic anchor policy
   - build and validate canonical `epoch_anchor_record`
   - append runtime anchor rows and write anchor artifacts
3. integrate the epoch anchor engine after per-tick hash-anchor frame emission in:
   - `src/net/policies/policy_server_authoritative.py`
   - `src/net/srz/shard_coordinator.py`
4. enforce compaction cuts only on epoch-anchor boundaries in:
   - `src/meta/provenance/compaction_engine.py`
   - `tools/xstack/sessionx/time_lineage.py`
5. add scoped static enforcement in RepoX and AuditX for mixed-width tick declarations

## Rare Immediate Stable Semantics

A small subset of temporal semantics is already mature enough to treat as stable immediately:

- canonical tick monotonicity from `docs/time/TEMPORAL_SEMANTICS_CONSTITUTION.md`
- deterministic batching over canonical ticks
- authoritative mutation ordered only by canonical tick
- no wall-clock authority coupling

The new TIME-ANCHOR-0 artifacts should therefore extend these semantics without reinterpreting them.

## Decision

TIME-ANCHOR-0 should proceed with:

- canonical `tick_t` defined as unsigned 64-bit
- canonical epoch anchors emitted at deterministic absolute intervals
- compaction cut enforcement at epoch-anchor boundaries
- explicit refusal near the canonical tick limit
- scoped RepoX/AuditX/TestX enforcement for mixed-width and missing-anchor violations
