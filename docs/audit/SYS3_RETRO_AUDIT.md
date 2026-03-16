Status: DERIVED
Last Reviewed: 2026-03-05
Supersedes: none
Superseded By: none
Version: 1.0.0
Compatibility: SYS-3 retro audit for deterministic tier integration.
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# SYS3 Retro Audit

## Scope
Audit existing tier/ROI behavior before integrating system-level micro/meso/macro transitions.

## 1) Existing ROI Micro Logic (MOB and Related Domains)
- Mobility and reality transitions already use deterministic tier selection and stable ordering in:
  - `src/reality/transitions/transition_controller.py`
  - `tools/xstack/sessionx/process_runtime.py` (region transition tick path)
- Existing logic is policy-driven and budget-aware, but not yet system-granular (`system_id` transitions were not first-class).

## 2) Implicit Collapse Risk Areas
- Prior to SYS-3, system collapse/expand were explicit processes (`process.system_collapse`, `process.system_expand`) but had no unified ROI scheduler process.
- Risk identified: direct tier/capsule field mutation (`current_tier`, `active_capsule_id`) outside process-governed paths could introduce silent transitions.
- Mitigation introduced in SYS-3 implementation:
  - canonical `process.system_roi_tick`
  - tier-change event rows + hash chains
  - DecisionLog entries for approvals/denials/refusals
  - AuditX/RepoX enforcement for unlogged transitions and implicit collapse paths.

## 3) Systems Lacking TierContract Clarity
- Audit target: every `system_rows[*].tier_contract_id` must resolve to a registered contract.
- Required contract added/verified: `tier.system.default` in `data/registries/tier_contract_registry.json`.
- Scheduler refusal path defined for missing contracts:
  - `refusal.system.tier_contract_missing`
  - deterministic denial decision + tier-transition denial record.

## 4) Migration Notes
- Tier transitions are now centralized and deterministic at system granularity:
  - scheduler: `src/system/roi/system_roi_scheduler.py`
  - runtime process branch: `process.system_roi_tick`
- Collapse safety checks strengthened:
  - unresolved hazards
  - pending internal events
  - open scheduled internal tasks
  - open branch dependencies
- Expand checks strengthened:
  - provenance anchor hash validation
  - interface signature unchanged validation.
