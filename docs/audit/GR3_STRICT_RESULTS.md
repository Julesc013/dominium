# GR3 STRICT Results

## Scope
- Profile: `STRICT`
- Goal: enforce architectural purity and remove GR3-introduced strict regressions without semantic changes.

## Commands Executed
- `python tools/xstack/repox/check.py --profile STRICT`
- `python tools/xstack/auditx/check.py --profile STRICT`
- `python tools/xstack/testx/runner.py --profile STRICT --subset "test_no_future_receipt_references,test_state_vector_required_for_capsule,test_roundtrip_serialization_deterministic,test_hidden_state_violation_detected,test_all_couplings_declared,test_coupling_scheduler_ref_matches_runtime,test_equivalence_proof_required,test_validity_domain_checked,test_compile_verify_ref_matches_runtime,test_access_policy_enforced,test_measurement_redaction_applied,test_forensics_routes_to_explain_engine,test_no_truth_leak_in_diegetic_mode,test_canonical_events_not_compacted,test_compaction_marker_hash_stable,test_replay_after_compaction_matches_hash" --cache off`
- `python tools/xstack/compatx/check.py --profile STRICT`

## Results
- RepoX STRICT: `pass` (warnings only).
- AuditX STRICT: `pass` (warnings only, no promoted blockers).
- TestX strict targeted suite: `pass` (16/16).
- CompatX STRICT: `refusal` (253 findings, pre-existing schema/registry debt outside GR3 touch set).

## Gate Notes
- `python tools/xstack/run.py strict --cache off` exceeded environment timeout window and was not used as authoritative gate evidence.
- Strict checks required by GR3 prompt were run directly and recorded above.

## Invariants/Contracts Upheld
- Canon: Determinism primary, process-only mutation, no runtime mode flags.
- META-PROFILE-0: no mode-flag path used for state-vector guard in runtime.
- STATEVEC-0: undeclared output-affecting state violation remains enforced.
- META-REF-0: reference evaluator path remains deterministic.
