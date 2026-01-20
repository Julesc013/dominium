# Governance Work IR Guide (ADOPT4)

This guide defines the authoritative GovernanceSystem Work IR contract and how to
emit governance tasks deterministically.

## Scope

- Authoritative system (STRICT determinism class).
- IR-only migration state.
- Jurisdiction, legitimacy, enforcement, and law lifecycle tasks.

## Task Structure

GovernanceSystem emits tasks in a fixed order:

1) `DOM_GOV_TASK_POLICY_APPLY`
2) `DOM_GOV_TASK_LEGITIMACY_UPDATE`
3) `DOM_GOV_TASK_AUTHORITY_ENFORCEMENT`
4) `DOM_GOV_TASK_LAW_LIFECYCLE`

Each task declares:

- AccessSets for policy, legitimacy, enforcement, and lifecycle data
- CostModels with bounded CPU/memory/bandwidth
- Stable task IDs and commit ordering keys

## Scheduling Rules

- `next_due_tick` is driven by policy schedules and event queues.
- Tasks emit only when inputs exist and are due.
- Emission order is deterministic and stable.

## Amortization Strategy

- Work is sliced with `start_index` + `count`.
- Budgets cap the number of records processed per tick.
- Remainders carry forward deterministically.

## Law & Module Integration

- Law can disable governance, elections, or policy application entirely.
- Disabled operations emit no tasks.
- No “silent fallback” behavior is allowed.

## Anti-Patterns (Forbidden)

- Background loops that bypass Work IR.
- Non-deterministic ordering of policies or legitimacy updates.
- Implicit policy application without audit records.
- Direct execution outside Work IR.
