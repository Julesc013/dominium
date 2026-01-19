# EXECUTION (Work IR + Scheduler)

Deterministic Work IR, scheduling, and budget enforcement for engine execution.

## Responsibilities
- Define work item schemas and queues (Work IR).
- Define scheduler phases and their ordering.
- Enforce bounded work per tick via budgets and carryover.
- Provide canonical traversal ordering hooks for deterministic execution.

## Non-responsibilities / prohibited
- No gameplay logic, solvers, or UI/platform time sources.
- No direct cross-system calls; only packet/bus interfaces.

## Spec
See `docs/specs/SPEC_SIM_SCHEDULER.md` and `docs/specs/SPEC_DETERMINISM.md`.
