Status: DERIVED
Version: 1.0.0
Last Reviewed: 2026-02-15
Scope: Prompt 19/20 acceleration baseline
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# Developer Acceleration Baseline

## Coverage Snapshot

- Impact graph engine: `tools/dev/impact_graph/engine.py`
- Dev command wrapper: `tools/dev/dev.py`
- FAST subset planner: `tools/xstack/testx/runner.py`
- Regression lock file: `data/regression/observer_baseline.json`
- Profile trace schema: `schemas/profile_trace.schema.json`
- RepoX negative invariants: `tools/xstack/repox/check.py`

## Impact Graph Coverage

- Node families covered: file, schema, registry, pack, domain, solver, command, test, artifact, product.
- Determinism controls:
  - sorted traversal
  - path normalization (`/`)
  - stable hash over canonical JSON payload
- Output artifact: `build/impact_graph.json` (derived, regenerable).

## TestX Subset Strategy

- FAST defaults to deterministic impacted subset computed from impact graph.
- Explicit subset is supported in every profile via `testx_all --subset`.
- Fallback strategy is explicit and safe:
  - if graph coverage is incomplete, FAST runs full suite.
  - no silent skipping is allowed.

## Regression Locks

- Baseline lock: `data/regression/observer_baseline.json`
- Locked values:
  - `composite_hash_anchor`
  - `pack_lock_hash`
  - real-data registry hashes (including ephemeris + terrain tile)
  - ROI final state/tick hash anchors
- Update policy:
  - baseline updates require commit subject tag `REGRESSION-UPDATE`.
  - RepoX invariant: `INV-REGRESSION-LOCK-PRESENT`.

## CI Lane Summary

- Lane workflow: `.github/workflows/ci.yml`
- `ci-dev`:
  - strict build
  - impacted tests
  - AuditX scan
- `ci-verify`:
  - strict build
  - full strict tests
  - packaging dry-run
- `ci-dist`:
  - strict build
  - strict tests
  - deterministic packaging and artifact verification
- RepoX guard:
  - `INV-NO-PACKAGING-FROM-DEV-LANE`

## Non-Gating Profile Artifact Pipeline

- Capture tool: `tools/dev/tool_profile_capture.py`
- Report tool: `tools/dev/tool_profile_report.py`
- Default outputs:
  - `docs/audit/perf/profile_trace.sample.json`
  - `docs/audit/perf/profile_trace.sample.md`
- Schema validation:
  - `schemas/profile_trace.schema.json`
  - `tools/xstack/compatx/version_registry.json` entry `profile_trace`
- Determinism note:
  - structure and hashes are deterministic for identical inputs;
  - metrics remain informational and non-gating.

## Known Slow Paths

- STRICT/FULL all-tests runs.
- Dist reproducibility checks (double build + compare).
- Full lab traversal/regression suite.

## Future Optimization Targets

1. Increase impact graph precision for C/C++ symbol-level mapping.
2. Add per-shard cache key visualization for FULL profile triage.
3. Add deterministic profile trend rollups without changing gate behavior.
4. Extend regression lock partitioning beyond observer MVP path.
