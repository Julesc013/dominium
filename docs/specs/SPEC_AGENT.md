--------------------------------
OWNERSHIP & RESPONSIBILITY
--------------------------------
ENGINE:
- Deterministic primitives and invariants defined by this spec.
- Implementation lives under `engine/` (public API in `engine/include/`).

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
# SPEC_AGENT — Agents (AGENT) and Legacy AI Compatibility

This spec defines the boundaries and determinism constraints for agent systems.
It exists to prevent cross-layer mutation and nondeterministic “AI shortcuts”.

## Scope
Applies to:
- the refactor agent data model (`dg_agent_*`) under `source/domino/agent/**`
- agent/controller participation in the intent→delta pipeline (`docs/SPEC_ACTIONS.md`)
- canonical ordering, budgeting, and replay/hash participation for agent work

This repo also contains a legacy AI/agent implementation under
`source/domino/ai/**` (`d_agent_*`). It is compatibility scaffolding and MUST
NOT be treated as the reference design for new deterministic agent work.

## AGENT boundaries (refactor)

### Owns (authoritative)
The refactor AGENT layer owns:
- agent records and component attachments (`source/domino/agent/dg_agent.h`)
- agent component storage (`source/domino/agent/dg_agent_comp.h`)
- deterministic LOD representation state (`dg_rep_state`; `docs/SPEC_LOD.md`)

### Produces (derived outputs)
- observations/events/messages as deterministic packets (derived cache)
- intents as deterministic packets (inputs to action compilation)

### Consumes
- authoritative world state via deterministic queries only
- field samples/events/messages delivered at deterministic phase boundaries
  (`docs/SPEC_FIELDS_EVENTS.md`, `docs/SPEC_SIM_SCHEDULER.md`)

### Must never do
- mutate authoritative world state directly
- call platform/system APIs in determinism paths (time, threads, IO)
- rely on unordered iteration, pointer identity, or floating-point tolerance

## Determinism + ordering
- Agent IDs are stable numeric IDs with a total order (`dg_agent_id`).
- Any per-tick iteration over agents MUST use ascending stable IDs.
- Tie-break rules for agent outputs are explicit and stable (see
  `docs/SPEC_ACTIONS.md` for ordering keys).
- Any budgeting MUST be in deterministic work units (no wall-clock).

## Legacy AI/agent (`d_agent_*`) rules
Legacy `d_agent_*` code is permitted to exist as compatibility scaffolding, but:
- it MUST NOT be expanded into a second authoritative agent architecture
- it MUST NOT be used to bypass the refactor intent/delta pipeline
- any bridging between legacy and refactor agent IDs MUST be explicit,
  deterministic, and versioned (no implicit ID aliasing)

## Forbidden behaviors
- Direct UI-driven mutation of agent/world state (UI emits intents only).
- Randomization without an explicit deterministic seed context.
- Self-modifying logic, dynamic allocation in hot deterministic loops without
  bounded capacity planning.

## Source of truth vs derived cache
**Source of truth:**
- agent records/components and committed deltas that mutate them

**Derived cache:**
- perception/visibility/knowledge state, observation buffers, debug probes

## Related specs
- `docs/specs/SPEC_DETERMINISM.md`
- `docs/SPEC_ACTIONS.md`
- `docs/SPEC_FIELDS_EVENTS.md`
- `docs/SPEC_SIM_SCHEDULER.md`
- `docs/SPEC_LOD.md`
