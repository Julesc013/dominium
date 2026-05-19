Status: DERIVED
Last Reviewed: 2026-03-16
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# FIELD Layer Baseline

Status: BASELINE
Date: 2026-03-02
Scope: FIELD-1 Global Field substrate completion baseline.

## 1) Field Types

- `field.temperature` (scalar)
- `field.moisture` (scalar)
- `field.friction` (scalar)
- `field.radiation` (scalar)
- `field.visibility` (scalar)
- `field.wind` (vector)

## 2) Update Policies

- `field.static`: deterministic static values.
- `field.scheduled`: deterministic scheduled tick updates.
- `field.flow_linked`: deterministic update from FlowSystem channel summaries.
- `field.hazard_linked`: deterministic update from HazardModel state summaries.

## 3) Integration Points

- MECH:
  - `process.field_tick` emits `effect.machine_degraded` from temperature-driven stress capacity and moisture-driven corrosion risk.
  - `process.mechanics_tick` consumes `machine_output_permille` through the effect stack during structural evaluation.
- MOB:
  - `process.field_tick` emits `effect.traction_reduction`, `effect.wind_drift`, and `effect.speed_cap` from field samples.
  - `process.body_move_attempt` applies deterministic movement scaling from traction/speed effects and aircraft drift from wind-drift effects.
- INT:
  - `process.compartment_flow_tick` applies exterior boundary conditions by sampling field layers at portal scope and materializing boundary parameters into `portal_flow_params`.
- ED:
  - `process.instrument_tick` exposes thermometer/hygrometer/dosimeter/wind/visibility readings.
  - precise values are gated by epistemic policy; diegetic default gets coarse bands.
- CTRL/Hazard:
  - Field layer updates remain process-driven; field conditions are surfaced as deterministic temporary effects.

## 4) Performance and Determinism Guarantees

- Canonical mutation remains process-only (`process.field_tick` and deterministic process integrations).
- Field update ordering is deterministic by sorted `field_id` then `cell_id`.
- Budget degradation is explicit and deterministic (`degrade.field.budget`) with critical field priority.
- Canonical macro field cells are persisted; meso/micro layers are derived on-demand.
- No wall-clock timers, no background nondeterministic mutation, no PDE/CFD solvers.

## 5) Extension Notes (DOM Climate/Hydrology)

- Domain solvers can plug in by writing deterministic `flow_quantities` and `hazard_states` inputs to `process.field_tick`.
- Additional domain fields should register via field type/update policy registries and schema-compatible layer/cell rows.
- Future solver activation should remain SRZ-compatible and budget-enveloped with deterministic degradation/refusal paths.
