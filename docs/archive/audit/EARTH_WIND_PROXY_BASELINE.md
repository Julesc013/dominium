Status: DERIVED
Last Reviewed: 2026-03-10
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# EARTH Wind Proxy Baseline

## Scope

- EARTH-7 adds a deterministic macro `field.wind_vector` over Earth surface tiles.
- Mutation occurs only through `process.earth_wind_tick`.
- The model remains a proxy surface for future weather, cloud drift, acoustics, sailing, flight, and POLL advection.

## Wind Parameters

- canonical params id: `wind.earth_stub_default`
- canonical update interval: `8` ticks
- canonical perturbation policy: `noise.none`
- canonical bands:
  - `wind.band.hadley`
  - `wind.band.ferrel`
  - `wind.band.polar`

## Update Behavior

- tile buckets are derived deterministically from stable `geo_cell_key`
- ordering is:
  1. bucket id
  2. geo cell ordering
  3. tile object id
- under budget pressure, EARTH-7 degrades by deferring tiles explicitly instead of changing evaluation order

## POLL Coupling

- `future.poll.advection_bias` is populated as a deterministic hook surface
- POLL dispersion may bias diffusion using `field.wind_vector` when policy allows
- no atmospheric circulation or weather-cell transport is introduced

## Readiness

- ready for EARTH-8 water visuals
- ready for future cloud drift and atmospheric presentation layers
- ready for future sound attenuation and sailing/flight coupling
