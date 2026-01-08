# SPEC_COSMO_ECONOMY_EVENTS - Galaxy Economy and Macro Events (v0)

This spec defines a logical, deterministic macro economy and event layer that
operates at system and galaxy scopes. It is non-physical and tick-driven.

## 1. Scope
- Macro economy is **logical only**; no physics or spatial simulation.
- Authoritative time is `tick_index` + `ups`.
- All changes occur via deterministic events at tick boundaries.
- No blocking I/O in runtime updates or queries.

## 2. Scope kinds
Macro economy state exists for:
- `SYSTEM` scope (system_id)
- `GALAXY` scope (galaxy_id)

Scope ordering is deterministic: `SYSTEM` then `GALAXY`, each sorted by id.

## 3. Aggregate state
Each scope has:
- `production_rate` map: `resource_id -> units_per_tick` (i64, integer)
- `demand_rate` map: `resource_id -> units_per_tick` (i64, integer)
- `stockpile` map (optional): `resource_id -> quantity` (i64, bounded)
- `flags` (u32 bitfield; e.g., embargo/boom)

Maps are stored and iterated in ascending `resource_id` order.

## 4. Event model
An event is a deterministic schedule entry:
- `event_id` (u64, stable)
- `scope_kind` (`SYSTEM` or `GALAXY`)
- `scope_id` (u64)
- `trigger_tick` (u64)
- `effects[]`:
  - `resource_id` (u64)
  - `production_delta` (i64, units/tick)
  - `demand_delta` (i64, units/tick)
  - `flags_set` / `flags_clear` (u32 bit masks)

Rules:
- Events fire exactly at `trigger_tick`.
- Event ordering is deterministic by `(trigger_tick, event_id)`.
- Event application is idempotent.

## 5. Event generation
- Events are generated deterministically from `seed` + content.
- No runtime randomness without an explicit seed.
- Empty event schedules are valid and deterministic.

## 6. Integration with system logistics (v0)
- Macro economy influences **rates and availability**, not inventory directly.
- Production rule deltas MAY be overridden by matching `production_rate` entries.
- Demand rates MAY provide informational caps for route usage; no enforcement in v0.

## 7. Persistence
Macro economy and events are sim-affecting and must be persisted:
- Universe bundle chunks: `MECO`, `MEVT` (versioned; skip-unknown)
- Save chunks: `MECO`, `MEVT`
- Replay headers store macro economy/events blobs (DMRP v4+); the record stream
  remains command-only.

## Related specs
- `docs/SPEC_COSMO_LANE.md`
- `docs/SPEC_SYSTEM_LOGISTICS.md`
- `docs/SPEC_UNIVERSE_BUNDLE.md`
- `docs/SPEC_SPACETIME.md`
- `docs/SPEC_DETERMINISM.md`
