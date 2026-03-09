Status: DERIVED
Last Reviewed: 2026-03-10
Supersedes: none
Superseded By: none
Version: 1.0.0
Compatibility: Informative retro audit for EARTH-2 against MW-3, EARTH-0, EARTH-1, FIELD-1, and TEMP-0/TEMP-2 surfaces.

# EARTH-2 Retro Audit

## Scope

This audit reviews the current Earth seasonal/climate-adjacent surfaces before EARTH-2 introduces deterministic seasonal field refresh.

## Current Temperature/Daylight Initialization

- `src/worldgen/mw/mw_surface_refiner_l3.py`
  - computes `season_phase_permille`, `daylight_value`, `insolation_value`, and `temperature_value` during tile refinement
  - emits `field.temperature.surface.<planet_id>` and `field.daylight.surface.<planet_id>` field layers with `update_policy_id = field.profile_defined`
  - initializes tile-local `field.temperature` and `field.daylight` cells only for requested surface tiles
- `src/worldgen/earth/earth_surface_generator.py`
  - consumes the already-computed base temperature/daylight/insolation inputs
  - adjusts biome/material/elevation output but does not own an ongoing climate update loop

Conclusion:

- Earth already has deterministic per-tile seasonal initialization at refinement time
- Earth does not yet have a lawful post-worldgen seasonal refresh path over canonical time

## TEMP Mapping Usage

- `docs/time/TEMPORAL_SEMANTICS_CONSTITUTION.md`
  - canonical truth remains ordered by `time.canonical_tick`
  - batching/substepping are derived execution concerns and must not reorder canonical ticks
- `src/time/time_mapping_engine.py`
  - exposes deterministic canonical-domain mapping helpers
  - confirms `time.canonical_tick` is the authoritative anchor domain
- `tools/xstack/sessionx/process_runtime.py`
  - already advances authoritative time through process execution and exposes `current_tick` to process handlers

Conclusion:

- EARTH-2 should derive seasonal phase from canonical tick only
- no wall-clock or implicit civil-time path is needed or allowed

## Insolation Helper Availability

- `src/worldgen/mw/insolation_proxy.py`
  - already provides integer-only helpers for:
    - `orbital_period_proxy_ticks`
    - `season_phase_permille`
    - `daylight_proxy_permille`
    - `insolation_proxy_permille`
  - uses deterministic triangle-wave approximations only

Conclusion:

- EARTH-2 can reuse the existing integer-only daylight/insolation approach
- Earth-specific phase and climate policy should still be isolated behind Earth-owned climate helpers rather than spread through generic MW code

## Deterministic Field Update Schedule

- `docs/fields/FIELD_LAYER_MODEL.md`
  - field mutation is process-driven only
  - budget degradation must be deterministic and explicit
- `tools/xstack/sessionx/process_runtime.py`
  - `process.field_update` already provides lawful deterministic field writes
  - `process.field_tick` supports deterministic budgeted field evaluation but is generic and not Earth-season aware
- current Earth field layers use `field.profile_defined`, which allows process-driven updates

Conclusion:

- EARTH-2 should add an explicit Earth climate process that computes deterministic update requests and routes them through the existing field-update path
- the update policy can remain `field.profile_defined` while the scheduling logic lives in an Earth-owned process/runtime helper

## Surface/Topology Compatibility

- `src/worldgen/mw/mw_surface_refiner_l3.py`
  - surface tiles already carry deterministic:
    - `latitude_mdeg`
    - `longitude_mdeg`
    - `orbital_period_ticks`
    - `season_phase_permille`
    - `insolation_permille`
    - `height_proxy`
- GEO surface ancestry and deterministic tile ordering are already available through tile `geo_cell_key`

Conclusion:

- Earth seasonal updates can operate over already-generated surface tiles only
- the authoritative iteration order should be tile `geo_cell_key` order, with bucket selection derived from stable cell hashes

## Gap Summary

Required EARTH-2 additions:

- Earth-specific climate parameter registry and schema
- deterministic Earth orbit-phase helper bound to canonical tick
- bounded climate field engine for existing Earth surface tiles
- process-driven seasonal refresh path with deterministic bucket selection and degrade logging
- replay/test surfaces proving:
  - phase determinism
  - seasonal temperature variation
  - polar daylight variation
  - bucketed update stability

Explicit non-goals reaffirmed:

- no PDE atmosphere or circulation model
- no wall-clock time
- no real geography data
- no direct UI/tool mutation of field cells
