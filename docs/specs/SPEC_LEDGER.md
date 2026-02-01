Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

--------------------------------
OWNERSHIP & RESPONSIBILITY
--------------------------------
ENGINE:
- Deterministic ledger primitives and invariants defined by this spec.
- Implementation lives under `engine/` (public API in `engine/include/`).

GAME:
- Rules, policy, and interpretation defined by this spec.
- Implementation lives under `game/` (rules/content/ui as applicable).

TOOLS:
- None. Tools may only consume public APIs if needed.

SCHEMA:
- None (no canonical schema formats defined here).

FORBIDDEN:
- No launcher/setup orchestration logic in engine or game.
- No engine internal headers exposed outside engine targets.
- No game rules or policy implemented inside engine primitives.

DEPENDENCIES (Phase 1 overrides apply):
- Engine -> (no dependencies outside engine/).
- Game -> engine public API only.
- Tools -> engine public API + game public API only.
- Launcher/Setup -> libs/ + schema only (no engine/game dependencies).
--------------------------------
# SPEC_LEDGER

Status: draft  
Version: 1

## Purpose
Define the deterministic ledger core used to represent conserved value and
obligations. The ledger is the authoritative accounting mechanism for assets,
contracts, and markets. It does not model markets, currencies, or pricing.

## Scope
- Accounts, balances, transactions, postings, lots, obligations.
- Deterministic ordering and event application.
- Conservation and refusal rules.
- Epistemic visibility constraints.

Out of scope:
- Currency formatting and standards (see `docs/specs/SPEC_MONEY_STANDARDS.md`).
- Market clearing (see `docs/specs/SPEC_MARKETS.md`).
- Instrument templates (see `docs/specs/SPEC_ASSETS_INSTRUMENTS.md`).

## Definitions
- Asset: A conserved unit defined by `asset_id`. Values are stored as scaled integers.
- Account: A container for balances of one or more assets with explicit rules.
- Transaction: A deterministic set of postings applied atomically.
- Posting: A single signed amount applied to an account for a specific asset.
- Lot: A traceable sub-balance with provenance and optional cost basis.
- Obligation: A rule that schedules future transactions.
- Ledger event: A scheduled application of a transaction at an ACT tick.

## Core data model
All amounts are scaled integers. No floating point is allowed.

Required fields (conceptual):
- account_id: stable hash or u64.
- asset_id: stable hash or u64.
- amount: signed i64 in asset-defined scale.
- transaction_id: stable hash or u64.
- trigger_tick: ACT tick when applied.
- posting_order_key: deterministic secondary key.

Optional fields:
- account_kind: asset, liability, equity, income, expense.
- allow_negative: bool (defaults to false unless defined).
- lot_id: stable identifier for provenance tracking.

## Invariants
1. Double-entry conservation: for each asset in a transaction,
   sum(postings.amount) == 0.
2. Atomicity: a transaction is applied fully or not at all.
3. Deterministic ordering: transactions are ordered by
   (trigger_tick, transaction_id, posting_order_key).
4. No implicit conversions: the ledger never converts between assets.
5. No fabrication: balances change only via transactions.
6. Refusal-first: invalid transactions are rejected deterministically.

## Event-driven application
Ledger updates are event-driven:
- Transactions are scheduled at ACT ticks.
- The ledger does not scan accounts per tick.
- Batch execution up to a target tick must equal step-by-step execution.

## Engine implementation notes
Domino engine implementation provides:
- Fixed-capacity account storage with deterministic ordering by account_id.
- Asset slots ordered by asset_id per account.
- Lot tracking per asset slot with deterministic insertion order.
- Obligation scheduling via `dom_time_events` with payload_id = obligation_id.
- Batch processing via `dom_ledger_process_until` with deterministic ordering by
  (trigger_tick, order_key, event_id).

Lots are consumed in deterministic order and preserve provenance metadata.

## Engine vs game responsibilities
ENGINE (Domino, C89/C90) MAY:
- implement ledger primitives (accounts, postings, transactions).
- implement deterministic application ordering.
- provide hashing and serialization primitives.

ENGINE MUST NOT:
- define asset names, currencies, or locales.
- interpret market or contract rules.

GAME (Dominium, C++98) MUST:
- load asset definitions and instrument templates.
- create transactions from contracts and markets.
- apply governance and access rules.

## Epistemic visibility
Ledger state is authoritative but not universally visible:
- Access to balances is governed by identity, authority, and device capability.
- Balances and statements are InfoRecords for UI (see `docs/specs/SPEC_INFORMATION_MODEL.md`).

## Diagram
```
Transaction T
  Posting P1: Account A  +100 (asset X)
  Posting P2: Account B  -100 (asset X)
  ----------------------------------
  Sum == 0  -> apply atomically
```

## Worked examples
1) Barter
- A gives 10 wheat_units to B, B gives 2 tool_units to A.
- Two transactions, one per asset, both balanced.

2) Wage payment
- Employer account -500 labor_credit, worker account +500 labor_credit.
- Scheduled at ACT tick end_of_week.

3) Tax collection
- Citizen account -20 credits, treasury account +20 credits.
- Triggered by jurisdiction schedule.

## Prohibitions
- Floating point money or balances.
- Implicit asset conversion inside the ledger.
- Per-tick global ledger scans.
- UI-visible balances without access rules.

## Tests and validation requirements
Future tests MUST include:
- Double-entry conservation per transaction.
- Deterministic ordering under batch vs step.
- Refusal on insufficient balance (when allow_negative is false).
- Lot/provenance preservation on transfers.

## Related specs
- `docs/specs/SPEC_ASSETS_INSTRUMENTS.md`
- `docs/specs/SPEC_CONTRACTS.md`
- `docs/specs/SPEC_MARKETS.md`
- `docs/specs/SPEC_MONEY_STANDARDS.md`
- `docs/specs/SPEC_PROVENANCE.md`