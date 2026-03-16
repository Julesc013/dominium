Status: DERIVED
Last Reviewed: 2026-03-06
Supersedes: none
Superseded By: none
Version: 1.0.0
Compatibility: SYS-5 deterministic certification/compliance workflow.
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: patched document aligned to current canon ownership and release scope

# System Certification Model

## Patch Notes

- Current status: partially aligned to the Constitutional Architecture and release-freeze documentation set.
- Required updates: documentation surface exists, but current canon ownership is not explicit
- Cross-check with: `docs/audit/CANON_MAP.md` and `docs/audit/DOC_DRIFT_MATRIX.md`.


## A) Certification Targets
Certification evaluation can target:
- systems (micro or macro),
- templates (pre-certification path),
- macro capsules (model-bound boundary representation).

Targets remain process-evaluated and deterministic; no direct mutation path may issue certificates.

## B) Certification Inputs
Certification evaluation consumes:
- interface signature row,
- boundary invariant declarations,
- spec bindings and latest compliance outcomes,
- safety pattern instances,
- degradation context (optional, profile-driven).

All inputs must be canonical rows/registries or deterministic derivations from canonical rows.

## C) Certification Outputs
On each certification evaluation:
- emit canonical `certification_result` RECORD summary,
- emit REPORT artifact with per-criterion pass/fail data.

If pass:
- issue CREDENTIAL artifact (`certificate_artifact`) with:
  - `cert_id`
  - `cert_type_id`
  - `issuer_subject_id`
  - validity scope and conditions
  - `issued_tick`

If fail:
- no certificate issuance,
- emit explain-ready failure context (deterministic and auditable).

## D) Revocation Rules
Existing certificates must be invalidated when relevant system truth changes:
- collapse/expand with material internal graph change,
- degradation threshold breach,
- spec compliance fail/violation on bound targets.

Invalidation must emit canonical revocation records and explain context; silent invalidation is forbidden.

## E) Policy Modes
Policy-gated operation modes:
- `cert.optional` (default)
- `cert.required_for_operation`
- `cert.required_for_ranked` (reserved)

Mode selection is profile/law data-driven (no mode flags).

## Determinism and Epistemics
- Certification evaluation order is deterministic (`system_id`, then `cert_type_id`).
- Certificate visibility follows SIG trust/receipt pathways; no omniscient leak.
- Proof/replay chains must include certification issuance and revocation state transitions.
