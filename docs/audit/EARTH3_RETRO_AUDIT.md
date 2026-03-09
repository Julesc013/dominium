Status: DERIVED
Last Reviewed: 2026-03-10
Supersedes: none
Superseded By: none

# EARTH-3 Retro Audit

## Audit Targets

- EARTH-0 surface generation and macro material classification
- SOL-0 Earth/Moon pin availability
- FIELD registry and GEO field bindings
- Existing climate tick runtime pathway
- Existing map/lens layer surfaces

## Findings

### Moon object and pin status

- SOL-0 already pins Luna through the official Sol overlay pack.
- `src/worldgen/mw/sol_anchor.py` defines the stable Sol moon slot `sol.moon.luna`.
- `packs/official/pack.sol.pin_minimal/data/overlay/sol_pin_patches.json` materializes a stable Luna object ID under the anchored Sol lineage.
- Conclusion:
  - EARTH-3 can safely assume a lawful Moon anchor exists for doctrine and future coupling.
  - EARTH-3 does not need to add a new identity path for Luna.

### Existing field registry and GEO field binding

- `data/registries/field_type_registry.json` already contains deterministic macro surface fields for:
  - `field.temperature`
  - `field.daylight`
  - `field.pressure_stub`
- `data/registries/field_binding_registry.json` already binds those fields to:
  - `geo.topology.sphere_surface_s2`
  - `geo.partition.atlas_tiles`
  - storage kind `tile`
- Conclusion:
  - EARTH-3 should add `field.tide_height_proxy` through the same registry/binding surface.
  - No new partition or topology contract is required.

### Existing tide / sea-level logic

- No canonical tide runtime exists yet.
- Repository search found no existing authoritative `tide`, `tide_height`, or `sea_level` field/process path for EARTH-series worldgen.
- Conclusion:
  - EARTH-3 needs a new deterministic phase engine, field engine, process entry, proof tool, and tests.

### Existing deterministic update path to reuse

- EARTH-2 already provides a deterministic, budgeted field refresh path through:
  - `src/worldgen/earth/climate_field_engine.py`
  - `tools/xstack/sessionx/process_runtime.py`
  - `process.earth_climate_tick`
- This path already includes:
  - bucketed geo-cell ordering
  - process-only field mutation
  - replay/probe tooling
  - runtime overlay persistence
- Conclusion:
  - EARTH-3 should mirror EARTH-2 rather than introducing an ad hoc updater.

### UI / map / inspect surfaces

- UX-0 map layers are currently surfaced through:
  - `data/registries/lens_layer_registry.json`
  - `src/client/ui/map_views.py`
- Inspector field panel currently exposes:
  - `temperature`
  - `daylight`
  - `pollution`
- Conclusion:
  - EARTH-3 should add a lawful `layer.tide_height_proxy` lens layer and expose tide in the field inspector.

## Compatibility Check

- EARTH-3 can fit the existing deterministic contracts without changing:
  - GEO topology or partition rules
  - SOL-0 identity derivation
  - FIELD process-only mutation law
  - Earth surface tile identity or routing

## Risks To Avoid

- No wall-clock or float-trig tide evaluation
- No direct field writes outside process execution
- No hardcoded renderer truth path for tide display
- No PDE or ocean transport logic in MVP

## Decision

Proceed with EARTH-3 as:

- a deterministic Moon/Earth phase proxy layer
- a new `field.tide_height_proxy` macro field
- a new process-driven Earth tide tick
- a viewer-safe field/layer hook
- a future coupling contract for FLUID/coastal hazard work
