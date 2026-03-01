Status: DERIVED
Version: 1.0.0
Last Reviewed: 2026-03-01
Scope: CTRL-8 deterministic effect system baseline

# Effect System Baseline

## Canon/Invariant Mapping
- A1 Determinism is primary (`docs/canon/constitution_v1.md`)
- A2 Process-only mutation (`docs/canon/constitution_v1.md`)
- A3 Law-gated authority (`docs/canon/constitution_v1.md`)
- A7 Observer/Renderer/Truth separation (`docs/canon/constitution_v1.md`)
- A9 Pack/registry-driven integration (`docs/canon/constitution_v1.md`)
- A10 Explicit degradation/refusal (`docs/canon/constitution_v1.md`)
- RepoX invariants:
  - `INV-EFFECT-USES-ENGINE`
  - `INV-NO-ADHOC-TEMP-MODIFIERS`

## CTRL-8 Contracts
- `schema/control/effect.schema`
- `schema/control/effect_type.schema`
- `schema/control/stacking_policy.schema`
- JSON schema mirrors:
  - `schemas/effect.schema.json`
  - `schemas/effect_type.schema.json`
  - `schemas/stacking_policy.schema.json`
  - `schemas/effect_type_registry.schema.json`
  - `schemas/stacking_policy_registry.schema.json`

## Baseline Effect Types
- `effect.speed_cap`
  - modifies: `max_speed_permille`
  - default visibility: `effect.visibility.diegetic_alarm`
- `effect.traction_reduction`
  - modifies: `traction_permille`
  - default visibility: `effect.visibility.diegetic_alarm`
- `effect.visibility_reduction`
  - modifies: `visibility_permille`
  - default visibility: `effect.visibility.diegetic_alarm`
- `effect.access_restricted`
  - modifies: `access_restricted`
  - default visibility: `effect.visibility.diegetic_alarm`
- `effect.tool_efficiency_modifier`
  - modifies: `tool_efficiency_permille`
  - default visibility: `effect.visibility.admin_numeric`
- `effect.machine_degraded`
  - modifies: `machine_output_permille`
  - default visibility: `effect.visibility.diegetic_alarm`
- `effect.pressure_hazard_warning`
  - modifies: `pressure_hazard_warning`
  - default visibility: `effect.visibility.diegetic_alarm`

Source registry: `data/registries/effect_type_registry.json`

## Baseline Stacking Policies
- `stack.replace_latest`
  - mode: `replace`
  - tie-break: `order.effect_type_applied_tick_effect_id`
- `stack.min`
  - mode: `min`
  - tie-break: `order.effect_type_applied_tick_effect_id`
- `stack.multiply`
  - mode: `multiply`
  - tie-break: `order.effect_type_applied_tick_effect_id`
- `stack.add`
  - mode: `add`
  - tie-break: `order.effect_type_applied_tick_effect_id`

Source registry: `data/registries/stacking_policy_registry.json`

## Deterministic Engine
- Engine module: `src/control/effects/effect_engine.py`
- Canonical ordering for stacking and target reduction:
  - `(effect_type_id, applied_tick, effect_id)`
- Expiration:
  - active iff `expires_tick is None` or `current_tick < expires_tick`
  - no wall-clock timers
- Query API:
  - `get_effective_modifier(target_id, key, ...)`
  - `get_effective_modifier_map(target_id, keys, ...)`
- Query cost accounting:
  - `query_cost_units=1` per modifier query (RS-5 cheap path)

## Process Integration
- Process handlers:
  - `process.effect_apply`
  - `process.effect_remove`
- Refusal codes:
  - `refusal.effect.forbidden`
  - `refusal.effect.invalid_target`
- State mutation path:
  - effect rows and effect provenance mutate only inside process runtime commit path.

## Control Plane Integration
- Control resolution computes effect influence before negotiation/refusal finalization.
- Active modifiers currently considered:
  - `access_restricted`
  - `visibility_permille`
  - `max_speed_permille`
  - `tool_efficiency_permille`
  - `machine_output_permille`
  - `pressure_hazard_warning`
- Decision logs include `extensions.effect_influence` fingerprint/context.
- Example behavior:
  - access-restricted target can refuse portal/hatch/vent operations with `refusal.effect.forbidden`.
  - visibility reduction can deterministically downgrade fidelity/view resolution.

## Diegetic/Admin Visibility
- Diegetic warning channels:
  - `ch.diegetic.warning.speed_cap`
  - `ch.diegetic.warning.low_visibility`
  - `ch.diegetic.warning.restricted_access`
- Warning instrument types:
  - `instr.warning.speed_cap`
  - `instr.warning.low_visibility`
  - `instr.warning.restricted_access`
- Diegetic channel payloads are coarse alarm state/bands.
- Admin/nondiegetic observation includes full effect vectors in `perceived_model.control.effects`.

## Migration Baseline
- Interior temporary restriction migration:
  - replaced ad hoc `interior_movement_constraints` state flags with auto effects:
    - `effect.access_restricted`
    - `effect.visibility_reduction`
    - `effect.pressure_hazard_warning`
- Maintenance degradation migration:
  - replaced ad hoc temporary degradation with `effect.machine_degraded` auto effects during `process.decay_tick`.

## Extension Points (MOB / DOM)
- MOB:
  - speed/traction control outputs can consume `max_speed_permille` and `traction_permille`.
  - per-track/per-region hazard packs can author effect rows via process routing.
- DOM/interior:
  - atmosphere/smoke/flood/hazard policies can emit effect rows through compartment process tick.
  - diegetic alarms remain coarse; admin tooling can inspect numeric vectors.

## Enforcement Baseline
- RepoX:
  - `INV-NO-ADHOC-TEMP-MODIFIERS`
  - `INV-EFFECT-USES-ENGINE`
- AuditX analyzers:
  - `E127_TEMP_MODIFIER_SMELL`
  - `E128_EFFECT_BYPASS_SMELL`

