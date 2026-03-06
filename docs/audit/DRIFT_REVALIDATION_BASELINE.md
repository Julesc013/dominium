# Drift Revalidation Baseline

Status: BASELINE  
Last Updated: 2026-03-06  
Scope: PROC-6 deterministic drift scoring, QC escalation, capsule invalidation, certification revocation hooks, revalidation workflow, proof/replay, enforcement, and TestX coverage.

## 1) Drift Scoring Function

Implemented in:

- `src/process/drift/drift_engine.py`
- `src/process/process_run_engine.py`

Deterministic score function:

- `drift = g(QC_fail_rate_delta, yield_variance_delta, environment_deviation_score, tool_degradation_score, calibration_deviation_score, entropy_growth_rate)`
- Inputs are clamped to deterministic `0..1000` ranges.
- Scoring uses weighted deterministic reduction from `data/registries/process_drift_policy_registry.json`.

Bands:

- `drift.normal`
- `drift.warning`
- `drift.critical`

Policies and thresholds are versioned in:

- `schema/process/drift_policy.schema`
- `data/registries/process_drift_policy_registry.json` (`drift.default`, `drift.strict`, `drift.fast_dev`)

## 2) Escalation Rules

Warning-band behavior:

- deterministic QC policy escalation is recorded in `qc_policy_change_rows`
- explain/report artifact emitted with `explain.drift_warning`

Critical-band behavior:

- capsule invalidation required
- certification revocation hooks required
- revalidation trials scheduled
- explain/report artifacts emitted (`explain.drift_critical`, `explain.revalidation_required`, `explain.capsule_invalidated_by_drift`)

Canonical and state artifacts:

- `schema/process/process_drift_state.schema`
- `schema/process/drift_event_record.schema`

## 3) Invalidation Rules

Critical drift triggers deterministic invalidation path:

- `process_capsule_forced_invalid = true`
- canonical capsule invalidation records appended
- drift event stream includes explicit critical action rows (`capsule_invalidate`, `cert_revoke`)
- process certification revocation path uses reason `process.drift_critical`

Capsule usage gate:

- capsule eligibility is suppressed while forced invalid is active
- reason code reflects drift invalidation (`process.capsule_invalidated_by_drift`)

## 4) Revalidation Workflow

Implemented in:

- `schedule_revalidation_trials(...)`
- `apply_revalidation_trial_result(...)`
- `process_run_end(...)` integration

Behavior:

- deterministic schedule of N micro revalidation trials
- one trial is consumed per qualifying run
- all-pass completion resets drift state to normal and clears forced invalidation
- failure keeps invalidation active
- all steps are logged via decision rows and canonical drift/revalidation rows

## 5) Explainability and Epistemic Surfaces

Explain contracts added:

- `explain.drift_warning`
- `explain.drift_critical`
- `explain.revalidation_required`
- `explain.capsule_invalidated_by_drift`

Inspection sections added:

- `section.process.drift_summary`
- `section.process.qc_escalation`

## 6) Proof / Replay Integration

Hash-chain surfaces added and included in process run extensions/control proof payload:

- `drift_state_hash_chain`
- `drift_event_hash_chain`
- `qc_policy_change_hash_chain`
- `revalidation_run_hash_chain`

Replay tool:

- `tools/process/tool_replay_drift_window.py`

Replay verification run:

- command: `python tools/process/tool_replay_drift_window.py --state-path build/process/proc6_report.json`
- status: `complete`
- observed hashes:
  - drift_state_hash_chain: `a2c2f4dcaa441e0cb4a4c48c9eb19e9c87e97b0b3d70fb0a7e4a7614edee45a4`
  - drift_event_hash_chain: `7e4ceb33333e337c0101d695e4dcc7ec2bbca33f83376bc32041703d7d501c2d`
  - qc_policy_change_hash_chain: `0e81c22189a93f4b10968e8839cd894f95c1a7642fd8a4a47de69fab1e0c3b05`
  - revalidation_run_hash_chain: `4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945`

## 7) TestX Coverage (PROC-6)

Required tests added and passing:

- `test_drift_score_deterministic`
- `test_qc_escalation_on_warning`
- `test_capsule_invalidated_on_critical`
- `test_revalidation_resets_on_success`
- `test_replay_drift_hash_match`

Command:

- `python tools/xstack/testx/runner.py --repo-root . --profile FAST --cache off --subset test_drift_score_deterministic,test_qc_escalation_on_warning,test_capsule_invalidated_on_critical,test_revalidation_resets_on_success,test_replay_drift_hash_match`
- status: `pass` (`selected_tests=5`)

## 8) Stress Harness (Long-Run Drift)

Deterministic long-run drift sweep executed with mixed warning/critical fixtures:

- artifact: `build/process/proc6_stress_report.json`
- scenario: `proc6_long_run_drift_160`
- status: `complete`
- deterministic match: `true`
- runs: `160`
- warning_or_critical: `80`
- critical: `40`
- forced_invalid: `40`
- suite hash: `8704e1e360461866eedf6ede5b0dad7187cefad80d9fc0971ac32a1f77accd04`

## 9) Gate Status

Topology map refresh:

- command: `python tools/governance/tool_topology_generate.py --repo-root . --out-json docs/audit/TOPOLOGY_MAP.json --out-md docs/audit/TOPOLOGY_MAP.md`
- status: `complete`
- fingerprint: `85094547f06ba58069a5a2dd65e99c4fc2405cc5c5698c3ec87abfe701f8589b`

RepoX STRICT:

- command: `python tools/xstack/repox/check.py --repo-root . --profile STRICT`
- status: `refusal` (`findings=27`)
- includes pre-existing/global blockers outside PROC-6 scope (RWAM series declarations, provenance classification, existing SYS envelope findings, worktree hygiene/topology declaration lag).

AuditX STRICT:

- command: `python tools/xstack/auditx/check.py --repo-root . --profile STRICT`
- status: `fail` (`promoted_blockers=1`)
- blocker: `E240_UNCLASSIFIED_ARTIFACT_SMELL` at `data/registries/provenance_classification_registry.json` (pre-existing/global).

TestX:

- required PROC-6 subset status: `pass`

Strict build:

- command: `python tools/xstack/run.py strict --repo-root . --cache on`
- status: `error` (exit_code `3`)
- blocking stages are pre-existing/global (`compatx` refusals, `repox` refusal, `auditx` fail, `testx` ecosystem failures) and packaging step missing strict dist path.

## 10) Readiness for PROC-7 (Research & Reverse Engineering)

- [x] Deterministic process drift scoring implemented
- [x] QC escalation/invalidation/revocation hooks are explicit and logged
- [x] Revalidation scheduling and reset path implemented
- [x] Drift explain and inspection surfaces integrated
- [x] Drift proof/replay hash chains integrated
- [ ] Repository-wide strict gates globally green (blocked by pre-existing/global findings outside PROC-6 scope)
