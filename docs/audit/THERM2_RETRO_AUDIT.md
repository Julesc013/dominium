# THERM2 Retro-Consistency Audit

Date: 2026-03-03  
Scope: THERM-2 phase change, curing, insulation, and exchanger interface prep

## Findings

1. Existing freeze/melt logic
- Result: no canonical material phase-transition process existed in runtime process dispatch.
- Notes: thermal behavior currently focused on THERM-1 network energy/temperature solve; phase transitions were only documented as future stubs.

2. Existing curing behavior
- Result: no canonical cure state row/process was found in authoritative runtime mutation paths.
- Notes: no deterministic cure-progress store existed for structures/parts.

3. Existing insulation modifiers
- Result: thermal edge kinds include `insulated_link`, but insulation factor handling was not yet model-driven in THERM solve.
- Notes: conductance values were consumed directly from edge payloads.

4. Heat exchanger compatibility hooks
- Result: `thermal.node.heat_exchanger_stub` exists, but interface-level thermal/fluid port declaration was incomplete.
- Notes: registry-level interface prep is required for FLUID coupling.

## Migration Plan

1. Add canonical data contracts
- `schema/materials/phase_profile.schema`
- `schema/thermal/cure_state.schema`
- `data/registries/material_phase_registry.json`

2. Enforce model-driven phase/cure/insulation behavior
- `model_type.therm_phase_transition`
- `model_type.therm_cure_progress`
- `model_type.therm_insulation_modifier`

3. Route mutations through processes
- `process.material_transform_phase`
- `process.cure_state_tick`

4. Expose THERM-2 inspection and UX summaries
- `section.thermal.phase_states`
- `section.thermal.cure_progress`
- `section.thermal.insulation_effects`

5. Add enforcement and tests
- RepoX: `INV-PHASE-CHANGE-MODEL-ONLY`, `INV-NO-ADHOC-CURE-LOGIC`
- AuditX: `InlinePhaseChangeSmell`, `InlineCureSmell`
