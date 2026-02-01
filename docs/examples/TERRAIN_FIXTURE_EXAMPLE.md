Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Terrain Fixture Example (TERRAIN1)

This example shows the fixture and navigation scripts used by the terrain T1
tests and tools. These files live under `tests/fixtures/terrain/`.

## Fixture

```
DOMINIUM_TERRAIN_FIXTURE_V1
fixture_id=terrain.fixture.example
world_seed=42
domain_id=1001
shape=sphere
radius_equatorial=256
meters_per_unit=1000
noise_seed=5
noise_amplitude=1
noise_cell_size=16
material_primary=1
roughness_base=0.1
travel_cost_base=1
travel_cost_slope_scale=1
travel_cost_roughness_scale=1
walkable_max_slope=1
cache_capacity=128
tile_size=64
max_resolution=medium
sample_dim_full=8
sample_dim_medium=4
sample_dim_coarse=2
cost_full=100
cost_medium=40
cost_coarse=10
cost_analytic=5
tile_build_cost_full=80
tile_build_cost_medium=30
tile_build_cost_coarse=10
ray_step=1
max_ray_steps=64
```

## Navigation script

```
DOMINIUM_TERRAIN_NAV_V1
latlon=0.00,0.00,0
latlon=0.00,0.05,0
latlon=0.00,0.10,0
latlon=0.00,0.15,0
latlon=0.05,0.00,0
latlon=-0.05,0.00,0
```

## Run the tool

```
dom_tool_terrain inspect --fixture tests/fixtures/terrain/earth_like.terrain --nav tests/fixtures/terrain/terrain_nav.txt --index 0
dom_tool_terrain walk --fixture tests/fixtures/terrain/earth_like.terrain --nav tests/fixtures/terrain/terrain_nav.txt
dom_tool_terrain render --fixture tests/fixtures/terrain/earth_like.terrain --center 0,0,0 --radius 128
```