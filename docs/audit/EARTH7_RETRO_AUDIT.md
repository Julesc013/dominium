Status: DERIVED
Last Reviewed: 2026-03-10
Supersedes: none
Superseded By: none

# EARTH-7 Retro Audit

## Audit Targets

- field registry and GEO field bindings relevant to Earth surface tiles
- existing POLL dispersion wind-advection integration points
- current Earth field-process pattern for deterministic bucketed updates
- viewer and inspection surfaces for derived field overlays

## Findings

### Existing Earth field updates already provide the right deterministic skeleton

- `src/worldgen/earth/climate_field_engine.py` and `src/worldgen/earth/tide_field_engine.py` already implement:
  - deterministic bucket selection from stable `geo_cell_key`
  - bounded `max_tiles_per_update` budgets
  - per-tile evaluation rows plus canonical field updates
  - replay hash helpers for proof tooling
- `tools/xstack/sessionx/process_runtime.py` already hosts:
  - `process.earth_climate_tick`
  - `process.earth_tide_tick`
  - runtime state persistence
  - derived overlay persistence
- Conclusion:
  - EARTH-7 should reuse the same process/runtime pattern rather than introduce a separate scheduler or field mutation path.

### POLL already has a deterministic wind-advection hook

- `src/pollution/dispersion_engine.py` already supports:
  - `wind_modifier_enabled`
  - `wind_bias_permille`
  - vector-field sampling through `_wind_by_cell(...)`
- The current default field id is `field.wind`.
- Conclusion:
  - EARTH-7 can add the canonical Earth wind field as `field.wind_vector` and update POLL to prefer it while retaining deterministic fallback to the legacy alias.

### Existing field registries include legacy wind but not the new canonical Earth field id

- `data/registries/field_type_registry.json` already declares `field.wind`.
- `data/registries/field_binding_registry.json` already binds `field.wind` for:
  - `geo.topology.r3_infinite`
  - `geo.topology.sphere_surface_s2`
- The prompt requires a canonical field id:
  - `field.wind_vector`
- Conclusion:
  - EARTH-7 should add `field.wind_vector` as the canonical field type and Earth surface binding, while preserving `field.wind` as a compatibility alias for older systems and tests.

### Viewer surfaces already accept new derived layers without truth coupling

- `data/registries/lens_layer_registry.json` already exposes field-backed layers such as:
  - `layer.temperature`
  - `layer.tide_height_proxy`
  - `layer.pollution`
- `src/client/ui/map_views.py` and `src/client/ui/inspect_panels.py` consume derived layer ids and field summaries only.
- Conclusion:
  - EARTH-7 can add `layer.wind_vector` without creating any renderer truth-read path.

### No conflicting Earth wind truth assumptions were found

- No existing authoritative Earth-specific wind field tick was present.
- Existing `field.wind` usage is generic, mostly in mobility and test fixtures, and does not impose an Earth-only semantic contract.
- Conclusion:
  - EARTH-7 can add a dedicated Earth surface wind-process path without conflicting with prior runtime meaning.
