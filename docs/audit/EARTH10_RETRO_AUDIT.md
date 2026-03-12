Status: DERIVED
Last Reviewed: unknown
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-ARCHIVE
Replacement Target: legacy reference surface retained without current binding authority

# EARTH-10 Retro Audit

Date: 2026-03-12
Series: EARTH-10
Scope: material proxy, surface flag, and albedo proxy stubs for Earth surface tiles

## Summary

EARTH-9 already exposes deterministic Earth surface artifacts, macro field initialization, hydrology overlays, collision sampling, water-view derivation, and illumination-view derivation. The safest EARTH-10 insertion point is additive Earth surface field derivation over existing surface tile artifacts and geometry state.

## Current Derivation Paths

### Terrain and water visuals

- `src/worldgen/earth/water/water_view_engine.py`
  - derives ocean, river, lake, and tide visual masks from `worldgen_surface_tile_artifacts`
  - already consumes deterministic artifact rows only
  - currently keys off `material_baseline_id`, `river_flag`, `lake_flag`, `flow_target_tile_key`, and tide overlays
- `src/worldgen/earth/lighting/illumination_engine.py`
  - derives illumination artifacts from sky-view artifacts only
  - does not mutate truth
- `src/worldgen/earth/lighting/lighting_view_engine.py`
  - combines sky and horizon shadow into derived illumination-view artifacts
- `src/worldgen/earth/earth_surface_generator.py`
  - already emits stable surface classification signals in tile artifact extensions:
    - `surface_class_id`
    - `material_baseline_id`
    - `height_proxy`
    - `climate_band_id`
    - `far_lod_visual_class`

### Collision and friction

- `tools/xstack/sessionx/process_runtime.py`
  - `process.body_tick` samples `field.friction` and passes it to `resolve_horizontal_damping_state`
  - collision state itself comes from `_body_surface_query(...)` and `resolve_macro_heightfield_sample(...)`
- `src/embodiment/movement/friction_model.py`
  - authoritative horizontal damping already accepts an optional scalar friction field input
  - safest EARTH-10 hook is additive and policy-gated before this call
- `src/embodiment/collision/macro_heightfield_provider.py`
  - authoritative terrain query already resolves the current Earth surface tile deterministically from tile artifacts and geometry rows

## Existing Field and Registry Patterns

- `src/worldgen/mw/mw_surface_refiner_l3.py`
  - already seeds Earth macro surface fields (`field.temperature`, `field.daylight`, `field.tide_height_proxy`, `field.pressure_stub`) during tile generation
  - same file is the safest additive insertion point for EARTH-10 initial field layers and initial field cells
- `src/worldgen/earth/climate_field_engine.py`
- `src/worldgen/earth/tide_field_engine.py`
- `src/worldgen/earth/wind/wind_field_engine.py`
  - all use the same deterministic pattern:
    - evaluate tile rows
    - emit ordered `field_updates`
    - process-mediated persistence through `process.field_update`
    - optional overlay rows plus runtime state for replay/proof
- `data/registries/field_type_registry.json`
  - canonical field type definitions already live here
- `data/registries/field_binding_registry.json`
  - Earth surface S2 tile bindings already exist here for macro Earth fields

## Recommended EARTH-10 Insertion Points

### Canonical fields

- add new Earth surface field types to `data/registries/field_type_registry.json`
- add Earth surface S2 bindings to `data/registries/field_binding_registry.json`
- seed initial Earth values in `src/worldgen/mw/mw_surface_refiner_l3.py`
- support deterministic recomputation through a dedicated Earth process/runtime path, matching climate/tide/wind patterns

### Derived-only hooks

- water visuals should reuse the same material-proxy derivation helper instead of inventing separate rendering logic
- illumination should reuse the same albedo derivation helper instead of storing any presentation state in truth
- collision friction must remain fallback-safe and policy-gated, using existing `field.friction` behavior unless explicitly enabled

## Safety Constraints

- additive only; no existing save schema removal
- no chemistry or density model insertion
- no presentation state persisted into TruthModel
- no direct mutation outside process-mediated field updates
- deterministic ordering must stay `geo_cell_key` sorted

## Conclusion

The EARTH-10 stub layer should be implemented as:

1. additive field/registry metadata
2. one deterministic Earth material-proxy engine reused by truth-field updates and derived views
3. one optional collision hook gated by policy

This preserves current EARTH semantics while avoiding later MAT/DOM/SOL refactors.
