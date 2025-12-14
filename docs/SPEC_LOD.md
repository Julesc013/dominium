# SPEC_LOD — Representation Ladder (R0/R1/R2/R3)

This spec defines the deterministic representation ladder and the rules for
promotion/demotion under per-tick budgets.

## Scope
Applies to:
- representation levels R0–R3
- deterministic selection and tie-breaking
- promotion/demotion and rebuild accumulators

## Representation ladder
The ladder is structural, not gameplay-specific. The meaning of "detail" is
defined per subsystem, but the invariants are shared.

- **R0 (Authoritative)**: minimal authoritative state required for determinism.
- **R1 (Coarse derived)**: coarse derived representation for broad queries.
- **R2 (Local derived)**: localized derived representation for focused work.
- **R3 (Full derived)**: highest-fidelity derived representation.

Only R0 is permitted to be a source of truth. R1–R3 MUST be regenerable.

## Promotion/demotion rules
- Promotion/demotion is driven by explicit deterministic inputs:
  - focus sets (stable ids)
  - explicit tick-stamped requests
  - deterministic budgets
- Selection MUST be deterministic:
  - sort candidates by stable key
  - apply a deterministic scoring rule (integer/fixed-point only)
  - tie-break by stable ID ordering

Demotion MUST also be deterministic and MUST NOT depend on wall-clock time.

## Accumulator semantics
Promotion/demotion and rebuild work MUST be expressed as work items:
- each item has a stable key and a required work-unit cost
- the scheduler processes items in canonical order within the per-tick budget
- remaining items carry over without reordering (see `docs/SPEC_SIM_SCHEDULER.md`)

Accumulators MUST:
- be deterministic counters or queued work, not time-based timers
- be part of derived cache state (regenerable) unless explicitly needed for
  determinism and hashed (prefer not)

## Forbidden behaviors
- Using wall-clock time to drive LOD decisions.
- Floating-point heuristics.
- Unordered iteration or randomized sampling in selection.
- Treating global grids or baked geometry as authoritative LOD inputs.

## Source of truth vs derived cache
**Source of truth:**
- R0 authoritative state and the delta stream that mutates it

**Derived cache:**
- R1–R3 representations
- rebuild queues and dirty flags (regenerable)

## Related specs
- `docs/SPEC_DETERMINISM.md`
- `docs/SPEC_SIM_SCHEDULER.md`
- `docs/SPEC_DOMAINS_FRAMES_PROP.md`
- `docs/SPEC_GRAPH_TOOLKIT.md`
- `docs/SPEC_KNOWLEDGE_VIS_COMMS.md`

