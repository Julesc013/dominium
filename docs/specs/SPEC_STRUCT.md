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
# SPEC_STRUCT — STRUCT (Structures / Infrastructure)

STRUCT is the structures subsystem in the strict stack:

`BUILD / TRANS / STRUCT / DECOR / SIM / RES / ENV / JOB / AGENT`

STRUCT owns structure authoring models (source of truth) and deterministic
compilation into runtime-friendly derived caches. STRUCT does not own gameplay
semantics; it provides generic structural representations for other subsystems.

## Scope
Applies to:
- structure authoring instances and parametric templates
- deterministic compilation (occupancy/enclosure/surface/support graphs)
- boundaries between authoring truth and compiled artifacts

## Owns (authoritative)
Authoring models are canonical sources of truth (see `source/domino/struct/model/**`):
- `dg_struct_instance`: authoritative placement via `(dg_anchor, dg_pose)`
- parametric templates referenced by instances:
  `dg_struct_footprint`, `dg_struct_volume`, `dg_struct_enclosure`,
  `dg_struct_surface_template`, `dg_struct_socket`, `dg_struct_carrier_intent`
- per-instance param overrides stored as canonical TLV blobs (opaque to STRUCT model code)

Authoritative rules:
- All placement is via anchor + local pose; arbitrary orientation is allowed.
- All fixed-point values MUST be quantized before commit (see `docs/SPEC_POSE_AND_ANCHORS.md`).
- No baked world-space mesh geometry is stored as truth.

## Produces (derived cache)
STRUCT compiles deterministic derived caches under budget (see `source/domino/struct/compile/**`):
- occupancy/void regions and chunk-aligned indices
- enclosure (room) graphs and aperture edges
- surface graphs and socket indices
- support/load topology graphs (scaffold; no solver-based physics fitting)
- carrier artifacts usable by TRANS/ENV consumers (parametric outputs only)

All compiled artifacts:
- MUST be rebuildable from authoritative inputs
- MUST be canonically ordered and stable across platforms
- MUST NOT be treated as gameplay truth

## Consumes
- BUILD placement/edit requests expressed as `(dg_anchor, dg_pose)` plus TLV parameters.
- TRANS compiled surface/slot catalogs for corridor/attachment binding.
- Content prototypes (structure archetypes) as opaque, versioned inputs; STRUCT
  must not embed product-specific rules in the core authoring model.

## Legacy runtime helpers
`source/domino/struct/d_struct_instance.h` and `source/domino/struct/d_struct.h`
expose legacy runtime helpers such as `d_struct_create` that operate in
world-space Q16.16 coordinates. These APIs are compatibility helpers and are not
the authoritative placement model for the BUILD/TRANS/STRUCT/DECOR refactor.

## Forbidden behaviors
- Storing or ingesting baked world-space meshes/triangles as authoritative state.
- Grid-locked placement requirements for structure authoring (UI snapping is non-authoritative).
- Solver-based fitting with tolerances/epsilons in deterministic compilation.
- Direct cross-subsystem mutation (e.g. STRUCT writing into ENV/TRANS internal state);
  cross-subsystem effects must be expressed explicitly (packets/deltas/artifacts).

## Source of truth vs derived cache
**Source of truth (authoritative):**
- structure instances with stable IDs and anchor+pose placement
- parametric templates (footprints/volumes/enclosures/surfaces/sockets/carrier intents)
- per-instance TLV param overrides

**Derived cache (must be regenerable):**
- occupancy/enclosure/surface/support graphs and indices
- any render/visualization geometry

## Related specs
- `docs/SPEC_TRANS_STRUCT_DECOR.md`
- `docs/SPEC_POSE_AND_ANCHORS.md`
- `docs/SPEC_GRAPH_TOOLKIT.md`
- `docs/SPEC_SIM_SCHEDULER.md`
- `docs/SPEC_DETERMINISM.md`
