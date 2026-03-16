Status: DERIVED
Last Reviewed: 2026-03-16
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-ARCHIVE
Replacement Target: legacy reference surface retained without current binding authority

# RWAM Baseline

Status: DERIVED
Last Updated: 2026-03-03
Scope: COMPLETENESS-1 final baseline report.

## 1) Canonical Affordance Coverage Summary

All nine canonical affordance categories are declared in `data/meta/real_world_affordance_matrix.json`.
No canonical affordance category is unmapped.

Coverage snapshot:

- `matter_transformation` -> substrates: MAT, MECH, SPEC, ACTION_GRAMMAR
- `motion_force_transmission` -> substrates: MOB, MECH, ABS, FIELD
- `containment_interfaces` -> substrates: INT, ACT, SPEC, ABS
- `measurement_verification` -> substrates: INFO_GRAMMAR, CTRL, SPEC, ACT
- `communication_coordination` -> substrates: SIG, INFO_GRAMMAR, CTRL, ABS, FIELD
- `institutions_contracts` -> substrates: CTRL, SPEC, SIG, MAT
- `environment_living_systems` -> substrates: FIELD, INT, MAT, MECH
- `time_synchronization` -> substrates: RS, ABS, MAT, CTRL
- `safety_protection` -> substrates: MOB, MECH, MAT, CTRL

## 2) Current Substrate/Series Mapping

Primary implemented mapping in this baseline:

- mobility/safety/time: MOB + ABS + CTRL + MECH + FIELD
- communication/coordination: SIG + INFO_GRAMMAR + CTRL
- transformation/maintenance: MAT + MECH + SPEC
- containment/interfaces: INT + ACT + SPEC
- time/provenance/proof: RS + MAT + CTRL

Series-level declaration coverage is tracked in `series_affordance_coverage` and enforced by RepoX `INV-AFFORDANCE-DECLARED`.

## 3) Future Domain Map

Planned future domain alignment captured in RWAM includes:

- ELEC
- LOGIC
- DOM
- ECO
- SCI
- MIL
- ADV
- BIO

## 4) Enforcement and Validation

Added enforcement:

- RepoX invariant: `INV-AFFORDANCE-DECLARED`
- AuditX analyzer: `E176_AFFORDANCE_GAP_SMELL` (`AffordanceGapSmell`)
- TestX checks:
  - `test_all_affordances_declared`
  - `test_no_series_without_affordance_mapping`
  - `test_rw_matrix_schema_valid`

## 5) Gate Results

Executed gates:

1. RepoX
- Command: `python tools/xstack/repox/check.py --repo-root . --profile FAST`
- Result: `FAIL` (pre-existing repository findings remain; current run reported one fail-level finding under `INV-NO-RANKED-FLAGS` in `tools/signals/tool_run_sig_stress.py` and multiple warn-level findings outside COMPLETENESS-1 scope).

2. AuditX
- Command: `python tools/auditx/auditx.py scan --repo-root . --changed-only`
- Result: `RUN COMPLETE` (artifacts refreshed in `docs/audit/auditx/`).

3. TestX (RWAM scope)
- Command: `python tools/xstack/testx_all.py --repo-root . --profile FAST --subset test_all_affordances_declared,test_no_series_without_affordance_mapping,test_rw_matrix_schema_valid,testx.lockfile.validate`
- Result: `PASS`.

4. Strict build/profile run
- Command: `python tools/xstack/run.py --repo-root . strict`
- Result: `FAIL` (pre-existing STRICT profile refusals/failures outside COMPLETENESS-1 scope, including compatx findings, repox findings, packaging refusal, and global test suite failures).

5. Topology map update
- Command: `python tools/governance/tool_topology_generate.py --repo-root .`
- Result: `UPDATED`
  - `docs/audit/TOPOLOGY_MAP.json`
  - `docs/audit/TOPOLOGY_MAP.md`
  - deterministic fingerprint: `b3cb3abf06fd9465fca6b54c78638b8e2cf8de91120e60cb99fe6e8ccd0029a9`

## 6) Determinism and Runtime Impact Statement

- RWAM additions are governance-only metadata and documentation.
- No runtime simulation semantics changed.
- No wall-clock or nondeterministic behavior was introduced.
