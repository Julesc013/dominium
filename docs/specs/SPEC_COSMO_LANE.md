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
# SPEC_COSMO_LANE — Logical Universe Scale (Filaments → Galaxies → Systems)

This spec defines the Cosmos Lane: a deterministic, non-physical, logical model
for large-scale universe structure and travel.

## 1. Scope
- Cosmos is **logical only**; no physical simulation at this scale.
- Cosmos state is authoritative and deterministic.
- Time is tick-based (`tick_index` + `ups`).
- No blocking I/O in runtime queries or updates.
- Cosmos anchors and edges are sourced from core data packs; see
  `docs/SPEC_CORE_DATA.md` and `docs/SPEC_COSMO_CORE_DATA.md`.

## 2. Entity kinds
Canonical entity kinds:
- `FILAMENT`
- `CLUSTER`
- `GALAXY`
- `SYSTEM`

## 3. IDs and ordering
Each entity has:
- Stable string ID (UTF-8; no null terminator).
- Deterministic numeric ID (u64) derived from the string ID using the canonical
  hash (see `domino/core/spacetime.h`).
- Parent reference (numeric ID), except for root-level filaments.

Ordering:
- Iteration order MUST be deterministic and sorted by numeric ID ascending.
- Duplicate numeric IDs are invalid and MUST refuse.

## 4. Hierarchy rules
The graph is a strict parent-child hierarchy:
- FILAMENT has no parent.
- CLUSTER parent MUST be FILAMENT.
- GALAXY parent MUST be CLUSTER.
- SYSTEM parent MUST be GALAXY.

Cycles are invalid and MUST refuse.

## 5. Presentation-only coordinates (optional)
- Cosmos entities MAY include presentation-only coordinates.
- Any coordinates are **non-authoritative** and MUST NOT affect simulation.
- No floats are required or allowed in authoritative state.

## 6. Travel edges
Travel edges are discrete links between entities with deterministic parameters:
- `src_id` (u64)
- `dst_id` (u64)
- `duration_ticks` (u64)
- `cost` (u32, resource units)
- `event_table_id` (u64, optional; 0 means none)

Edges are stored in deterministic order (by edge numeric ID ascending).

## 7. Transit mode (authoritative)
Travel is an in-sim state (see `docs/SPEC_LOGICAL_TRAVEL.md`):
- Travel does not pause the sim.
- Arrival occurs at `start_tick + duration_ticks`.
- Arrival must be emitted deterministically.

## 8. System logistics (non-physical)
- System-scale logistics are scheduled gameplay anchored to systems/bodies and
  remain non-physical.
- Logistics MUST NOT introduce physics or alter cosmos graph topology.
- See `docs/SPEC_SYSTEM_LOGISTICS.md` for authoritative logistics rules.

## 9. Macro economy and events (logical)
- Galaxy/system aggregates and scheduled events operate above logistics and
  remain non-physical.
- Macro events MUST NOT alter cosmos graph topology.
- See `docs/SPEC_COSMO_ECONOMY_EVENTS.md` for authoritative rules.

## 10. Factions and AI planners (logical)
- Factions operate at cosmos/logistics scales only; no physical simulation.
- AI planners MUST emit explicit commands/events; no hidden mutations.
- See `docs/SPEC_FACTIONS.md` and `docs/SPEC_AI_DETERMINISM.md`.

## Related specs
- `docs/SPEC_LOGICAL_TRAVEL.md`
- `docs/SPEC_UNIVERSE_MODEL.md`
- `docs/SPEC_CORE_DATA.md`
- `docs/SPEC_COSMO_CORE_DATA.md`
- `docs/SPEC_SYSTEM_LOGISTICS.md`
- `docs/SPEC_COSMO_ECONOMY_EVENTS.md`
- `docs/SPEC_FACTIONS.md`
- `docs/SPEC_AI_DETERMINISM.md`
- `docs/SPEC_SPACETIME.md`
- `docs/specs/SPEC_DETERMINISM.md`
