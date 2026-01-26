# Budget Policy (BUDGET0)

Status: binding.
Scope: admission control policies and deterministic refusal under load.

## Purpose
Budgets are policy-layer limits. They are not systems and do not alter
simulation semantics. They only gate admission and scheduling.

## BudgetPolicy definition
- BudgetPolicy is a policy layer (data-defined).
- Budgets are evaluated deterministically at admission time.
- Exceeding a budget MUST emit a refusal and audit event.

## Allowed budget types (non-exhaustive)
- planning budget
- refinement budget
- snapshot budget
- network graph budget

## Required behavior
- Exceeding budget => explicit refusal (REFUSE_BUDGET_EXCEEDED).
- Emit deterministic events for budget refusal.
- Never degrade determinism or change outcomes silently.
- No silent performance collapse.

## See also
- `docs/arch/REFUSAL_SEMANTICS.md`
- `docs/arch/ARCH0_CONSTITUTION.md`
