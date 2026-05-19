Status: DERIVED
Last Reviewed: 2026-03-24
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: OMEGA
Replacement Target: WORLDGEN_LOCK_v0_0_0 lock record and post-freeze audit archive

# WORLDGEN-LOCK-0 Retro Audit

## Scope

This audit inventories the current MVP worldgen truth path before the Ω-1 lock is frozen.

Audited code paths:

- `src/geo/worldgen/worldgen_engine.py`
- `src/worldgen/galaxy/galaxy_object_stub_generator.py`
- `src/worldgen/galaxy/galaxy_proxy_field_engine.py`
- `src/worldgen/mw/mw_cell_generator.py`
- `src/worldgen/mw/mw_system_refiner_l2.py`
- `src/worldgen/mw/mw_surface_refiner_l3.py`
- `src/worldgen/mw/sol_anchor.py`
- `src/worldgen/mw/system_query_engine.py`
- `src/worldgen/earth/earth_surface_generator.py`
- `src/worldgen/earth/climate_field_engine.py`
- `src/worldgen/earth/hydrology_engine.py`
- `src/worldgen/earth/tide_field_engine.py`
- `src/worldgen/earth/material/material_proxy_engine.py`
- `src/worldgen/mw/insolation_proxy.py`
- `src/worldgen/earth/season_phase_engine.py`
- `src/worldgen/earth/tide_phase_engine.py`

## Current Entry Points

- GEO orchestration:
  - `src/geo/worldgen/worldgen_engine.py::build_worldgen_request`
  - `src/geo/worldgen/worldgen_engine.py::generate_worldgen_result`
  - `src/geo/worldgen/worldgen_engine.py::worldgen_rng_stream_policy`
  - `src/geo/worldgen/worldgen_engine.py::worldgen_stream_seed`
- GAL sidecars:
  - `src/worldgen/galaxy/galaxy_object_stub_generator.py::generate_galaxy_object_stub_payload`
  - `src/worldgen/galaxy/galaxy_proxy_field_engine.py::evaluate_galaxy_cell_proxy`
- MW coarse and refinement:
  - `src/worldgen/mw/mw_cell_generator.py::generate_mw_cell_payload`
  - `src/worldgen/mw/mw_system_refiner_l2.py::generate_mw_system_l2_payload`
  - `src/worldgen/mw/mw_surface_refiner_l3.py::generate_mw_surface_l3_payload`
  - `src/worldgen/mw/mw_surface_refiner_l3.py::build_planet_surface_cell_key`
- SOL anchor helpers:
  - `src/worldgen/mw/sol_anchor.py::resolve_sol_anchor_cell_key`
  - `src/worldgen/mw/sol_anchor.py::sol_anchor_object_rows`
  - `src/worldgen/mw/sol_anchor.py::sol_anchor_object_ids`
- EARTH sub-stages invoked from MW-3:
  - `src/worldgen/earth/earth_surface_generator.py::generate_earth_surface_tile_plan`
  - `src/worldgen/earth/climate_field_engine.py::evaluate_earth_tile_climate`
  - `src/worldgen/earth/tide_field_engine.py::evaluate_earth_tile_tide`
  - `src/worldgen/earth/material/material_proxy_engine.py::evaluate_earth_tile_material_proxy`
  - `src/worldgen/earth/hydrology_engine.py::evaluate_earth_tile_hydrology`

## Seed Handling

- Canonical worldgen input seed currently enters as `universe_identity.global_seed`, a UTF-8 string.
- `src/geo/worldgen/worldgen_engine.py::worldgen_stream_seed` derives root stream seeds with:
  - `canonical_sha256({universe_seed, generator_version_id, realism_profile_id, geo_cell_key, stream_name})`
- Authoritative object identifiers do not depend on seed alone.
  - `src/geo/index/object_id_engine.py::geo_object_id` hashes `universe_identity_hash`, semantic cell key, object kind, and local subkey.
  - `universe_identity_hash` is currently produced by `tools.xstack.sessionx.common::identity_hash_for_payload`.
- Result: the lock must freeze both the seed string and the identity template fields that feed `identity_hash`.

## RNG Stream Names

Root streams declared by GEO:

- `rng.worldgen.galaxy`
- `rng.worldgen.system`
- `rng.worldgen.planet`
- `rng.worldgen.surface`

Derived streams declared by current generators:

- `rng.worldgen.galaxy_objects`
- `rng.worldgen.system.primary_star`
- `rng.worldgen.system.planet_count`
- `rng.worldgen.system.planet.{planet_index}`
- `rng.worldgen.surface.tile`
- `rng.worldgen.surface.generator`
- `rng.worldgen.surface.elevation`
- `rng.worldgen.surface.earth.elevation`

Audit result:

- No direct `random.`, `uuid.uuid4(`, `secrets.`, or `os.urandom(` calls were found in the audited authoritative worldgen Python paths.
- RNG derivation is hash-based and stream-named throughout the audited truth path.

## Refinement Stages Present In MVP

- L0 galaxy coarse structure:
  - MW cell summary, galactocentric placement, density/metallicity/habitability proxies, and `system_seed_rows`
  - Primary surface: `src/worldgen/mw/mw_cell_generator.py`
- L1 star distribution:
  - `star_system_artifact_rows`
  - GAL-1 compact-object stubs as a sidecar artifact set
- L2 Sol/system derivation:
  - star identities
  - planet orbit/basic rows
  - moon stub identities
  - system summary rows
  - Sol anchor is a deterministic identity overlay on the anchor cell, not a separate RNG stage
- L3 Earth terrain projection:
  - surface cell key derivation
  - route selection and handler selection
  - EARTH tile plan
  - climate, tide, material proxy, and hydrology projections
  - field initialization and geometry initialization for the requested tile only

## Float Usage In Truth Path

- No `float(` calls were found in the audited authoritative worldgen truth path.
- No `math.` calls were found in the audited authoritative worldgen truth path.
- Numeric reduction in the audited lock path is integer and fixed-point style:
  - permille
  - milli-degrees
  - milli-AU
  - integer proxy fields
- Renderer and view-only sky/lighting modules were not included in the Ω-1 truth lock baseline.

## Non-Named RNG Calls

- No non-named RNG calls were found in:
  - `src/geo/worldgen/worldgen_engine.py`
  - `src/worldgen/galaxy/galaxy_object_stub_generator.py`
  - `src/worldgen/mw/mw_cell_generator.py`
  - `src/worldgen/mw/mw_system_refiner_l2.py`
  - `src/worldgen/mw/mw_surface_refiner_l3.py`
  - `src/worldgen/earth/earth_surface_generator.py`
  - `src/worldgen/earth/climate_field_engine.py`
  - `src/worldgen/earth/hydrology_engine.py`
  - `src/worldgen/earth/tide_field_engine.py`
  - `src/worldgen/earth/material/material_proxy_engine.py`

## Implicit Defaults Found

- GEO default generator version:
  - `gen.v0_stub`
- GEO default realism profile:
  - `realism.realistic_default_milkyway_stub`
- MW default galaxy priors:
  - `priors.milkyway_stub_default`
- MW default system priors:
  - `priors.system_default_stub`
- MW default planet priors:
  - `priors.planet_default_stub`
- MW default surface priors:
  - `priors.surface_default_stub`
- MW-3 Earth binding fallbacks:
  - `DEFAULT_EARTH_CLIMATE_PARAMS_ID`
  - `DEFAULT_TIDE_PARAMS_ID`
  - `DEFAULT_HYDROLOGY_PARAMS_ID`
- SOL anchor fallback:
  - `_default_anchor_cell_key()` in `src/worldgen/mw/sol_anchor.py`

Audit conclusion:

- The current pipeline is deterministic, but several profile/priors defaults are implicit in code and therefore must be surfaced by the Ω-1 lock documents and registry.

## Deterministic ID Derivation Functions

- `tools.xstack.sessionx.common::identity_hash_for_payload`
  - freezes the universe identity hash used by object identity derivation
- `src/geo/index/object_id_engine.py::geo_object_id`
  - authoritative object ID derivation for:
    - `kind.star_system`
    - `kind.star`
    - `kind.planet`
    - `kind.moon`
    - `kind.surface_tile`
- `src/worldgen/mw/sol_anchor.py::sol_anchor_object_rows`
  - deterministic slot-to-object mapping for Sol anchor bodies
- `src/worldgen/mw/sol_anchor.py::sol_anchor_object_ids`
  - canonical Sol slot lookup built on `geo_object_id`
- `src/worldgen/mw/mw_surface_refiner_l3.py::build_planet_surface_cell_key`
  - deterministic Earth/surface tile cell-key derivation prior to `geo_object_id`

## Retro Audit Verdict

- Determinism status: `confirmed`
- Float leakage in audited truth path: `not detected`
- Non-named RNG in audited truth path: `not detected`
- Silent default surfaces: `present and must be frozen explicitly`
