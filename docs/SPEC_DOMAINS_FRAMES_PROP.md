# SPEC_DOMAINS_FRAMES_PROP — Domains, Frames, Propagators

This spec defines structural partitioning (domains), coordinate frames (frame
graph), and propagators used to update representations deterministically.

## Scope
Applies to:
- world domains and their stable identifiers
- frame graph and fixed-point transforms
- propagators and representation ladders
- deterministic, bounded incremental update rules

## World domains
Domains partition authoritative state.

Invariants:
- domain IDs MUST be stable and totally ordered
- domain iteration order MUST be canonical (stable ID ordering)
- cross-domain effects MUST be expressed explicitly (packets/deltas), not by
  hidden cross-calls

## Frame graph
Frames define coordinate contexts for poses and transforms.

Invariants:
- frame IDs MUST be stable and totally ordered
- transforms MUST be fixed-point and quantized (see `docs/SPEC_POSE_AND_ANCHORS.md`)
- frame graph updates MUST be deterministic and bounded

## Propagators
Propagators are deterministic mechanisms that:
- react to authoritative changes (deltas)
- update derived representations and caches
- operate under explicit per-tick budgets with carryover

Propagators MUST:
- be incremental (dirty marking) rather than unbounded scans
- have canonical processing order (stable keys)

## Representation ladders
Domains and propagators interact with the LOD ladder:
- R0 is authoritative within domains
- R1–R3 are derived caches updated by propagators under budget

See `docs/SPEC_LOD.md`.

## Forbidden behaviors
- Treating global grids as authoritative state or logic dependencies.
- World-space baked geometry as authoritative truth.
- Unordered iteration in propagators (hash tables, pointer identity).
- Platform-dependent behavior (time/threads/locale).

## Source of truth vs derived cache
**Source of truth:**
- domain-owned R0 state and committed deltas
- stable frame identifiers and anchor/pose relationships

**Derived cache:**
- propagator indices, adjacency caches, spatial accelerators
- R1–R3 representations

## Related specs
- `docs/SPEC_DETERMINISM.md`
- `docs/SPEC_SIM_SCHEDULER.md`
- `docs/SPEC_LOD.md`
- `docs/SPEC_GRAPH_TOOLKIT.md`
- `docs/SPEC_POSE_AND_ANCHORS.md`

