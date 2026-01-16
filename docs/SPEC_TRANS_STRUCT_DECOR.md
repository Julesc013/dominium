--------------------------------
OWNERSHIP & RESPONSIBILITY
--------------------------------
ENGINE:
- None. Engine provides generic primitives only if referenced.

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
# SPEC_TRANS_STRUCT_DECOR — TRANS / STRUCT / DECOR Responsibilities

This spec defines the responsibilities and boundaries of TRANS, STRUCT, and
DECOR in the strict layer stack:

`BUILD / TRANS / STRUCT / DECOR / SIM / RES / ENV / JOB / AGENT`

## Scope
Applies to:
- separation of concerns between TRANS/STRUCT/DECOR
- authoring vs compiled artifacts
- deterministic compilation constraints
- explicit prohibitions (no solvers, no baked geometry truth)

## TRANS (Transform/Topology)
**Responsibilities**
- Own transform/topology representations used to connect structures and anchors.
- Provide deterministic, canonical representations suitable for SIM consumption.
- Provide deterministic compilation from authored inputs (see `compile/`).
- Represent corridor overlap/co-location only via cross-section slots and
  attachments (no stacked independent splines).

**Non-responsibilities**
- No rendering integration.
- No platform APIs.
- No tolerance/epsilon solvers.

## STRUCT (Structures)
**Responsibilities**
- Own structure/infrastructure authoring models (canonical source of truth) and
  compiled STRUCT artifacts (derived caches).
- Authoring supports arbitrary orientation and placement (no grids):
  - `dg_struct_instance`: `(dg_anchor, local dg_pose)` placement + stable `struct_id`
  - `dg_struct_footprint`: parametric polygons in local frame (holes allowed)
  - `dg_struct_volume`: parametric solid/void templates (limited boolean ops)
  - `dg_struct_enclosure`: interior definitions + apertures (room graph)
  - `dg_struct_surface` + `dg_struct_socket`: surface selections + attachment points
  - `dg_struct_carrier_intent`: bridge/tunnel/viaduct/cut/fill intents (parametric)
- Compile derived caches deterministically under a bounded budget:
  - occupancy/void regions + chunk-aligned spatial indices
  - enclosure (room) graphs + aperture edges
  - surface graphs (facades + interior surfaces) + sockets
  - support/load topology graphs (no physics solving yet)
  - carrier artifacts usable by TRANS/ENV later (no direct calls in this layer)

**Non-responsibilities**
- No baked world-space geometry as authoritative truth.
- No solver-based fitting.
- No rendering, UI, or gameplay semantics.

## DECOR (Decoration)
**Responsibilities**
- Own decoration rulepacks and deterministic compilation to runtime artifacts.
- Provide derived decoration outputs only; decor is non-authoritative.
- Provide a unified, host-agnostic authoring model for surface detail:
  signage, markings, decals, and small surface props (placement only).
- Consume only compiled host catalogs/indices (no direct access to TRANS/STRUCT authoring).
- Default to render-only derived outputs and only promote to simulation entities via explicit hooks.

**Non-responsibilities**
- Decor MUST NOT become gameplay truth.
- No platform rendering dependencies.

### DECOR authoring vs compiled artifacts
**Authoring (source of truth)**
- Rulepacks: deterministic baseline generation rules keyed by stable `rulepack_id`.
- Overrides: authoritative edit records (PIN/SUPPRESS/REPLACE/MOVE/TAG) keyed by stable `override_id`.
- Anchors + local pose offsets: authoritative placement references to host parameter spaces.

**Derived caches**
- Chunk-aligned instance lists with cached evaluated poses (renderer-agnostic).
- Chunk-aligned tile batches suitable for later dgfx consumption.

### Host-agnostic binding (no baked geometry)
DECOR binds to hosts via stable authoring IDs, not compiled triangles/meshes:
- terrain patches (chunk-aligned)
- TRANS corridor slot surfaces / rails
- STRUCT exterior surfaces
- STRUCT room/interior surfaces
- sockets/attachment points

Anchors evaluate through the world frame graph; DECOR never stores baked world-space geometry as authoritative state.

## Authoring vs compiled artifacts
- Authoring models (parametric, fixed-point, quantized at commit) are the
  canonical source of truth for BUILD/TRANS/STRUCT/DECOR.
- Compiled artifacts are deterministic derived caches used for performance and
  SIM queries; they MUST be rebuildable under budget and MUST NOT be
  authoritative truth.
- Compilation MUST be deterministic and canonically ordered (`docs/SPEC_DETERMINISM.md`).

## Explicit prohibitions
TRANS/STRUCT/DECOR MUST forbid:
- tolerance/epsilon solvers
- world-space baked geometry as authoritative state
- treating a global grid as authoritative placement truth or a required
  representation for all objects (UI snapping/grids are non-authoritative;
  explicit lattices are permitted only when the owning subsystem specifies them)
- unordered iteration in determinism paths
- platform-dependent behavior

## Source of truth vs derived cache
**Source of truth:**
- TRANS authoring: alignments, cross-sections (slots), attachments, junctions
- anchors/poses referenced by stable IDs

**Derived cache:**
- TRANS compiled: microsegments, frames, slotmaps, chunk-aligned spatial indices
- render geometry
- visualization geometry
- any occupancy grids or spatial accelerators (regenerable)

**STRUCT authoring (source of truth):**
- structure instances with stable IDs and anchor+pose placement
- footprints, volumes, enclosures, surface templates, sockets, carrier intents
- per-instance param overrides (TLV)

**STRUCT derived caches:**
- occupancy/void regions + chunk-aligned indices
- enclosure graphs (rooms + apertures) + room indices
- surface graphs + sockets + surface indices
- support/load graphs + support indices
- carrier artifacts + carrier indices

## Integration points (no semantics)
### TRANS integration
- STRUCT carriers compile into parametric artifacts that TRANS may consume later.
- STRUCT MUST NOT call TRANS directly during compilation; only emit artifacts.

### DECOR integration
- DECOR consumes only compiled surface graphs and sockets.
- DECOR MUST NOT read STRUCT authoring directly.

## Related specs
- `docs/SPEC_DETERMINISM.md`
- `docs/SPEC_PACKETS.md`
- `docs/SPEC_GRAPH_TOOLKIT.md`
- `docs/SPEC_POSE_AND_ANCHORS.md`
- `docs/SPEC_DOMAINS_FRAMES_PROP.md`
