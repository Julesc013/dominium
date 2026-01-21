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
# SPEC_KNOWLEDGE_VIS_COMMS — Knowledge, Visibility, Communications

This spec defines deterministic, derived observer state: knowledge/belief,
visibility/occlusion, and communications routing.

## Scope
Applies to:
- observer contexts and derived belief state
- deterministic visibility and occlusion evaluation
- deterministic communications routing and message delivery

## Observer contexts
An observer context is identified by a stable numeric ID and contains:
- configuration (what it can observe)
- derived belief/knowledge state
- derived visibility state

Observer contexts MUST be processed in canonical order (stable IDs).

## Belief/knowledge state
Knowledge/belief is always derived cache.

Rules:
- it MUST be computed only from deterministic inputs (observations/messages)
- it MUST NOT be authoritative world state
- it MUST be regenerable given authoritative state + packet streams

## Visibility and occlusion
Visibility is derived cache and MUST be deterministic:
- fixed-point only (no floats)
- canonical traversal order and tie-breaking
- bounded per-tick work under budgets (see `docs/SPEC_SIM_SCHEDULER.md`)

## Communications routing
Comms routing is deterministic and explicit:
- messages are packetized (`docs/SPEC_PACKETS.md`)
- routing and fanout use canonical ordering
- delivery does not depend on platform timing or network jitter

## Forbidden behaviors
- Using UI state or wall-clock time to change visibility/comms outcomes.
- Unordered iteration or pointer-based ordering.
- Treating derived visibility/knowledge as authoritative truth.

## Source of truth vs derived cache
**Source of truth:**
- authoritative world state and committed deltas
- packet streams (messages/observations) as recorded outputs if needed

**Derived cache:**
- belief/knowledge state
- visibility state and occlusion caches
- routing tables and acceleration structures

## Related specs
- `docs/specs/SPEC_DETERMINISM.md`
- `docs/SPEC_FIELDS_EVENTS.md`
- `docs/SPEC_PACKETS.md`
- `docs/SPEC_LOD.md`
- `docs/SPEC_SIM_SCHEDULER.md`

