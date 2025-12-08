# Elements and Aggregates

- All constructed things (buildings, rooms, hulls, vehicles, stations, portable modules) are expressed as Elements grouped into Aggregates.
- Types live in `include/domino/daggregate.h`; registry stubs live in `source/domino/daggregate.c`.

## Element
- `Element { ElementId id, MaterialId material_id, ChunkPos chunk, LocalPos local, rot, agg, flags }`.
- Flags: `ELEM_FLAG_SOLID`, `ELEM_FLAG_HULL`, `ELEM_FLAG_VENT`, `ELEM_FLAG_DOOR`, `ELEM_FLAG_MACHINE`, `ELEM_FLAG_WINDOW` (extend later).
- Elements sit on the world grid (chunk + local coordinates) and reference materials/archetypes in later prompts.

## Aggregate
- `Aggregate { AggregateId id, mobility, env, element_count, element_ids, mass, volume, drag_coeff, lift_coeff, buoyancy_factor }`.
- Mobility: `AGG_STATIC`, `AGG_SURFACE`, `AGG_WATER`, `AGG_AIR`, `AGG_SPACE`.
- Environment: `EnvironmentKind` (`ENV_SURFACE_GRID`, `ENV_AIR_LOCAL`, `ENV_HIGH_ATMO`, `ENV_WATER_SURFACE`, `ENV_WATER_SUBMERGED`, `ENV_ORBIT`, `ENV_VACUUM_LOCAL`).
- Aggregates own the authoritative list of their elements; physics/mobility operate at the aggregate level.

## Registry stubs
- `dagg_create/dagg_destroy` allocate/free aggregates from a fixed pool (deterministic, C89).
- `dagg_attach_element`/`dagg_detach_element` mutate membership and set the `agg` field on Elements; current mass/volume stubs derive from element count (TODO material-based).
- `dagg_recompute_mass_volume` is called on membership changes and will later pull real densities/geometry.
- Registries are simple arrays for now; TODO: migrate to proper ECS/graphs, add room/zone graphs, structural graphs, HP/damage, and network hooks (power/fluid/gas).

## Intent
- Every building/vehicle/ship/station/base is an Aggregate of Elements, tied to an environment band and mobility kind.
- Later systems (orbits, climate, HVAC, AI, markets) will consume these APIs instead of inventing parallel structures.
- Deterministic simulation code stays integer-only; no floating-point in aggregate/element logic.
