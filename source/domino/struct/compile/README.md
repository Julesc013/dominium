# STRUCT/COMPILE (Authoring → Compiled)

Deterministic compilation pipeline for STRUCT artifacts.

## Responsibilities
- Produce canonical compiled artifacts (stable IDs, stable ordering).
- Support slot-based corridor packing and rulepack application as a compile step.

## Non-responsibilities / prohibited
- No solvers; no tolerance-based fitting during compilation.
- No gameplay semantics.

## Spec
See `docs/SPEC_TRANS_STRUCT_DECOR.md` and `docs/SPEC_DETERMINISM.md`.

