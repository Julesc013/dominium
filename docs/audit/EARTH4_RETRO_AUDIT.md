Status: DERIVED
Last Reviewed: 2026-03-10
Supersedes: none
Superseded By: none

# EARTH-4 Retro Audit

## Audit Targets

- EARTH-2 daylight and seasonal phase helpers
- EARTH-3 lunar/rotation phase helpers
- MW-0 galaxy priors and deterministic stream rules
- UX-0 viewer shell and RenderModel adapter surfaces
- Existing renderer paths and lens/view artifact contracts

## Findings

### Daylight proxy and seasonal phase surface

- `src/worldgen/earth/season_phase_engine.py` already provides:
  - `earth_orbit_phase_from_params`
  - `axial_tilt_mdeg`
  - `solar_declination_mdeg`
- `src/worldgen/earth/climate_field_engine.py` already uses those helpers to derive deterministic Earth latitude/daylight behavior.
- Conclusion:
  - EARTH-4 can reuse the canonical orbit/tilt phase surface instead of inventing a parallel season clock.

### MW priors and deterministic stream discipline

- `data/registries/realism_profile_registry.json` already binds Earth-capable realism profiles to:
  - `galaxy_priors_ref`
  - `surface_priors_ref`
- `data/registries/galaxy_priors_registry.json` already provides bounded Milky Way priors:
  - disk/bulge scale
  - arm count
  - density and metallicity tendencies
- MW series doctrine already forbids catalog dependence and anonymous RNG.
- Conclusion:
  - EARTH-4 starfield generation can remain procedural, bounded, and seeded from canonical named hash streams without introducing catalog data.

### Camera/lens/view artifact pipeline

- `src/client/ui/viewer_shell.py` already states:
  - `consumes_perceived_model_only`
  - `consumes_projection_and_lens_artifacts`
  - explicit forbidden truth inputs
- `src/client/render/render_model_adapter.py` builds `RenderModel` strictly from `PerceivedModel` plus derived overlay surfaces.
- `tools/xstack/sessionx/observation.py` already derives lawful `camera_viewpoint` and `time_state` into perception.
- Conclusion:
  - EARTH-4 should produce a derived sky-view artifact inside the viewer/render path, not by mutating TruthModel.

### Existing render backends

- `src/client/render/renderers/software_renderer.py` and `src/client/render/renderers/null_renderer.py` already consume only `RenderModel`.
- No existing skybox or sky dome implementation was found.
- No existing renderer path reads `truth_model` directly for sky or celestial background composition.
- Conclusion:
  - EARTH-4 can extend `RenderModel.extensions` with a bounded sky artifact and keep renderer truth-separation intact.

### Truth-leak risk review

- Viewer shell, map views, and inspection panels already have RepoX/AuditX guards against direct truth access.
- The highest EARTH-4 risk surface is any shortcut that:
  - reaches into runtime state from renderer code
  - seeds star generation from wall-clock or backend randomness
  - bypasses lens/profile gating for debug galactic-plane overlays
- Conclusion:
  - EARTH-4 must keep astronomy, starfield, and debug overlay logic in deterministic derived helpers and pass only compact derived payloads to UI/renderers.

## Compatibility Check

- EARTH-4 fits current contracts without changing:
  - authoritative world mutation rules
  - Earth tile identity
  - GEO partitioning
  - MW base galaxy generation
- The required additions are:
  - derived sky/starfield schemas and registries
  - deterministic sky runtime helpers
  - viewer/render integration through derived artifacts only
