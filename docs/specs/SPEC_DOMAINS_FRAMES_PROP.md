--------------------------------
OWNERSHIP & RESPONSIBILITY
--------------------------------
ENGINE:
- Deterministic primitives and invariants defined by this spec.
- Implementation lives under `engine/` (public API in `engine/include/`).

GAME:
- Rules, policy, and interpretation defined by this spec.
- Implementation lives under `game/` (rules/content/ui as applicable).

TOOLS:
- None. Tools may only consume public APIs if needed.

SCHEMA:
- None (no canonical schema formats defined here).

FORBIDDEN:
- No launcher/setup orchestration logic in engine or game.
- No engine internal headers exposed outside engine targets.
- No game rules or policy implemented inside engine primitives.

DEPENDENCIES:
- Engine -> libs/ and schema/ only (never game/launcher/setup/tools).
- Game -> engine public API and schema/ only.
- Tools -> engine public API, game public API, and schema/ only.
- Launcher/Setup (if applicable) -> libs/contracts + schema (launcher may also use engine public API).
--------------------------------
# SPEC_DOMAINS_FRAMES_PROP — Domains, Frames, Propagators

This spec defines structural partitioning (domains), coordinate frames (frame
graph), and propagators used to update representations deterministically.

## Semantics-free primitives
Domains, frames, and propagators are **generic core primitives**. They MUST NOT
encode subsystem meaning (e.g. not "space", not "surface", not "combat").
Subsystems and DLCs attach meaning *around* these primitives by registering
domain types, frame graphs, and propagators.

All three are subject to:
- deterministic scheduler phases and bounded budgets (no clocks)
- the representation ladder (R0–R3) and deterministic promotion/demotion
- replay and per-tick hashing contracts (canonical ordering, stable IDs)

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
- domains are containers only; they do not imply gameplay semantics

## Frame graph
Frames define coordinate contexts for poses and transforms.

Invariants:
- frame IDs MUST be stable and totally ordered
- transforms MUST be fixed-point and quantized (see `docs/SPEC_POSE_AND_ANCHORS.md`)
- frame graph updates MUST be deterministic and bounded
- evaluation MUST traverse parent chains in a fixed, non-recursive order

## Propagators
Propagators are deterministic mechanisms that:
- react to authoritative changes (deltas)
- update derived representations and caches
- operate under explicit per-tick budgets with carryover

Propagators MUST:
- be incremental (dirty marking) rather than unbounded scans
- have canonical processing order (stable keys)
- use accumulators for lossless deferral when work is decimated or deferred

## Representation ladders
Domains and propagators interact with the LOD ladder:
- R0 is authoritative within domains
- R1–R3 are derived caches updated by propagators under budget

See `docs/SPEC_LOD.md`.

## Forbidden behaviors
- Treating a global grid as authoritative placement truth or a required
  representation for all objects (UI snapping/grids are non-authoritative;
  explicit lattices are permitted only when the owning subsystem specifies them).
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
