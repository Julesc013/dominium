# Geology Fixture Example (GEOLOGY2)

This example shows the fixture format used by geology tools and tests. These
files live under `tests/fixtures/geology/`.

## Fixture

```
DOMINIUM_GEOLOGY_FIXTURE_V1
fixture_id=geology.fixture.example
world_seed=303
domain_id=13
shape=oblate
radius_equatorial=256
radius_polar=240
meters_per_unit=1
noise_seed=9
noise_amplitude=1
noise_cell_size=24
layer_count=2
layer0_id=geo.sediment
layer0_thickness=20
layer0_hardness=0.3
layer0_fracture=0.6
layer1_id=geo.bedrock
layer1_thickness=0
layer1_hardness=0.8
layer1_fracture=0.2
resource_count=2
resource0_id=resource.pocket_a
resource0_base=0.02
resource0_noise_amp=0.06
resource0_noise_cell=12
resource0_pocket_threshold=0.85
resource0_pocket_boost=0.3
resource0_pocket_cell=18
resource1_id=resource.pocket_b
resource1_base=0.01
resource1_noise_amp=0.04
resource1_noise_cell=14
resource1_pocket_threshold=0.9
resource1_pocket_boost=0.25
resource1_pocket_cell=20
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

## Run the tool

```
dom_tool_geology validate --fixture tests/fixtures/geology/resource_pockets.geology
dom_tool_geology inspect --fixture tests/fixtures/geology/resource_pockets.geology --pos 0,0,0
dom_tool_geology core-sample --fixture tests/fixtures/geology/resource_pockets.geology --origin 0,0,0 --dir 0,0,1
dom_tool_geology map --fixture tests/fixtures/geology/resource_pockets.geology --center-latlon 0.0,0.0
dom_tool_geology slice --fixture tests/fixtures/geology/resource_pockets.geology --resource resource.pocket_a --center 0,0,0 --radius 32
```
