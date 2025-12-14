# WORLD/FRAME (Frame Graph)

Deterministic coordinate frames and frame graph scaffolding.

## Responsibilities
- Define stable frame IDs and canonical frame ordering.
- Provide deterministic frame composition rules (fixed-point only).

## Non-responsibilities / prohibited
- No floating point; no platform time sources.
- No baked geometry or external transforms as authoritative state.

## Spec
See `docs/SPEC_DOMAINS_FRAMES_PROP.md`, `docs/SPEC_POSE_AND_ANCHORS.md`, and `docs/SPEC_DETERMINISM.md`.

