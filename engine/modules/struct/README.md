# STRUCT (Structure Systems)

STRUCT owns structure models, compiled structure artifacts, and structure-local
physical representation scaffolding.

## Boundaries
- Deterministic fixed-point representations only.
- No baked world-space geometry as authoritative truth; use anchors/frames.
- Slot-based / rule-based packing only; no tolerance solvers.

## Submodules (scaffold)
- `model/` authored/semantic models and rulepack inputs.
- `compile/` deterministic compile pipeline into runtime-friendly artifacts.
- `phys/` structure-local physical representation scaffolding (no solvers yet).

## Spec
See `docs/specs/SPEC_TRANS_STRUCT_DECOR.md`, `docs/specs/SPEC_POSE_AND_ANCHORS.md`,
and `docs/specs/SPEC_DETERMINISM.md`.

