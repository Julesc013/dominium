--------------------------------
OWNERSHIP & RESPONSIBILITY
--------------------------------
ENGINE:
- None. Engine provides generic primitives only if referenced.

GAME:
- Rules, policy, and interpretation defined by this spec.
- Implementation lives under `game/` (rules/content/ui as applicable).

TOOLS:
- None. Tools may only consume public APIs if needed.

SCHEMA:
- None (no canonical schema formats defined here).

FORBIDDEN:
- No launcher/setup orchestration logic in engine or game.
- No engine internal headers exposed outside engine targets.
- No game rules or policy implemented inside engine primitives.

DEPENDENCIES:
- Engine -> libs/ and schema/ only (never game/launcher/setup/tools).
- Game -> engine public API and schema/ only.
- Tools -> engine public API, game public API, and schema/ only.
- Launcher/Setup (if applicable) -> libs/contracts + schema (launcher may also use engine public API).
--------------------------------
# SPEC_SYSTEM_LOGISTICS - Scheduled Transfers and Station Inventories (v0)

This spec defines system-scale logistics as deterministic, scheduled gameplay
without physical simulation. Logistics runs on tick time and is authoritative.

## 1. Scope
- Logistics is **non-physical** and event-driven.
- Authoritative time is `tick_index` + `ups`.
- No blocking I/O in runtime updates or queries.
- State changes occur only at tick boundaries via commands or scheduled events.

## 2. Core entities
### 2.1 Station
A station is a deterministic inventory node anchored to a body/frame.

Fields:
- `station_id` (u64, required, non-zero)
- `body_id` (u64, required, non-zero)
- `frame_id` (u64, required; 0 allowed for default body-fixed)
- `inventory` map: `resource_id` -> `quantity` (i64 or fixed-point integer)

Rules:
- Inventory entries are stored in deterministic order by `resource_id`.
- Negative inventory is forbidden.

### 2.2 Route
A route defines a scheduled transfer path between two stations.

Fields:
- `route_id` (u64, required, non-zero)
- `src_station_id` (u64, required)
- `dst_station_id` (u64, required)
- `duration_ticks` (u64, required, > 0)
- `capacity_units` (u64, required, > 0)

Rules:
- Routes are deterministic data; no physical simulation.
- Capacity limits total units per transfer.

### 2.3 Transfer
A transfer is a scheduled inventory movement along a route.

Fields:
- `transfer_id` (u64, required, non-zero)
- `route_id` (u64, required)
- `start_tick` (u64, required)
- `arrival_tick` (u64, required, `start_tick + duration_ticks`)
- `items` map: `resource_id` -> `quantity` (positive)

Rules:
- Inventory is debited at scheduling time.
- Inventory is credited at arrival tick.
- Multiple transfers arriving at the same tick are applied in deterministic
  order (ascending `transfer_id`).

### 2.4 Production Rule (v0)
Production applies periodic deltas to station inventories.

Fields:
- `rule_id` (u64, required, non-zero)
- `station_id` (u64, required)
- `resource_id` (u64, required)
- `delta_per_period` (i64, non-zero)
- `period_ticks` (u64, required, > 0)

Rules:
- Deltas apply at exact multiples of `period_ticks`.
- Production is deterministic and idempotent under tick batching.

## 3. Determinism requirements
- Ordering is deterministic for stations, routes, transfers, and rules.
- Scheduling and arrival are invariant under tick batching and warp pacing.
- Logistics state changes must not depend on wall-clock time or I/O timing.

## 4. Refusal conditions
Refuse commands or loads when:
- IDs are zero or duplicate.
- Referenced stations/routes do not exist.
- Transfer quantity exceeds route capacity.
- Inventory is insufficient at scheduling time.
- Any inventory operation would go negative.

## 5. Persistence (authoritative)
Logistics state is sim-affecting and MUST be persisted:
- Universe bundle chunks: `STATIONS`, `ROUTES`, `TRANSFERS`, `PRODUCTION_RULES`
- Save chunks: `STAT`, `ROUT`, `TRAN`, `PROD`
- Chunks are versioned, skip-unknown, and included in identity digests.

## 6. Macro economy linkage (v0)
- Macro economy aggregates MAY influence production rates or availability but
  MUST NOT directly move inventory or bypass logistics rules.
- See `docs/SPEC_COSMO_ECONOMY_EVENTS.md` for macro-level rules.

## 7. Factions and AI planners (v0)
- Factions may create stations, routes, and transfers only through the same
  command pipeline as players.
- AI planners MUST be deterministic, budgeted, and auditable.
- See `docs/SPEC_FACTIONS.md` and `docs/SPEC_AI_DETERMINISM.md`.

## Related specs
- `docs/SPEC_UNIVERSE_MODEL.md`
- `docs/SPEC_COSMO_LANE.md`
- `docs/SPEC_COSMO_ECONOMY_EVENTS.md`
- `docs/SPEC_FACTIONS.md`
- `docs/SPEC_AI_DETERMINISM.md`
- `docs/SPEC_SPACETIME.md`
- `docs/SPEC_DETERMINISM.md`
