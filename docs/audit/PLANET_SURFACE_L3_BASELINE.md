Status: DERIVED
Last Reviewed: 2026-03-09
Supersedes: none
Superseded By: none
Version: 1.0.0
Compatibility: Bound to `docs/specs/SPEC_MVP0_SCOPE_CONSTITUTION.md`, `docs/worldgen/MILKY_WAY_CONSTITUTION.md`, `docs/worldgen/STAR_SYSTEM_ORBITAL_PRIORS.md`, `docs/worldgen/PLANET_SURFACE_MACRO_MODEL.md`, `schema/worldgen/surface_tile_artifact.schema`, `schema/worldgen/surface_generator_routing.schema`, and `src/worldgen/mw/mw_surface_refiner_l3.py`.

# Planet Surface L3 Baseline

## Tile Schema And Routing

- Canonical realism profile: `realism.realistic_default_milkyway_stub`
- Canonical surface priors: `priors.surface_default_stub`
- Canonical default route: `route.default`
- Canonical Earth placeholder route: `route.earth`
- Canonical default generator: `gen.surface.default_stub`
- Canonical Earth placeholder generator: `gen.surface.earth_stub`

MW-3 now materializes one deterministic `kind.surface_tile` per requested tile-scoped `geo_cell_key`.

Canonical surface fixture:

- ancestor world cell `= [800, 0, 0]`
- surface tile index `= [1, 2]`
- chart `= chart.atlas.north`
- canonical tick `= 4096`

Observed canonical surface fixture outputs:

- `tile_object_id = 2b5ef9e41f3d0d4ece0ce3649cf437ad2841c12f35038f669c50459a1a536ea1`
- `surface_tile_artifact_fingerprint = c6399b2dfbecf58ea02d0a699c97a2e1bde3da50c9cf087df57eebc3efe2c3fe`
- `combined_l3_hash = efbc3e731770147f9eea30ffa08fdcd9865ea54bb196a4b5b3283610de0bb166`
- route resolution:
  - `surface_routing_id = route.default`
  - `surface_generator_id = gen.surface.default_stub`
  - `surface_handler_id = mw.surface.default_stub`

Routing remains registry-driven:

- runtime code resolves generator selection through `surface_generator_routing_registry.json`
- the Earth placeholder route remains a tag-driven overlay hook only
- generator delegation uses data-declared `delegate_generator_id`, not runtime `Earth` branches

## Macro Climate Proxies

MW-3 initializes the requested tile only.

The canonical fixture above yields:

- `field_initialization_count = 3`
- `geometry_initialization_count = 1`
- `material_baseline_id = material.stone_basic`
- `biome_stub_id = biome.stub.tundra`
- `temperature_value = 161`
- `daylight_value = 0`
- `pressure_value = 1800`

The L3 proxy ladder remains intentionally coarse:

- daylight derives from latitude band, axial tilt, and canonical tick season phase
- insolation derives from daylight, star luminosity proxy, and semi-major axis proxy
- temperature derives from insolation, latitude cooling, daylight weighting, ocean moderation, and atmosphere bias
- pressure derives only from the atmosphere class and remains a stub field, not a fluid solve

## Validation Snapshot

- Frozen contract hash guard: PASS on 2026-03-09
- Identity fingerprint check: PASS on 2026-03-09
- Targeted RepoX MW-3 invariants: PASS on 2026-03-09
  - `INV-SURFACE-GEN-ROUTED`
  - `INV-TILES-ON-DEMAND-ONLY`
- Targeted AuditX MW-3 analyzers: PASS on 2026-03-09
  - `E361_HARDCODED_EARTH_GEN_SMELL`
  - `E362_EAGER_TILE_GENERATION_SMELL`
- Targeted TestX MW-3 subset: PASS on 2026-03-09
  - `test_surface_tile_id_stable`
  - `test_surface_gen_routing_deterministic`
  - `test_tile_refinement_idempotent`
  - `test_fields_initialized_for_tile`
  - `test_cross_platform_tile_hash_match`
- AuditX full scan: completed on 2026-03-09
  - output root `build/mw3/auditx/`
  - `findings_count = 2270`
  - `promotion_candidate_count = 69`
- RepoX STRICT full-repo run: failed on 2026-03-09 due pre-existing repository-wide governance drift
  - output root `build/mw3/repox/`
  - MW task-local groups remained clean:
    - `repox.runtime.bundle violation_count = 0`
    - `repox.runtime.worldgen violation_count = 0`
  - dominant blocking classes remained `INV-DOC-STATUS-HEADER`, `INV-CANON-INDEX`, `INV-REPOX-STRUCTURE`, and `INV-TOOL-VERSION-MISMATCH`
- Strict build lane: blocked on 2026-03-09
  - `cmake --build --preset msvc-verify`
  - environment lacks `Visual Studio 18 2026`

## Topology Map

- `docs/audit/TOPOLOGY_MAP.json` regenerated on 2026-03-09
- deterministic fingerprint `e35c3e08756ff0f8653ab12509ec80415e4310fc6f901cd903b79cdb3a6d6ec9`
- node count `4362`
- edge count `9196`

## SOL-0 And EARTH-0 Readiness

MW-3 leaves the repository ready for:

- `SOL-0` overlay pinning that tags the Sol Earth artifact lineage without changing base surface-tile IDs
- `EARTH-0` generator replacement through `route.earth` / `gen.surface.earth_stub`
- later high-detail terrain and climate enrichments that patch tile content while preserving tile ancestry, field bindings, and process-only refinement flow
