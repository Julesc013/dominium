# Biomes

- Types: `BiomeType { id, name, min/max temp, precip, height, humidity }` (TempK/Q16.16). Register via `dbiome_register_type`; defaults include temperate_forest, desert, tundra, and wetland.
- Field: `biome_id` is a registered `dfield` (U8 storage for now) so tile/chunk storage can be shared with other systems.
- Classification: `dbiome_get_at_tile(body, WPosTile)` samples `dclimate` means, folds in local height and nearby water depth from `dhydro`, then calls `dbiome_classify`. Ranges are inclusive; zero ranges are treated as “don’t care”.
- Usage: game/ecs picks flora/fauna/visual sets from the returned `BiomeId`; callers can also fetch types via `dbiome_get_type`.
- Determinism: fixed-point only; no floating-point thresholds. All queries are on-demand—no private biome grids that bypass `dfield`.
