--------------------------------
OWNERSHIP & RESPONSIBILITY
--------------------------------
ENGINE:
- None. Engine provides generic primitives only if referenced.

GAME:
- Rules, policy, and interpretation defined by this spec.
- Implementation lives under `game/` (rules/content/ui as applicable).

TOOLS:
- Authoring/inspection utilities described here.
- Implementation lives under `tools/` (including shared tool runtime).

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
# SPEC_UI_CAPABILITIES — Capability Engine (UI Inputs)

Status: draft  
Owner: Dominium game layer  
Scope: Capability Engine outputs only (no authoritative world access).

## Purpose
Defines the deterministic capability objects produced by the Capability Engine.
Capabilities are the only inputs to UI/HUD projections. They are derived from
BeliefStores and Time Knowledge state; they are not authoritative facts.

## Core invariants
- Capabilities are derived, not authoritative.
- Capability derivation is deterministic and replayable.
- Missing knowledge yields `UNKNOWN` or absent capabilities.
- Conflicts are visible; no silent resolution.
- Capabilities never mutate simulation state.

## Capability taxonomy (mandatory)
Each capability declares its category and subject scope:
- `TIME_READOUT`
- `CALENDAR_VIEW`
- `MAP_VIEW`
- `POSITION_ESTIMATE`
- `HEALTH_STATUS`
- `INVENTORY_SUMMARY`
- `ECONOMIC_ACCOUNT`
- `MARKET_QUOTES`
- `COMMUNICATIONS`
- `COMMAND_STATUS`
- `ENVIRONMENTAL_STATUS`
- `LEGAL_STATUS`

## Capability structure (minimum fields)
Each capability instance includes:
- `capability_id` (stable id)
- `subject` (kind + id)
- `resolution_tier` (UNKNOWN/BINARY/COARSE/BOUNDED/EXACT)
- `value_min` / `value_max` (uncertainty envelope)
- `observed_tick`
- `delivery_tick`
- `expiry_tick`
- `latency_ticks`
- `staleness_ticks`
- `source_provenance`
- `flags` (UNKNOWN/STALE/DEGRADED/CONFLICT)

## Derivation pipeline
```
[ Belief Store ]
        ↓
[ Capability Derivation Rules ]
        ↓
[ Effect Field Filters ]
        ↓
[ Capability Snapshot ]
```
Notes:
- Derivation rules may merge multiple belief records per subject.
- Time knowledge inputs generate `TIME_READOUT` and `CALENDAR_VIEW` capabilities.
- Effect fields may widen uncertainty or increase latency, deterministically.

## Conflict & UNKNOWN handling
- `UNKNOWN` = missing data or explicit unknown record.
- Conflicts:
  - multiple belief records for the same subject with incompatible ranges or provenance.
  - represented by the `CONFLICT` flag and widened envelopes.
- No automatic conflict resolution.

## Performance requirements
- Derivation cost is O(n) in relevant belief records.
- Snapshots are cached per tick and invalidated on belief/time-knowledge revision changes.
- No per-frame recomputation.

## Determinism & replay
- Snapshot ordering is deterministic:
  `capability_id` → `subject.kind` → `subject.id` → `source_provenance`.
- Replays produce byte-identical capability snapshots for identical inputs.

## Testing requirements (non-exhaustive)
- Deterministic snapshot ordering.
- Capability removal when beliefs are removed.
- Conflict visibility with widened envelopes.
- Uncertainty scaling via effect field filters.
- UNKNOWN propagation from missing knowledge.
- Replay equivalence.

## References
- `docs/SPEC_EPISTEMIC_INTERFACE.md`
- `docs/SPEC_INFORMATION_MODEL.md`
- `docs/SPEC_TIME_KNOWLEDGE.md`
