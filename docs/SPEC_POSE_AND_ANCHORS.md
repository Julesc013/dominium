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
# SPEC_POSE_AND_ANCHORS — Fixed-Point Pose + Anchors

This spec defines fixed-point pose representation and anchor-based positioning.
It explicitly forbids baked world-space geometry as authoritative truth.

## Scope
Applies to:
- pose representation used in deterministic simulation and packets
- quantization rules
- anchor-based positioning and frame references

## Canonical pose model (authoritative representation)
The canonical engine pose is `dg_pose` (see `source/domino/core/dg_pose.h`).

```
dg_pose {
    dg_vec3_q pos;     // fixed-point world or frame-local position
    dg_rot_q  rot;     // fixed-point orientation (quaternion; Q48.16)
    dg_q      incline; // slope relative to host (turns; Q48.16)
    dg_q      roll;    // roll about forward axis (turns; Q48.16)
}
```

### Q formats
All pose scalars are fixed-point, with explicit Q formats declared in code:
- `dg_q` is Q48.16 (signed).
- **Positions** are in meters in Q48.16.
- **Angles** are in turns in Q48.16 (`1.0 == 360°`).

### Deterministic pose operations
Pose operations MUST:
- use fixed-point only (no float/double)
- specify an explicit rounding mode on downscales
- be deterministic across platforms (see `source/domino/core/det_invariants.h`)

Implemented helpers:
- compose: `dg_pose_compose`
- invert: `dg_pose_invert`
- transform: `dg_pose_transform_point`, `dg_pose_transform_dir`

## Quantization guarantees
- All pose components MUST be explicitly quantized using deterministic rounding
  rules (`source/domino/core/det_invariants.h`).
- Unquantized placement/edit commands are invalid.
- Quantization rules MUST be stable across platforms and versions.
- Float-derived values from tools MUST be quantized before entering SIM.

Quantization API:
- `source/domino/core/dg_quant.h`
- `dg_quant_pos`, `dg_quant_angle`, `dg_quant_param`

Default quanta are defined in code (Q48.16):
- position: `DG_QUANT_POS_DEFAULT_Q` (1/1024 m)
- angle: `DG_QUANT_ANGLE_DEFAULT_Q` (1/4096 turn)
- param: `DG_QUANT_PARAM_DEFAULT_Q` (1/1024 unit in param spaces)

## Anchor-based positioning (authoritative)
Anchors are stable reference points used to attach objects and structures.

Rules:
- Anchors and their relationships are authoritative state.
- World-space baked geometry MUST NOT be authoritative state.
- Any world-space geometry is a derived cache generated from anchors + compiled
  artifacts.

### Anchor kinds
Anchors are represented by `dg_anchor` (see `source/domino/world/frame/dg_anchor.h`):
- Terrain: `(u, v, h)` in terrain patch space
- Corridor (TRANS): `(alignment_id, s, t, h, roll)`
- Structure surface: `(structure_id, surface_id, u, v, offset)`
- Room surface: `(room_id, surface_id, u, v, offset)`
- Socket: `(socket_id, param)`

All parameters are fixed-point and MUST be quantized before becoming
authoritative.

### Anchor invariants
- Anchors reference authoring primitives, not baked geometry.
- Anchors survive rebuilds of compiled artifacts.
- Anchor evaluation produces a pose only when queried, not stored.

### Frame graph integration
Anchor evaluation MUST resolve through the deterministic frame graph
(`source/domino/world/frame/d_world_frame.h`) in canonical order:
`anchor local -> host frame -> parent frames -> world frame`.
Traversal MUST be bounded and non-recursive.

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
- `docs/SPEC_PACKETS.md`
- `docs/SPEC_DOMAINS_FRAMES_PROP.md`
- `docs/SPEC_TRANS_STRUCT_DECOR.md`
- `docs/SPEC_GRAPH_TOOLKIT.md`
