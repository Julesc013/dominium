Status: DERIVED
Last Reviewed: 2026-03-10
Supersedes: none
Superseded By: none
Version: 1.0.0
Compatibility: Bound to `docs/worldgen/EARTH_HYDROLOGY_MODEL.md`, `src/worldgen/earth/hydrology_engine.py`, `src/worldgen/mw/mw_surface_refiner_l3.py`, `tools/worldgen/earth1_probe.py`, and `tools/worldgen/tool_replay_hydrology_window.py`.

# Earth Hydrology Baseline

## Accumulation Threshold

- canonical hydrology params row: `params.hydrology.default_stub`
- `accumulation_threshold = 7`
- `lake_elevation_delta_threshold = 220`
- `analysis_radius = 2`
- `local_recompute_radius = 2`

## Flow Ordering Rules

EARTH-1 now computes local macro hydrology by:

- selecting the strictly lowest deterministic GEO neighbor as `flow_target_tile_key`
- breaking ties by canonical `geo_cell_key` order
- accumulating drainage in descending effective-height order
- marking `river_flag` when `drainage_accumulation_proxy >= 7`

Observed deterministic proof values on 2026-03-10:

- Earth sample hydrology hash: `04f917f853b6b572ac16408c2318292609d3da2f196b9a740765f13ac8c2fda1`
- local replay window hash: `e6599106b217c2efefbe0a412252028905d5c8916d70321022bee2823b22bc72`
- synthetic river-threshold window hash: `104a05e1661314c4c5c2ccc2abc950934f4ff421e654c00276b0f2b1416b6082`

## Integration Summary

- `surface_tile_artifact` now carries `flow_target_tile_key`, `drainage_accumulation_proxy`, and `river_flag`
- L3 summaries now expose hydrology structure kind plus POLL/FLUID guidance stubs
- geometry-edit processes trigger bounded local hydrology recompute through lawful process execution
- observed local edit probe:
  - candidate tile `chart.atlas.north [3, 2]`
  - `dirty_tile_count = 1`
  - `recomputed_tile_count = 1`
  - changed tile artifact count = `1`

## Readiness

EARTH-1 is now ready for:

- EARTH-2 seasonal climate variation over stable flow structure
- later POLL transport stubs following deterministic flow chains
- later FLUID channel guidance reusing the bounded hydrology graph
- continued embodiment traversal over edit-responsive Earth macro terrain
