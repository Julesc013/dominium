Status: DERIVED
Last Reviewed: 2026-03-09
Supersedes: none
Superseded By: none

# EARTH0 Retro Audit

This audit records the repository state immediately before EARTH-0 implementation.

Authority:

- `docs/canon/constitution_v1.md`
- `docs/canon/glossary_v1.md`
- `docs/specs/SPEC_MVP0_SCOPE_CONSTITUTION.md`
- `docs/worldgen/PLANET_SURFACE_MACRO_MODEL.md`
- `docs/packs/sol/PACK_SOL_PIN_MINIMAL.md`

## 1. Surface Routing Baseline

Current MW-3 routing already supports Earth delegation in data:

- `data/registries/surface_generator_routing_registry.json`
  - `route.earth`
  - `selector_kind = by_tag`
  - `match_rule.planet_tags = ["planet.earth"]`
  - `generator_id = gen.surface.earth_stub`
- `data/registries/surface_generator_registry.json`
  - `gen.surface.earth_stub` exists only as a placeholder
  - current handler is still `mw.surface.default_stub`
  - current generator row delegates to `gen.surface.default_stub`

Conclusion:

- routing contract already exists
- EARTH-0 must replace only the handler binding and parameter source
- no runtime branch on Earth identity is required to select the generator

## 2. Field Binding Baseline

Current MW-3 surface refinement initializes GEO-bound macro field rows through:

- `field.temperature`
- `field.daylight`
- `field.pressure_stub` when atmosphere exists

Observed runtime path:

- `src/worldgen/mw/mw_surface_refiner_l3.py`
  - creates tile-scoped field layers
  - creates tile-scoped field cells
  - binds both to the requested surface `geo_cell_key`
- `src/geo/worldgen/worldgen_engine.py`
  - runs `generate_mw_surface_l3_payload(...)` only for `refinement_level >= 3`
  - preserves the single-tile on-demand contract

Conclusion:

- EARTH-0 can reuse the existing field initialization surface
- no new field types are required for MVP

## 3. Geometry Edit Compatibility

Current MW-3 surface refinement initializes macro geometry through:

- `src.geo.edit.build_geometry_cell_state(...)`

Observed behavior:

- tile geometry is initialized at macro fidelity only
- `height_proxy` and `material_id` are sufficient for GEO-7 macro initialization
- authoritative state mutation persists through the worldgen process path

Conclusion:

- EARTH-0 can supply Earth-specific `elevation_params_ref` and `height_proxy`
- no geometry-contract change is required

## 4. Earth Tag Baseline

Current Sol pin overlay already marks Earth for routing:

- `packs/official/pack.sol.pin_minimal/data/overlay/sol_pin_patches.json`
  - Earth patch sets `tags = ["official", "planet.earth", "sol.planet.earth"]`

Observed identity relationship:

- the Sol pack targets GEO-derived procedural object IDs
- the `planet.earth` tag is an overlay property, not a new identity
- MW-3 routing can already consume route tags passed through tile `geo_cell_key.extensions`

Conclusion:

- EARTH-0 can be activated by the existing Sol pin pack with no identity migration
- generator selection remains overlay-safe

## 5. Reuse Candidates

Direct reuse:

- `src/worldgen/mw/mw_surface_refiner_l3.py`
  - routing
  - tile identity
  - field/geometry initialization
  - temperature/daylight/pressure proxy scaffolding
- `src/worldgen/mw/insolation_proxy.py`
  - daylight and seasonal proxy functions
- `tools/xstack/testx/tests/mw3_testlib.py`
  - fixture pattern for tile requests
- `tools/xstack/testx/tests/sol0_testlib.py`
  - canonical Sol/Earth object identity fixture helpers

Missing pieces:

- Earth-specific continental/ocean macro model
- Earth-specific parameter schema
- Earth-specific test helper and far-LOD verification tool

## 6. Risks Identified Before Implementation

- If the Earth handler is selected by runtime Earth-name checks instead of registry routing, MW-3 routing law is broken.
- If Earth parameters are embedded as ad hoc literals in `mw_surface_refiner_l3.py`, later overlay/profile replacement becomes harder.
- If Earth tiles are generated in batches instead of one requested tile at a time, MW-3 on-demand guarantees are broken.

## 7. Implementation Direction

EARTH-0 should:

- keep generator selection data-driven through `route.earth`
- install a dedicated Earth handler behind `gen.surface.earth_stub`
- reuse MW-3 field and geometry output contracts
- source Earth continent/ocean/mountain thresholds from a small Earth parameter record
- preserve single-tile deterministic refinement only
