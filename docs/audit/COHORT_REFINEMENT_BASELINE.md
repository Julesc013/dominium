Status: DERIVED
Last Reviewed: 2026-02-17
Version: 1.0.0
Scope: CIV-2/4 cohort refinement baseline

# Cohort Refinement Baseline

## Cohort Fields and Policies
- Cohort assembly fields:
  - `cohort_id`, `size`, `faction_id`, `territory_id`, `location_ref`
  - `demographic_tags`, `skill_distribution`
  - `refinement_state`, `created_tick`
- Mapping policy registry:
  - `cohort.map.default`
  - `cohort.map.rank_strict`

## Expand / Collapse Rules
- Expand path:
  - `process.cohort_expand_to_micro`
  - deterministic child IDs from `(cohort_id, slot_index)`
  - parent linkage through `agent.parent_cohort_id`
- Collapse path:
  - `process.cohort_collapse_from_micro`
  - deterministic aggregation over sorted micro rows
  - cohort size reflects collapsed + unexpanded remainder
- Partial expansion:
  - deterministic budgeted selection
  - remaining population preserved in macro cohort

## ROI Integration
- Region management can trigger deterministic cohort expansion/collapse.
- Deterministic priority ordering:
  - `(cohort_id, faction_id, -size, quantized_distance)`
- Budget-limited outcomes emit deterministic run metadata in process results.

## Epistemic Guarantees
- Cohort refinement integrates with LOD epistemic invariance.
- Mapping policy can enforce anonymous micro entities for non-entitled observers.
- Expand/collapse does not grant hidden-state channels by itself.

## Extension Points
- CIV-3: order systems over cohorts and micro agents.
- CIV-4: deterministic demography/procreation transitions.
- Macro population solvers and shard-aware migration strategies.

