Status: DERIVED
Last Reviewed: 2026-03-09
Supersedes: none
Superseded By: none

# MW3 Retro Audit

## Scope

This audit records the repository state before MW-3 planet-surface macro refinement work.

Audit targets:

- GEO surface partition profiles and tile-key behavior
- current GEO-bound field coverage for surface use
- existing worldgen/runtime hooks for lazy tile generation

## Existing Surface Partition Profiles

The GEO profile registry already exposes the two partition families MW-3 needs.

Relevant surfaces:

- `data/registries/partition_profile_registry.json`
  - `geo.partition.atlas_tiles`
  - `geo.partition.grid_zd`
- `data/registries/space_topology_profile_registry.json`
  - `geo.topology.sphere_surface_s2`
  - `geo.topology.r2_infinite`
  - `geo.topology.torus_r2`
- `src/geo/index/geo_index_engine.py`
  - canonical atlas/grid cell-key coercion
  - deterministic `index_tuple` and `chart_id` normalization

Current conclusion:

- sphere planets can use `geo.topology.sphere_surface_s2` with `geo.partition.atlas_tiles`
- flat or torus surfaces can stay on `grid_zd`
- `geo_cell_key.extensions` can carry ancestry metadata without changing semantic tile coordinates

## Existing GEO-Bound Field Coverage

The FIELD-to-GEO baseline already supports tile-addressed field storage on sphere surfaces.

Relevant surfaces:

- `data/registries/field_binding_registry.json`
  - tile bindings already exist for `field.temperature`, `field.moisture`, `field.visibility`, and `field.wind`
  - atlas-tile storage is declared for `geo.topology.sphere_surface_s2` + `geo.partition.atlas_tiles`
- `src/fields/field_engine.py`
  - `build_field_layer(...)`
  - `build_field_cell(...)`
  - `field_set_value(...)`

Current gaps:

- no canonical `field.daylight` field type or binding
- no canonical `field.pressure_stub` field type or binding
- worldgen currently initializes only `field.temperature`

Audit conclusion:

- MW-3 can initialize surface tile fields through the existing FIELD runtime
- daylight and pressure stub fields need registry rows before use

## Existing Lazy Worldgen Hooks

The worldgen/runtime boundary is already cell-scoped and process-routed.

Relevant surfaces:

- `src/geo/worldgen/worldgen_engine.py`
  - request/result normalization
  - named RNG stream policy
  - current refinement ladder through MW-2
  - existing `refinement_level >= 3` path is only a generic placeholder tile/object initializer
- `tools/xstack/sessionx/process_runtime.py`
  - `process.worldgen_request` is the authoritative mutation boundary
  - field and geometry initialization rows are persisted idempotently
- `tools/xstack/testx/tests/geo8_testlib.py`
  - deterministic worldgen fixtures already seed process/runtime state for MW tests

Current gaps:

- no dedicated MW L3 surface refiner
- no persisted `worldgen_surface_tile_artifacts` state surface
- no routing registry for default vs Earth-delegated generators

Audit conclusion:

- MW-3 can remain on-demand by refining exactly one requested tile cell at a time
- the correct insertion point is `generate_worldgen_result(...)` plus the existing `process.worldgen_request` persistence path

## Reuse and Compatibility Notes

- `kind.surface_tile` is already declared in `data/registries/object_kind_registry.json`
- `schema/geo/realism_profile.schema` already requires `surface_priors_ref`
- current MW-2 planet artifacts already expose `radius`, `atmosphere_class_id`, `ocean_fraction`, and `axial_tilt`, which are sufficient inputs for macro-surface stubs

## Audit Outcome

MW-3 can be added without reopening the GEO identity contract, field binding model, or process-only mutation boundary.

The missing work is:

- declare surface priors and generator routing registries
- add a deterministic L3 surface refiner and insolation helper
- persist surface tile artifacts through the existing worldgen process path
