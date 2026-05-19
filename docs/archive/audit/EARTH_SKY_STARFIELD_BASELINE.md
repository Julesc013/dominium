Status: DERIVED
Last Reviewed: 2026-03-10
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# EARTH-4 Sky And Starfield Baseline

## Scope

EARTH-4 adds a deterministic, data-light sky dome and procedural starfield stub for Earth-facing observation without truth mutation, wall-clock time, textures, or catalog dependency.

## Model Parameters

- `sky_model_id`: `sky.gradient_stub_default`
- `starfield_policy_id`: `stars.mvp_default`
- `milkyway_band_policy_id`: `mwband.mvp_stub`
- `tick_bucket_size`: `6`
- `max_stars`: `2048`
- `cache_policy_id`: `cache.sky.observer_tick_bucket`

## Determinism And Cache Keys

- Sun and moon direction proxies depend only on canonical tick, observer latitude/longitude, and registry-backed climate/tide params.
- The starfield named stream is `rng.view.sky.starfield`.
- Starfield seed inputs are:
  - `universe_seed`
  - `generator_version_id`
  - `realism_profile_id`
  - `observer_cell_key`
  - `tick_bucket`
- Derived cache keys include:
  - observer cell key hash
  - lens profile id
  - camera orientation
  - sky model / starfield / Milky Way policy ids

## Behavioral Summary

- Day uses a blue gradient with nonzero sun intensity and zero visible stars.
- Twilight uses warm horizon blending with reduced sun intensity and partial star visibility.
- Night resolves to zero sun intensity, visible bounded stars, and a bounded Milky Way band.
- The software renderer consumes `sky_view_artifact` through the RenderModel extension surface only.

## Stubbed vs Future

Implemented in EARTH-4:

- gradient sky colors
- sun disk
- moon direction plus phase illumination proxy
- bounded procedural stars
- bounded coarse Milky Way band

Deferred:

- Rayleigh/Mie scattering
- catalog-backed overlays
- higher-fidelity lunar rendering
- clouds, haze, aurora, and shadows

## Readiness

- Ready for `EARTH-5` illumination and shadow proxies.
- Ready for future catalog overlays because the MVP starfield remains procedural and derived-only.
- Ready for future hardware renderers because the artifact contract is renderer-agnostic and texture-free.
