# Fluid Constitution

Status: CANONICAL
Last Updated: 2026-03-04
Scope: FLUID-0 constitutional contract for liquids/gases substrate.

## 1) Purpose

FLUID defines a deterministic, model-driven, networked substrate for infrastructure-scale liquids and gases without CFD.

FLUID does not replace INT interior compartment simulation; it couples to INT through declared contracts.

## 2) Canonical Quantities & Bundle

### Required Quantities

- `quantity.mass_flow`
  - unit policy: `kg/s` equivalent per tick budget scaling
  - dimension: `dim.mass_flow`
- `quantity.pressure_head`
  - proxy pressure/head channel for F1 network solve
  - dimension: `dim.pressure`

### Required Bundle

- `bundle.fluid_basic = {quantity.mass_flow, quantity.pressure_head}`

Temperature remains coupled via THERM interfaces, not embedded into FLUID basic bundle.

## 3) Topology Contract

FLUID network graph payload types:

- Nodes: junctions, tanks, pumps, valves, pressure vessels
- Edges: pipes, hoses, channels

Graph substrate is NetworkGraph/Flow-native; no bespoke solver state outside declared payloads.

## 4) Constitutive Model Contract

All response behavior is model-driven:

- pump curve behavior
- valve curve behavior
- pipe friction/loss proxy
- cavitation hazard increment hook

No inline pressure/flow heuristics in domain runtime logic.

## 5) Safety Pattern Contract

FLUID protection is SAFETY-mediated:

- pressure relief
- burst disk
- fail-safe shutdown
- LOTO for maintenance isolation

No ad-hoc safety branching outside SafetyPattern pathways.

## 6) Tier Contract

- `F0` bookkeeping only:
  - mass transfer accounting
  - no pressure/head solve
- `F1` network pressure/head proxy solve:
  - deterministic ordering
  - budgeted degradation policy
- `F2` reserved:
  - optional ROI CFD in future series

## 7) Coupling Contract (META-CONTRACT-0)

Cross-domain couplings are declaration-only and model-mediated:

- `FLUID -> THERM`
  - heat exchanger model binding
- `FLUID -> INT`
  - leak/flood transfer model binding
- `FLUID -> POLL`
  - contamination/pollutant coupling (future)
- `FLUID -> MECH`
  - pressure load contributes to structural hazards

Direct cross-domain mutation is forbidden.

## 8) Epistemics / UX Contract

- Pressure/flow knowledge requires instruments/gauges.
- No omniscient pipe-map or hidden-state exposure by default.
- Inspection overlays remain policy-gated and epistemically filtered.

## 9) Null-Boot / Optionality

- FLUID is optional.
- Runtime must boot deterministically without FLUID packs.
- `fluid.policy.none` must remain available as explicit refusal/degrade path.

## 10) Non-Goals

- No CFD.
- No full compressible flow solver.
- No wall-clock behavior.
- No bespoke solver paths outside FlowSystem + ConstitutiveModel.
