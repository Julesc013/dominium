# TRANS (Transforms / Topology)

TRANS owns topology/transform representations that connect STRUCT and world
anchoring, compiled from authored data.

This directory also contains legacy “transport spline/mover” plumbing
(`d_trans_*`). Do not confuse the legacy `d_trans_*` subsystem with the refactor
TRANS corridor authoring/compile pipeline (`dg_trans_*`).

## Boundaries
- Deterministic storage and canonical ordering.
- No platform APIs; no rendering geometry as authoritative state.

## Submodules (scaffold)
- `compile/` deterministic authoring → compiled artifact pipeline.
- `model/` deterministic authoring models (`dg_trans_*`).
- Legacy: `d_trans.*`, `d_trans_spline.*`, `d_trans_mover.*` (compat runtime).

## Spec
See `docs/SPEC_TRANS.md`, `docs/SPEC_TRANS_STRUCT_DECOR.md`,
`docs/SPEC_POSE_AND_ANCHORS.md`, and `docs/SPEC_DETERMINISM.md`.
