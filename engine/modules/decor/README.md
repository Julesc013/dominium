# DECOR (Decoration)

DECOR contains decorative representation and rulepack scaffolding.
Decor is explicitly non-authoritative: it must never become gameplay truth.

## Boundaries
- Deterministic inputs/outputs; fixed-point only.
- No baked world-space geometry as authoritative state.
- No platform rendering integration (rendering consumes compiled decor outputs).

## Submodules (scaffold)
- `model/` decoration rulepacks and override definitions (authoring-side).
- `compile/` deterministic compilation of decor into runtime artifacts.

## Spec
See `docs/specs/SPEC_TRANS_STRUCT_DECOR.md` and `docs/specs/SPEC_DETERMINISM.md`.

