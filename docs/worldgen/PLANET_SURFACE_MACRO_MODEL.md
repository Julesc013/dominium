Status: CANONICAL
Last Reviewed: 2026-03-09
Supersedes: none
Superseded By: none

# Planet Surface Macro Model

This document freezes the MW-3 planet-surface macro refinement contract for Dominium v0.0.0.

It is subordinate to:

- `docs/canon/constitution_v1.md`
- `docs/canon/glossary_v1.md`
- `docs/specs/SPEC_MVP0_SCOPE_CONSTITUTION.md`
- `docs/worldgen/MILKY_WAY_CONSTITUTION.md`
- `docs/worldgen/STAR_SYSTEM_SEED_MODEL.md`
- `docs/worldgen/STAR_SYSTEM_ORBITAL_PRIORS.md`

## Relevant Invariants

- `docs/canon/constitution_v1.md` `A1` Determinism is primary
- `docs/canon/constitution_v1.md` `A2` Process-only mutation
- `docs/canon/constitution_v1.md` `A6` Provenance is mandatory
- `docs/canon/constitution_v1.md` `A9` Pack-driven integration
- `docs/canon/constitution_v1.md` `E2` Deterministic ordering
- `docs/canon/constitution_v1.md` `E4` Named RNG streams
- `docs/canon/constitution_v1.md` `E6` Replay equivalence
- `docs/worldgen/MILKY_WAY_CONSTITUTION.md`
- `docs/worldgen/STAR_SYSTEM_ORBITAL_PRIORS.md`

## 1. Scope

MW-3 upgrades MW-2 coarse `kind.planet` artifacts into on-demand macro surface tiles.

MW-3 defines:

- stable `kind.surface_tile` identities
- macro tile artifacts
- macro geometry initialization per tile
- macro surface field initialization per tile
- generator routing for default and future Earth-specific delegation

MW-3 does not define:

- detailed terrain meshes
- erosion or climate simulation
- real Earth geography or DEM data
- hardcoded Earth rules in runtime code

## 2. Surface Partition

Surface refinement targets a tile-scoped `geo_cell_key`.

Rules:

- sphere planets use `geo.topology.sphere_surface_s2` with `geo.partition.atlas_tiles`
- flat worlds use grid partitions declared by surface priors
- tile `chart_id`, `index_tuple`, and `refinement_level` are canonical GEO coordinates
- planet ancestry is carried in `geo_cell_key.extensions`; that ancestry may include:
  - `planet_object_id`
  - `ancestor_world_cell_key`
  - optional routing tags

The semantic tile coordinate remains GEO-native.
The parent planet lineage remains explicit in ancestry metadata and local subkey derivation.

## 3. Surface Tile Identity

Each tile materializes as one deterministic `kind.surface_tile`.

Identity rules:

- tile object IDs are derived by GEO-1 identity rules
- tile identity depends on:
  - universe identity hash
  - tile `geo_cell_key`
  - object kind `kind.surface_tile`
  - local subkey containing the parent `planet_object_id`
- tile IDs must remain stable if overlays later change content but not identity lineage

Later Earth overlays may replace macro content through patch/generator routing, but must not replace tile IDs.

## 4. Surface Tile Artifact

Each macro tile artifact stores:

- `tile_object_id`
- `planet_object_id`
- `tile_cell_key`
- `elevation_params_ref`
- `material_baseline_id`
- `biome_stub_id`

The artifact is coarse and planet-agnostic.
It is sufficient to anchor later detailed terrain generators without changing identity.

Allowed macro classes include:

- water/ocean stubs
- rocky land stubs
- ice-cap or frozen stubs
- desert / temperate / tundra biome tags

## 5. Macro Fields

MW-3 initializes GEO-bound field cells for the requested tile only.

Required field outputs:

- `field.temperature`
- `field.daylight`
- `field.pressure_stub` when the planet atmosphere class is not `atmo.none`

Rules:

- temperature is a deterministic proxy, not a simulated thermal equilibrium solve
- daylight is a deterministic insolation/season proxy
- pressure is a deterministic atmosphere-pressure proxy, not a fluid simulation
- the worldgen process initializes only the targeted tile cell and never eagerly expands all surface tiles

## 6. Macro Climate Proxy Inputs

MW-3 uses only coarse deterministic inputs already available by MW-2 plus TEMP tick context.

Inputs include:

- planet radius
- atmosphere class
- ocean fraction
- axial tilt
- orbital proxy data
- star luminosity proxy
- current canonical tick for season phase
- realism-declared surface priors

Required behavior:

- temperature proxy varies by latitude band and insolation
- daylight proxy varies by latitude band, axial tilt, and season phase
- pressure proxy varies by atmosphere class only

## 7. Generator Routing

Surface generation is selected through registries, never through hardcoded object-name checks.

Routing surfaces:

- default generator: `gen.surface.default_stub`
- Earth placeholder generator: `gen.surface.earth_stub`
- selector aliases:
  - `planet_default_surface_generator` -> `gen.surface.default_stub`
  - `earth_surface_generator` -> `gen.surface.earth_stub`

Allowed selector kinds:

- `by_object_id`
- `by_tag`
- `by_profile`

Deterministic route precedence:

1. `by_object_id`
2. `by_tag`
3. `by_profile`
4. lexical `routing_id`

Rules:

- runtime code must not branch on `"Earth"` or `planet.earth` literals to choose the generator
- later Sol/Earth overlays may supply route tags such as `planet.earth`
- route selection may delegate from a placeholder generator to a default stub only through data-declared registry metadata

## 8. Refinement L3

`worldgen_request.refinement_level >= 3` for a valid surface-tile target performs:

1. resolve the parent planet lineage from tile ancestry
2. regenerate or resolve the required MW-2 parent priors deterministically
3. choose a surface generator through the routing registry
4. derive the stable tile object ID
5. emit one `surface_tile_artifact`
6. emit one macro `geometry_cell_state`
7. emit the required field-cell initializations for that tile

Rules:

- refinement is idempotent
- the same tile request yields byte-identical artifacts
- no eager neighboring tile generation is permitted

## 9. Earth Delegation Contract

MW-3 reserves Earth specialization without embedding Earth logic in the base runtime.

Rules:

- Earth-specific generation must enter through overlay tags or generator routing registry rows
- the default procedural generator remains valid if the Earth-specific generator is absent
- future Earth packs may enrich tile content, but must preserve stable tile identity and tile ancestry

## 10. Non-Goals

MW-3 does not define:

- continent realism
- real coastlines
- tectonics
- hydrology
- weather solvers
- authored settlements or borders

## 11. Required Stability Guarantees

- identical inputs produce identical tile artifact rows, field initializations, and geometry initializations
- tile ordering is canonical by `geo_cell_key` then `tile_object_id`
- named RNG streams remain rooted in worldgen lineage; no anonymous randomness is permitted
- no wall-clock or platform-local time may affect surface outputs
