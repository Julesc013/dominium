Status: DERIVED
Last Reviewed: 2026-03-16
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-ARCHIVE
Replacement Target: legacy reference surface retained without current binding authority

# MOB4 Retro-Consistency Audit

Status: AUDIT
Date: 2026-03-02
Scope: MOB-4 macro travel (itineraries, commitments, timetables) pre-implementation review.

## 1) Existing teleport and direct relocation semantics

Findings:
- Camera teleport exists as a control-plane process (`process.camera_teleport`) for view control, not vehicle travel.
  - `tools/xstack/sessionx/process_runtime.py:321`
  - `tools/xstack/sessionx/process_runtime.py:647`
  - `tools/xstack/sessionx/process_runtime.py:8101`
- Cohort relocation currently mutates location references via migration metadata and arrival tick completion.
  - `tools/xstack/sessionx/process_runtime.py:6180`
  - `tools/xstack/sessionx/process_runtime.py:6235`
  - `tools/xstack/sessionx/process_runtime.py:6189`

Assessment:
- Vehicle macro travel is not yet implemented; existing teleport/relocation paths are domain-specific and should not be reused as mobility vehicle motion.

## 2) Existing schedule logic that overlaps travel semantics

Findings:
- Logistics manifests already use deterministic route edges and scheduled depart/arrive ticks.
  - `src/logistics/logistics_engine.py:697`
  - `src/logistics/logistics_engine.py:730`
  - `src/logistics/logistics_engine.py:901`
- This logic models shipment/material movement, not vehicle macro motion state over mobility network edges.

Assessment:
- Logistics schedule patterns are good references for deterministic timing/event handling, but mobility vehicles need separate canonical itinerary and travel commitment artifacts.

## 3) Existing mobility routing baseline

Findings:
- Mobility routing query process exists (`process.mobility_route_query`) with deterministic routing, switch filtering, and budget limits.
  - `tools/xstack/sessionx/process_runtime.py:20108`
  - `tools/xstack/sessionx/process_runtime.py:20175`
  - `tools/xstack/sessionx/process_runtime.py:20216`
- Current outputs are route-query artifacts only (`mobility_route_results`), not active travel execution.

Assessment:
- MOB-4 should consume this deterministic routing substrate for itinerary creation, then add commitment-driven macro execution.

## 4) Existing ad-hoc speed/traction logic

Findings:
- No vehicle macro speed progression logic currently exists in mobility runtime.
- Field/friction hooks were introduced in prior mobility/field phases, but no direct vehicle travel tick integration was found.

Assessment:
- MOB-4 should introduce explicit speed policy selection and ETA computation at itinerary creation, with no inline speed hacks.

## 5) Migration plan to macro travel commitments

1. Introduce canonical mobility travel contracts:
- Add `itinerary`, `travel_commitment`, and `travel_event` schemas and registries.

2. Add deterministic itinerary process:
- `process.itinerary_create` routes over MobilityNetworkGraph and validates per-edge vehicle/spec compatibility.
- Deterministically computes ETA from edge lengths and allowed speed policy.

3. Add macro execution process pair:
- `process.travel_start` creates depart/waypoint/arrive commitments and emits depart event.
- `process.travel_tick` advances edge progress deterministically in `vehicle_motion_states` macro tier.

4. Integrate timetables via ScheduleComponent:
- schedule due events trigger `process.travel_start` without direct state mutation outside process runtime.

5. Deprecation targets:
- Any future vehicle movement represented as direct position/location mutation without itinerary + travel commitments.
- Any mobility travel execution path bypassing control plane intents.
