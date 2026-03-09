Status: CANONICAL
Last Reviewed: 2026-03-09
Supersedes: none
Superseded By: none

# Earth Procedural Constitution

This document freezes the EARTH-0 procedural Earth generator contract for Dominium v0.0.0.

It is subordinate to:

- `docs/canon/constitution_v1.md`
- `docs/canon/glossary_v1.md`
- `docs/specs/SPEC_MVP0_SCOPE_CONSTITUTION.md`
- `docs/worldgen/MILKY_WAY_CONSTITUTION.md`
- `docs/worldgen/PLANET_SURFACE_MACRO_MODEL.md`
- `docs/packs/sol/PACK_SOL_PIN_MINIMAL.md`

## Relevant Invariants

- `docs/canon/constitution_v1.md` `A1` Determinism is primary
- `docs/canon/constitution_v1.md` `A2` Process-only mutation
- `docs/canon/constitution_v1.md` `A6` Provenance is mandatory
- `docs/canon/constitution_v1.md` `A9` Pack-driven integration
- `docs/canon/constitution_v1.md` `E2` Deterministic ordering
- `docs/canon/constitution_v1.md` `E4` Named RNG streams
- `docs/canon/constitution_v1.md` `E6` Replay equivalence
- `docs/worldgen/PLANET_SURFACE_MACRO_MODEL.md`
- `docs/packs/sol/PACK_SOL_PIN_MINIMAL.md`

## 1. Scope

EARTH-0 defines the dedicated Earth surface generator for Dominium v0.0.0.

It provides:

- Earth-specific generator routing
- deterministic continent and ocean macro masks
- deterministic macro mountain ridges
- deterministic climate-band biome stubs
- deterministic polar ice-cap assignment
- far-LOD visual class expectations for oceans, land, and poles

It does not provide:

- real DEM data
- real coastlines
- real political boundaries
- cities
- authored terrain datasets
- full climate simulation

## 2. Generator Role

Earth generation is selected only through routing data.

Required routing law:

- if a planet surface request carries the routed tag `planet.earth`, the route must resolve to `gen.surface.earth_stub`
- `gen.surface.earth_stub` must bind to an Earth-specific handler
- runtime code must not choose the Earth generator by checking display names or hardcoded object IDs

Earth remains overlay-safe:

- the Sol pin pack supplies the Earth tag
- future higher-fidelity Earth packs may replace generator routing or overlay generated properties
- tile and planet identities remain unchanged

## 3. Continental Generation Model

Earth macro continents are generated from low-frequency deterministic spherical noise.

Inputs:

- `universe_seed`
- `generator_version_id`
- `planet_object_id`
- tile `geo_cell_key`

Required properties:

- continent count target remains small and macro-only
- ocean coverage target remains approximately seventy percent
- land/ocean classification is derived from deterministic spherical noise, not from any real map

Permitted model ingredients:

- low-frequency continental mask noise
- longitudinal wave modulation
- hemisphere-safe spherical atlas mapping
- deterministic thresholding against the configured ocean target

## 4. Mountain and Elevation Model

Earth macro mountains are generated from deterministic ridge and plate-proxy terms.

Allowed drivers:

- ridged noise bands
- simple deterministic Voronoi-like plate proxy regions
- coastal uplift bias

Required output:

- only macro `elevation_params_ref`
- only macro `height_proxy`
- sufficient structure for later detailed terrain generators

EARTH-0 does not simulate tectonics.

## 5. Climate Bands and Biome Stubs

EARTH-0 climate output is a macro proxy.

Required drivers:

- latitude
- axial tilt
- daylight/insolation proxy
- ocean moderation bias

Required biome classes:

- `biome.stub.polar`
- `biome.stub.temperate`
- `biome.stub.tropical`
- `biome.stub.arid`
- `biome.stub.ocean`

Additional coarse stubs are allowed if they remain deterministic and data-light.

## 6. Ice Caps

High-latitude Earth tiles must be able to resolve to polar ice without any real geography source.

Rules:

- ice assignment is driven by latitude and temperature proxy thresholds
- polar ice is a material override, not a replacement identity
- polar coverage must remain bounded and testable

## 7. Daylight and Season

EARTH-0 uses the canonical temporal and orbital proxy path.

Rules:

- daylight depends on the current canonical tick
- daylight responds to Earth axial tilt
- seasonal variation must be deterministic for identical inputs
- wall-clock time must never participate

## 8. Far-LOD Expectations

At far LOD, Earth tiles must classify into macro visual expectations:

- oceans resolve to blue water baselines
- land resolves to green or brown biome classes
- polar regions resolve to white ice classes

These expectations are satisfied by material and biome classes, not by authored textures.

## 9. Determinism

All Earth generation must derive only from declared inputs:

- `universe_seed`
- `generator_version_id`
- `planet_object_id`
- surface tile `geo_cell_key`
- configured Earth parameter record
- canonical tick for seasonal/daylight evaluation

All random variation must use named RNG substreams only.

Forbidden:

- real-world datasets
- wall-clock time
- unordered iteration
- platform-specific floating behavior as an authority input

## 10. Output Contract

EARTH-0 emits the same MW-3 tile-surface contract shape:

- `generated_surface_tile_artifact_rows`
- `field_layers`
- `field_initializations`
- `geometry_initializations`
- `surface_summary`

EARTH-0 extends content, not the identity law.

## 11. Upgrade Path

Future Earth overlays may add:

- DEM-backed elevation overlays
- authored climate overlays
- cultural or political layers
- traversal/detail packs

Those later packs must:

- layer over the same tile identities
- preserve the generator routing contract or version it explicitly
- avoid replacing GEO-owned object identity
