# Economy Work IR Guide (ADOPT4)

Scope: authoritative economy Work IR emission for macro systems.

## Invariants
- Economy tasks are authoritative and emitted as Work IR only.
- Ordering and reductions are deterministic.
- No silent fallback on budget exhaustion.

## Dependencies
- `docs/guides/WORK_IR_EMISSION_GUIDE.md`
- `docs/architecture/EXECUTION_MODEL.md`
- `docs/architecture/ECONOMY_AND_LOGISTICS.md`

This guide defines the authoritative EconomySystem Work IR contract and how to
emit macro economy tasks deterministically.

## Scope

- Authoritative system (STRICT determinism class).
- IR-only migration state.
- Long-horizon economic progression (ledger, contracts, production, maintenance).

## Task Structure

EconomySystem emits tasks in a fixed order:

1) `DOM_ECON_TASK_LEDGER_TRANSFERS`
2) `DOM_ECON_TASK_CONTRACT_SETTLEMENT`
3) `DOM_ECON_TASK_PRODUCTION_STEP`
4) `DOM_ECON_TASK_CONSUMPTION_STEP`
5) `DOM_ECON_TASK_MAINTENANCE_DECAY`

Each task declares:

- AccessSets for explicit reads and writes
- CostModels with bounded CPU/memory/bandwidth
- Stable task IDs and commit ordering keys

## Scheduling Rules

- `next_due_act` (legacy field name: `next_due_tick`, deprecated terminology) is event-driven by queues of pending work.
- Tasks are emitted only when work exists.
- Task emission order is deterministic and stable across runs.

## Amortization Strategy

- Work is sliced with `start_index` + `count`.
- Budgets cap the number of entries processed per ACT step.
- Remainders carry forward deterministically.

## Law & Module Integration

- Law can disable any subset of economy operations.
- Disabled operations emit no tasks.
- No “silent fallback” behavior is allowed.

## Forbidden assumptions

- Per-ACT global ledger scans.
- Floating-point arithmetic on authoritative money.
- Silent ledger mutations outside declared AccessSets.
- Direct execution outside Work IR.

## See also
- `schema/economy/README.md`
