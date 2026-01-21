# SPEC TRAVEL CAPACITY (TRAVEL1)

Status: draft.
Version: 1.0
Scope: deterministic capacity limits for travel edges.

## Capacity Types
Each edge declares capacity_type:
- FINITE (fixed capacity pool)
- INFINITE (explicitly unbounded)
- BURST (finite per ACT window)

## Capacity Units
Edges declare capacity_units and unit semantics, e.g.:
- entities
- mass
- volume
- bandwidth

## Consumption and Return
Capacity is consumed on OP_TRAVEL_BEGIN and returned on:
- OP_TRAVEL_ARRIVE
- OP_TRAVEL_CANCEL

## Refill Rules
Edges declare refill_rule:
- continuous (per ACT)
- discrete (at ACT windows)
- scheduled (explicit refill events)

## Determinism Rules
- Capacity evaluation is deterministic given inputs.
- No implicit capacity expansion.
- Insufficient capacity yields queue, defer, or refusal.

## Integration Points
- TRAVEL0 scheduling and denial semantics
- EXEC/HWCAPS budgets for admission
- LAW gating for capacity overrides
