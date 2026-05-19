Status: DERIVED
Last Reviewed: 2026-03-16
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-ARCHIVE
Replacement Target: legacy reference surface retained without current binding authority

# MACRO_TRAVEL_BASELINE

Status: BASELINE
Last Updated: 2026-03-02
Scope: MOB-4 macro itinerary, commitment, schedule, UX, and reenactment integration.

## 1) Itinerary Planning Rules

- Authoritative itinerary creation is process-only via `process.itinerary_create`.
- Route source is MobilityNetworkGraph through ABS deterministic routing.
- Deterministic ETA:
  - per-edge `eta_ticks = ceil(length_mm / allowed_speed_mm_per_tick)`
  - `estimated_arrival_tick = departure_tick + sum(eta_ticks)`
- Vehicle compatibility is enforced edge-by-edge through MOB-3 checks.
- Deterministic refusal paths:
  - `refusal.mob.no_route`
  - `refusal.mob.spec_noncompliant`
- Route artifacts now include deterministic per-edge profile metadata:
  - `guide_geometry_id`
  - `spec_id`
  - `allowed_speed_mm_per_tick`
  - curvature/spec warning flags for planning and inspection overlays

## 2) Travel Commitment Lifecycle

- Macro execution is process-only:
  - `process.travel_start`
  - `process.travel_tick`
- `process.travel_start` creates commitment chain and depart event:
  - `depart`
  - `waypoint` commitments per route edge
  - `arrive`
- `process.travel_tick` deterministically advances:
  - `motion_state.macro_state.current_edge_id`
  - `progress_fraction_q16`
  - edge transitions (`edge_exit`/`edge_enter`)
  - arrival completion (`arrive`)
- No silent movement mutation is allowed outside process runtime.

## 3) Timetable Behavior

- Timetables are ScheduleComponent rows (`travel_schedules`) created by `process.travel_schedule_set`.
- `process.travel_tick` consumes due schedule events and triggers travel start semantics through process runtime.
- Deterministic skip outcomes are event-sourced (`delay`) with explicit reason payloads.
- Runtime budget and downgrade outcomes are explicit:
  - schedule processing caps
  - deterministic deferred schedule ids

## 4) UX and Diegetic Integration

- Inspection/overlay integration now exposes:
  - route overlays with spec/curvature warnings
  - station-board style timetable rows in mobility network summary
  - driver coarse instrument states (speed/ETA/schedule state)
- Planning-side inspection includes:
  - per-edge warnings from route profile
  - itinerary/speed policy metadata
- All outputs are deterministic overlays/inspection payloads (no authoritative mutation in render path).

## 5) Reenactment Hooks

- Travel events carry replay anchors:
  - `guide_geometry_id`
  - `planned_speed_mm_per_tick`
  - itinerary/vehicle semantic refs
- Event stream indices are maintained per itinerary during:
  - `process.travel_start`
  - `process.travel_tick`
- Itinerary extensions store deterministic stream refs:
  - `travel_event_stream_id`
  - `travel_event_stream_hash`

## 6) Multiplayer and Performance

- Server-authoritative macro ticking is preserved in hybrid deployment.
- Lockstep behavior remains deterministic under identical inputs.
- Deterministic degradation paths:
  - update-budget deferral by stable ordering
  - optional far-vehicle cadence buckets for non-ROI macro updates
  - fidelity decisions logged with explicit downgrade reasons
- Macro-only simulation is preserved; no MOB-6/7 micro body stepping introduced.

## 7) Extension Points

- MOB-5 (congestion):
  - consume `travel_commitments`, active edge occupancy, and schedule pressure to alter ETA/speed policy.
- MOB-6/7 (micro physics):
  - use itinerary per-edge profile and travel event stream as handoff anchors for ROI micro stepping.
- Future incident models:
  - extend `incident_stub` with congestion/signal/field-driven incident families without changing commitment core.

## 8) Gate Runs (2026-03-02)

- RepoX:
  - command: `python tools/xstack/repox/check.py --repo-root . --profile STRICT`
  - status: `pass` (warn findings only)
- AuditX:
  - command: `python tools/xstack/auditx/check.py --repo-root . --profile STRICT`
  - status: `pass` (scan executed; findings reported)
- TestX (MOB-4 subset):
  - command: `python tools/xstack/testx/runner.py --repo-root . --profile STRICT --cache off --subset testx.mobility.travel.itinerary_deterministic,testx.mobility.travel.spec_noncompliance_refusal,testx.mobility.travel.tick_progress_deterministic,testx.mobility.travel.schedule_departures_deterministic,testx.mobility.travel.reenactment_event_stream_index_deterministic`
  - status: `pass` (5/5)
- strict build:
  - command: `python tools/setup/build.py --repo-root . --bundle bundle.base.lab --out build/dist.strict.mob4 --cache on --format json`
  - status: `complete` (`result=complete`)
- topology map update:
  - command: `python tools/governance/tool_topology_generate.py --repo-root . --out-json docs/audit/TOPOLOGY_MAP.json --out-md docs/audit/TOPOLOGY_MAP.md`
  - status: `complete` (`node_count=2377`, `edge_count=101838`)
  - deterministic fingerprint: `082a3519f830bef8b51c88cd75f414b900443aad23ddf21fe3d9affacdf7a6eb`
