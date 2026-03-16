Status: DERIVED
Last Reviewed: 2026-03-16
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-ARCHIVE
Replacement Target: legacy reference surface retained without current binding authority

# MOB5 Retro Audit

Status: BASELINE
Last Updated: 2026-03-02
Scope: MOB-5 meso traffic occupancy/capacity/congestion integration audit.

## 1) Existing Capacity Logic

- Static route-capacity filtering exists in ABS routing:
  - `src/core/graph/routing_engine.py`
  - `_route_constraints()` exposes `required_capacity`
  - `_filtered_graph()` removes edges where `edge.capacity < required_capacity`
  - this is admission filtering only; there is no time-varying occupancy state.
- Edge capacity fields already exist in graph payload and network normalization:
  - `src/core/graph/network_graph_engine.py` (`capacity`, `delay_ticks`)
  - `src/mobility/network/mobility_network_engine.py` maps edge payload `capacity_units`/`capacity`.
- Mobility network edit path can mutate static capacity values:
  - `tools/xstack/sessionx/process_runtime.py` (`set_edge_capacity` operation).

## 2) Existing Delay/Travel-Time Logic

- Itinerary ETA currently uses deterministic static per-edge speed and geometry metrics:
  - `src/mobility/travel/itinerary_engine.py`
  - `_edge_eta_ticks()` uses `length_mm / allowed_speed_mm_per_tick`.
- Macro travel progression currently uses precomputed edge ETA ticks:
  - `src/mobility/travel/travel_engine.py`
  - `tick_macro_travel()` increments `edge_elapsed_ticks` toward `edge_eta_ticks`.
- Delay events currently exist for schedule/start failures, not congestion:
  - `tools/xstack/sessionx/process_runtime.py` emits `travel_event(kind="delay")`
  - reasons include `vehicle_busy`, `schedule_target_missing`, and start-refusal reasons.

## 3) Current Gaps vs MOB-5 Objective

- No authoritative per-edge occupancy table.
- No congestion ratio or congestion policy evaluation.
- No reservation model for future edge-time capacity claims.
- No congestion-specific delay events (`event.delay.congestion`) in travel flow.
- No inspection/overlay surfaces for occupancy or congestion heatmap.

## 4) Migration Plan to Unified Meso Occupancy Model

- Introduce canonical `edge_occupancy` rows keyed by `edge_id`:
  - `capacity_units`, `current_occupancy`, `congestion_ratio`.
- Introduce congestion policy registry + deterministic multiplier function:
  - derive `effective_speed = base_speed / multiplier(congestion_ratio)`.
- Integrate occupancy updates into macro travel transitions:
  - increment on edge entry, decrement on edge exit via process runtime only.
  - deterministic vehicle ordering (`vehicle_id`) preserved.
- Add optional reservation rows and process API:
  - deterministic conflict resolution and explicit refusal on overflow.
- Extend travel events with congestion delay events:
  - explicit event logging, no silent itinerary/time mutation.
- Surface meso state in inspection + overlays:
  - edge occupancy section and congestion summary section
  - congestion visual encodings in network overlays.

## 5) Deprecation and Compatibility Notes

- Keep existing static `required_capacity` route constraints as admission gate.
- Layer dynamic meso occupancy on top; do not remove existing routing contract in MOB-5.
- Preserve deterministic behavior under budget pressure by deferring updates in stable order and logging downgrades.
