Status: CANONICAL
Last Reviewed: 2026-03-10
Supersedes: none
Superseded By: none

# Earth Wind Proxy Model

## 1) Purpose

EARTH-7 adds a deterministic macro wind-vector proxy for Earth surface tiles.

The model exists to:

- make the Earth surface feel seasonally alive at macro scale
- provide a lawful field surface for later cloud drift, weather, acoustics, sailing, and flight
- provide an optional deterministic advection bias for POLL dispersion

It does not solve atmospheric circulation, pressure PDEs, or weather-cell dynamics.

## 2) Activation Surface

- EARTH-7 applies to Earth surface tiles generated through the routed Earth surface generator.
- The canonical truth output is `field.wind_vector`.
- Mutation occurs only through `process.earth_wind_tick`.

## 3) Field Definition

- `field.wind_vector` is stored at tile resolution.
- The value is a deterministic horizontal vector in the local tangent plane:
  - `x`: east-west component
  - `y`: north-south component
  - `z`: always `0` in MVP

The field is authoritative truth only after process commit.
UI and renderers consume perceived or derived views only.

## 4) Inputs

For each tile, the wind proxy uses:

- canonical tick
- latitude `phi`
- season phase from the EARTH-2 orbit-phase model
- deterministic band priors
- optional deterministic perturbation policy

Wall-clock time is forbidden.
Anonymous randomness is forbidden.

## 5) Band Model

### 5.1 Latitude bands

The wind model uses three deterministic circulation bands:

- `wind.band.hadley`
- `wind.band.ferrel`
- `wind.band.polar`

Band assignment is based on effective latitude after a small seasonal shift.

### 5.2 Prevailing directions

MVP prevailing directions are coarse proxies only:

- Hadley band:
  - easterly zonal component
  - weak equatorward meridional component
- Ferrel band:
  - westerly zonal component
  - weak poleward meridional component
- Polar band:
  - easterly zonal component
  - weak equatorward meridional component

These are profile-driven approximations, not a meteorological solver.

### 5.3 Seasonal shift

Band boundaries shift by a small deterministic amount derived from season phase.

The shift:

- depends only on canonical tick and profile parameters
- is bounded
- must not cause random or discontinuous band flips outside lawful threshold crossings

## 6) Noise Policy

EARTH-7 supports policy-controlled perturbation:

- `noise.none`
- `noise.hash_tile_bucket`

`noise.none` is the canonical MVP default.

If perturbation is enabled:

- it must be deterministic
- it must derive only from stable tile identity and tick bucket
- it must remain bounded by `noise_magnitude`

Named RNG is not required for EARTH-7 because the MVP perturbation may be implemented as deterministic hash-noise.

## 7) Update Policy

- Wind fields update every `update_interval_ticks`.
- Tile refresh is bucketed deterministically by stable `geo_cell_key`.
- Ordering is deterministic:
  1. bucket id
  2. geo cell ordering
  3. tile object id
- Under compute pressure, only the budgeted subset updates.
- Degradation must be explicit and logged.

Replayed batched execution must match step-by-step canonical hashes.

## 8) POLL Coupling

If a POLL dispersion policy enables wind modifier:

- `field.wind_vector` may bias deterministic neighbor diffusion terms
- the bias must remain bounded
- the bias must not change neighbor ordering or introduce random routing

EARTH-7 declares this hook surface only.
It does not implement weather-cell transport or atmospheric chemistry.

## 9) Determinism Contract

- canonical tick only
- no wall-clock APIs
- no anonymous RNG
- no floating atmospheric solver
- deterministic bucket scheduling
- deterministic tie-breaks by stable cell ordering
- time warp is lawful because wind evaluation depends only on canonical tick buckets and stable tile identity

## 10) Output Surface

EARTH-7 writes:

- `field.wind_vector`

EARTH-7 may also persist derived overlay rows for:

- wind band id
- wind speed
- band shift
- tick bucket

These overlays must not replace tile identity.

## 11) UX Surface

EARTH-7 exposes:

- `layer.wind_vector` for map and inspection use

Derived wind overlays are profile and instrumentation gated.
No omniscient weather UI bypass is allowed.

## 12) Future Coupling Hooks

This proxy is the canonical hook surface for future:

- sky and cloud drift
- sound attenuation and direction bias
- sail or flight control modifiers
- richer weather and cloud systems

Reserved hook identifiers are:

- `future.poll.advection_bias`
- `future.sky.cloud_drift_bias`
- `future.sound.wind_attenuation_bias`

These hooks are declarative only in MVP.

## 13) Non-Goals

- no atmospheric PDE solver
- no storm cell simulation
- no humidity transport
- no cloud rendering system
- no wall-clock weather updates
