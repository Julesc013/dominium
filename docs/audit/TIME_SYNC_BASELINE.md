Status: DERIVED
Last Reviewed: unknown
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# Time Sync Baseline

Date: 2026-03-04  
Scope: TEMP-2

## Drift Rules

- `drift_policy_registry` added with:
  - `drift.none`
  - `drift.linear_small`
  - `drift.profile_defined`
- `time_mapping_registry` supports optional `drift_policy_id`.
- Time mapping engine applies drift deterministically per mapping/scope/tick.

## Sync Policies

- `sync_policy_registry` added with:
  - `sync.none`
  - `sync.adjust_on_receipt`
  - `sync.strict_reject`
- `process.time_adjust` performs signal-based correction with bounded deltas.

## Proof Integration

- Control proof bundle now includes:
  - `time_adjust_event_hash_chain`
  - `drift_policy_id`
- Runtime now emits/maintains:
  - `time_adjust_events`
  - `time_adjust_event_hash_chain`

## Enforcement

- RepoX rules added/extended for:
  - canonical tick drift prohibition
  - logged time adjustments
  - no wall-clock dependence
- AuditX analyzers added for:
  - implicit clock sync logic
  - direct domain-time writes

## Validation Summary

- TEMP-2 targeted tests added for drift/sync behavior and replay hash stability.
- RepoX/AuditX/TestX strict status depends on branch-wide pre-existing blockers outside TEMP-2 scope.

## Readiness

Baseline is ready for LOGIC timer semantics that depend on deterministic schedule + domain mapping + explicit synchronization artifacts.
