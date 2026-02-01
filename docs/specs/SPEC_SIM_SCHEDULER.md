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
- None. Game consumes engine primitives where applicable.

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
# SPEC_SIM_SCHEDULER — Deterministic Tick Scheduler

This spec defines the authoritative tick scheduler for deterministic simulation
(SIM). It formalizes tick phases, commit points, and bounded work rules.

## Scope
Applies to:
- SIM tick advancement
- phase ordering within a tick
- delta commit rules
- budgets and carryover semantics

Does not define gameplay logic; it defines a deterministic execution framework.

## Invariants
- Simulation progresses in integer ticks; tick `N` is globally comparable.
- Phases are ordered and versioned; phase order MUST NOT depend on platform.
- All authoritative state mutation MUST occur via deltas at defined commit
  points (see `docs/specs/SPEC_ACTIONS.md`).
- All work is bounded per tick via deterministic budgets (work units, not time).

## Global tick phases (authoritative)
This is the fixed global phase list. Implementations MUST preserve ordering and
commit semantics.

1. **PH_INPUT**
   - Apply deterministic input/command packets for tick `N`.
   - No ad-hoc authoritative mutation outside delta commit.

2. **PH_TOPOLOGY**
   - Budgeted incremental compilation and dirty rebuild triggers.
   - Canonical graph rebuild scheduling (see `docs/specs/SPEC_GRAPH_TOOLKIT.md`):
     - dirty sets are converted into `dg_work_item` records keyed by `dg_order_key`
     - chunk-aligned graph partitions SHOULD use `dg_order_key.chunk_id` so per-chunk
       budgets can bound rebuild work deterministically
   - Deterministic LOD promotion/demotion planning and application:
     - `dg_promo_plan_and_enqueue()`
     - `dg_promo_apply_transitions_under_budget()`
   - No heavy solvers in this phase (scaffold only in early refactor).

3. **PH_SENSE**
   - Deterministic sensing/sampling.
   - Produces observation packets (immutable).

4. **PH_MIND**
   - Deterministic controller evaluation.
   - Produces intent packets (immutable).

5. **PH_ACTION**
   - Deterministic action dispatch.
   - Produces delta packets (buffered; NOT applied yet).

6. **PH_SOLVE**
   - Placeholder for physics/constraint solvers.
   - No domain logic in the scheduler spine; solvers compile deltas only.

7. **PH_COMMIT**
   - Apply buffered deltas to authoritative state in canonical order.
   - This is the only authorized mutation point for tick `N`.

8. **PH_HASH**
   - Compute per-phase hashes and replay trace hooks.
   - Deltas committed MUST be hashed in canonical commit order.

Any change to this list requires updating both this spec and `dg_phase` in
`source/domino/sim/sched/dg_phase.h`.

## Canonical ordering key (dg_order_key)
Scheduler-owned queues and the delta commit pipeline use a single canonical
stable total ordering key:

Fields (all fixed-size integers):
- `phase` (u16): phase id (matches `dg_phase` values)
- `domain_id` (u64)
- `chunk_id` (u64)
- `entity_id` (u64)
- `component_id` (u64): optional sub-identifier; `0` allowed
- `type_id` (u64): packet type or delta type id
- `seq` (u32): monotonic per producer; last-resort tie-break

Canonical comparison is lexicographic ascending by the field order above.
No pointer-order, hash-table iteration order, or platform-dependent ordering is
permitted in SIM scheduling.

## Delta commit rules
- Deltas are the only authorized mechanism for mutating engine state
  (`docs/specs/SPEC_ACTIONS.md`).
- The PH_COMMIT phase MUST apply deltas in a canonical total order.
- Deltas MUST carry an explicit stable sort key (`dg_order_key` or an equivalent
  delta-specific key derived from packet headers + monotonic `seq`).
- Commit MUST be a single source of truth: subsystems compile deltas, but only
  commit applies them.
- Partial application of a single delta within a tick is forbidden. If commit
  becomes budgeted in a later revision, deferral MUST be whole-delta (no partials).

## Budget + carryover semantics
Budgets are measured in deterministic "work units" (not wall-clock time).

Per phase:
- Each phase has a fixed budget `B_phase` for tick `N`.
- Work is expressed as discrete work items with stable keys.
- Items are processed in canonical key order until the budget is exhausted.
- If the next item cannot fit in the remaining budget, the scheduler MUST stop
  (no skipping) and carry over the remaining suffix unchanged.
- Unprocessed items are carried over to tick `N+1` without reordering.

Per-scope provisioning:
- If per-domain or per-chunk scoping is used (`domain_id != 0` and/or `chunk_id != 0`),
  the scheduler MUST provision bounded tables for those scopes at init time
  (no dynamic resizing during deterministic ticks).

Fairness must be deterministic:
- If rotation/round-robin is needed, rotation MUST be based on stable keys, not
  pointer identity or hash-table iteration.

## Forbidden behaviors
- Using OS time, threads, or async completion as a scheduling input.
- Making phase execution conditional on wall-clock, frame rate, or UI state.
- Unbounded scans in a phase without an explicit budget and carryover queue.

## Source of truth vs derived cache
**Source of truth:**
- tick number and scheduler queue state (stable ordering + deterministic budget)
- committed deltas and authoritative state

**Derived cache:**
- per-phase diagnostics/metrics
- any opportunistic caches used to accelerate scheduling decisions

## Related specs
- `docs/specs/SPEC_DETERMINISM.md`
- `docs/specs/SPEC_ACTIONS.md`
- `docs/specs/SPEC_PACKETS.md`
- `docs/specs/SPEC_FIELDS_EVENTS.md`
- `docs/specs/SPEC_LOD.md`
- `docs/specs/SPEC_DOMAINS_FRAMES_PROP.md`

## Engine core eligibility

> Any system that cannot be hashed, replayed, budgeted, and ordered canonically
> is not eligible to exist in the engine core.
