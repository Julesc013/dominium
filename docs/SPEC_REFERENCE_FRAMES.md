# SPEC_REFERENCE_FRAMES - Deterministic Frame Registry

This spec defines the reference-frame registry used by the game runtime. It is
scaffolding-only in v1 and is designed for deterministic evolution.

## 1. Frame IDs and tree structure
- `frame_id` is a stable `u64` derived from a UTF-8 string ID (FNV-1a 64-bit).
- Each frame declares a `parent_id`; the root uses `parent_id = 0`.
- Frames form a strict tree: no cycles, no multiple parents.
- Tree validation is deterministic: iterate frames in ascending `frame_id`.

## 2. Transform semantics
- Transforms are defined at tick boundaries and are tick-indexed inputs.
- All transforms must be fixed-point and deterministic.
- No wall-clock or UI state may influence transforms.

### 2.1 Transition rules (hysteresis)
- Frame transitions (e.g., surface -> orbit) may only occur on tick boundaries.
- Switching decisions must use deterministic thresholds and hysteresis to
  prevent oscillation; no mid-tick switching.

## 3. Minimal API contract (v1 scaffolding)
- `frames_transform_pos(src, dst, pos, tick, out_pos)`:
  - Must return success only when `src == dst` (identity).
  - Any other transform returns `NOT_IMPLEMENTED` in v1.
- Callers must treat non-identity transforms as unsupported in v1.

## Related specs
- `docs/SPEC_SPACETIME.md`
- `docs/SPEC_ORBITS_TIMEWARP.md`
- `docs/SPEC_UNIVERSE_MODEL.md`
- `docs/SPEC_DETERMINISM.md`
