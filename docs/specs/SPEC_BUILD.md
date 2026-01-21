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
# SPEC_BUILD — BUILD (Placement / Construction Requests)

BUILD is the placement/edit request subsystem in the strict stack:

`BUILD / TRANS / STRUCT / DECOR / SIM / RES / ENV / JOB / AGENT`

BUILD is responsible for validating placement/edit requests at the boundary
between UI/tools and deterministic world state. It does not own rendering or
gameplay semantics.

## Scope
Applies to:
- placement request framing (`d_build_request`)
- quantization requirements for authoritative placement inputs
- subsystem registration/serialization scaffolding

## Authoritative placement contract
All placement/edit requests MUST be expressed as:
- `dg_anchor`: a parametric reference to authoring primitives (stable IDs)
- `dg_pose` offset: a local pose relative to the anchor

These fields MUST already be quantized before validation/commit. UI snapping is
non-authoritative and MUST NOT live in BUILD logic.

See `source/domino/build/d_build.h` and `docs/SPEC_POSE_AND_ANCHORS.md`.

## Current implementation status (refactor pass)
Implemented:
- `d_build_validate` enforces:
  - request kind is supported (`D_BUILD_KIND_STRUCTURE` / `D_BUILD_KIND_SPLINE`)
  - anchor is present and of a supported kind
  - anchor and pose are quantized to the default quanta

Not implemented:
- semantic placement validation (collision/overlap/terrain fitting/etc.)
- authoritative commit/apply behavior (`d_build_commit` returns an error in this pass)
- foundation metadata (`d_build_get_foundation_down` is a stub in this pass)

The BUILD subsystem registers ABI/schema version `3` to reflect the anchor+pose
placement contract.

## Forbidden behaviors
- Treating UI snapping/grids as authoritative placement truth.
- Storing or ingesting baked world-space mesh geometry as authoritative state.
- Floating point or tolerance-based solvers in deterministic placement paths.
- Direct platform/OS calls from BUILD deterministic logic.

## Source of truth vs derived cache
**Source of truth (authoritative):**
- quantized authoring-time placement requests expressed as `(dg_anchor, dg_pose)`

**Derived cache:**
- any preview geometry, snapped poses, and placement visualization state

## Related specs
- `docs/SPEC_POSE_AND_ANCHORS.md`
- `docs/SPEC_PACKETS.md`
- `docs/SPEC_TRANS_STRUCT_DECOR.md`
- `docs/specs/SPEC_DETERMINISM.md`
