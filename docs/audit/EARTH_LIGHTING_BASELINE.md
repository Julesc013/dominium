Status: DERIVED
Last Reviewed: 2026-03-10
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# EARTH-5 Illumination Baseline

## Scope

EARTH-5 adds deterministic observer-side illumination and a coarse bounded horizon-shadow stub for Earth traversal without truth mutation, wall-clock time, textures, or renderer-specific light models.

## Models

- `illum_model_id`: `illum.basic_diffuse_default`
- `shadow_model_id`: `shadow.horizon_stub_default`
- `cache_policy_id`: `cache.lighting.observer_tick_bucket`
- `lens_layer_ids`:
  - `layer.illumination`
  - `layer.shadow_factor`

## Shadow Sampling Policy

- Shadowing samples a fixed local terrain profile only.
- `sample_count`: `8`
- `step_distance_cells`: `1`
- sampling order is deterministic by `sample_index`
- `shadow_factor` is derived from:
  - sun elevation
  - bounded sampled horizon angle
  - a fixed soft-transition band from the shadow model row

## Renderer Integration

- `viewer_shell` derives `illumination_view_surface` from EARTH-4 `sky_view_artifact` plus derived observer surface context.
- `render_model_adapter` forwards `illumination_view_artifact` through `RenderModel.extensions`.
- `software_renderer` applies ambient, key, fill, and `shadow_factor` to primitives.
- `null_renderer` lawfully ignores the artifact and reports that choice in presentation metadata.
- Renderers consume the derived artifact only and do not read terrain truth or process runtime directly.

## Behavioral Summary

- Daylight produces nonzero ambient plus sun key light.
- Night suppresses sun contribution and allows moon fill light scaled by lunar phase.
- Low-sun cases can be locally occluded by high macro relief.
- Night remains fully shadowed without extra terrain sampling behavior.

## Stubbed vs Future

Implemented in EARTH-5:

- derived ambient / key / fill lighting
- coarse local horizon-shadow approximation
- renderer-portable illumination artifacts
- deterministic replay and cache keys

Deferred:

- PBR materials
- shadow maps
- terrain self-shadow mesh solving
- atmospheric scattering-driven light transport

## Readiness

- Ready for `EARTH-6` terrain collision and slope-response work.
- Ready for future hardware renderers because the lighting contract is artifact-based and renderer-agnostic.
- Ready for future shadow model upgrades because the registry/model surface is already split from renderer consumption.
