Status: DERIVED
Last Reviewed: 2026-03-16
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-ARCHIVE
Replacement Target: legacy reference surface retained without current binding authority

# Fire And Runaway Model

Status: CANONICAL  
Last Updated: 2026-03-04  
Scope: THERM-4 deterministic ignition, combustion hooks, spread bounds, and runaway coupling.

## 1) Ignition Model

Ignition is model-driven through `model.therm_ignite_stub`.

Required conditions:
- `temperature >= ignition_threshold`
- combustible material/profile is present
- oxygen proxy is available (stub policy, default true unless denied)
- target is not already in active fire state

Output:
- deterministic ignition trigger (`derived.therm.ignite_trigger`)

## 2) Combustion Model (Stub)

Combustion is model-driven through `model.therm_combust_stub`.

Inputs:
- active `fire_state`
- combustion profile rates

Outputs:
- heat emission (`quantity.thermal.heat_loss_stub` convention)
- pollutant emission stub (`derived.pollutant.emission_stub`)
- deterministic fuel consumption signal (`derived.therm.fuel_consumed`)
- hazard increment (`hazard.fire.basic`)

No full chemistry kinetics are simulated in THERM-4.

## 3) Spread Model

Spread evaluation runs over thermal-network adjacency with deterministic ordering:
- source targets sorted by `target_id`
- adjacency sorted by node id
- ignition queue order stable by deterministic traversal

Spread is bounded per tick:
- `max_fire_spread_per_tick`
- fixed iteration limit (`fire_iteration_limit`)

If cap is reached, deterministic degradation is logged.

## 4) Runaway Cascade

Cascade chain:
- overheat -> ignition -> combustion -> additional heat -> spread

Safety hook:
- `safety.thermal_runaway` events are generated via thermal safety integration when escalation criteria are met.

## 5) Process Lifecycle

Canonical process handlers:
- `process.start_fire`
- `process.fire_tick`
- `process.end_fire`

All state mutation and event emission for fire lifecycle occurs through these deterministic process paths.

## 6) Safety and Domain Hooks

- Fire tick may emit fail-safe safety hook events (`safety.fail_safe_stop`).
- LOTO and electrical interlocks remain authoritative in ELEC domain paths.
- POLL/FLUID remain stubs:
  - pollutant emissions are emitted as deterministic stub artifacts/rows
  - no fluid dynamics coupling is required in THERM-4.

## 7) Replay and Proof

Fire lifecycle surfaces:
- `fire_state_hash_chain`
- `ignition_event_hash_chain`
- `fire_spread_hash_chain`
- `runaway_event_hash_chain`

These are deterministic and replay-safe for proof generation and incident investigation.
