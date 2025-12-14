# SIM/LOD (Level of Detail)

Representation ladder and deterministic promotion/demotion under budget.

## Responsibilities
- Define R0/R1/R2/R3 ladder and invariants.
- Deterministic selection and tie-breaking under a fixed budget per tick.
- Accumulator semantics for deferred work and rebuilds.

## Non-responsibilities / prohibited
- No heuristic/non-deterministic selection (no floats, no RNG, no wall clock).

## Spec
See `docs/SPEC_LOD.md` and `docs/SPEC_DETERMINISM.md`.

