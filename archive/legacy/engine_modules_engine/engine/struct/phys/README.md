# STRUCT/PHYS (Structure Physical Representation)

Scaffolding for structure-local physical representation used by SIM.

## Responsibilities
- Define interfaces for physical constraints/contacts at fixed-point precision.
- Provide deterministic, bounded update hooks (no solvers in this scaffold).

## Non-responsibilities / prohibited
- No tolerance/epsilon solvers.
- No platform APIs.

## Spec
See `docs/SPEC_TRANS_STRUCT_DECOR.md` and `docs/SPEC_DETERMINISM.md`.

