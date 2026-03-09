Status: CANONICAL
Last Updated: 2026-03-10
Scope: EARTH-3 deterministic Moon-driven tide proxy for macro Earth surface tiles.

# Earth Tide Proxy Model

## 1) Purpose

EARTH-3 adds a deterministic, data-light tide proxy for Earth surface tiles.

The tide model exists to:

- make coastlines feel temporally alive at macro scale
- provide a lawful field substrate for future ocean and coastal systems
- remain replay-stable under batching and time warp

It does not simulate ocean transport, pressure solve, or shoreline fluid dynamics.

## 2) Activation Surface

- EARTH-3 applies to Earth surface tiles generated through the routed Earth surface generator.
- The canonical truth output is `field.tide_height_proxy`.
- Mutation occurs only through `process.earth_tide_tick`.

## 3) Inputs

For each tile, the tide proxy uses:

- canonical tick
- lunar phase `lunar_phase ∈ [0, 1)`
- Earth rotation phase `rotation_phase ∈ [0, 1)`
- latitude `phi`
- local surface class:
  - ocean
  - land
  - ice
- optional coastal proximity proxy from the Earth surface generator

Moon phase and Earth rotation phase are fixed-point only.
Wall-clock time is forbidden.

## 4) Phase Definitions

### 4.1 Lunar phase

`lunar_phase(tick)` is derived from:

- canonical tick
- `lunar_period_ticks`
- `epoch_offset_ticks`

using modular fixed-point arithmetic only.

### 4.2 Earth rotation phase

`rotation_phase(tick)` is derived from:

- canonical tick
- `day_length_ticks`

using modular fixed-point arithmetic only.

### 4.3 Carrier

The semidiurnal carrier is a deterministic cosine-like proxy:

- `carrier = g(rotation_phase - lunar_phase)`
- `g` is implemented as a fixed-point piecewise-linear approximation
- no floating trig is required or assumed
- platform-stable integer rounding is mandatory

## 5) Tide Height Proxy

For tile latitude `phi`, tide parameters row `P`, and carrier `carrier`:

`tide_height_proxy = amplitude * latitude_factor(phi) * surface_factor(tile) * carrier`

Where:

- `amplitude` is the canonical EARTH-3 macro tide amplitude
- `latitude_factor(phi)` is a deterministic bounded latitude weighting
- `surface_factor(tile)` is:
  - strongest for ocean tiles
  - boosted for coastal tiles
  - damped for inland land tiles

The result is a signed proxy field centered around zero.

## 6) Local Surface Factors

### 6.1 Ocean tiles

- receive the full ocean factor
- remain the canonical visual surface for the tide layer

### 6.2 Land tiles

- receive `inland_damping_factor`
- may still carry a small non-zero proxy for future estuary and flood coupling

### 6.3 Ice tiles

- use the land/inland damping path unless a future pack overrides the behavior

## 7) Update Policy

- Tide fields update every `update_interval_ticks`.
- Tile selection is bucketed deterministically by `geo_cell_key`.
- Ordering is deterministic:
  1. bucket id
  2. geo cell ordering
  3. tile object id
- Under compute pressure, only the budgeted subset updates.
- Degradation must be explicit and logged.

Replayed batched execution must match step-by-step canonical hashes.

## 8) Determinism Contract

- canonical tick only
- no wall-clock APIs
- no anonymous RNG
- no floating trig in authoritative tide evaluation
- no platform-dependent math branches
- tide update buckets are deterministic
- time warp is lawful because phase depends only on canonical tick

## 9) Output Surface

EARTH-3 writes:

- `field.tide_height_proxy`

EARTH-3 may also persist derived overlay rows for:

- tile tide value
- lunar phase
- rotation phase
- due bucket membership

These derived rows do not replace tile identity.

## 10) UX Surface

EARTH-3 exposes:

- `layer.tide_height_proxy` for map/minimap/lens use
- tide values through field inspection panels when lawful

No shoreline renderer or water mesh animation is required for MVP.

## 11) Future Coupling Hooks

This proxy is the canonical hook surface for future:

- ocean surface height bias
- coastal flooding hazard
- estuary flow direction bias

Those systems must layer on top of EARTH-3.
EARTH-3 itself does not solve volume transport or ocean PDEs.

## 12) Non-Goals

- no ocean PDE solver
- no real coastline data
- no water mass conservation model
- no shoreline erosion
- no real-time fluid transport
