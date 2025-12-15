# Dominium — Milestones (Engine v0)

## v0 — Deterministic core bootstrap
- Build `domino_core` as a C90 static library with fixed-point math and deterministic hashing primitives.
- World lattice and chunk mapping implemented (`include/domino/dworld.h`).
- Deterministic SIM scaffolding present (scheduler, packets, stimulus buses, LOD ladder, replay/hash plumbing).
- TRANS/STRUCT/DECOR authoring + compile scaffolding present (anchor+pose placement; compiled artifacts are derived caches).
- Determinism regression tests and core determinism unit tests runnable via CTest (`source/tests`).

## Next steps (post-v0)
- Expand deterministic field sampling and world/environment solvers under budget.
- Extend save/load and replay formats while preserving TLV versioning and canonical ordering.
- Expand runtime front-ends (renderer/UI) without mutating authoritative state outside intent/delta contracts.
