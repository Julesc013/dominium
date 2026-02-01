Status: CANONICAL
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

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
# SPEC_LOD — Representation Ladder (R0/R1/R2/R3)

This spec defines the engine-wide deterministic LOD framework: the
representation ladder, deterministic interest volumes, budgeted promotion/
demotion, and accumulator-safe deferral.

## Scope
Applies to:
- representation levels R0–R3 (`dg_rep_state`)
- representable interface/vtable (`dg_representable`)
- deterministic interest volumes (`dg_interest`)
- deterministic promotion/demotion planning (`dg_promo`)
- accumulator semantics for deferred integration (`dg_accum`, `dg_stride`)

Does not define gameplay logic, rendering, UI-driven interest, or platform code.

## Representation ladder (authoritative names)
The canonical ladder lives in `source/domino/sim/lod/dg_rep.h`:

- **R0_FULL**: full/highest-fidelity representation (baseline cadence).
- **R1_LITE**: reduced work/fidelity; must preserve invariants via accumulators.
- **R2_AGG**: aggregated/decimated representation (coarse derived/cached form).
- **R3_DORMANT**: dormant/minimal bookkeeping; reversible.

Subsystem semantics differ, but transitions MUST be explicit and reversible.

## Representable interface (vtable)
Every representable instance implements:
- `get_rep_state()`
- `set_rep_state(new_state)` (authoritative transition; phase boundary only)
- `step_rep(phase, budget)` (do only what current rep permits)
- `serialize_rep_state()` (for replay hashing + save/load)
- `rep_invariants_check()` (debug-only, deterministic)

Transitions MUST NOT occur mid-phase. Promotion/demotion runs at scheduler phase
boundaries (see `docs/specs/SPEC_SIM_SCHEDULER.md`).

## Deterministic interest volumes
Interest volumes are deterministic regions derived only from lockstep state.
They are NOT camera frusta and MUST NOT depend on UI state.

Volume families:
- `IV_PLAYER` (player-controlled entities)
- `IV_OWNERSHIP` (owned assets / claimed zones)
- `IV_HAZARD` (fires, floods, alarms, failures)
- `IV_ACTIVITY` (active jobs/tasks, interactions)
- `IV_CRITICAL_INFRA` (registered importance anchors)

All positions and extents:
- are fixed-point (no floats)
- are quantized/snapped to deterministic quanta
- are collected in deterministic order

## Promotion/demotion planner (deterministic under budget)
Promotion/demotion is executed in **PH_TOPOLOGY** as a deterministic substep:
- `dg_promo_plan_and_enqueue()`
- `dg_promo_apply_transitions_under_budget()`

Algorithm (authoritative):
1. Gather candidate objects from chunk-aligned indices (no unordered scans).
2. Compute deterministic interest score for each candidate (fixed-point only).
3. Determine desired rep state from score thresholds (engine defaults for now).
4. Sort candidates by:
   - desired rep state priority (R0 first, then R1, then R2, then R3)
   - descending interest score
   - stable tiebreak key: `(domain_id, chunk_id, entity_id, sub_id)`
5. Apply transitions in that order under deterministic budgets:
   - each transition consumes deterministic work units
   - if the next transition cannot fit in remaining budget, STOP (no skipping)
   - remaining transitions carry over to later ticks without reordering

## Accumulator semantics (critical)
LOD may change cadence/fidelity, but MUST NOT change authoritative outcomes.
All conserved quantities and deferred integration MUST use accumulators:
- `dg_accum_add()` records owed deltas deterministically
- `dg_accum_apply()` applies owed deltas under budget without loss

Cadence decimation uses:
- `dg_stride_should_run(tick, stable_id, stride)` using
  `(tick + hash(stable_id)) % stride == 0` with a deterministic hash

## Forbidden behaviors
- Float/double arithmetic in deterministic paths.
- UI-driven interest or wall-clock time inputs.
- Unordered iteration (hash-table iteration order, pointer ordering).
- LOD affecting results via hidden heuristics; all effects must be explicit and
  accumulator-safe.

## Related specs
- `docs/specs/SPEC_DETERMINISM.md`
- `docs/specs/SPEC_SIM_SCHEDULER.md`
- `docs/specs/SPEC_DOMAINS_FRAMES_PROP.md`
