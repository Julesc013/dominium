# WORLD (Authoritative World State)

This directory contains authoritative world state and serialization primitives
for the deterministic engine core (C89).

## Boundaries
- Deterministic only: fixed-point math; canonical ordering for iteration/IO.
- No world-space baked geometry as authoritative truth (geometry is derived).
- Do not treat a global grid as authoritative placement truth or a required
  representation for all objects (UI snapping/grids are non-authoritative;
  explicit lattices are permitted only when the owning subsystem specifies them).

## Submodules (scaffold)
- `domain/` world domains and stable domain identifiers.
- `frame/` frame graph / coordinate frames used by simulation.

## Specs
See `docs/SPEC_DOMAINS_FRAMES_PROP.md`, `docs/SPEC_POSE_AND_ANCHORS.md`,
and `docs/SPEC_DETERMINISM.md`.
