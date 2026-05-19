Status: DERIVED
Last Reviewed: 2026-03-10
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# EARTH-2 Seasonal Climate Baseline

## Scope

EARTH-2 adds deterministic seasonal variation for macro Earth climate without introducing PDE weather, wall-clock dependence, or eager planet-wide evaluation.

## Climate Params

- `climate_params_id`: `climate.earth_stub_default`
- `year_length_ticks`: `3650`
- `axial_tilt_deg`: `23`
- `seasonal_amplitude`: `36`
- `update_interval_ticks`: `12`
- `default_max_tiles_per_update`: `32`

## Update Behavior

- Climate refresh executes only through `process.earth_climate_tick`.
- Orbit phase is fixed-point and canonical-tick driven through `earth_orbit_phase_from_params(...)`.
- Due buckets are computed deterministically from stable `geo_cell_key` identity.
- Batched/time-warp execution records `tick_window_start`, `tick_window_end`, and `tick_window_span`.
- Budget pressure degrades deterministically by preserving canonical bucket/key ordering and logging skipped tile ids.

## Derived Outputs

- `field.temperature.surface.<planet_object_id>`
- `field.daylight.surface.<planet_object_id>`
- `earth_climate_tile_overlays`
- derived climate band tags:
  - `climate.band.tropical`
  - `climate.band.temperate`
  - `climate.band.polar`
  - `climate.band.arid`

## Seasonal Behavior Summary

- Quarter-year and three-quarter-year samples produce opposite hemisphere daylight envelopes.
- Polar daylight reaches strong contrast across the sampled solstice window.
- Sampled Earth tiles shift temperature and daylight deterministically over the year while preserving stable tile identity and replay hashes.

## Readiness

- Ready for `EARTH-3` tide/shoreline proxy work.
- Ready for `MW-4` navigation/time-aware traversal integration.
- Overlay-safe for future higher-fidelity climate or Earth data packs because tile/object identity remains unchanged.
