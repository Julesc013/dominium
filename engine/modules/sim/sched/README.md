# SIM/SCHED (Tick Scheduler)

Authoritative deterministic tick scheduler and phase orchestration for SIM.

## Responsibilities
- Define global tick phases and their ordering.
- Enforce bounded work per tick via budgets and carryover.
- Provide canonical traversal ordering hooks for deterministic execution.

## Non-responsibilities / prohibited
- No gameplay logic, solvers, or UI/platform time sources.
- No direct cross-system calls; only packet/bus interfaces.

## Spec
See `docs/SPEC_SIM_SCHEDULER.md` and `docs/SPEC_DETERMINISM.md`.

