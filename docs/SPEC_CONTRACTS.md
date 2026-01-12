# SPEC_CONTRACTS

Status: draft  
Version: 1

## Purpose
Define deterministic contract state machines that create obligations and schedule
ledger transactions at ACT ticks. Contracts are data-defined and event-driven.

## Scope
- Contract schema and lifecycle.
- Obligations, triggers, and schedules.
- Event-driven execution and ordering.

Out of scope:
- Market clearing (see `docs/SPEC_MARKETS.md`).
- Money standards and formatting (see `docs/SPEC_MONEY_STANDARDS.md`).

## Definitions
- Contract: A deterministic state machine over obligations and schedules.
- Obligation: A rule that creates ledger transactions when triggered.
- Trigger: Deterministic condition that activates an obligation.
- Schedule: ACT-based recurrence or time window.
- Contract event: A scheduled execution step for a contract.

## Contract lifecycle
```
[ Created ]
    ↓
[ Active ]
    ↓ (obligation events)
[ Matured | Completed | Defaulted ]
```

Contracts never mutate ledger state directly; they emit transactions.

## Schema (conceptual)
Required fields:
- contract_id: stable hash or string ID.
- template_id: instrument template reference.
- parties: issuer, counterparty, guarantor (as applicable).
- obligations: list of obligation definitions.
- schedule: ACT-based triggers for obligations.
- jurisdiction_policy_id: policy reference.

Optional fields:
- collateral_asset_ids.
- grace_period_ticks.
- termination_conditions.

## Deterministic ordering
Contract events are ordered by:
1. trigger_tick
2. contract_id
3. obligation_id

Batch processing up to a target ACT tick must equal step-by-step processing.

## Event-driven execution
Contracts expose next_due_tick and are processed by scheduled events only.
No per-tick scanning is allowed.

## Engine vs game responsibilities
ENGINE (Domino, C89/C90) MAY:
- provide deterministic event scheduling primitives.
- implement contract state machines as data-driven logic.

ENGINE MUST NOT:
- interpret jurisdiction or human policy meaning.
- format or localize contract terms.

GAME (Dominium, C++98) MUST:
- load contract templates and policy references.
- resolve party authority and governance constraints.
- emit audit records for contract transitions.

## Examples
1) Bond coupon
- Contract schedules quarterly coupons.
- Each coupon triggers a ledger transaction at ACT tick.

2) Lease
- Monthly rent obligation with grace period.
- Default triggers penalty obligation.

3) Insurance
- Premium schedule.
- Claim trigger creates payout obligation.

## Prohibitions
- Continuous contract evaluation.
- Floating point obligations.
- Hidden auto-renewal without explicit rule.
- Non-deterministic triggers.

## Tests and validation requirements
Future tests MUST include:
- Contract schedule invariance under batching.
- Deterministic ordering across equal trigger ticks.
- Refusal on missing template or invalid party authority.
- Replay equivalence of contract outcomes.

## Related specs
- `docs/SPEC_LEDGER.md`
- `docs/SPEC_ASSETS_INSTRUMENTS.md`
- `docs/SPEC_MARKETS.md`
- `docs/SPEC_EVENT_DRIVEN_STEPPING.md`
