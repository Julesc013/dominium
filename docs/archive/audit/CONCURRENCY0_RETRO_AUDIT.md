Status: DERIVED
Last Reviewed: 2026-03-14
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: ENGINE/CONCURRENCY
Replacement Target: release-pinned concurrency and scheduling governance after sharded truth execution exists

# Concurrency0 Retro Audit

## Observed Runtime Concurrency

- `src/appshell/ipc/ipc_endpoint_server.py` uses a dedicated serving thread, a stop event, and a sequence lock for local IPC only.
- `src/appshell/supervisor/supervisor_engine.py` uses thread events for supervisor shutdown coordination and merges attached log streams deterministically.
- `tools/xstack/sessionx/scheduler.py` exposes `worker_count` and `logical_shards` inputs but still reports `worker_count_effective=1` for canonical truth execution.

## Observed Tooling Parallelism

- `tools/xstack/core/scheduler.py` uses `ThreadPoolExecutor` for validation-plan execution and canonically sorts ready nodes and final results.
- `tools/system/anb_omega.py` uses thread pools inside a stress harness only; it is not a canonical truth path.

## Safe Parallel Zones Today

- validation and audit orchestration, provided outputs are canonically sorted before hashing or persistence
- derived log aggregation, provided merge ordering is canonicalized
- future derived-view generation, provided the outputs are pure and canonically merged before hashing

## Forbidden / Unimplemented Today

- threaded truth mutation
- race-dependent process commit ordering
- lock timing or atomic timing deciding authoritative outcomes
- any canonical state path whose result depends on thread completion order

## Existing Determinism Anchors

- `tools/xstack/testx/tests/test_srz_worker_invariance.py`
- `tools/xstack/testx/tests/test_thread_count_invariance_for_collision.py`
- `tools/xstack/testx/tests/test_log_merge_order_stable.py`
