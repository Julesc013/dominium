# SPEC TRAVEL COST (TRAVEL1)

Status: draft.
Version: 1.0
Scope: explicit, deterministic travel costs.

## Cost Components
Edges may declare one or more costs:
- time_cost (ACT)
- energy_cost
- fuel_cost
- bandwidth_cost
- economic_cost (ledger transfer)
- risk_cost (deterministic outcome distribution)

## Payment Semantics
Costs may be:
- prepaid
- escrowed
- settled on arrival

Refunds on cancellation must be deterministic.

## Determinism Rules
- Cost evaluation is pure and stable given inputs.
- No runtime benchmarking or wall-clock dependence.
- Costs cannot fabricate resources.

## Integration Points
- Economy and ledger tasks (ADOPT4)
- Logistics capacity (TRAVEL1 capacity)
- Law gating and capability checks
