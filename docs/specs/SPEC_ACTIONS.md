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
# SPEC_ACTIONS — Intent → Action → Delta

This spec defines the deterministic command pipeline used by SIM.

## Scope
Applies to:
- intent ingestion from Dominium/UI/tools/agents
- validation and action compilation
- delta application as the only legal state mutation

This spec also covers the semantic-free agent/controller substrate:
- sensors sample deterministic world views into **observations**
- minds/controllers consume observations and emit **intents**
- the action pipeline converts intents into **deltas** for commit

## Pipeline (authoritative)
0. **Sensors → Observations → Minds/Controllers**
   - Sensors read authoritative state via deterministic queries only and buffer
     `dg_pkt_observation` per agent.
   - Minds/controllers may read observation buffers + agent components and emit
     `dg_pkt_intent` packets only.
   - No direct mutation is permitted from sensors/minds/controllers.

1. **Intent**
   - External deterministic command input for tick `N`.
   - Immutable and TLV-versioned (`docs/SPEC_PACKETS.md`).

2. **Validation**
   - Deterministic, side-effect free read of the current authoritative state.
   - Produces either rejection or one-or-more actions/deltas.

3. **Action**
   - Internal representation of a validated intent (optional encoding).
   - Immutable and deterministic.

4. **Delta**
   - The only mechanism that mutates authoritative simulation state.
   - Applied at defined commit points in the scheduler (`docs/SPEC_SIM_SCHEDULER.md`).

## Delta handler registry (authoritative dispatch)
Delta application is performed via a deterministic handler registry:
- Registry key: `delta_type_id` (u64, carried in `dg_pkt_hdr.type_id`)
- Handler vtable: `apply(world, delta_packet)` (deterministic, no IO),
  optional `estimate_cost(delta_packet)` for budgeting
- Iteration order: ascending `delta_type_id` (no hash-map iteration)
- Unknown delta types MUST NOT mutate state; they are rejected at commit.

Commit (`PH_COMMIT`) is the sole mutation point:
- Subsystems may only *produce* deltas during earlier phases.
- Only the commit pipeline is allowed to call `apply()`.
  Any direct mutation outside commit is a determinism violation.

## Validation vs application
- Validation MUST NOT mutate state.
- Application MUST NOT perform validation-dependent branching that can diverge
  across peers; all required decisions MUST be encoded into deltas.

## Canonical ordering
- Intents are processed in canonical order.
- Deltas are applied in canonical order; tie-breaking by stable IDs.
- No pointer-order or hash-order behavior is permitted.

Additional canonical orderings for the agent substrate:
- Observations: `(type_id, src_entity, seq)` with deterministic tie-breaks.
- Intents: `(tick, agent_id, intent_type_id, seq)` where `agent_id = src_entity`.

## Forbidden behaviors
- Direct mutation of engine state outside deltas (including UI-driven writes).
- Platform-dependent branching (time, threads, locale, filesystem enumeration).
- Tolerance/epsilon comparisons that can diverge across platforms.

## Source of truth vs derived cache
**Source of truth:**
- the delta stream committed each tick
- the authoritative state after delta commit

**Derived cache:**
- pre-validation indices or lookup caches used to validate efficiently
- action graphs built from intents (rebuildable)

## Related specs
- `docs/SPEC_DETERMINISM.md`
- `docs/SPEC_PACKETS.md`
- `docs/SPEC_SIM_SCHEDULER.md`
- `docs/SPEC_VM.md`
