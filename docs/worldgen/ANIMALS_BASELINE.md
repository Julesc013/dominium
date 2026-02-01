Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Animals Baseline (ANIMALS6)

Status: binding for T6 baseline.  
Scope: deterministic animal agents with coarse, event-driven needs and lifecycle.

## What animals are
- Animals are agents constrained by terrain, vegetation, climate, and weather fields.
- Agents produce intents without privilege; all actions are law-gated (AI0).
- Needs are evaluated at coarse intervals to preserve constant-cost scaling.

## Data model (authoritative)
- Species descriptors:
  - `species_id`, `preferred_biomes[]`, `climate_tolerance`
  - `movement_mode`, `diet`, `metabolism`, `reproduction`
  - `lifespan`, `size_class`, `maturity`
- Agent instances:
  - `species_id`, `location_ref`, `energy`, `health`, `age`, `current_need`, `provenance`
- All numeric fields are unit-tagged per `docs/architecture/UNIT_SYSTEM_POLICY.md`.

## Processes (event-driven only)
- Movement, feeding, reproduction, and death are scheduled macro events, not per-tick loops.
- Determinism uses named RNG streams:
  - `noise.stream.<domain>.animal.<purpose>`
- Feeding emits deterministic vegetation deltas; vegetation regrowth is handled by T5 processes.

## What is NOT included yet
- No economy, ownership, or domestication.
- No combat systems or hunting rewards.
- No per-tick AI loops or global pathfinding.

## Collapse/expand compatibility
- Macro capsules store:
  - Population counts per species
  - Age and energy histograms
  - RNG cursor continuity per species stream
- Expand deterministically reproduces local agent distributions.

## Maturity labels
- animal.needs_model: **BOUNDED**
- animal.population: **BOUNDED**
- animal.movement: **BOUNDED**
- animal.reproduction: **BOUNDED**
- animal.species_traits: **STRUCTURAL** (stable tags, extensible traits)

## See also
- `docs/architecture/AI_INTENT_MODEL.md`
- `docs/architecture/PROCESS_ONLY_MUTATION.md`
- `docs/architecture/SCALING_MODEL.md`
- `docs/architecture/COLLAPSE_EXPAND_CONTRACT.md`