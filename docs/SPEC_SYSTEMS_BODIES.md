# SPEC_SYSTEMS_BODIES - Systems and Bodies (Deterministic Registry)

This spec defines the deterministic registry for star systems and celestial
bodies. It establishes IDs, ordering rules, and minimal validated fields for
baseline content (Sol/Earth) without physical simulation.

## 1. Scope
- Systems and bodies are authoritative, deterministic data.
- IDs are stable across machines and builds.
- All fields are fixed-point or integer (no floats).
- Ordering and validation are deterministic.

## 2. IDs and ordering
Each system/body has:
- Stable UTF-8 string ID (no null terminator).
- Numeric `u64` ID derived via canonical FNV-1a 64-bit hashing
  (see `include/domino/core/spacetime.h`).

Ordering:
- Registries iterate in ascending numeric ID order.
- Duplicate numeric IDs are invalid and must refuse.

## 3. System descriptors
Minimum system fields:
- `system_id` (u64, required)
- `parent_galaxy_id` (u64, optional; 0 if unspecified)

Validation:
- `system_id` must be non-zero.
- If a string ID is provided, its hash must match `system_id`.

## 4. Body descriptors
Body kinds:
- `STAR`
- `PLANET`
- `MOON`
- `STATION` (placeholder; may be empty in v1)

Minimum body fields:
- `body_id` (u64, required)
- `system_id` (u64, required)
- `kind` (enum)
- `radius_m` (Q48.16 meters, required, > 0)
- `mu_m3_s2` (u64, required, > 0) — integer in m^3/s^2
- `rotation_period_ticks` (u64, optional; 0 means no rotation)
- `rotation_epoch_tick` (u64, optional; default 0)
- `axial_tilt_turns` (Q16.16 turns, optional; range [0, 0.5])

Notes:
- `rotation_period_ticks` defines the fixed rotation rate as an integer period.
  The derived rotation rate is `1 / rotation_period_ticks` turns per tick.
- All rotation math is performed deterministically; no floats are permitted.

Validation:
- `body_id`, `system_id` must be non-zero.
- `radius_m > 0`, `mu_m3_s2 > 0`.
- If a string ID is provided, its hash must match `body_id`.
- `axial_tilt_turns` must be in the range [0, 0.5] turns if present.

## 5. Baseline content
Baseline content MUST include:
- Galaxy: Milky Way (defined in cosmos lane; referenced by ID only)
- System: Sol
- Body: Earth (kind `PLANET`)

## Related specs
- `docs/SPEC_REFERENCE_FRAMES.md`
- `docs/SPEC_SURFACE_TOPOLOGY.md`
- `docs/SPEC_UNIVERSE_MODEL.md`
- `docs/SPEC_SPACETIME.md`
- `docs/SPEC_DETERMINISM.md`
