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
# Elements and Aggregates

- All constructed things (buildings, rooms, hulls, vehicles, stations, portable modules) are expressed as Elements grouped into Aggregates.
- Types live in `include/domino/daggregate.h`; registry stubs live in `source/domino/daggregate.c`.

## Element
- `Element { ElementId id, MaterialId material_id, ChunkPos chunk, LocalPos local, rot, agg, flags }`.
- Flags: `ELEM_FLAG_SOLID`, `ELEM_FLAG_HULL`, `ELEM_FLAG_VENT`, `ELEM_FLAG_DOOR`, `ELEM_FLAG_MACHINE`, `ELEM_FLAG_WINDOW` (unused bits are reserved).
- Elements are addressed in a deterministic lattice coordinate system (chunk + local).
  This does not imply global grid-locked placement for other subsystems; aggregate
  placement (when applicable) is expressed via anchors/poses per
  `docs/SPEC_POSE_AND_ANCHORS.md`.

## Aggregate
- `Aggregate { AggregateId id, mobility, env, element_count, element_ids, mass, volume, drag_coeff, lift_coeff, buoyancy_factor }`.
- Mobility: `AGG_STATIC`, `AGG_SURFACE`, `AGG_WATER`, `AGG_AIR`, `AGG_SPACE`.
- Environment: `EnvironmentKind` (`ENV_SURFACE_GRID`, `ENV_AIR_LOCAL`, `ENV_HIGH_ATMO`, `ENV_WATER_SURFACE`, `ENV_WATER_SUBMERGED`, `ENV_ORBIT`, `ENV_VACUUM_LOCAL`).
- Aggregates own the authoritative list of their elements; physics/mobility operate at the aggregate level.

## Registry stubs
- `dagg_create/dagg_destroy` allocate/free aggregates from a fixed pool (deterministic, C89).
- `dagg_attach_element`/`dagg_detach_element` mutate membership and set the `agg` field on Elements; current mass/volume are deterministic stubs derived from element count (no material-based computation in this pass).
- `dagg_recompute_mass_volume` is called on membership changes and recomputes the same deterministic stub values.
- Storage is bounded arrays; no per-tick dynamic allocation.

## Intent
- Every building/vehicle/ship/station/base is an Aggregate of Elements, tied to an environment band and mobility kind.
- Other subsystems should consume these APIs (stable IDs and canonical membership) instead of inventing parallel structures.
- Deterministic simulation code stays integer-only; no floating-point in aggregate/element logic.
