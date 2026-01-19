--------------------------------
OWNERSHIP & RESPONSIBILITY
--------------------------------
ENGINE:
- IDs, coordinate frames, ACT time, deterministic scheduling primitives.
GAME:
- Interprets rail positions for travel, visibility, and logistics effects.
SCHEMA:
- Orbital rail formats, versioning, and validation rules.
TOOLS:
- Future editors/importers/inspectors only (no runtime behavior).
FORBIDDEN:
- No runtime logic or mechanics in schema specs.
- No physics simulation; rails are deterministic tables/functions only.
- No floating-point time dependence.
DEPENDENCIES:
- Engine -> (no dependencies outside engine/).
- Game -> engine public API only.
- Schema -> none (formats only).
- Tools -> schema + engine/game public APIs only.
--------------------------------
# SPEC_ORBITAL_RAILS - Orbital Rails (CONTENT0)

Status: draft
Version: 1

## Purpose
Define deterministic orbital relationships as rails with ACT-based position
functions, not physics simulation.

## OrbitalRailRecord schema
Required fields:
- rail_id
- system_ref
- parent_body_ref
- child_body_ref
- rail_model_id (static/periodic/keyframe)
- rail_frame_ref
- period_act
- phase_offset_act
- inclination_mdeg
- ascending_node_mdeg
- drift_schedule_ref (nullable)
- provenance_ref

Optional fields:
- eccentricity_ppm
- argument_of_periapsis_mdeg
- keyframe_ref

Rules:
- rail_model_id defines the deterministic position function.
- period_act and phase_offset_act are ACT ticks (integers).
- rail_frame_ref defines the coordinate frame for position outputs.
- For keyframe models, keyframes must be ordered by act and bounded in count.
- drift_schedule_ref points to deterministic parameter updates keyed by ACT.

## OrbitalRailKeyframe schema
Required fields:
- keyframe_id
- rail_id
- act
- position_ref

Rules:
- position_ref uses integer coordinates in rail_frame_ref.
- Keyframes must not imply interpolation beyond declared rules.

## OrbitalRailDriftEvent schema
Required fields:
- drift_id
- rail_id
- act
- parameter_delta_map

Rules:
- Drift events are discrete, deterministic parameter changes.
- No continuous physics integration is permitted.

## Determinism and performance rules
- Rail outputs are pure functions of ACT and fixed parameters.
- No per-tick updates are implied; evaluation occurs on demand.
- Time warp compatibility is required; ACT is the sole time axis.

## Epistemic rules
- Rail data existence does not imply player knowledge of positions.
- Visibility must flow through sensors and reports.

## Validation rules
- rail_id is stable, unique, and immutable.
- parent_body_ref and child_body_ref must be valid and within the same system.
- Lists are schema-bounded with explicit max sizes.

## Integration points
- Star systems: `schema/world/SPEC_SYSTEM_MODEL.md`
- Celestial bodies: `schema/world/SPEC_CELESTIAL_BODY.md`
- Time warp: `schema/scale/SPEC_SCALE_TIME_WARP.md`
- Reference frames: `docs/SPEC_REFERENCE_FRAMES.md`

## Prohibitions
- No physics simulation or continuous integration.
- No floating-point time dependence.
- No per-tick global orbit updates.

## Test plan (spec-level)
Required scenarios:
- Structural validation: unique IDs, bounded lists, and valid references.
- Migration: MAJOR version bump requires explicit migration or refusal.
- Determinism: identical ACT inputs produce identical rail positions.
- Performance: on-demand evaluation only; no global rail scans.
