# SPEC_POSE_AND_ANCHORS — Fixed-Point Pose + Anchors

This spec defines fixed-point pose representation and anchor-based positioning.
It explicitly forbids baked world-space geometry as authoritative truth.

## Scope
Applies to:
- pose representation used in deterministic simulation and packets
- quantization rules
- anchor-based positioning and frame references

## Fixed-point pose definition
A pose is:
- a reference `frame_id` (stable id)
- a fixed-point translation vector (Q format)
- an orientation represented in a deterministic, quantized form

All pose fields MUST be deterministic and serialized without padding.

## Quantization guarantees
- All pose components MUST be explicitly quantized using deterministic rounding
  rules (`source/domino/core/det_invariants.h`).
- Quantization rules MUST be stable across platforms and versions.
- Float-derived values from tools MUST be quantized before entering SIM.

## Anchor-based positioning (authoritative)
Anchors are stable reference points used to attach objects and structures.

Rules:
- Anchors and their relationships are authoritative state.
- World-space baked geometry MUST NOT be authoritative state.
- Any world-space geometry is a derived cache generated from anchors + compiled
  artifacts.

## Forbidden behaviors
- Storing world-space baked mesh geometry as truth.
- Using global grids as authoritative placement truth.
- Floating-point transforms in determinism paths.
- Tolerance/epsilon placement solvers.

## Source of truth vs derived cache
**Source of truth:**
- anchors, frames, and quantized poses

**Derived cache:**
- world-space transforms
- render meshes, collision meshes, visualization geometry

## Related specs
- `docs/SPEC_DETERMINISM.md`
- `docs/SPEC_DOMAINS_FRAMES_PROP.md`
- `docs/SPEC_TRANS_STRUCT_DECOR.md`
- `docs/SPEC_GRAPH_TOOLKIT.md`

