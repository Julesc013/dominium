# THERM0 Retro-Consistency Audit

Status: Baseline audit complete (THERM-0 Phase 0)  
Date: 2026-03-03

## Scope

Audit targets:

- ad-hoc heat variables in machines/vehicles and thermal-sensitive domains
- inline overheat logic not expressed via hazard/effect/model pathways
- ELEC loss-to-heat convention usage status
- FIELD temperature usage consistency
- migration/deprecation path toward THERM domain governance

## Findings

1. Existing thermal-like logic already exists in multiple stacks and is not yet unified under a THERM constitution namespace.
- `engine/modules/world/heat_fields.cpp` and `engine/include/domino/world/heat_fields.h` implement deterministic heat stores/flows/stress with domain-local semantics.
- `schema/heat.store.schema`, `schema/heat.flow.schema`, and `schema/thermal.stress.schema` exist as earlier schema surfaces.

2. Inline overheat/temperature threshold logic exists outside an explicit THERM policy envelope.
- `tools/xstack/sessionx/process_runtime.py` contains direct temperature-band checks used for effects/conditioning and environmental transitions.
- `src/fields/field_engine.py` contains direct temperature threshold checks for derived state (for example icing/temperature bands).

3. ELEC currently follows the intended loss-to-heat convention in baseline paths.
- `src/electric/power_network_engine.py` emits `quantity.thermal.heat_loss_stub`.
- Electrical fault hooks in `tools/xstack/sessionx/process_runtime.py` emit `effect.temperature_increase_local`.
- Electrical inspection/report paths aggregate `heat_loss_stub` deterministically (`src/inspection/inspection_engine.py`, `src/client/interaction/inspection_overlays.py`).

4. FIELD temperature is available and used, but coupling contracts are not yet centralized under THERM policy IDs.
- `field.temperature` is sampled in `src/fields/field_engine.py` and in multiple runtime integration paths.
- Usage is deterministic but currently dispersed across subsystems.

## Migration / Deprecation Plan

1. Treat legacy heat schemas and runtime thermal hooks as pre-THERM substrate inputs.
2. Establish THERM constitution, policy, and registry scaffolding first (this prompt).
3. Enforce cross-domain loss mapping through THERM loss-to-heat conventions (`quantity.heat_loss` or fallback local temperature effect).
4. Migrate inline thermal response curves into constitutive model declarations in THERM-1+.
5. Keep null boot valid by making thermal policies optional (`therm.policy.none`) and refusing/degenerating deterministically when inactive.

