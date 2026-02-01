Status: CANONICAL
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# CIV0 Population Genesis (Cohorts, Households, Migration)

This document describes the CIV0 population substrate: deterministic cohorts,
bounded households, and migration flows. It is event-driven and scales without
global iteration.

## Core components

- Cohorts (`schema/civ/SPEC_POPULATION_COHORTS.md`)
  - Stable cohort_id derived from cohort_key.
  - Fixed bucket distributions (age/sex/health).
  - next_due_tick required for macro stepping.
- Households (`schema/civ/SPEC_HOUSEHOLDS.md`)
  - Bounded, ordered membership lists.
  - Used to bound eligibility and authority queries.
- Migration flows (`schema/civ/SPEC_MIGRATION.md`)
  - Deterministic flow records with arrival_act scheduling.

## Event-driven stepping

Population updates are processed only when due:

- Cohort updates are scheduled via next_due_tick.
- Migration flows are applied at arrival_act.
- No subsystem may scan all cohorts or households each tick.

This aligns with `docs/specs/SPEC_EVENT_DRIVEN_STEPPING.md` and the macro due
scheduler used by CIV0a survival.

## Determinism and ordering

- Cohort registries are sorted by cohort_id.
- Household members are kept in deterministic order.
- Migration flow application is deterministic and batch-vs-step equivalent.

Determinism tests are listed in `docs/ci/DETERMINISM_TEST_MATRIX.md`.

## Integration points

- CIV0a survival needs: cohorts reference CIV0a needs via needs_state_ref.
- LIFE2/LIFE3: births and deaths adjust cohort counts deterministically.
- Interest sets + fidelity: micro persons refine from cohorts only when interested.
- Epistemic UI: population visibility is reported via projections, not omniscient.

## Prohibitions

- No global iteration over cohorts/households.
- No fabricated population growth or migration.
- No stochastic wandering or OS time usage.

## CI enforcement

The following IDs in `docs/CI_ENFORCEMENT_MATRIX.md` cover CIV0:

- CIV0-NOGLOB-001: no global iteration for population.
- CIV0-NEXTDUE-001: next_due_tick required for cohorts.
- CIV0-DET-001: batch vs step equivalence.
