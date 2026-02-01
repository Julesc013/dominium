Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Failure Scenarios (MMO-2)

Failure handling MUST be explicit, deterministic, and auditable.
No silent drops or best-effort mutations are allowed.

## Canonical Scenarios

### Missing Checkpoint

- Symptom: no committed checkpoint is available.
- Required behavior: refuse authoritatively.
- Refusal code: `REFUSE_CHECKPOINT_MISSING`.
- Fallback: frozen/inspect-only mode.

### Missing Log Tail

- Symptom: log tail from the checkpoint position cannot be loaded.
- Required behavior: refuse authoritatively.
- Refusal code: `REFUSE_LOG_TAIL_MISSING`.
- Fallback: frozen/inspect-only mode.

### Schema or Capability Incompatibility

- Symptom: checkpoint schema or capability baseline mismatch.
- Required behavior: refuse without reinterpretation.
- Refusal code: `REFUSE_SCHEMA_INCOMPATIBLE` or `REFUSE_CAPABILITY_MISSING`.
- Fallback: frozen/inspect-only mode.

### Snapshot Budget Exhaustion

- Symptom: checkpoint capture exceeds snapshot budget.
- Required behavior: refuse and leave state unchanged.
- Refusal code: `REFUSE_SNAPSHOT_BUDGET`.

### Capability Gap During Rolling Update

- Symptom: cross-shard interaction without overlapping capabilities.
- Required behavior: refuse deterministically.
- Refusal code: `REFUSE_CAPABILITY_GAP`.

### Invalid Lifecycle Transition

- Symptom: state change violates lifecycle transition rules.
- Required behavior: refuse and log lifecycle refusal.
- Refusal code: `REFUSE_SHARD_STATE`.