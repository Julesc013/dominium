Status: DERIVED
Last Reviewed: 2026-03-10
Supersedes: none
Superseded By: none

# EARTH-8 Retro Audit

## Audit Targets

- current render-model and software-renderer derived-artifact inputs
- existing map/minimap layer pipeline and lens-layer registry
- hydrology/tide surfaces already available on Earth tiles
- viewer-shell integration points that can add water visuals without Truth reads

## Findings

### Existing Earth tile artifacts already carry enough macro water cues

- `src/worldgen/earth/hydrology_engine.py` already persists:
  - `river_flag`
  - `flow_target_tile_key`
  - `extensions.lake_flag`
  - `extensions.hydrology_structure_kind`
- `src/worldgen/earth/tide_field_engine.py` already produces deterministic per-tile tide overlays and `field.tide_height_proxy`.
- Conclusion:
  - EARTH-8 can remain derived-only and avoid any new authoritative simulation path.

### The viewer and renderer already accept derived Earth presentation artifacts

- `src/client/ui/viewer_shell.py` already builds and carries:
  - `sky_view_surface`
  - `illumination_view_surface`
- `src/client/render/render_model_adapter.py` already forwards derived artifacts into `RenderModel.extensions`.
- `src/client/render/renderers/software_renderer.py` already renders bounded sky and lighting overlays from derived artifacts only.
- Conclusion:
  - EARTH-8 should mirror the same pattern with a compact `water_view_artifact`.

### GEO lens layers need one new source kind, not a separate map subsystem

- `src/geo/lens/lens_engine.py` already supports field, terrain, geometry, and marker-backed layers.
- `data/registries/lens_layer_registry.json` already governs view-facing layer semantics.
- Conclusion:
  - EARTH-8 should add `water_view` as a bounded derived source kind rather than inventing a parallel map renderer.

### No existing renderer-side water simulation path was found

- The software renderer currently draws:
  - sky background
  - sky band
  - sun/moon disks
  - stars
  - primitive renderables
- No ocean solver, shoreline wave code, or authoritative water state mutation path exists.
- Conclusion:
  - EARTH-8 can safely add a presentation-only water overlay without colliding with an existing fluid implementation.
