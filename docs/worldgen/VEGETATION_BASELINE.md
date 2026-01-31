# Vegetation Baseline (VEGETATION5)

Status: binding for T5 baseline.  
Scope: deterministic vegetation placement with slow, event-driven growth and decay.

## What vegetation is
- Plants are assemblies constrained by terrain, climate, weather, and geology fields.
- Vegetation truth is sampled from providers; meshes are view-only and disposable.
- Two phases are supported:
  - Static placement (initial validation, no time evolution).
  - Regenerative placement (slow, event-driven growth/death).

## Data model (authoritative)
- Species descriptors:
  - `species_id`, `preferred_biomes[]`, `climate_tolerance`
  - `growth_rate`, `max_size`, `lifespan`, `material_traits`
  - `maturity` (BOUNDED or STRUCTURAL)
- Instance records:
  - `species_id`, `location_ref`, `size`, `health`, `age`, `provenance`
- All numeric fields are unit-tagged per `docs/architecture/UNIT_SYSTEM_POLICY.md`.

## Processes (event-driven only)
- Growth, death, and regeneration are scheduled macro events, not per-tick loops.
- Determinism uses named RNG streams:
  - `noise.stream.<domain>.vegetation.<purpose>`
- No background mutation outside Process execution.

## What is NOT included yet
- No animals, grazing, or AI agents.
- No farming, planting, or harvesting loops.
- No seed dispersal or nutrient depletion feedback.

## Collapse/expand compatibility
- Macro capsules store:
  - Coverage averages per domain/tile
  - Size and age histograms per species
  - RNG cursor continuity per species stream
- Expand deterministically reproduces placement and growth.

## Maturity labels
- vegetation.static_placement: **BOUNDED**
- vegetation.regeneration: **BOUNDED**
- vegetation.material_traits: **STRUCTURAL** (reserved for later harvesting)

## See also
- `docs/architecture/PROCESS_ONLY_MUTATION.md`
- `docs/architecture/SCALING_MODEL.md`
- `docs/architecture/COLLAPSE_EXPAND_CONTRACT.md`
