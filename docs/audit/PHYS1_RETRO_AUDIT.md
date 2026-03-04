# PHYS1 Retro-Consistency Audit

Status: CANONICAL  
Last Updated: 2026-03-04  
Scope: PHYS-1 Phase 0 audit for force/momentum substrate alignment with process-only mutation and determinism.

## 1) Audit Inputs

Primary artifacts inspected:

- `tools/xstack/sessionx/process_runtime.py`
- `src/physics/momentum_engine.py`
- `src/mobility/micro/free_motion_solver.py`
- `src/models/model_engine.py`
- `data/registries/constitutive_model_registry.json`
- `data/registries/model_type_registry.json`
- `data/registries/field_type_registry.json`
- `schema/physics/momentum_state.schema`
- `schema/physics/force_application.schema`
- `schema/physics/impulse_application.schema`

Audit method:

- process dispatch path scan (`process.apply_force`, `process.apply_impulse`, `process.mobility_free_tick`, `process.model_evaluate_tick`)
- velocity/acceleration write pattern scan inside mobility runtime
- gravity pathway scan for non-model bypasses
- schema/registry presence check for PHYS-1 substrate payloads

## 2) Direct Velocity Mutation Audit

### Findings

- ROI free-motion integration path is momentum-backed:
  - `process.mobility_free_tick` resolves/creates `momentum_state`.
  - `step_free_motion` integrates momentum (`p`) and derives velocity (`v = p/m`) deterministically.
  - updated momentum rows are persisted and hashed (`momentum_hash_chain`).
- `process.apply_force` and `process.apply_impulse` update momentum only; they do not directly mutate body velocity.
- Model-driven force outputs (`process.model_evaluate_tick` + `model.phys.gravity_stub`) route through momentum updates.

### Transitional compatibility paths still present

- When momentum rows are absent, runtime seeds initial momentum from existing body/free-motion velocity to preserve legacy continuity.
- Legacy/adjacent mobility surfaces outside PHYS-1 ROI force substrate still contain direct velocity writes (for existing macro/meso compatibility behavior).

## 3) Inline Acceleration / Bypass Audit

### Findings

- Control inputs still produce acceleration intents in `src/mobility/micro/free_motion_solver.py`.
- PHYS-1 path no longer applies acceleration directly to velocity; acceleration contributes to momentum delta first, then velocity is derived from momentum.
- No new acceleration-to-velocity bypass introduced in PHYS-1 force/impulse processes.

## 4) Implicit Gravity Audit

### Findings

- Gravity application is routed through constitutive model path:
  - model type: `model_type.phys_gravity_stub`
  - model: `model.phys.gravity_stub`
  - process entry: `process.model_evaluate_tick`
  - emitted output: `derived_quantity` with `output_id = process.apply_force`
- No ad hoc direct gravity write path was found in MOB/PHYS process handlers.

## 5) Migration Notes (PHYS-1)

1. ROI free-motion now has an explicit momentum substrate (`momentum_states`, `force_application_rows`, `impulse_application_rows`).
2. Force and impulse mutation authority is centralized in `process.apply_force` and `process.apply_impulse`.
3. Gravity coupling is model-driven and profile-gated; no runtime mode flag added.
4. Legacy velocity-seeded momentum bootstrapping remains as a compatibility bridge and should be retired once all relevant producers emit momentum state natively.

## 6) Deprecation Notes

The following patterns are transitional and should not be expanded:

- initializing authoritative motion solely from velocity without persisted momentum state
- adding new direct velocity mutation paths outside PHYS process/model routes
- introducing gravity effects outside `Field -> ConstitutiveModel -> process.apply_force`

