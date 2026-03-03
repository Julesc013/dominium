# THERM3 Retro-Consistency Audit

Date: 2026-03-03  
Scope: THERM-3 cooling systems, radiators, and ambient coupling.

## Findings

1. Existing cooling/heat sink logic
- `src/thermal/network/thermal_network_engine.py` currently supports THERM-1 conduction, heat capacity, loss-to-temp, and insulation modifier evaluation.
- No canonical ambient boundary exchange model is currently executed in T1/T0.
- No dedicated radiator profile registry is currently consumed by the T1 solver.

2. Direct ambient temperature mutation
- No direct mutation of `FieldLayer` ambient temperature baselines was found in THERM solver paths.
- Ambient influence is currently only a baseline scalar in local temperature derivation, not explicit boundary exchange.

3. Overheat behavior path
- Overtemperature hazards and `safety.overtemp_trip` are emitted in thermal solver safety pass.
- No explicit thermal-runaway escalation based on repeated cooling failure events is present.

4. Migration gaps for THERM-3
- Missing canonical contracts for ambient boundary rows and radiator profile rows.
- Missing constitutive model dispatch for ambient and radiator exchange.
- Missing inspection surfaces for ambient exchange summary and radiator efficiency.

## Migration Plan

1. Add canonical THERM-3 contracts
- `schema/thermal/ambient_boundary.schema`
- `schema/thermal/radiator_profile.schema`
- `data/registries/ambient_coupling_policy_registry.json`
- `data/registries/radiator_profile_registry.json`

2. Add model-driven cooling
- `model_type.therm_ambient_exchange`
- `model_type.therm_radiator_exchange`
- Keep insulation modifier in-model; no inline cooling coefficients outside model paths.

3. Integrate deterministic ambient/radiator execution into T0/T1
- T0: bookkeeping ambient exchange.
- T1: boundary/radiator exchange integrated in deterministic model ordering with budgeted degradation.

4. Extend safety/proof/inspection hooks
- Optional `hazard.thermal_runaway` escalation.
- Add `ambient_exchange_hash` surface for proof bundles.
- Add inspection sections for ambient exchange and radiator efficiency.

5. Enforce and test
- RepoX: no ad-hoc cooling; ambient through model path.
- AuditX: inline cooling and direct ambient temperature bypass smells.
- TestX: deterministic ambient/radiator behavior and budget degradation checks.
