Status: DERIVED
Last Reviewed: 2026-03-10
Supersedes: none
Superseded By: none

# EARTH-5 Retro Audit

## Audit Targets

- current RenderModel and renderer integration surfaces
- EARTH-4 sky-view artifact outputs and viewer-shell handoff
- available terrain elevation proxy surfaces for coarse horizon testing
- truth-leak risk in null/software renderer paths

## Findings

### Rendering pipeline interfaces

- `src/client/ui/viewer_shell.py` already builds `sky_view_surface` as a derived payload and passes only `sky_view_artifact` into the render contract.
- `src/client/render/render_model_adapter.py` already extends `RenderModel.extensions` with derived EARTH-4 sky data.
- `src/client/render/renderers/software_renderer.py` and `src/client/render/renderers/null_renderer.py` consume `RenderModel` only.
- Conclusion:
  - EARTH-5 can extend the same render-model extension surface with illumination artifacts without adding a renderer-side truth dependency.

### Existing lighting assumptions

- No canonical lighting or shadow artifact pipeline exists yet.
- The software renderer currently:
  - draws sky background, Milky Way band, sun disk, moon disk, and stars from `sky_view_artifact`
  - draws world primitives with unlit base-color fills
- The null renderer currently emits summaries only.
- Conclusion:
  - EARTH-5 needs a new derived illumination artifact and a renderer adapter path, not a mutation to authoritative world state.

### Sky-view outputs are already consumable

- `src/worldgen/earth/sky/sky_view_engine.py` already exposes:
  - `sun_direction`
  - `moon_direction`
  - `sky_colors_ref.sun_intensity_permille`
  - `extensions.sun_screen`
  - `extensions.moon_screen`
  - `extensions.sun_elevation_mdeg`
  - `extensions.moon_illumination_permille`
- Conclusion:
  - EARTH-5 can derive directional key/fill lighting entirely from EARTH-4 artifacts and EARTH-3 lunar phase behavior.

### Terrain elevation proxy access

- `src/worldgen/earth/earth_surface_generator.py` already stores deterministic macro elevation descriptors in `elevation_params_ref`, including:
  - `height_proxy`
  - `macro_relief_permille`
  - `ridge_bias_permille`
  - `coastal_bias_permille`
  - `continent_mask_permille`
- Earth surface artifacts already carry:
  - `tile_cell_key`
  - `planet_object_id`
  - `extensions.latitude_mdeg`
  - `extensions.longitude_mdeg`
- Conclusion:
  - EARTH-5 can build a bounded local horizon-shadow approximation from derived surface tile inputs without reading authoritative terrain truth directly.

### Truth-leak risk review

- No existing skybox or lighting code path was found that reads `truth_model`, `universe_state`, or process runtime directly inside renderer modules.
- The highest EARTH-5 risk surface is introducing:
  - direct terrain/runtime reads inside renderers
  - unbounded shadow sampling loops
  - wall-clock or backend randomness in view-artifact generation
- Conclusion:
  - EARTH-5 must keep illumination and shadow evaluation in deterministic derived helpers and pass only compact view artifacts to renderers.

## Compatibility Check

- EARTH-5 fits the existing observer/render/truth split.
- No authoritative world mutation is required for MVP illumination.
- The required additions are:
  - derived illumination/shadow schemas and registries
  - deterministic illumination and bounded horizon-shadow helpers
  - viewer/render integration through derived artifacts only
