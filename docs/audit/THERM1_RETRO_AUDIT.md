# THERM1 Retro-Consistency Audit

Date: 2026-03-03  
Scope: THERM-1 ThermalNetworkGraph + T1 meso conduction

## Findings

1. Direct temperature mutation outside model/process layer
- Result: No direct truth mutation path was found that writes thermal node temperatures as authoritative state outside the thermal/model stack.
- Notes: Existing thermal handling is mostly scaffolding (THERM-0 docs/registries). New THERM-1 solve path centralizes deterministic temperature evolution in `src/thermal/network/thermal_network_engine.py`.

2. ELEC loss-to-heat consistency
- Result: ELEC runtime already emits `quantity.thermal.heat_loss_stub` and temperature-increase hooks in power/fault paths.
- Notes: THERM-1 now consumes loss-style heat inputs through `model.therm_loss_to_temp` bindings and deterministic `heat_input_rows`.

3. Overheat logic coupling to hazards/safety
- Result: Legacy direct "overheat" gameplay branching is limited; core safety path now routed through hazard rows + `safety.overtemp_trip` event emission in thermal solve output.
- Notes: No direct shutdown mutation is performed in thermal engine; consumers are expected to apply trips through safety/process runtime.

## Migration Plan

1. Route thermal topology to THERM-1 payload schemas:
- `dominium.schema.thermal.thermal_node_payload@1.0.0`
- `dominium.schema.thermal.thermal_edge_payload@1.0.0`

2. Standardize thermal model usage:
- Node capacity/temperature: `model.therm_heat_capacity`
- Edge conduction: `model.therm_conductance`
- Cross-domain heat input mapping: `model.therm_loss_to_temp`

3. Enforce invariants in governance tooling:
- `INV-THERM-MODEL-ONLY`
- `INV-NO-DIRECT-TEMP-MUTATION`

4. Preserve deterministic downgrade behavior:
- T1 budget overflow falls back to T0 with explicit decision-log downgrade records.
