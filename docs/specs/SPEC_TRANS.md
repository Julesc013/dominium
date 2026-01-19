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
# SPEC_TRANS — TRANS (Transforms / Topology)

TRANS is the transform/topology subsystem in the strict stack:

`BUILD / TRANS / STRUCT / DECOR / SIM / RES / ENV / JOB / AGENT`

TRANS owns authored corridor/connection topology and deterministic compilation
of derived runtime artifacts used by SIM queries and by downstream consumers
(STRUCT/DECOR bindings).

## Scope
Applies to:
- TRANS authoring models (alignments, section archetypes, attachments, junctions)
- deterministic compilation (microsegments, frames, slotmaps, spatial indices)
- anchor-based positioning for corridor surfaces (see `docs/SPEC_POSE_AND_ANCHORS.md`)

This spec does not define gameplay semantics (logistics/economy/pathfinding). It
defines structural, semantics-free primitives.

## Owns (authoritative)
Authoring models are canonical sources of truth:
- `dg_trans_alignment` (spine curve; fixed-point control points + z/roll profiles)
- `dg_trans_section_archetype` (cross-section slot layout)
- `dg_trans_attachment` (slot occupancy ranges and offsets along an alignment)
- `dg_trans_junction` (topology nodes and incident connections)

Authoritative rules:
- All parameters are fixed-point and MUST be quantized before commit.
- IDs are stable and totally ordered; storage is canonical sorted arrays.
- TRANS authoring MUST NOT store baked world-space mesh geometry as truth.

## Produces (derived cache)
Compiled TRANS artifacts are derived caches and MUST be rebuildable:
- microsegments (chunk-aligned partitions) and spatial indices
- sampled frames along alignments and per-slot frames
- slotmaps and surface catalogs for STRUCT/DECOR binding

Compilation is deterministic, budgeted, and ordered canonically (see
`docs/SPEC_SIM_SCHEDULER.md` and `docs/SPEC_DETERMINISM.md`).

## Consumes
- BUILD placement/edit intents expressed as `(dg_anchor, dg_pose)` plus TLV
  parameters (see `docs/SPEC_PACKETS.md` and `docs/SPEC_POSE_AND_ANCHORS.md`)
- STRUCT carrier artifacts emitted as parametric intent records (see
  `docs/SPEC_TRANS_STRUCT_DECOR.md`)
- world frame graph evaluation through public frame/anchor APIs only (no
  internal struct peeking)

## Determinism + ordering rules
- All compilation and rebuild work is expressed as stable work items and run
  under deterministic budgets with carryover (no skipping and no reordering).
- Tie-breaking MUST be explicit and stable; TRANS MUST NOT depend on pointer
  identity, hash-table iteration, filesystem enumeration order, or wall-clock.

## Forbidden behaviors
- Storing or ingesting baked world-space meshes/triangles as authoritative
  state.
- Tolerance/epsilon solvers for fitting, merging, or intersection resolution.
- Platform-dependent behavior in deterministic paths (time, threads, OS APIs).
- Treating UI snapping/grids as authoritative placement truth.

## Note: legacy spline/mover helpers
`source/domino/trans/d_trans_spline.*` and `source/domino/trans/d_trans_mover.*`
implement a generic spline+mover runtime. They are not a replacement for TRANS
authoring models. Any world-space node lists are treated as derived/compat
representations and MUST NOT become placement truth.

`source/domino/trans/d_trans.*` is a legacy subsystem wrapper around these
helpers (registered under `D_SUBSYS_TRANS` in the legacy subsystem registry).
It MUST NOT be used as the authoritative placement/topology source for the
refactor TRANS corridor pipeline described in this spec.

## Source of truth vs derived cache
**Source of truth (authoritative):**
- TRANS authoring models (alignments/sections/attachments/junctions) and their
  quantized parameters
- stable IDs and committed edits/deltas

**Derived cache (must be regenerable):**
- microsegments, frames, slotmaps, spatial indices, and other compiled artifacts
- any visualization or render geometry

## Related specs
- `docs/SPEC_TRANS_STRUCT_DECOR.md`
- `docs/SPEC_POSE_AND_ANCHORS.md`
- `docs/SPEC_GRAPH_TOOLKIT.md`
- `docs/SPEC_SIM_SCHEDULER.md`
- `docs/SPEC_DETERMINISM.md`
