Status: DERIVED
Last Reviewed: unknown
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# THERM4 Retro-Consistency Audit

Date: 2026-03-04  
Scope: THERM-4 fire ignition, combustion stub, and runaway cascade framework.

## Findings

1. Existing fire/burn flags
- No canonical `thermal_fire_states`/`fire_state_rows` substrate existed in process runtime.
- No deterministic `event.fire_*` lifecycle rows were normalized in runtime state.

2. Hardcoded overheat to destruction logic
- THERM safety hooks for `hazard.overheat` and `safety.overtemp_trip` already exist in thermal solve.
- No deterministic process family existed for explicit `start_fire` / `fire_tick` / `end_fire`.

3. Model-driven ignition migration gap
- THERM T1 solve now includes model stubs (`model.therm_ignite_stub`, `model.therm_combust_stub`) and bounded spread behavior.
- Runtime, inspection, and proof surfaces still required explicit integration to make fire lifecycle replayable and inspectable.

## Migration Plan

1. Add canonical combustion contracts
- Add `schema/thermal/combustion_profile.schema` and `schema/thermal/fire_state.schema`.
- Add registry `data/registries/combustion_profile_registry.json`.

2. Keep ignition/combustion model-driven
- Use only `model_type.therm_ignite_stub` and `model_type.therm_combust_stub`.
- Keep spread deterministic and bounded (`max_fire_spread_per_tick`, iteration cap).

3. Add explicit fire process lifecycle
- `process.start_fire`
- `process.fire_tick`
- `process.end_fire`

4. Integrate safety, inspection, and proof
- Emit safety hooks for fail-safe on active combustion.
- Add inspection sections for fire states/runaway events.
- Extend proof bundle with fire hash chains.

5. Enforce against ad-hoc fire logic
- RepoX: `INV-FIRE-MODEL-ONLY`, `INV-NO-ADHOC-BURN-LOGIC`.
- AuditX: `InlineFireLogicSmell`, `UnboundedSpreadSmell`.
