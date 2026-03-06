# Stabilization And Maturity Model

Status: AUTHORITATIVE
Last Updated: 2026-03-06
Scope: PROC-4 deterministic process stabilization, maturity transition, and capsule-eligibility gating.

## 1) Metrics

Each `(process_id, version)` maintains deterministic `process_metrics_state` values:

- `runs_count`
- `yield_mean` (permille scale `[0..1000]`)
- `yield_variance` (permille-squared proxy)
- `defect_rate` (permille, weighted by defect severity)
- `qc_pass_rate` (permille over sampled rows)
- `env_deviation_score` (permille)
- `calibration_deviation_score` (permille)
- `drift_incidents_count` (extensions; integrates PROC-6+)

Metric updates are derived from canonical artifacts:

- `process_run_record`
- `process_quality_record`
- `qc_result_record`
- deterministic environment/calibration snapshot fingerprints

## 2) Stabilization Score

The score is deterministic and policy-driven:

`score = +w_runs * f_runs + w_consistency * f_consistency + w_qc * f_qc - w_defect * f_defect - w_env * f_env - w_cal * f_cal`

Where:

- `f_runs` is normalized from `runs_count`
- `f_consistency` derives from inverse variance
- `f_qc` derives from sampled QC pass rate
- `f_defect` derives from weighted defect rate
- `f_env` derives from environment deviation
- `f_cal` derives from calibration deviation

All weights, minimums, and thresholds are sourced from `stabilization_policy_registry`.
No wall-clock inputs are permitted.

## 3) Lifecycle Transition Rules

Deterministic maturity states:

- `exploration` (default)
- `defined` (definition exists and minimum runs reached)
- `stabilized` (score >= `threshold_stabilized`)
- `certified` (stabilized and policy/cert checks pass)
- `capsule_eligible` (certified and `stability_horizon_ticks` satisfied)

Transitions are monotonic upward unless explicit revocation/degradation policy applies.
Every state change must emit a canonical `process_maturity_record`.

## 4) Governance And Artifacts

Required behavior:

- No silent maturity transitions.
- Every transition/denial emits deterministic explain metadata.
- Process-level certificates are CREDENTIAL artifacts bound to `(process_id, version)`.
- Certificate revocation triggers include QC instability and drift events.
- Capsule eligibility is a derived gate and must not be bypassed.

## 5) Determinism And Budget Discipline

- Process ordering is stable by `(process_id, version)`.
- Metrics updates may be bucketed by deterministic policy (`update_every_n_ticks`) and logged.
- Numeric updates follow TOL fixed-point/rounding discipline.
- Replay on identical inputs must reproduce score, state, and hash chains.
