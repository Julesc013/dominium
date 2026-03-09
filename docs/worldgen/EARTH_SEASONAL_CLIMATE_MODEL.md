Status: CANONICAL
Last Reviewed: 2026-03-10
Supersedes: none
Superseded By: none
Version: 1.0.0
Compatibility: Bound to `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `docs/worldgen/EARTH_PROCEDURAL_CONSTITUTION.md`, `docs/worldgen/PLANET_SURFACE_MACRO_MODEL.md`, and EARTH-2 runtime/proof tooling.

# Earth Seasonal Climate Model

This document freezes the EARTH-2 seasonal climate proxy contract for Dominium v0.0.0.

## Relevant Invariants

- `docs/canon/constitution_v1.md` `A1` Determinism is primary
- `docs/canon/constitution_v1.md` `A2` Process-only mutation
- `docs/canon/constitution_v1.md` `A6` Provenance is mandatory
- `docs/canon/constitution_v1.md` `A10` Explicit degradation and refusal
- `docs/canon/constitution_v1.md` `E2` Deterministic ordering
- `docs/canon/constitution_v1.md` `E6` Replay equivalence
- `docs/time/TEMPORAL_SEMANTICS_CONSTITUTION.md`
- `docs/fields/FIELD_LAYER_MODEL.md`

## 1. Scope

EARTH-2 adds deterministic seasonal variation for Earth surface macro climate.

It provides:

- Earth orbit phase from canonical tick
- deterministic seasonal daylight variation
- deterministic seasonal temperature variation
- bounded climate-field refresh over already-generated Earth tiles
- derived climate band tags with small seasonal boundary motion

It does not provide:

- atmospheric circulation
- cloud/rain PDEs
- evaporation cycles
- continuous fluid or thermal simulation

## 2. Seasonal Phase

EARTH-2 defines `orbit_phase` as a fixed-point fraction derived from:

- `canonical_tick`
- `year_length_ticks`
- optional `epoch_offset_ticks`

Rules:

- `orbit_phase` is computed with integer arithmetic only
- the phase range is `[0, 1)` represented by deterministic fixed-point units
- identical `(canonical_tick, year_length_ticks, epoch_offset_ticks)` inputs must produce identical phase outputs
- wall-clock time is forbidden

## 3. Insolation Proxy

For Earth surface tiles, insolation is a deterministic proxy of:

- tile latitude
- Earth axial tilt
- orbit phase

EARTH-2 may use deterministic triangle-wave and lookup-style approximations.

Rules:

- no floating trig is required or assumed
- any approximation must be platform-stable and integer-rounded
- the proxy must increase/decrease seasonally in the correct hemisphere direction

## 4. Temperature Proxy

Temperature proxy is computed as:

- a latitude-driven base band
- plus a seasonal delta derived from insolation/daylight
- minus an altitude lapse term from tile elevation proxy

Interpretation rules:

- `base_temp_equator` and `base_temp_pole` anchor the macro climate envelope
- `seasonal_amplitude` bounds the seasonal shift
- `lapse_rate_per_km` applies to coarse elevation proxy only
- temperature is a macro field proxy, not a thermodynamic equilibrium solve

## 5. Daylight Proxy

Daylight proxy must vary with:

- latitude
- axial tilt
- orbit phase

Rules:

- polar regions may resolve to near-zero or near-max daylight at opposite seasons
- equatorial daylight remains comparatively stable
- the daylight proxy is updated through the same lawful climate update path as temperature

## 6. Update Policy

EARTH-2 climate updates are process-driven only.

Required rules:

- update cadence is declared by `update_interval_ticks`
- tiles are assigned deterministic update buckets from stable GEO cell identity
- a climate process evaluates all buckets that became due since the last climate tick
- if due work exceeds budget, the selected subset must be:
  - deterministic
  - explicitly logged as degraded
  - ordered by canonical tile key ordering

No hidden background update loop is allowed.

## 7. Derived Climate Band Tags

EARTH-2 derives stable seasonal band tags from updated climate proxies.

Required classification surface:

- `climate.band.tropical`
- `climate.band.temperate`
- `climate.band.polar`
- `climate.band.arid`

Rules:

- tags are derived from current climate proxy values and coarse continentality/hydrology heuristics
- seasonal movement must be small and plausible, not abrupt
- the tags are derived overlays, not new GEO identities

## 8. Time Warp and Batching

EARTH-2 must remain equivalent under:

- ordinary tick stepping
- tick batching
- lawful time warp policies

Rules:

- the climate result at canonical tick `T` depends only on deterministic inputs visible at `T`
- skipped intermediate ticks may affect which buckets are due, but not the final value formula
- replayed batched execution must match step-by-step canonical hashes for the same authoritative tick sequence

## 9. Boundedness

EARTH-2 climate refresh must remain bounded.

Rules:

- only already-generated Earth surface tiles are candidates for update
- no whole-planet eager tile generation is permitted
- update ordering is canonical by:
  - bucket id
  - `geo_cell_key`
  - `tile_object_id`

## 10. Upgrade Path

Future Earth climate work may add:

- finer precipitation proxies
- ocean moderation refinements
- winds or tides
- biome overlays informed by more domains

Those additions must:

- preserve deterministic phase law
- preserve process-only mutation
- preserve stable tile identity and field binding
