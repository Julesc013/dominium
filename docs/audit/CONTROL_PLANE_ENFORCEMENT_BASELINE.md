# Control Plane Enforcement Baseline (CTRL-9)

Status: BASELINE  
Version: 1.0.0  
Date: 2026-03-01

## Scope

This baseline hardens the control plane as the sole interaction gateway and locks regression behavior for control decisions, fidelity arbitration, and replay-safe execution.

## Hard Rules Summary

- `INV-CONTROL-PLANE-ONLY-DISPATCH` is boundary-blocker enforced.
- `INV-CONTROL-INTENT-REQUIRED` is boundary-blocker enforced for public interaction entrypoints.
- `INV-NO-MODE-FLAGS` is hard-fail in FAST/STRICT/FULL governance scans.
- `INV-NO-DOMAIN-DOWNGRADE-LOGIC` remains control-kernel only.
- `INV-NO-ADHOC-TEMP-MODIFIERS` remains effect-engine only.
- `INV-NO-TYPE-BRANCHING` remains enforced on control resolution paths.
- `INV-VIEW-CHANGES-THROUGH-CONTROL` remains enforced for view/camera mutations.
- UI modules are blocked from direct `process.*` dispatch outside approved control/authoritative paths.

## Regression Lock Policy

- Decision-log fingerprint baseline is stored at:
  - `data/regression/control_decision_baseline.json`
- Baseline stores deterministic fingerprints only (no full logs).
- Baseline updates require explicit commit tag:
  - `CTRL-DECISION-REGRESSION-UPDATE`
- RepoX enforces:
  - file presence and schema shape
  - fingerprint case completeness
  - required commit-tag usage for updates

## Stress Suite Baseline

- Tool:
  - `tools/control/tool_run_control_stress`
  - `tools/control/tool_run_control_stress.cmd`
  - `tools/control/tool_run_control_stress.py`
- Scenario characteristics:
  - 100+ subjects
  - mixed abstraction, fidelity, and view requests
  - private/admin and ranked constraints in same run set
  - ranked AL4/meta requests are intentionally exercised
- Collected metrics:
  - per-tick cost usage
  - downgrade counts
  - refusal counts
  - decision-log fingerprint streams
- Deterministic assertions:
  - repeated runs produce identical report fingerprints
  - no envelope overflow
  - no ranked fairness starvation
  - ranked AL4/meta forbidden path remains active

## Safe MOB Extension Points

- Add new temporary mobility constraints only via `src/control/effects/effect_engine.py`.
- Register mobility effect types and stacking policies in registries; do not add inline mobility flags.
- Route mobility interaction inputs through ControlIntent and control resolution.
- Express downgrade/refusal through negotiation + DecisionLog (no domain-local downgrade logic).
- Keep mobility view/access changes in control/view policy paths, not renderer/UI mutation paths.

## Future Domain Integration Policy

- Any public interaction entrypoint in new domains (`MOB`, `SIG`, `DOM`, `INF`) must:
  - construct `ControlIntent`
  - call control resolution
  - avoid direct process dispatch
- Any module using control APIs must declare topology dependency on:
  - `module:src/control/control_plane_engine.py`
- Any temporary modifier behavior must use effects, with explicit policy and deterministic expiry.
- Any refusal/downgrade outcome must be decision-log visible.
- Ranked/private policy differences must remain profile-driven; no mode-flag branching.

## AuditX Expansion (CTRL-9)

Added analyzers:

- `E129_CONTROL_PLANE_BYPASS_SMELL`
- `E130_HIDDEN_PRIVILEGE_ESCALATION_SMELL`
- `E131_SILENT_DOWNGRADE_SMELL`
- `E132_MISSING_DECISION_LOG_SMELL`

These analyzers consume topology declarations to detect undeclared control dependencies and bypass paths.

