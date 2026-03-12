Status: DERIVED
Last Reviewed: 2026-03-09
Supersedes: none
Superseded By: none
Version: 1.0.0
Compatibility: Bound to `docs/specs/SPEC_MVP0_SCOPE_CONSTITUTION.md`, `docs/worldgen/PLANET_SURFACE_MACRO_MODEL.md`, `docs/worldgen/EARTH_PROCEDURAL_CONSTITUTION.md`, `schema/worldgen/earth_surface_params.schema`, `data/registries/earth_surface_params_registry.json`, `src/worldgen/earth/earth_surface_generator.py`, `tools/worldgen/earth0_probe.py`, and `tools/worldgen/tool_verify_earth_surface.py`.
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# Earth Procedural Baseline

## Continent And Ocean Distribution Summary

- Canonical Earth route: `route.earth`
- Canonical Earth generator: `gen.surface.earth_stub`
- Canonical Earth handler: `earth.surface.stub`
- Canonical Earth parameter row: `params.earth.surface_default_stub`
- Canonical Sol/Earth activation tag: `planet.earth`

EARTH-0 now upgrades the routed Sol Earth planet into a dedicated data-light Earth macro generator.

Observed far-LOD Earth probe on 2026-03-09:

- `sample_count = 128` atlas tiles
- weighted `ocean_ratio_permille = 600`
- weighted `land_ratio_permille = 383`
- weighted `polar_ice_ratio_permille = 15`
- canonical sampled Earth surface hash `= b8864a86235a1bfd88f2d9f00792b70c6ac3731a8c0710fe9b66028c319c70bb`

The resulting macro Earth remains intentionally approximate:

- oceans dominate the visible disk
- continents remain few and macro-scale
- no sampled output depends on real coastlines or DEM input

## Biome Distribution Summary

EARTH-0 emits coarse biome and visual classes only.

Required far-LOD classes now appear through deterministic tile summaries:

- `visual.class.blue_ocean`
- `visual.class.green_brown_land`
- `visual.class.white_polar`

Observed routed Earth tiles classify into:

- `surface.class.ocean`
- `surface.class.land`
- `surface.class.ice`

And biome stubs such as:

- `biome.stub.ocean`
- `biome.stub.temperate`
- `biome.stub.tropical`
- `biome.stub.arid`
- `biome.stub.polar`

## Climate Proxy Summary

EARTH-0 still uses macro proxies rather than full climate simulation.

Drivers:

- latitude from the routed surface atlas tile
- axial tilt from the pinned Earth spin constants
- canonical tick through MW-3 insolation/daylight proxies
- deterministic continental and mountain modulation

Observed seasonal daylight probe:

- `tick_0 daylight_value = 157`
- `tick_500000 daylight_value = 166`
- `axial_tilt_affects_daylight = true`

## Overlay And Upgrade Readiness

EARTH-0 preserves the later overlay path:

- future DEM-backed Earth overlays can refine geometry without replacing GEO tile identity
- future climate packs can refine field values without replacing routed Earth lineage
- embodiment traversal can target the same stable `kind.surface_tile` identities produced now

EARTH-0 does not embed:

- DEM sources
- cities
- borders
- authored geography

## Validation Snapshot

- `python tools/worldgen/tool_verify_earth_surface.py --repo-root .` -> PASS on 2026-03-09
- Targeted RepoX Earth invariants -> PASS on 2026-03-09
  - `INV-NO-REAL-DATA-IN-EARTH-STUB`
  - `INV-EARTH-GEN-DETERMINISTIC`
- Targeted AuditX Earth analyzers -> PASS on 2026-03-09
  - `E365_HARDCODED_DEM_REFERENCE_SMELL`
  - `E366_NONDETERMINISTIC_NOISE_SMELL`
- Targeted TestX EARTH-0 subset -> PASS on 2026-03-09
  - `test_earth_tile_deterministic`
  - `test_ocean_fraction_within_bounds`
  - `test_polar_ice_present`
  - `test_axial_tilt_affects_daylight`
  - `test_cross_platform_earth_hash_match`

## Readiness

EARTH-0 is ready for:

- future Earth DEM overlay packs
- future Earth climate/detail overlays
- embodiment traversal across stable routed Earth tile identities
