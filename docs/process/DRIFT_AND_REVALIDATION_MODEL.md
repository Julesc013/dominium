Status: DERIVED
Last Reviewed: 2026-03-16
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: patched document aligned to current canon ownership and release scope

# Drift And Revalidation Model

## Patch Notes

- Current status: partially aligned to the Constitutional Architecture and release-freeze documentation set.
- Required updates: documentation surface exists, but current canon ownership is not explicit
- Cross-check with: `docs/audit/CANON_MAP.md` and `docs/audit/DOC_DRIFT_MATRIX.md`.


Status: AUTHORITATIVE
Last Updated: 2026-03-06
Scope: PROC-6 deterministic process/capsule drift detection and revalidation.

## 1) DriftScore

Each `(process_id, version)` evaluates a deterministic drift score:

`drift = g(qc_fail_rate_delta, yield_variance_delta, environment_deviation_score, tool_degradation_score, calibration_deviation_score, entropy_growth_rate)`

Score inputs must be measurable and replay-stable from canonical process/QC/metrics artifacts.

## 2) Drift Bands

- `drift.normal`
- `drift.warning`
- `drift.critical`

Threshold values are policy-driven via `drift_policy_registry` and versioned.

## 3) Actions By Band

### Warning

- deterministically escalate QC policy (`qc_policy_change` record)
- optionally emit inspector-visible warning report
- keep capsule execution allowed unless stricter policy says otherwise

### Critical

- invalidate process capsule usage
- revoke process certificate where active
- require deterministic micro revalidation trials
- emit explain/report artifacts and decision logs

No silent escalation or invalidation is allowed.

## 4) Revalidation Workflow

`process.revalidation_schedule` semantics:

1. Schedule `N` micro revalidation trials (policy-driven).
2. Execute trials deterministically in process-id/version/trial order.
3. On completion:
   - pass horizon: reset drift state to normal, re-enable capsule path, allow recertification
   - fail horizon: remain invalidated/escalated

All transitions must emit canonical records and replay-stable hash chains.

## 5) Determinism And Budgeting

- drift evaluation order is stable by `process_id` then `version`
- budget pressure uses deterministic stride/bucket degradation with decision-log entries
- no wall-clock dependency and no unnamed RNG
- optional stochastic behavior is only allowed by explicit named-RNG policy and must be proof-logged

## 6) Integrations

- PROC-3 QC outcomes feed drift deltas and escalation paths
- PROC-4 metrics/maturity feed drift computation and recertification eligibility
- PROC-5 capsules consume invalidation/forced-expand outcomes
- SYS-5 process certificates are revoked/reissued through explicit records
- COUPLE relevance/budget rules classify drift checks as important (non-optional) evaluations
