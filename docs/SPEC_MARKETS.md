--------------------------------
OWNERSHIP & RESPONSIBILITY
--------------------------------
ENGINE:
- None. Engine provides generic primitives only if referenced.

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

DEPENDENCIES:
- Engine -> libs/ and schema/ only (never game/launcher/setup/tools).
- Game -> engine public API and schema/ only.
- Tools -> engine public API, game public API, and schema/ only.
- Launcher/Setup (if applicable) -> libs/contracts + schema (launcher may also use engine public API).
--------------------------------
# SPEC_MARKETS

Status: draft  
Version: 1

## Purpose
Define deterministic market clearing mechanisms that produce trades and price
quotes without continuous simulation. Markets are event-driven and bounded.

## Scope
- Market types and clearing schedules.
- Deterministic order matching rules.
- Quote production as InfoRecords.

Out of scope:
- Money standards (see `docs/SPEC_MONEY_STANDARDS.md`).
- Contract mechanics beyond trade settlement.

## Definitions
- Market: A deterministic clearing mechanism for asset exchanges.
- Order: A request to buy or sell with explicit constraints.
- Clearing event: A scheduled processing step for a market.
- Trade: A matched order pair that results in ledger transactions.
- Quote: An InfoRecord representing observed prices.

## Market types (minimum set)
1) Barter
- Reciprocal exchange of asset A for asset B.
- Deterministic matching of reciprocal orders.

2) Fixed price
- Clears at posted price (market account acts as counterparty).
- Deterministic fill; no best-effort price shifts.

3) Auction
- Clears only at scheduled ticks.
- Orders collected until the auction tick; clearing uses deterministic priority.

4) Order book (CDA with discrete clearing)
- Clears on order arrival or scheduled ticks, but only via bounded clears.
- Matching uses deterministic price-time ordering.

5) Clearinghouse
- Coordination stub for multi-market settlement (v0: NOT_IMPLEMENTED).

## Deterministic matching rules
Tie-breaking order (mandatory):
1. price priority (if applicable)
2. time priority (order timestamp)
3. order_id (stable ID)

No randomness. No probabilistic fills.

## Provider matching behavior (implementation notes)
- Barter:
  - Orders match only if asset_in/asset_out and quantities are reciprocal.
  - Deterministic buy/sell assignment derived from base/quote asset IDs.
- Fixed price:
  - Price is fixed; orders are converted to base/quote quantities deterministically.
  - Market account acts as counterparty; refusal if no market account defined.
- Auction:
  - Buy orders sorted by descending price, then order_id.
  - Sell orders sorted by ascending price, then order_id.
  - Execution price is the sell price in the matched pair.
- Order book:
  - Same sorting and tie-break as auction.
  - Clears only via explicit clear calls; no continuous matching loop.

## Clearing schedule
Markets clear only when:
- a scheduled auction tick occurs, OR
- a bounded order arrival trigger fires.

No continuous price simulation. No per-tick scanning.

## Settlement and ledger integration
- Each trade settles via a deterministic double-entry transaction:
  - buyer: quote decrease, base increase
  - seller: base decrease, quote increase
- Settlement is atomic: insufficient balance refuses the trade.

## Quotes and epistemic gating
Price quotes are InfoRecords:
- subject to latency and uncertainty
- distributed via communication channels
- never authoritative truth

## Engine vs game responsibilities
ENGINE (Domino, C89/C90) MAY:
- provide deterministic data structures and ordering helpers.

ENGINE MUST NOT:
- interpret market institutions or rules.

GAME (Dominium, C++98) MUST:
- implement market definitions and clearing policies.
- create ledger transactions for trades.
- emit quotes and audit records.

## Diagram
```
Orders -> [ Clearing Event ] -> Trades -> Ledger postings
                 |
                 -> Quotes (InfoRecords)
```

## Worked examples
1) Auction clearing
- Orders collected until ACT tick T.
- All fills determined by price, then order_id.

2) Order book tie
- Two orders at same price and time.
- Deterministic tie-break by order_id.

3) Fixed price market
- Buyers match at posted price until volume cap reached.

## Prohibitions
- Continuous market ticks.
- Floating point price storage.
- Random or best-effort matching.
- Implicit asset conversion.

## Tests and validation requirements
Future tests MUST include:
- Deterministic clearing under identical inputs.
- Batch vs step equivalence on clearing events.
- Quote production determinism with latency.
- Settlement conservation (double-entry).
- No-clearing when market has no active orders.

## Related specs
- `docs/SPEC_LEDGER.md`
- `docs/SPEC_ASSETS_INSTRUMENTS.md`
- `docs/SPEC_CONTRACTS.md`
- `docs/SPEC_INFORMATION_MODEL.md`
