Status: CANONICAL
Last Reviewed: 2026-02-17
Supersedes: none
Superseded By: none
Version: 1.0.0
Stability: provisional
Future Series: DOC-ARCHIVE
Replacement Target: legacy reference surface retained without current binding authority

# Cohort Model

## Scope
This document defines CIV-2 macro population cohorts and deterministic macro<->micro refinement mapping.

## Cohort Assembly
- Cohort is a Truth-side assembly (`assembly.cohort.*`) that represents many agents without simulating each individual.
- Required core fields:
  - `cohort_id`
  - `size`
  - `faction_id`
  - `territory_id`
  - `location_ref`
  - `demographic_tags` (stub)
  - `skill_distribution` (stub)
  - `refinement_state` (`macro|micro|mixed`)
  - `created_tick`

## Expand / Collapse Mapping
- `process.cohort_expand_to_micro` creates deterministic micro agents linked to parent cohort.
- `process.cohort_collapse_from_micro` aggregates child micro agents back into cohort state.
- Expand/collapse must preserve:
  - population conservation
  - faction/affiliation consistency
  - territory/location association
  - deterministic aggregation order

## Determinism Contract
- Mapping uses named deterministic stream material from stable inputs:
  - `cohort_id`
  - `simulation_tick`
  - `pack_lock_hash`
  - `mapping_policy_id`
- Created micro IDs are stable:
  - `agent.{H(cohort_id, slot_index)[:24]}`
- Ordering is stable for creation, aggregation, and eviction:
  - lexical by `cohort_id`, then deterministic slot index.

## ROI and Capsule Discipline
- ROI activation may trigger expansion under budget limits.
- Region collapse may trigger cohort collapse for linked micro agents.
- Partial expansion is allowed and deterministic:
  - expanded subset selected by stable policy ordering.
  - non-expanded remainder stays macro in same cohort.

## Epistemic Safety
- Refinement must not reveal hidden individual details outside law/epistemic allowances.
- Mapping policies can enforce anonymous micro projections for non-entitled observers.
- Expansion itself cannot be an epistemic side channel.

## Refusal Codes
- `refusal.civ.invalid_size`
- `refusal.civ.policy_missing`
- `refusal.civ.cohort_cross_shard_forbidden`
