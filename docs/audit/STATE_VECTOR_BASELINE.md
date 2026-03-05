Status: BASELINE
Scope: STATEVEC-0 explicit state exposure for SYS/COMPILE/PROC

# STATE_VECTOR Baseline

## Declared State Vectors
- `system.macro_capsule_default`
  - `captured_tick`
  - `assembly_rows`
  - `root_assembly_id`
- `process.process_capsule_default`
  - `run_id`
  - `progress`
  - `status`
- `compiled.compiled_model_default`
  - `execution_count`
  - `last_input_hash`
  - `last_output_hash`

Registry source:
- `data/registries/state_vector_registry.json`

## Hidden State Violations Fixed
- Added debug-profile collapse guard in `src/system/system_collapse_engine.py`:
  - runs `detect_undeclared_output_state`
  - records `state_vector_violation_rows`
  - refuses collapse when output-affecting fields are undeclared
- Added RepoX enforcement invariants:
  - `INV-STATE-VECTOR-DECLARED-FOR-SYSTEM`
  - `INV-NO-UNDECLARED-STATE-MUTATION`
- Added AuditX smell:
  - `OutputDependsOnUndeclaredFieldSmell`

## Integration Points
- SYS collapse/expand:
  - collapse serializes via `serialize_state`
  - expand restores via `deserialize_state`
  - provenance anchor remains tied to serialized snapshot hash
- COMPILE runtime:
  - compiled model rows expose state-vector definition/snapshot metadata
  - execute path restores and advances explicit compiled runtime state
- PROC/session runtime:
  - deterministic state-vector definition/snapshot hash chains are surfaced and refreshed

## Proof and Replay
- Added `tools/system/tool_verify_statevec_roundtrip.py`.
- Verifies deterministic `serialize -> deserialize -> serialize` equivalence and hash stability.

## TestX Coverage Added
- `test_state_vector_required_for_capsule`
- `test_roundtrip_serialization_deterministic`
- `test_hidden_state_violation_detected`
- `test_expand_restores_internal_state`
- `test_cross_platform_statevec_hash_match`

## Validation Snapshot
- TestX FAST subset (five STATEVEC tests): PASS.
- RepoX STRICT: NOT clean due pre-existing repository-level refusals unrelated to STATEVEC-only diffs (existing topology/worktree/audit debt).
- AuditX STRICT: PASS wrapper status (warnings present).

## Readiness
STATEVEC-0 baseline is integrated for SYS/COMPILE/PROC and ready for GLOBAL-REVIEW-REFRACTOR-2 and PROC series follow-on hardening.
