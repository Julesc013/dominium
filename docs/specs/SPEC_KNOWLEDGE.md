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

DEPENDENCIES (Phase 1 overrides apply):
- Engine -> (no dependencies outside engine/).
- Game -> engine public API only.
- Tools -> engine public API + game public API only.
- Launcher/Setup -> libs/ + schema only (no engine/game dependencies).
--------------------------------
# Knowledge / Fog of War

NOTE:
This document is legacy and is superseded by:
- `docs/SPEC_INFORMATION_MODEL.md`
- `docs/SPEC_KNOWLEDGE_VIS_COMMS.md`
Any `dknowledge_*` naming here is a placeholder for game-layer derived cache
functions. It MUST NOT imply engine ownership or authoritative state.

- Knowledge types: tile visibility, entity sightings, market info. Keys are `KnowledgeKey { type, subject_id }`.
- Records: `KnowledgeRecord { key, last_seen_tick, confidence_0_1 }` stored in `KnowledgeBase { id, records[], record_count, record_capacity }`.
- Registry: `dknowledge_create(capacity)` grabs a fixed slice of the global record pool; lookup via `dknowledge_get`; destroy clears handles (pool memory is static).
- Updates: `dknowledge_observe` finds or inserts a record (linear scan). On full capacity, replacement is deterministic: lowest confidence wins; ties broken by oldest `last_seen_tick`. Confidence clamps to 0..1 (Q16.16).
- Queries: `dknowledge_query` returns a record pointer; `dknowledge_mark_tile_visible` hashes tile coords into a subject id and inserts visibility with full confidence.
- All storage is bounded arrays; no dynamic allocation during ticks.
