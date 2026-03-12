Status: BASELINE
Last Reviewed: 2026-03-06
Version: 1.0.0
Scope: SYS-6 retro-consistency audit for reliability coverage.
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# SYS6 Retro Audit

## Existing Failure Mechanisms Across Domains
- ELEC protection faults and breaker trips are already canonical through electrical fault/protection process pathways.
- THERM overheat/fire escalation is process-driven with deterministic thermal hazard and fire events.
- FLUID burst/leak behavior is already safety-mediated and logged with deterministic refusal/degrade pathways.
- MOB derailment/failure pathways are already event-sourced in mobility process/tick pipelines.
- CHEM corrosion/fouling/scaling degradation exists through chemical degradation models and event logs.

## Elevation Targets for System-Level Reliability Profiles
- Aggregate domain hazard outputs to system-level health vectors per `system_id`.
- Map aggregated hazards to explicit system failure modes for macro capsules:
  - `failure.mode.overheat`
  - `failure.mode.overpressure`
  - `failure.mode.electrical_fault`
  - `failure.mode.corrosion_breach`
  - `failure.mode.control_loss`
  - `failure.mode.structural_fracture`
- Reuse SYS-2 forced-expand pathway as the canonical expand-on-edge action.
- Reuse safety pattern application as deterministic fallback when expand is denied.

## Implicit Failures To Make Explicit
- Macro-side output suppression currently tied to forced expand/error-bound pathways should also be attributable to reliability threshold policy.
- System-level warning states are not currently persisted as deterministic health outputs.
- No explicit system failure event chain currently exists for macro reliability threshold crossings.

## Migration Plan
- Introduce canonical reliability profile + health + failure schemas.
- Add deterministic health aggregation and reliability evaluation engines under `src/system/reliability/`.
- Route reliability-triggered expands through SYS-3/CTRL budget discipline.
- Emit canonical `failure_event` rows and deterministic explain hooks.
- Extend proof hashes with system health and failure chains plus logged stochastic outcomes (profile-gated only).
