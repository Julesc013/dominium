Status: DERIVED
Last Reviewed: 2026-03-16
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-ARCHIVE
Replacement Target: legacy reference surface retained without current binding authority

# COUPLE-0 Retro-Consistency Audit

Date: 2026-03-06
Scope: Coupling budgets and relevance filtering constitution for cross-domain model evaluations.

## Inputs Audited
- `data/registries/coupling_contract_registry.json`
- `schema/meta/coupling_contract.schema`
- `tools/xstack/sessionx/process_runtime.py`
- `src/thermal/network/thermal_network_engine.py`
- `src/fluid/network/fluid_network_engine.py`
- `src/electric/power_network_engine.py`
- `src/chem/degradation/degradation_engine.py`
- `src/system/macro/macro_capsule_engine.py`

## Coupling Contract Inventory
Current declared coupling contracts:

1. `coupling.elec.loss_to_therm.heat`
2. `coupling.field.irradiance_to_therm.heating`
3. `coupling.therm.temperature_to_mech.strength`
4. `coupling.sig.trust_to_acceptance`
5. `coupling.field.friction_to_mob.traction`
6. `coupling.phys.gravity_to_mob.force`
7. `coupling.fluid.heat_to_therm.exchange`
8. `coupling.fluid.leak_to_int.flood`
9. `coupling.fluid.pressure_to_mech.load`
10. `coupling.chem.degradation_to_fluid.restriction`
11. `coupling.chem.degradation_to_therm.conductance`
12. `coupling.chem.degradation_to_mech.strength`
13. `coupling.chem.degradation_to_elec.insulation`
14. `coupling.chem.emission_to_poll.source`
15. `coupling.therm.fire_to_poll.source`
16. `coupling.fluid.contaminant_to_poll.transport`
17. `coupling.poll.concentration_to_field.visibility`
18. `coupling.poll.reporting_to_sig.institutional`

## Current Evaluation Sites and Cost Risk
Observed deterministic model evaluation hotspots:

- `process.model_evaluate_tick` in runtime:
  - Central model dispatch with generic budget (`max_cost_units`) and deterministic deferred rows.
  - Missing coupling-specific relevance policy, budget ownership, and explicit coupling evaluation records.
- Thermal network:
  - Multiple per-tick model passes (`loss`, `capacity`, `insulation`, `conduction`, `cooling`, `ignition`, `combustion`).
  - Heavy path under large node/edge counts; partly budgeted, but mostly unconditional by relevance.
- Fluid network:
  - Per-edge model binding evaluation with deterministic budget and optional deferral by model type.
  - No declared coupling relevance policy per coupling contract.
- Electric power network:
  - Per-context model runs with remaining-budget enforcement.
  - No coupling-level relevance gating beyond generic model budget.
- CHEM degradation:
  - Deterministic target cap + model-budget path.
  - Cross-domain coupling effects exist without coupling-level relevance records.
- SYS macro capsules:
  - Deterministic model evaluation with budget caps and forced expand logic.
  - Coupling contract relevance/budget classification not currently explicit.

## Preliminary Coupling Categorization
### Critical
- `coupling.elec.loss_to_therm.heat` (energy accounting integrity)
- `coupling.phys.gravity_to_mob.force` (core motion force substrate)
- `coupling.fluid.pressure_to_mech.load` (safety/failure coupling)
- `coupling.chem.degradation_to_elec.insulation` (fault/safety coupling)

### Important
- `coupling.field.irradiance_to_therm.heating`
- `coupling.field.friction_to_mob.traction`
- `coupling.fluid.heat_to_therm.exchange`
- `coupling.chem.degradation_to_fluid.restriction`
- `coupling.chem.degradation_to_therm.conductance`
- `coupling.chem.degradation_to_mech.strength`
- `coupling.chem.emission_to_poll.source`
- `coupling.therm.fire_to_poll.source`
- `coupling.fluid.contaminant_to_poll.transport`

### Optional / Diagnostic / Institutional
- `coupling.sig.trust_to_acceptance`
- `coupling.fluid.leak_to_int.flood` (scenario/profile-dependent priority)
- `coupling.poll.concentration_to_field.visibility` (visual/observer-oriented)
- `coupling.poll.reporting_to_sig.institutional` (already marked reserved)

## Findings
1. Coupling contracts are declared, but coupling-specific scheduling is not yet first-class.
2. Relevance checks are missing at coupling-contract level; many evaluations still run every tick when unchanged.
3. Degrade decisions exist at model/domain level, but not as canonical coupling-evaluation records.
4. Critical coupling fail-safe escalation is not explicitly enforced in a dedicated coupling scheduler path.

## Migration Plan
1. Add coupling budget and relevance policy schemas + registries.
2. Extend coupling contract rows with:
   - `coupling_relevance_policy_id`
   - `coupling_priority_class`
   - `coupling_cost_units`
3. Add deterministic relevance engine (`src/meta/coupling/coupling_relevance_engine.py`).
4. Add deterministic budget scheduler (`src/meta/coupling/coupling_scheduler.py`).
5. Integrate scheduler into `process.model_evaluate_tick` to gate coupling-bound model bindings.
6. Persist coupling evaluation records and proof hash chains.
7. Add RepoX invariants, AuditX smells, replay tool, and TestX coverage.
