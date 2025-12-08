# Hydrology

- Fields: `water_depth` is the canonical per-tile depth field (Q16.16, metres proxy) registered via `dfield`. Hydrology does not own hidden 3D arrays; it tracks tiles through the shared registry and lightweight caches.
- River graph: `HydroRiverLink { body, from, to, gradient }` captures static down-slope paths; registration is via `dhydro_register_river_link` (no full solver yet).
- Flow model: `dhydro_step(body, ChunkPos region, ticks)` walks the surface layer of the chunk, applies accumulated rain, routes outflow toward lower neighbours (4-neighbour, gradient-based) and subtracts evaporation (`dhydro_register_evaporation_bias` sets the per-body rate).
- Inputs: rainfall comes from weather through `dhydro_add_rainfall(body, tile, depth)`. Terrain height comes from tile `z` for now; plug in real terrain fields later to refine gradients.
- Outputs/queries: `dhydro_get_water_depth` returns stored depth for a tile; `dhydro_get_flow` reports the last computed outflow vector (wind-style `u/v` in Q16.16).
- Determinism: all math is fixed-point (Q16.16). Updates are local to regions so world-scale floods stay deterministic and bounded even with stub storage.
