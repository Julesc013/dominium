--------------------------------
OWNERSHIP & RESPONSIBILITY
--------------------------------
ENGINE:
- None. Engine provides generic primitives only if referenced.

GAME:
- None. Game consumes engine primitives where applicable.

TOOLS:
- None. Tools may only consume public APIs if needed.

SCHEMA:
- Canonical formats and migrations defined here live under `schema/`.

FORBIDDEN:
- No launcher/setup orchestration logic in engine or game.
- No engine internal headers exposed outside engine targets.
- No game rules or policy implemented inside engine primitives.

DEPENDENCIES:
- Engine -> libs/ and schema/ only (never game/launcher/setup/tools).
- Game -> engine public API and schema/ only.
- Tools -> engine public API, game public API, and schema/ only.
- Launcher/Setup (if applicable) -> libs/contracts + schema (launcher may also use engine public API).
--------------------------------
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

## Implementation notes (game layer)
- Templates load into a registry and are addressed by `template_id_hash`.
- Obligations are sorted deterministically by:
  1. offset_ticks
  2. role_from_hash
  3. role_to_hash
  4. asset_id_hash
  5. amount
- Scheduling binds roles to ledger accounts, then computes trigger_time as
  `start_act + offset_ticks` with overflow checks.
- Each obligation schedules a ledger transaction via engine obligations.
- Missing roles or ledger failures MUST refuse deterministically.

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
