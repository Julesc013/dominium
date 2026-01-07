# SPEC_LOGICAL_TRAVEL — TransitMode (Non-Physical Travel)

This spec defines logical travel between cosmos entities as an authoritative
state machine.

## 1. Scope
- Travel is **logical**, not physical; no orbital dynamics or physics.
- Travel is represented as a `TransitMode` state in the sim.
- Travel MUST NOT block UI/render or loading.

## 2. Transit state
Transit state fields:
- `src_entity_id` (u64)
- `dst_entity_id` (u64)
- `start_tick` (u64)
- `end_tick` (u64)
- `travel_edge_id` (u64)

## 3. Rules
- Transit is active when `current_tick < end_tick`.
- Arrival occurs exactly when `current_tick >= end_tick`.
- Arrival MUST emit a deterministic arrival event.
- Time warp advances ticks faster but MUST NOT skip arrival events.

## 4. Determinism
- Transit schedule is purely arithmetic: `end_tick = start_tick + duration_ticks`.
- Duration is an integer tick count; no floats or wall-clock time.
- Updating with different tick batching MUST yield identical arrival behavior.

## Related specs
- `docs/SPEC_COSMO_LANE.md`
- `docs/SPEC_DETERMINISM.md`
