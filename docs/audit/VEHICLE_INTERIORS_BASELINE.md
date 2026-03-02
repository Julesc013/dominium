# VEHICLE_INTERIORS_BASELINE

Status: BASELINE
Last Updated: 2026-03-03
Scope: MOB-10 vehicle interior and compartment-flow integration during mobility.

## 1) Spatial Frame Rules

- Vehicle interior behavior is assembly-consistent with building interiors:
  - interior volumes are attached to vehicle spatial nodes.
  - pose slot spatial metadata is synchronized to the vehicle frame.
- Deterministic sync is process-driven in:
  - `process.vehicle_register_from_structure`
  - `process.vehicle_apply_environment_hooks`
- Runtime frame sync metadata is explicit (`interior_frame_sync` / `interior_frame_updates`) and event-sourced.
- Vehicle movement updates preserve interior-relative offsets via composed transforms and vehicle world-position resolution.

## 2) Boundary Exchange Model

- `process.compartment_flow_tick` resolves owner vehicle context for an interior graph and applies external boundary conditions at portals.
- Boundary sampling is deterministic and field-driven:
  - `field.temperature`
  - `field.moisture`
  - `field.visibility`
  - `field.wind`
- Boundary sample positions are computed as:
  - owner vehicle world position + portal local offset.
- Micro-tier ram-air stub is integrated deterministically:
  - `ram_air_boost_air_conductance` from vehicle speed.
  - wind magnitude + ram-air boost modifies portal air conductance.
- Boundary payload is persisted in `portal_flow_params[*].extensions.field_boundary` with source tick/process metadata.

## 3) Breach/Leak Behavior

- Portal/hull breach path:
  - `process.portal_seal_breach`
  - mechanics fracture linkage path in `process.mechanics_fracture`
- Effects of breach:
  - portal sealing coefficient reduction
  - deterministic leak hazard creation (`interior_leak_hazards`)
  - interior portal transition provenance event
- Incident reason codes emitted (when conditions apply):
  - `incident.breach`
  - `incident.decompression` (stub threshold)
  - `incident.flooding_started`
- Vehicle/travel incident traces are written for reenactment:
  - `travel_events` with `kind=incident_stub`
  - `vehicle_events` with `event_kind=vehicle_interior_incident`

## 4) UX and Instrumentation

- Vehicle diegetic dashboard instruments are surfaced from compartment flow state:
  - `instrument.vehicle.pressure`
  - `instrument.vehicle.oxygen`
  - `instrument.vehicle.smoke_alarm`
  - `instrument.vehicle.flood_alarm`
- Observation channels added:
  - `ch.diegetic.vehicle.pressure`
  - `ch.diegetic.vehicle.oxygen`
  - `ch.diegetic.vehicle.smoke_alarm`
  - `ch.diegetic.vehicle.flood_alarm`
- Inspection coverage added:
  - `section.vehicle.interior_summary`
  - `section.vehicle.portal_states`
  - `section.vehicle.pressure_map`
- Values remain coarse/quantized for diegetic visibility policies; no direct truth-side bypass introduced.

## 5) Extension Points

- HVAC machine-level simulation remains deferred and can be layered through existing ports/machine operations.
- Health/survival effects remain deferred; current scope is environmental state + alarms + hazards only.
- Existing hooks are compatible with future:
  - richer pressure/atmosphere machines
  - advanced decompression/flood propagation policies
  - deeper reenactment playback paths.

## 6) Gate Runs (2026-03-03)

- RepoX:
  - command: `python tools/xstack/repox/check.py --repo-root . --profile STRICT`
  - status: `pass`
- AuditX:
  - command: `python tools/xstack/auditx/check.py --repo-root . --profile STRICT`
  - status: `pass` (findings reported at warn severity)
- TestX (MOB-10 subset):
  - command: `python tools/xstack/testx/runner.py --repo-root . --profile STRICT --cache off --subset test_vehicle_interior_moves_with_vehicle,test_boundary_field_exchange_deterministic,test_breach_creates_leak_hazard,test_pose_access_requires_portal_path,test_instrument_redaction`
  - status: `pass` (5/5)
- strict build:
  - command: `python tools/setup/build.py --repo-root . --bundle bundle.base.lab --out build/dist.strict.mob10 --cache on --format json`
  - status: `complete`
- topology map update:
  - command: `python tools/governance/tool_topology_generate.py --repo-root . --out-json docs/audit/TOPOLOGY_MAP.json --out-md docs/audit/TOPOLOGY_MAP.md`
  - status: `complete`
  - deterministic fingerprint: `73530baacee5e71285da09d0b8e8391c4cf0a1bc21bdeb4d0e7b8778e0fe27ba`
