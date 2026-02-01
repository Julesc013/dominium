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
# SPEC_FACTIONS - Deterministic Factions v0

This spec defines the deterministic faction model used by macro-scale AI.
Factions operate on logical systems/cosmos and never simulate physics.

## 1. Scope
- Faction logic is **non-physical** and schedule-driven.
- Authoritative time is `tick_index` + `ups`.
- Faction actions are explicit commands or scheduled macro events.
- No blocking I/O inside faction decision loops.

## 2. Faction definition
A faction is a deterministic, reproducible planning entity.

Fields:
- `faction_id` (u64, required, non-zero)
- `home_scope_kind` (`SYSTEM` or `GALAXY`, required)
- `home_scope_id` (u64, required, non-zero)
- `resources` map: `resource_id` -> `quantity` (i64 or fixed-point integer)
- `policies` (v0: small enum/flag set)
- `known_nodes` set (optional; list of system/galaxy IDs)
- `ai_seed` (u64, required; deterministic input)

Rules:
- Factions are stored in deterministic order by `faction_id`.
- Resource entries are stored in deterministic order by `resource_id`.
- `known_nodes` is stored in deterministic order by ID with duplicates removed.
- Resource quantities MUST NOT be negative.

## 3. Capabilities (v0)
Factions may generate:
- `CMD_STATION_CREATE_V1`
- `CMD_ROUTE_CREATE_V1`
- `CMD_TRANSFER_SCHEDULE_V1`
- Macro events (via `dom_macro_events_schedule`)

Factions MUST NOT:
- mutate simulation state directly,
- bypass command validation,
- use wall-clock or platform RNG.

## 4. Determinism rules
- Faction decisions are deterministic given:
  - `(tick, faction_state, world_state_digest, ai_seed)`.
- Output ordering is deterministic:
  - actions sorted by deterministic planner rules,
  - ties broken by ID ordering.
- Budget exhaustion yields deterministic no-ops with trace logging.

## 5. Persistence (authoritative)
Faction state is sim-affecting and MUST be persisted:
- Universe bundle chunk: `FACTIONS`
- Save chunk: `FACT`
- Replay metadata: `FACT` (for state reconstruction)
- Scheduler state: `AI_SCHED` (decision ticks and plan counters)
- Seeds: `AI_SEED` (if stored separately)

Chunks are versioned, skip-unknown, and included in identity digests where
they affect authoritative behavior.

## Related specs
- `docs/specs/SPEC_COSMO_ECONOMY_EVENTS.md`
- `docs/specs/SPEC_SYSTEM_LOGISTICS.md`
- `docs/specs/SPEC_AI_DETERMINISM.md`
- `docs/specs/SPEC_AI_DECISION_TRACES.md`
- `docs/specs/SPEC_DETERMINISM.md`