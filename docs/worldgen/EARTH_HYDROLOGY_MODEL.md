Status: CANONICAL
Last Reviewed: 2026-03-10
Supersedes: none
Superseded By: none

# Earth Hydrology Model

This document freezes the EARTH-1 macro hydrology stub for Dominium v0.0.0.

It is subordinate to:

- `docs/canon/constitution_v1.md`
- `docs/canon/glossary_v1.md`
- `docs/specs/SPEC_MVP0_SCOPE_CONSTITUTION.md`
- `docs/worldgen/PLANET_SURFACE_MACRO_MODEL.md`
- `docs/worldgen/EARTH_PROCEDURAL_CONSTITUTION.md`

## Relevant Invariants

- `docs/canon/constitution_v1.md` `A1` Determinism is primary
- `docs/canon/constitution_v1.md` `A2` Process-only mutation
- `docs/canon/constitution_v1.md` `A6` Provenance is mandatory
- `docs/canon/constitution_v1.md` `A9` Pack-driven integration
- `docs/canon/constitution_v1.md` `E2` Deterministic ordering
- `docs/canon/constitution_v1.md` `E4` Named RNG streams
- `docs/canon/constitution_v1.md` `E6` Replay equivalence
- `docs/worldgen/PLANET_SURFACE_MACRO_MODEL.md`
- `docs/worldgen/EARTH_PROCEDURAL_CONSTITUTION.md`

## 1. Scope

EARTH-1 adds a macro hydrology layer for surface tiles.

It provides:

- deterministic downhill flow targets
- deterministic drainage accumulation proxies
- deterministic river marking
- deterministic sink and lake stubs
- bounded local recompute after geometry edits
- hook surfaces for later POLL and FLUID systems

It does not provide:

- PDE fluid solve
- erosion
- sediment transport
- water-volume conservation
- real river datasets
- real-time water simulation

## 2. Elevation Proxy

Hydrology treats tile elevation as a scalar height.

Required source order:

1. effective geometry override height when a lawful geometry edit has changed the tile
2. otherwise `surface_tile_artifact.elevation_params_ref.height_proxy`
3. otherwise the generator-provided tile `height_proxy`

Hydrology must not consult DEM data or authored river masks.

## 3. Flow Direction Rule

For a tile `T`:

1. enumerate `geo_cell_key_neighbors(T, radius = 1)`
2. normalize neighbors into canonical `geo_cell_key` order
3. compare effective elevation scalar for each neighbor
4. choose the strictly lowest neighbor as `flow_target_tile_key`
5. if multiple neighbors share the same lowest elevation, choose the lower canonical `geo_cell_key`
6. if no neighbor is lower, `T` is a sink

Hydrology may inspect the center tile plus its immediate neighbors only for flow-direction selection.

## 4. Drainage Accumulation Proxy

EARTH-1 computes drainage as a bounded proxy, not as a whole-planet exact solve.

Hydrology window:

- center tile plus `geo_cell_key_neighbors(center, radius = analysis_radius)`
- `analysis_radius` is a declared hydrology parameter
- the window must remain bounded and deterministic

Accumulation rule inside the window:

- initialize `A(tile) = 1` for every tile in the window
- sort the window by:
  - descending effective elevation
  - then canonical `geo_cell_key`
- iterate once in that order
- if tile `T` has `flow_target_tile_key = U` and `U` is inside the same window:
  - `A(U) = A(U) + A(T)`
- if `U` is outside the window:
  - flow is treated as leaving the local accumulation window

Implications:

- `drainage_accumulation_proxy` is exact for the bounded hydrology window
- it is intentionally a proxy for global basin size
- the proxy remains deterministic and scalable

## 5. River Threshold

A tile is river-marked when:

- `drainage_accumulation_proxy >= accumulation_threshold`
- and the tile is not classified as ocean

Required artifact effects:

- `river_flag = true`
- add overlay tag `river` to biome/hydrology extensions

River marking is structural only.
It does not authorize water volume simulation.

## 6. Sink and Lake Rule

If a tile has no lower neighbor, it is a sink.

A sink may be marked as a lake stub when:

- the tile is not ocean
- the tile is not polar ice
- the delta between the sink elevation and the lowest spill neighbor elevation is less than or equal to `lake_elevation_delta_threshold`

Lake state is advisory:

- it affects hydrology extensions and future guidance hooks
- it does not create a water-volume simulation

## 7. Determinism

Hydrology inputs are limited to:

- `universe_seed`
- `generator_version_id`
- surface tile `geo_cell_key`
- declared hydrology parameter record
- effective height overrides derived from lawful geometry edits
- deterministic generator tile plans

Required rules:

- GEO neighbor iteration order must remain canonical
- no random tie-breaking is allowed
- no recursion is allowed in accumulation evaluation
- no wall-clock input is allowed

## 8. Geometry Edit Integration

Geometry edits may change effective hydrology by changing tile height.

Required update rule:

- a geometry edit affecting elevation marks the target tile and a bounded neighbor window dirty
- only that bounded local window may be recomputed automatically
- recompute radius is data-declared and deterministic
- small edits must not require whole-planet recompute

Hydrology recompute must execute through the existing lawful process path that handled the geometry edit.

## 9. POLL and FLUID Hooks

EARTH-1 exposes structural guidance only.

Required hooks:

- POLL transport stubs may follow `flow_target_tile_key` chains
- FLUID surface-channel stubs may use the local flow graph as channel guidance

EARTH-1 does not transport mass.

## 10. Output Contract

EARTH-1 extends `surface_tile_artifact` with:

- `flow_target_tile_key` when a downhill target exists
- `drainage_accumulation_proxy`
- `river_flag`

Additional advisory values may appear in `extensions`, including:

- `lake_flag`
- `hydrology_params_id`
- `hydrology_window_fingerprint`
- `hydrology_effective_height_proxy`

Worldgen and replay surfaces must expose the same hydrology values for identical inputs.

## 11. Upgrade Path

Future Earth and FLUID layers may add:

- seasonal discharge variation
- water storage
- pollutant transport
- erosion and deposition
- high-fidelity river overlays

Those later systems must:

- preserve tile identity
- preserve deterministic local flow ordering unless versioned explicitly
- treat EARTH-1 flow structure as a low-data baseline, not as real-world geography
