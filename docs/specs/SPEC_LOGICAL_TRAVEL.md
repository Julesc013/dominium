Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

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
- `docs/specs/SPEC_COSMO_LANE.md`
- `docs/specs/SPEC_DETERMINISM.md`