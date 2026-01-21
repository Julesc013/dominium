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
# SPEC_REFERENCE_FRAMES - Deterministic Frame Registry

This spec defines the reference-frame registry used by the game runtime. It
supports baseline Sol/Earth frames with deterministic transforms and is designed
for deterministic evolution.

## 1. Frame IDs and tree structure
- `frame_id` is a stable `u64` derived from a UTF-8 string ID (FNV-1a 64-bit).
- Each frame declares a `parent_id`; the root uses `parent_id = 0`.
- Frames form a strict tree: no cycles, no multiple parents.
- Tree validation is deterministic: iterate frames in ascending `frame_id`.

## 2. Frame kinds and baseline frames
Frame kinds:
- `INERTIAL_BARYCENTRIC`
- `BODY_CENTERED_INERTIAL`
- `BODY_FIXED`

Baseline frames:
- `SOL_BARYCENTRIC_INERTIAL`
- `EARTH_CENTERED_INERTIAL`
- `EARTH_FIXED_ROTATING`

## 3. Transform semantics
- Transforms are defined at tick boundaries and are tick-indexed inputs.
- All transforms must be fixed-point and deterministic.
- No wall-clock or UI state may influence transforms.
- Angles use Q16.16 turns (`1.0 == full turn`), normalized to `[0,1)` turns.

Baseline transforms:
- `src == dst` -> identity copy.
- `INERTIAL_BARYCENTRIC <-> BODY_CENTERED_INERTIAL`:
  - Translation by body position in segmented Q16.16 meters.
  - Until orbit propagation exists, body position may be `(0,0,0)`.
- `BODY_CENTERED_INERTIAL <-> BODY_FIXED`:
  - Rotation about body spin axis using deterministic math wrappers.
  - Rotation angle computed from `rotation_period_ticks` and `tick_index`.

### 3.1 Canonicalization
- Angles are normalized with `dom_angle_normalize_q16`.
- Position and velocity outputs are canonicalized via fixed-point rules only.

### 3.2 Transition rules (hysteresis)
- Frame transitions (e.g., surface -> orbit) may only occur on tick boundaries.
- Switching decisions must use deterministic thresholds and hysteresis to
  prevent oscillation; no mid-tick switching.

## 4. Minimal API contract (v1 baseline)
- `frames_transform_pos(src, dst, pos, tick, out_pos)`:
  - Must support baseline transforms listed above.
  - Any unsupported transform returns `NOT_IMPLEMENTED`.
- `frames_transform_vel(src, dst, vel, tick, out_vel)`:
  - Must support identity and baseline body-fixed/inertial rotations.
  - Any unsupported transform returns `NOT_IMPLEMENTED`.

## Related specs
- `docs/SPEC_SPACETIME.md`
- `docs/SPEC_ORBITS_TIMEWARP.md`
- `docs/SPEC_UNIVERSE_MODEL.md`
- `docs/specs/SPEC_DETERMINISM.md`
