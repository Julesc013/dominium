# SPEC TRAVEL DENIAL (TRAVEL0)

Status: draft.
Version: 1.0
Scope: deterministic denial and deferral semantics.

## Denial Outcomes
- TRAVEL_ACCEPT
- TRAVEL_DEFER (with next_due_tick)
- TRAVEL_REFUSE (with refusal_code)

## Refusal Codes (canonical)
- NO_PATH
- DOMAIN_FORBIDDEN
- LAW_FORBIDDEN
- CAPABILITY_MISSING
- BUDGET_INSUFFICIENT
- DESTINATION_NOT_VISITABLE

## Determinism Rules
- Refusal must be stable and explainable.
- Uncertainty yields refusal or deferral.
- No optimistic acceptance under ambiguity.

## Integration Points
- DOMAIN4 visitability pipeline
- Law kernel gating and capability checks
- EXEC budgets and scheduling
