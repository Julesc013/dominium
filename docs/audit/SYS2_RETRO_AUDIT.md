Status: DERIVED
Last Reviewed: 2026-03-05
Supersedes: none
Superseded By: none
Version: 1.0.0
Compatibility: SYS-2 retro audit for deterministic macro capsule behavior execution.
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# SYS2 Retro Audit

## Scope
Audit existing macro behavior execution paths before introducing SYS-2 MacroCapsule runtime behavior.

## 1) Existing Macro Behaviors and Model Discipline
Current macro/meso behavior exists mainly in mobility and transition domains, with deterministic helpers:

- Macro travel lifecycle and tick logic:
  - `src/mobility/travel/travel_engine.py` (`start_macro_travel`, `tick_macro_travel`)
  - `tools/xstack/sessionx/process_runtime.py` (`process.travel_start`, `process.travel_tick`)
- Tier transition planner for region macro/meso/micro states:
  - `src/reality/transitions/transition_controller.py`
  - `tools/xstack/sessionx/process_runtime.py` transition helpers around region expand/collapse planning
- SYS-0/1 collapse/expand and signature/invariant checks:
  - `src/system/system_collapse_engine.py`
  - `src/system/system_expand_engine.py`
  - `src/system/system_validation_engine.py`

Assessment:
- Deterministic ordering and explicit event pathways are present.
- No bespoke runtime "engine object" abstraction was found for systems.
- SYS collapsed capsules are currently structural placeholders only; boundary behavior execution is not yet active.

## 2) Candidate Macro Models Already Registry-Usable
Constitutive model registry contains usable starter models for thin macro wrappers:

- Electrical:
  - `model.elec.load.phasor.default`
  - `model.elec_load_resistive_stub`
  - `model.elec_load_motor_stub`
  - `model.elec_device_loss`
- Fluid:
  - `model.fluid.pump_curve.default`
  - `model.fluid_pump_curve_stub`
  - `model.fluid_leak_rate_stub`
- Thermal:
  - `model.therm_combust_stub`
  - `model.therm_loss_to_temp`
  - `model.therm.conductance.default`
  - `model.therm_ambient_exchange`

Sources:
- `data/registries/constitutive_model_registry.json`
- `data/registries/model_type_registry.json`
- `data/registries/model_residual_policy_registry.json`

Gap:
- `data/registries/macro_model_set_registry.json` is still empty and needs SYS-2 starter sets.

## 3) Existing Implicit Black-Box Behavior Without SYS Artifacts
Observed abstraction surfaces not yet represented as SYS capsule runtime artifacts:

- Region-level `macro_capsules` in transition/runtime paths are not SYS `system_macro_capsule_rows`.
- No canonical `forced_expand_event` schema/artifact exists for systems.
- No `macro_output_record` artifact exists for deterministic capsule boundary I/O history.
- No dedicated SYS macro execution process exists (`process.system_macro_tick` absent).

Paths:
- `tools/xstack/sessionx/process_runtime.py` (region macro capsule handling and travel macro state)
- `src/reality/transitions/transition_controller.py`
- `src/system/*` (no macro runtime executor yet)

## 4) Migration Direction for SYS-2
SYS-2 should add:

- Dedicated macro runtime schemas/artifacts:
  - `macro_runtime_state`
  - `forced_expand_event`
  - `macro_output_record`
- Deterministic capsule execution engine over constitutive models:
  - no direct bespoke solver logic
  - process-only output application paths
- Error-bound and validity enforcement with forced-expand logging.
- Replay/proof hooks for macro output and forced-expand chains.

No domain semantics change is required; this is a system-layer runtime extension over existing contracts.
