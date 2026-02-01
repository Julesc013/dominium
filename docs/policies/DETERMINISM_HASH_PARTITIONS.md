Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Determinism Hash Partitions (DET0)

This document defines canonical hash partitions for deterministic validation.
All determinism tests MUST compute these partitions and compare them per gate rules.

## General rules

- Partitions MUST be computed deterministically from authoritative state only.
- Partitions MUST be stable across execution mode, step strategy, and hardware variance.
- Any partition mismatch in a gating test is a merge-blocking failure.
- Partition hashes MUST be emitted into the run_root as part of the desync bundle.

## Partition: HASH_SIM_CORE

**Includes**
- Authoritative engine and game simulation state excluding presentation.
- Entity state, component state, authoritative indices, and deterministic caches.

**Excludes**
- UI state, render state, client-only caches, non-authoritative telemetry.

**Computed by**
- Engine in authoritative sim core; server in server-auth runs.

**Mismatch means**
- Core simulation divergence or nondeterministic update order.

**Stored in**
- `run_root/hash/HASH_SIM_CORE.<tick>.txt`

## Partition: HASH_SIM_ECON

**Includes**
- Ledger balances, obligations, contracts, economic state transitions.

**Excludes**
- Presentation summaries, UI aggregates, render-only overlays.

**Computed by**
- Game economy module; server in server-auth runs.

**Mismatch means**
- Economic determinism drift or ledger ordering instability.

**Stored in**
- `run_root/hash/HASH_SIM_ECON.<tick>.txt`

## Partition: HASH_SIM_INFO

**Includes**
- Belief store state, message queues, comm buffers treated as sim-affecting.

**Excludes**
- Client-only HUD views, UI caches, visualization layers.

**Computed by**
- Engine info/comm systems; server in server-auth runs.

**Mismatch means**
- Information propagation or queue ordering divergence.

**Stored in**
- `run_root/hash/HASH_SIM_INFO.<tick>.txt`

## Partition: HASH_SIM_TIME

**Includes**
- ACT time state, event queue, recurrence/cron state, schedule indices.

**Excludes**
- Wall clock timestamps, OS timers, profiling time.

**Computed by**
- Engine time system.

**Mismatch means**
- Time model divergence or event scheduling nondeterminism.

**Stored in**
- `run_root/hash/HASH_SIM_TIME.<tick>.txt`

## Partition: HASH_SIM_WORLD

**Includes**
- World state summaries, WSS bindings, provenance summaries, region states.

**Excludes**
- Terrain visual meshes, client-only LOD caches, render resource handles.

**Computed by**
- Engine world modules and game world overlays; server in server-auth runs.

**Mismatch means**
- World state divergence or nondeterministic streaming application.

**Stored in**
- `run_root/hash/HASH_SIM_WORLD.<tick>.txt`

## Partition: HASH_PRESENTATION (non-gating)

**Includes**
- UI snapshots, render traces, presentation state for diagnostics only.

**Excludes**
- Authoritative simulation state.

**Computed by**
- Client or presentation layer.

**Mismatch means**
- Visual divergence only; does NOT gate merges.

**Stored in**
- `run_root/hash/HASH_PRESENTATION.<tick>.txt`

## Partition mismatch rules

- Any mismatch in SIM partitions is a determinism failure.
- Presentation mismatches are logged but do not block merges unless explicitly escalated.