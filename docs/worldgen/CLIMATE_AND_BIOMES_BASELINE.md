# Climate Envelopes & Biomes Baseline (CLIMATE0)

Status: binding for T3 baseline.  
Scope: static, deterministic climate envelopes and biome classification.

## What climate envelopes are
- Climate is represented as **envelopes**: mean and range fields over space.
- Envelopes are **static** and deterministic; no per-tick simulation exists here.
- Mandatory climate fields:
  - `climate.temperature_mean`
  - `climate.temperature_range`
  - `climate.precipitation_mean`
  - `climate.precipitation_range`
  - `climate.seasonality`
  - `climate.wind_prevailing` (symbolic)
- All numeric fields are unit-tagged per `docs/architecture/UNIT_SYSTEM_POLICY.md`.

## Provider chain (T3 baseline)
1) **Procedural base provider**
   - Seeded and deterministic
   - Latitude/altitude dependent
   - Shape-aware (sphere, oblate, slab)
2) **Anchor provider** (optional)
   - Artist/real-world authored overrides
3) **Overlays**: none in T3

Providers are sparse, chunk-resolved, and budget/interest bounded.

## Biome classification
- **Biome classification is a pure resolver**:
  - Inputs: climate envelopes, terrain elevation + moisture proxy, geology surface traits
  - Outputs: `biome_id` (categorical), `biome_confidence` (0..1)
- Classification is deterministic, reversible (recomputable), and does not mutate state.
- Example biome ids are data-defined and extensible:
  - tundra, desert, temperate_forest, rainforest, savanna, alpine, volcanic, barren

## What is not included yet
- No dynamic weather or storm events (reserved for T4).
- No erosion, growth, or life simulation.
- No mining or resource extraction logic.

## Collapse/expand compatibility
- Climate collapse stores sufficient statistics (histograms + averages).
- Expand reproduces envelope queries deterministically from providers.

## Maturity labels
- Climate envelopes: **BOUNDED** (static baseline, deterministic).
- Biome classification: **BOUNDED** (pure resolver; data-defined rules only).

## See also
- `docs/worldgen/CLIMATE_BODY_SHAPES.md`
- `docs/architecture/SCALING_MODEL.md`
- `docs/architecture/COLLAPSE_EXPAND_CONTRACT.md`
