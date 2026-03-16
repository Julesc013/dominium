Status: DERIVED
Last Reviewed: 2026-03-16
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: release-pinned concurrency policies and shard-merge execution contracts.

# Concurrency Contract Baseline

- result: `complete`
- release_status: `pass`
- concurrency_policy_registry_hash: `a57f62fc785b809247bc956fec4901df451b59368b5319584fcc46bd5aeaf4b0`
- concurrency_scan_fingerprint: `68e55f9570429563f4f99143f0b8d73ce1e166575f430d868391f8f76761b5cc`
- deterministic_fingerprint: `26904666ac80b3811ebecd62963148a9adbd23ef1951d66e751d7e747a94ee60`

## Allowed Parallel Zones

- `src/appshell/ipc/ipc_endpoint_server.py`: Dedicated local IPC serving thread; no truth mutation.
- `src/appshell/supervisor/supervisor_engine.py`: Derived log/status aggregation only; merge order canonicalized before persistence.
- `tools/xstack/core/scheduler.py`: Validation and audit execution only; ready and final results are canonically ordered.

## Forbidden Zones

- `src/field/`: Field mutation is authoritative and may not race.
- `src/fields/`: Field mutation is authoritative and may not race.
- `src/logic/`: Logic truth evaluation may not depend on scheduling.
- `src/process/`: Canonical process execution remains ordered truth execution.
- `src/time/`: Canonical time and proof paths may not depend on thread timing.
- `tools/xstack/sessionx/process_runtime.py`: Authoritative state mutation must remain deterministic and must not depend on thread completion order.
- `tools/xstack/sessionx/scheduler.py`: Truth execution may not become parallel without an explicit deterministic shard-merge contract.

## Concurrency Policies

- `concurrency.parallel_derived`
- `concurrency.parallel_validation`
- `concurrency.single_thread`

## Enforcement Coverage

- ARCH-AUDIT concurrency checks: `parallel_truth_scan`, `parallel_output_scan`, `truth_atomic_scan`
- RepoX rules: `INV-NO-PARALLEL-TRUTH-WITHOUT-SHARD-MERGE`, `INV-PARALLEL-DERIVED-MUST-CANONICALIZE`
- AuditX analyzers: `E528`, `E529`
- TestX coverage: derived merge canonicalization, validation merge canonicalization, worker invariance, threaded truth fixture detection

## Readiness

- OBSERVABILITY-0: `ready`
- STORE-GC-0: `ready`
