Status: CANONICAL
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# AI Budget Model (AI0)

Status: FROZEN.  
Scope: AI budget classes and fairness enforcement.

## Budget Classes

AI budgets are meta-law constraints applied to intent production:
- `intent_rate_budget`
- `planning_budget`
- `observation_budget`
- `cpu_budget` (embedded/sidecar only)

## Rules

- Budgets are enforced via meta-law.
- Budget exhaustion produces explicit refusals.
- No AI may exceed player-equivalent budgets without explicit configuration.
- Budgets are visible in compat_report (extensions payload).

## Visibility & Refusals

When a budget is exhausted:
- compatibility_mode becomes `refuse`.
- refusal code is `REFUSE_BUDGET_EXCEEDED`.
- mitigation hints must explain which budget is exhausted.

## Notes

Budgets do not grant privileges; they only cap activity.