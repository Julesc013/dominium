Status: DERIVED
Last Reviewed: 2026-03-10
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# EARTH1 Retro Audit

This audit records the repository state immediately before EARTH-1 hydrology implementation.

Authority:

- `docs/canon/constitution_v1.md`
- `docs/canon/glossary_v1.md`
- `docs/specs/SPEC_MVP0_SCOPE_CONSTITUTION.md`
- `docs/worldgen/PLANET_SURFACE_MACRO_MODEL.md`
- `docs/worldgen/EARTH_PROCEDURAL_CONSTITUTION.md`

## 1. Surface Tile Artifact Baseline

Current surface tile artifacts are normalized through:

- `src/worldgen/mw/mw_surface_refiner_l3.py`
- `schema/worldgen/surface_tile_artifact.schema`

Observed artifact fields before EARTH-1:

- `tile_object_id`
- `planet_object_id`
- `tile_cell_key`
- `elevation_params_ref`
- `material_baseline_id`
- `biome_stub_id`
- `deterministic_fingerprint`
- `extensions`

Conclusion:

- every generated surface tile already carries a deterministic scalar elevation proxy through `elevation_params_ref.height_proxy`
- EARTH-1 can extend the artifact contract instead of introducing a separate hydrology artifact type for MVP

## 2. Elevation Proxy Availability

Earth tiles already produce macro elevation through:

- `src/worldgen/earth/earth_surface_generator.py`
  - `height_proxy`
  - `elevation_params_ref.height_proxy`
  - `elevation_params_ref.macro_relief_permille`
  - `elevation_params_ref.ridge_bias_permille`
  - `elevation_params_ref.coastal_bias_permille`

Generic MW-3 tiles already produce:

- default `height_proxy`
- default `elevation_params_ref`

Conclusion:

- a deterministic scalar height input is already available for every generated surface tile
- EARTH-1 does not require DEM or a new terrain source

## 3. GEO Neighbor Ordering

Deterministic neighbor enumeration already exists through:

- `src/geo/metric/neighborhood_engine.py`
- `src/geo/index/geo_index_engine.py`
- exported `src.geo.geo_cell_key_neighbors(...)`

Observed ordering rules:

- grid neighbors are sorted by distance, then chart, then index tuple
- atlas neighbors are sorted by breadth-first depth, then chart, then index tuple
- returned `geo_cell_key` rows are canonicalized before exposure

Conclusion:

- EARTH-1 can use GEO neighbor APIs directly
- tie-breaking by canonical `geo_cell_key` ordering is already compatible with the determinism contract

## 4. Surface Topology Compatibility

Current MW-3 surface routing already supports multiple surface topologies through data:

- `data/registries/surface_priors_registry.json`
  - `geo.topology.sphere_surface_s2`
  - `geo.topology.r2_infinite`
  - `geo.topology.torus_r2`

Observed runtime behavior:

- `mw_surface_refiner_l3.py` validates the tile topology/partition against the selected surface priors
- `geo_cell_key_neighbors(...)` derives neighbors from the tile key topology rather than Earth-only assumptions

Conclusion:

- the hydrology engine can remain topology-generic if it consumes GEO neighbor APIs and tile elevation proxies only

## 5. Geometry Edit Coupling Hooks

Current geometry edit support already provides:

- `src.geo.edit.build_geometry_edit_event(...)`
- `src.geo.edit.geometry_edit_event_hash_chain(...)`
- `tools/xstack/sessionx/process_runtime.py`
  - persistence of `geometry_edit_events`
  - deterministic geometry mutation processes
  - coupling update hooks after geometry edits

Observed relevant behavior:

- geometry edits update `geometry_cell_states`
- macro `height_proxy` can change as occupancy changes
- post-edit coupling hooks already run in process runtime

Conclusion:

- EARTH-1 can attach bounded hydrology recompute to the existing post-geometry-edit process path
- no new mutation bypass is required

## 6. Earth Routing Baseline

Earth routing remains data-driven through:

- `data/registries/surface_generator_registry.json`
  - `gen.surface.earth_stub`
  - `handler_id = earth.surface.stub`
- `data/registries/surface_generator_routing_registry.json`
  - `route.earth`
  - `selector_kind = by_tag`
  - `match_rule.planet_tags = ["planet.earth"]`

Conclusion:

- EARTH-1 hydrology must attach to routed Earth tile generation
- no hardcoded Earth object ID or display-name branch is required

## 7. Reuse Candidates

Direct reuse surfaces:

- `src/worldgen/mw/mw_surface_refiner_l3.py`
  - tile routing
  - lineage resolution
  - temperature/daylight proxy setup
  - surface artifact persistence
- `src/worldgen/earth/earth_surface_generator.py`
  - deterministic macro elevation proxy generation
- `tools/worldgen/earth0_probe.py`
  - Earth tile fixture context
- `tools/xstack/testx/tests/earth0_testlib.py`
  - reusable Earth fixture helpers

Missing pieces:

- hydrology parameter declaration
- deterministic downhill-flow engine
- bounded drainage accumulation proxy
- local recompute hook after geometry edits
- replay/proof surface for hydrology windows

## 8. Risks Before Implementation

- If hydrology scans an unbounded planet surface, MW-3 on-demand guarantees are broken.
- If flow ties use insertion-order neighbor iteration, cross-platform determinism is broken.
- If geometry edits require full-planet recompute, EARTH-1 violates bounded update intent.
- If hydrology reads real DEM or authored rivers, EARTH-0/EARTH-1 low-data law is broken.

## 9. Implementation Direction

EARTH-1 should:

- treat `elevation_params_ref.height_proxy` as the canonical macro height input
- compute downhill flow by deterministic GEO neighbor ordering
- compute drainage as a bounded local accumulation proxy over a deterministic tile window
- expose `flow_target_tile_key`, `drainage_accumulation_proxy`, and `river_flag` on the tile artifact
- recompute only affected local windows after geometry edits
- keep POLL/FLUID integration at the hook level only
