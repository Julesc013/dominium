Status: DERIVED
Last Reviewed: unknown
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: patched document aligned to current canon ownership and release scope

# Thermal Constitution

## Patch Notes

- Current status: partially aligned to the Constitutional Architecture and release-freeze documentation set.
- Required updates: documentation surface exists, but current canon ownership is not explicit
- Cross-check with: `docs/audit/CANON_MAP.md` and `docs/audit/DOC_DRIFT_MATRIX.md`.


Status: CANONICAL  
Last Updated: 2026-03-03  
Scope: THERM-0 domain constitution and governance baseline.

## 1) Purpose

THERM defines heat as a first-class cross-domain substrate using existing systems:

- quantities
- fields
- flows
- constitutive models
- hazards/safety patterns

THERM is a governance and integration constitution in this phase. It does not introduce a new bespoke runtime engine.

## 2) Canonical Thermal Quantities

Units align with MAT unit policy and fixed-tick simulation:

- `quantity.thermal_energy` (J)
- `quantity.heat_flow` (J/tick)
- `quantity.heat_loss` (J/tick)
- temperature is represented as field layer `field.temperature` (Kelvin canonical, display conversions policy-driven)

Conventions:

- `quantity.heat_loss` is dissipated energy output attributable to a source process/domain.
- `field.temperature` is sampled deterministically and never written directly by UI/render paths.

## 3) Field Model

- Temperature is a deterministic `FieldLayer` (`field.temperature`).
- Macro temperature coverage is always available (T0 baseline).
- Temperature updates occur only through process/model/scheduled pathways.
- No wall-clock dependence.

## 4) Flow Model

- Thermal transfer at meso tier uses `FlowSystem` channels and graph topology.
- Recommended bundle: `bundle.thermal_basic = {quantity.heat_flow, quantity.heat_loss_stub}`.
- Global PDE/CFD thermal diffusion is out of scope for THERM-0.
- T1 conduction remains graph/flow-based and deterministic.

## 5) Constitutive Model Discipline

Thermal response must be model-driven (META-MODEL), not inline domain math:

- `therm.conductance`
- `therm.heat_capacity`
- `therm.phase_change_stub`
- `therm.loss_to_temperature`

Model outputs may produce:

- effects
- hazard increments
- flow adjustments
- derived observations/reports

All outputs remain process-only mutations.

## 6) Safety And Hazard Hooks

Thermal baseline hazards:

- `hazard.overheat`
- `hazard.freeze_damage` (optional policy-controlled)

Safety patterns:

- `safety.overtemp_trip`
- `safety.thermal_runaway` (hook template)

Thermal safety responses must execute via SAFETY + process pathways.

## 7) Tiering

- `T0` macro: bookkeeping + `heat_loss` accounting + coarse temperature updates.
- `T1` meso: thermal network conduction updates local energy/temperature summaries.
- `T2` micro: ROI diffusion (future, optional; not implemented in THERM-0).

Budget/degrade behavior must be deterministic and CTRL/RS-governed.

## 8) Epistemics And UX

- Diegetic thermal readings are coarse and policy-gated.
- Inspector/admin views can access richer thermal summaries by entitlement.
- No omniscient thermal truth-map exposure in diegetic profiles.

## 9) Cross-Domain Coupling

Inbound heat sources:

- ELEC losses (`quantity.heat_loss` / `effect.temperature_increase_local`)
- MECH dissipation hooks
- CHEM combustion/reaction hooks (future)

Outbound coupling:

- hazard/effect outputs for overtemp/freeze pathways
- compliance/inspection artifacts through INFO grammar

## 10) Non-Goals (THERM-0)

- no detailed thermal solver implementation
- no CFD/PDE global simulation
- no direct mutation bypassing process/model engines
- no mandatory thermal pack requirement for null boot
