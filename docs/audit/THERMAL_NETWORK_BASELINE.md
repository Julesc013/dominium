Status: DERIVED
Last Reviewed: unknown
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# THERMAL_NETWORK_BASELINE

Date: 2026-03-03  
Series: THERM-1

## Implemented Scope

1. Thermal network payloads
- Node payload schema: thermal mass/source/sink/radiator/exchanger-stub kinds with heat-capacity and thermal-energy fields.
- Edge payload schema: conduction/insulated/radiator link kinds with conductance.

2. Deterministic T1 solve
- Thermal networks are normalized and processed in stable order:
  - networks by `graph_id`
  - nodes by `node_id`
  - edges by `edge_id`
- T1 conduction rule:
  - model-driven transfer from higher temperature node to lower temperature node.
  - deterministic proportional transfer based on conductance and delta temperature.
- T0 fallback:
  - deterministic downgrade when budget/edge limits are exceeded.
  - downgrade logged via decision-log rows.

3. Constitutive models
- `model.therm_heat_capacity` -> energy-to-temperature mapping.
- `model.therm_conductance` -> edge heat transfer.
- `model.therm_loss_to_temp` -> cross-domain heat-loss ingestion.
- Evaluated through META-MODEL engine; no bespoke solver-side response curves.

4. Field integration
- Thermal node temperatures are exported as deterministic `field.temperature.global` cells at node positions.
- No global PDE diffusion is introduced; updates are local graph interactions.

5. Safety integration
- Overtemperature detection derives `hazard.overheat` rows and `safety.overtemp_trip` events.
- No direct device shutdown mutation occurs in thermal solver output.

6. Inspection and proofs
- Added thermal inspection sections:
  - `section.thermal.node_summary`
  - `section.thermal.edge_summary`
  - `section.thermal.overheat_risks`
- Extended control proof bundle mobility surface with:
  - `thermal_network_hash`
  - `overheat_event_hash_chain`

## Determinism and Budget Behavior

1. Stable ordering and canonical hashing are used for all THERM-1 outputs.
2. T1 budget pressure deterministically degrades to T0; no silent drift.
3. Output hashes are replay-stable for equivalent inputs.

## Readiness for THERM-2

1. Phase change and curing models can be introduced as additional constitutive model types.
2. Heat exchanger behavior can be expanded from `heat_exchanger_stub` and `radiator_link`.
3. INT/FLUID coupling can be added through loss/input artifacts without changing T1 invariants.
