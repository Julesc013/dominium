Status: DERIVED
Last Reviewed: 2026-03-10
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# EARTH-3 Tide Proxy Baseline

## Scope

EARTH-3 adds a deterministic Moon-driven tide-height proxy for Earth surface tiles without introducing ocean PDEs, wall-clock dependence, or water-volume transport.

## Tide Params

- `tide_params_id`: `tide.earth_stub_default`
- `amplitude`: `240`
- `update_interval_ticks`: `6`
- `inland_damping_factor`: `180`
- `default_max_tiles_per_update`: `32`

## Phase Definitions

- `lunar_phase(tick)` is fixed-point and driven by `lunar_period_ticks`.
- `rotation_phase(tick)` is fixed-point and driven by `day_length_ticks`.
- The semidiurnal carrier is a deterministic piecewise cosine-like proxy over `2 * (rotation_phase - lunar_phase)`.

## Update Behavior

- Tide refresh executes only through `process.earth_tide_tick`.
- Due buckets are computed deterministically from stable `geo_cell_key` identity.
- Batched/time-warp execution records `tick_window_start`, `tick_window_end`, and `tick_window_span`.
- Budget pressure degrades deterministically by preserving canonical bucket/key ordering and logging skipped tile ids.

## Derived Outputs

- `field.tide_height_proxy.surface.<planet_object_id>`
- `earth_tide_tile_overlays`
- derived coupling descriptors:
  - `future.ocean.surface_height_bias`
  - `future.hazard.coastal_flood_bias`
  - `future.fluid.estuary_flow_bias`

## Seasonal / Daily Behavior Summary

- Sampled Earth coast and ocean tiles vary over the day window while preserving stable tile identity and replay hashes.
- Inland land tiles remain damped below ocean amplitudes under the same tick window.
- The replay tool reproduces identical overlay hashes and tide window hashes across repeated runs.

## Readiness

- Ready for `MW-4` navigation/time-aware sea-state presentation hooks.
- Ready for `EMB-1` tools that inspect or visualize coastline and estuary tide proxies.
- Overlay-safe for future higher-fidelity ocean, shoreline, or Luna-coupled packs because tile/object identity remains unchanged.
