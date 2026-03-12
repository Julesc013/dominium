Status: ACTIVE
Version: 1.0.0
Owner: Core Engineering
Last Updated: 2026-03-01
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: patched document aligned to current canon ownership and release scope

# Formalization Model

## Patch Notes

- Current status: partially aligned to the Constitutional Architecture and release-freeze documentation set.
- Required updates: documentation surface exists, but current canon ownership is not explicit
- Cross-check with: `docs/audit/CANON_MAP.md` and `docs/audit/DOC_DRIFT_MATRIX.md`.


## 1. Purpose
`FormalizationState` is the deterministic infrastructure lifecycle substrate for moving from raw placed assemblies to network-connected infrastructure artifacts.

The lifecycle is universal and not rail/road hardcoded.

## 2. Lifecycle States
- `raw`: only physical/raw sources exist (placed parts, terrain edits, markers).
- `inferred`: derived candidates exist for review; no truth mutation.
- `formal`: accepted formal artifact reference and constraints exist via process mutation.
- `networked`: formal artifact is attached to network graph/rules/schedules.

## 3. Core Guarantees
- Inference is derived-only and does not mutate authoritative truth.
- Acceptance/promotion/revert are process-only mutations.
- All transitions emit deterministic `formalization_event` rows.
- Every transition is event-sourced and reenactable.
- No wall-clock behavior; tick-only.

## 4. Acceptance Contract
Accepting a candidate (`inferred -> formal`) must:
- run through ControlPlane action routing,
- emit provenance/formalization event artifacts,
- create commitments when strictness or build policy requires it,
- optionally attach `spec_id` binding for SPEC-1 compliance checks,
- create `formal_artifact_ref` placeholder for MOB-1 guide geometry realization.

## 5. Promotion Contract
Promoting formal infrastructure (`formal -> networked`) must:
- run through ControlPlane,
- attach deterministic network graph rows,
- emit transition event,
- remain reversible through policy-governed revert.

## 6. Revert Contract
Revert may remove formal/network attachments while preserving `raw_sources`.

Revert is policy-governed and must emit deterministic transition events.

## 7. UX Semantics by Policy
- `policy.diegetic_strict`: no auto accept; hints only when epistemically allowed.
- `policy.assisted`: suggestions plus explicit confirmation.
- `policy.auto_network`: procedural flow may auto-promote under declared policy.
- `policy.admin_instant`: immediate formalization allowed for admin/meta contexts, still logged.

## 8. Epistemic Rules
- Diegetic users receive coarse overlays/alignment hints only.
- Planner views can inspect ghost corridors and candidate summaries.
- Admin can inspect full candidate/fingerprint/state payloads.

## 9. Non-Goals (FORM1)
- No MOB guide geometry object implementation.
- No heavy solver/stress computation.
- No direct domain bypass around control/process paths.
