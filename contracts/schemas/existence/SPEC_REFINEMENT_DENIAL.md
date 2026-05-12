# SPEC_REFINEMENT_DENIAL (EXIST1)

Schema ID: REFINEMENT_DENIAL
Schema Version: 1.0.0
Status: binding.
Scope: deterministic denial/deferral semantics for refinement.

## Purpose
Define explicit outcomes and refusal reasons when refinement cannot proceed.

## Outcomes (Closed Set)
- REFINE_ACCEPT
- REFINE_DEFER (must include next_due_tick)
- REFINE_DEGRADE (refine to lower tier)
- REFINE_REFUSE (must include refusal code)

## Refusal Codes (Canonical)
- LAW_FORBIDS_REFINEMENT
- BUDGET_INSUFFICIENT
- SUBJECT_NOT_REFINABLE
- ARCHIVED_NO_FORK
- VISIBILITY_PINNED_CONFLICT

## Determinism Rules
- Outcome must be deterministic given identical inputs.
- Deferral tick must be deterministic and auditable.
- Refusal codes must be explainable and stable.

## Audit Requirements
Every denial/deferral must record:
- subject_id
- requested_tier
- decision outcome
- refusal code (if REFUSE)
- next_due_tick (if DEFER)
- law decision summary
- budget summary

## References
- `schema/existence/SPEC_REFINEMENT_CONTRACTS.md`
