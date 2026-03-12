Status: DERIVED
Last Reviewed: unknown
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# PROC4 Retro-Consistency Audit

Status: AUDIT
Last Updated: 2026-03-06
Scope: PROC-4 stabilization and maturity scoring readiness.

## Existing Unlock/Mastery Patterns

- No process-level "magic unlock" runtime path exists in `src/process/`; process progression is currently implicit via run outcomes.
- Existing lifecycle policy registries from PROC-0 (`process_lifecycle_policy_registry`, `process_stabilization_policy_registry`, `process_drift_policy_registry`) define policy intent but are not yet wired to deterministic maturity state transitions.
- No canonical maturity transition RECORDs are currently emitted.

## Existing Process-Like Stabilization Logic

- `src/process/process_run_engine.py` already emits deterministic run/quality/QC artifacts:
  - `process_run_record`
  - `process_step_record`
  - `process_quality_record`
  - `qc_result_record` rows and hash chains
- QC drift/cert invalidation hooks from PROC-3 exist:
  - `qc_drift_escalation_rows`
  - `qc_certification_hook_rows`
- These provide deterministic inputs for maturity scoring but do not compute a lifecycle state.

## Data Sufficiency for Deterministic Maturity

Existing artifacts are sufficient to derive baseline metrics deterministically:

- Run count: from canonical process run records.
- Yield mean/variance: from process quality rows (`yield_factor`).
- Defect rate: from process quality defect flags + severity extension.
- QC pass rate: from QC result rows (`sampled`, `passed`).
- Environment stability: from run-level environment snapshot hash (available in batch traceability / run context).
- Calibration stability: from QC measurement/calibration references.

## Gaps to Backfill for PROC-4

1. No first-class `process_metrics_state` schema artifact.
2. No deterministic `stabilization_score` function implementation.
3. No canonical `process_maturity_record` transition artifact.
4. No process-level certificate issuance/revocation artifact chain.
5. No explicit capsule-eligibility gate tied to maturity state.
6. No dedicated replay tool for maturity score/state transitions.

## Migration Plan

1. Add maturity schemas/registry (`process_metrics_state`, `process_maturity_record`, `stabilization_policy`).
2. Implement deterministic metrics aggregation engine and maturity evaluation engine.
3. Integrate metrics + maturity transitions into `process_run_end`.
4. Emit process certification hook artifacts and capsule eligibility flags.
5. Add explain/inspection contracts for maturity observability.
6. Extend proof surface and replay tooling for maturity hashes.
