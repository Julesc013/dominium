Status: DERIVED
Last Reviewed: 2026-03-16
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# FLUID-0 Retro-Consistency Audit

Status: CANONICAL
Last Updated: 2026-03-04
Scope: FLUID-0 phase 0 retro-audit for infrastructure-scale fluid substrate introduction.

## Audit Summary

- Existing dedicated FLUID runtime substrate is not implemented (`src/fluid/` absent).
- Existing fluid references are registry-level stubs only:
  - `dom.domain.fluids.basic` in domain/solver registries.
  - `model_type.fluid_pump_curve_stub` and `model.fluid.pump_curve.default` in model registries.
  - `bundle.fluid_basic` present but currently bound to placeholder quantity ids.
- Interior pressure/flood/leak behavior exists in INT and remains interior-scale (compartment atmosphere/water handling).

## Existing Patterns Reviewed

### 1) Pipe/Pump/Valve Logic

- No dedicated infrastructure fluid network solver found.
- Existing references are constitutive/registry stubs only:
  - `data/registries/model_type_registry.json`
  - `data/registries/constitutive_model_registry.json`

### 2) Ad-Hoc Pressure Logic in INT

- Interior pressure proxy and flood thresholds exist in compartment engine/builder:
  - `src/interior/compartment_flow_engine.py`
  - `src/interior/compartment_flow_builder.py`
- Process-runtime breach/portal pathways can create leak hazard rows for interior compartments:
  - `tools/xstack/sessionx/process_runtime.py`

Assessment:
- This is valid interior-scale simulation and should remain INT-owned.
- It must not be promoted into infrastructure-scale FLUID behavior via direct mutation.

### 3) Direct Flooding Logic Outside Flow/Hazard

- Interior flooding/leak progression is routed through interior flow/hazard pathways (not a standalone FLUID subsystem yet).
- No separate FLUID flooding bypass path found.

### 4) Migration Boundary (INT vs FLUID)

- INT remains interior-scale domain:
  - compartment atmosphere, portal venting, leak hazard propagation.
- FLUID-0 defines infrastructure-scale domain:
  - tanks/pipes/pumps/valves/pressure-vessel abstractions over NetworkGraph + FlowSystem.
- Coupling is contract-only and model-mediated:
  - FLUID -> INT via declared leak/flood model bindings.
  - No direct FLUID writes into INT truth state.

## Inconsistencies & Deprecations

- `bundle.fluid_basic` currently references placeholder quantity IDs that are not canonical substrate quantities.
- Migration action in FLUID-0:
  - normalize to canonical `quantity.mass_flow` and `quantity.pressure_head`.

## Determinism / Null-Boot Checks

- No mandatory default fluid pack dependency found.
- FLUID remains optional at boot; policies include explicit `fluid.policy.none` path.

## Migration Notes (for FLUID-1)

- Keep INT pressure/flood implementation scoped to compartment internals.
- Introduce FLUID network solve in F1 using FlowSystem + ConstitutiveModel only.
- All FLUID->THERM/INT/MECH effects must be declared in coupling contracts and routed through model/process pathways.
