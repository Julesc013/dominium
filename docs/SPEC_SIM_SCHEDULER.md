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
  points (see `docs/SPEC_ACTIONS.md`).
- All work is bounded per tick via deterministic budgets (work units, not time).

## Global tick phases (authoritative)
Phase names are conceptual; implementations may rename internals but MUST
preserve ordering and commit semantics.

1. **TICK_BEGIN**
   - Establish tick `N` context.
   - Snapshot deterministic counters needed for reproducibility.

2. **INGEST**
   - Ingest canonical intent packets for tick `N`.
   - No mutation of authoritative state.

3. **VALIDATE**
   - Validate intents against the current authoritative state.
   - Produce actions and candidate deltas (immutable).

4. **APPLY (DELTA COMMIT)**
   - Apply deltas to authoritative state in canonical order.
   - This is the primary authoritative commit point for tick `N`.

5. **DERIVE**
   - Update derived caches (LOD, graphs, knowledge/visibility).
   - Derived updates MUST be deterministic and bounded by budgets.

6. **EMIT**
   - Emit events/messages/observations derived from the committed state.
   - Outputs MUST be canonicalized and versioned (see `docs/SPEC_PACKETS.md`).

7. **HASH**
   - Compute world hash over authoritative state after delta commit.
   - Record/assert hash as configured (see `docs/SPEC_DETERMINISM.md`).

8. **TICK_END**
   - Finalize tick accounting (budgets, carryover queues, counters).

## Delta commit rules
- Deltas are the only authorized mechanism for mutating engine state
  (`docs/SPEC_ACTIONS.md`).
- The APPLY phase MUST apply deltas in a canonical total order.
- Deltas MUST carry an explicit stable sort key. Tie-breaking is by stable IDs.
- Partial application of a single delta within a tick is forbidden. If a delta
  cannot be applied within budget, it MUST be deferred whole.

## Budget + carryover semantics
Budgets are measured in deterministic "work units" (not wall-clock time).

Per phase:
- Each phase has a fixed budget `B_phase` for tick `N`.
- Work is expressed as discrete work items with stable keys.
- Items are processed in canonical key order until the budget is exhausted.
- Unprocessed items are carried over to tick `N+1` without reordering.

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
- `docs/SPEC_DETERMINISM.md`
- `docs/SPEC_ACTIONS.md`
- `docs/SPEC_PACKETS.md`
- `docs/SPEC_FIELDS_EVENTS.md`
- `docs/SPEC_LOD.md`
- `docs/SPEC_DOMAINS_FRAMES_PROP.md`

