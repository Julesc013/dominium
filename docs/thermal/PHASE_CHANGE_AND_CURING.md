Status: DERIVED
Last Reviewed: unknown
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: patched document aligned to current canon ownership and release scope

# Phase Change And Curing

## Patch Notes

- Current status: partially aligned to the Constitutional Architecture and release-freeze documentation set.
- Required updates: documentation surface exists, but current canon ownership is not explicit
- Cross-check with: `docs/audit/CANON_MAP.md` and `docs/audit/DOC_DRIFT_MATRIX.md`.


Status: CANONICAL  
Last Updated: 2026-03-03  
Scope: THERM-2 deterministic phase/cure/insulation behavior.

## 1) Phase Change Model

Phase transitions are constitutive-model-driven threshold checks:

- if `T <= freeze_point`: liquid -> solid
- if `T >= melt_point`: solid -> liquid
- if `T >= boil_point`: liquid -> gas (optional policy use)

Authoritative transition application is process-only through:

- `process.material_transform_phase`

No UI/renderer/tool path may mutate phase state directly.

## 2) Transformation Semantics

`process.material_transform_phase` must:

- identify source batch/material stock deterministically
- validate current phase against optional `from_phase`
- apply `to_phase`
- emit deterministic provenance/event rows
- optionally emit byproduct batches (for example steam) when explicitly configured

All transitions are replayable and traceable by event fingerprint.

## 3) Curing Model

Curing is a deterministic progress state updated per tick:

- state variable: `cure_progress` (fixed-point, 0..1 represented in permille)
- update process: `process.cure_state_tick`
- model: `model.therm_cure_progress`

Cure increment is a deterministic function of temperature and policy rate.

Out-of-range curing temperature:

- increments defect hazard output
- marks defect flags in cure state
- may trigger safety hooks (for example overtemperature trip)

## 4) Insulation Conductance Rule

Insulation effects are model-driven and deterministic:

- model: `model.therm_insulation_modifier`
- input: insulation factor from SpecSheet or edge parameters
- output: effective conductance used by THERM T1 conduction solve

Canonical rule:

`effective_conductance = base_conductance * insulation_factor`

where insulation factor is fixed-point/per-mille.

## 5) Heat Exchanger Interface Stub

Heat exchanger is represented as a standard assembly interface, not bespoke THERM code:

- thermal ports:
  - `port.thermal_in`
  - `port.thermal_out`
- future fluid ports (stub now):
  - `port.fluid_in_stub`
  - `port.fluid_out_stub`

Spec hook:

- `spec.heat_exchanger` drives effectiveness/limits as data.

## 6) Safety Hooks

If phase transition creates gas/steam in a sealed context:

- emit overpressure hook event (`hazard.overpressure` hook path)
- keep mutation process-driven and logged

Curing overtemperature may emit:

- `safety.overtemp_trip` hook event

## 7) Determinism

- no wall-clock time
- stable ordering by target IDs
- process-only mutation
- replay/provenance required for all transition and curing events
