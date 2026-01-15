# SIM/BUS (Routing)

Deterministic routing of fields, events, and messages between SIM modules.

## Responsibilities
- Canonical routing and sampling (stable ordering, stable fanout).
- Enforce "no direct cross-system calls" by making communication explicit.
- Provide deterministic batching under per-tick budgets.

## Non-responsibilities / prohibited
- No implicit global dispatch based on pointer identity or hash iteration.
- No UI-driven state mutation.

## Spec
See `docs/SPEC_FIELDS_EVENTS.md` and `docs/SPEC_DETERMINISM.md`.

