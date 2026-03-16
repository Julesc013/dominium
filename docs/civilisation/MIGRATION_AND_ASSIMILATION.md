Status: CANONICAL
Last Reviewed: 2026-02-26
Supersedes: none
Superseded By: none
Version: 1.0.0
Stability: provisional
Future Series: DOC-ARCHIVE
Replacement Target: legacy reference surface retained without current binding authority

# Migration And Assimilation

## Migration
- Migration is executed through deterministic process mutation:
  - `process.cohort_relocate`
- Inputs:
  - `cohort_id`
  - destination (`site_id` or `region_id`)
  - `migration_model_id`
- Travel time is model-driven:
  - instant migration is allowed by model
  - delayed migration stores in-transit metadata and applies location update only on arrival tick

## Deterministic Travel
- Travel delay uses deterministic distance-band policy data.
- Canonical delayed form is `ticks = distance_band_table[band]`.
- No runtime pathfinding randomness is introduced.
- Cross-shard migration follows SRZ ownership and deterministic refusal paths.
- `order.migrate` resolves through `process.cohort_relocate` and uses the same model tables.

## Assimilation
- Assimilation remains order/process-driven:
  - `order.assimilate`
  - `process.affiliation_join`
  - `process.affiliation_change_micro` (stub-safe)
- CIV-4 does not add combat/trade/economy effects to assimilation.

## Law And Policy Gating
- Migration and assimilation require explicit law/entitlement allowances.
- Missing or forbidden policy/model inputs produce deterministic refusal codes.
