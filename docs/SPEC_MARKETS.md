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
1) Auction
- Clears at scheduled ticks.
- All valid orders are collected until the auction tick.

2) Order book
- Clears on order arrival or at scheduled ticks.
- Uses deterministic tie-breaking.

3) Fixed price
- Clears at posted price with bounded volume.

4) OTC bilateral
- Deterministic pairing by explicit counterparty.

## Deterministic matching rules
Tie-breaking order (mandatory):
1. price priority (if applicable)
2. time priority (order timestamp)
3. order_id (stable ID)

No randomness. No probabilistic fills.

## Clearing schedule
Markets clear only when:
- a scheduled auction tick occurs, OR
- a bounded order arrival trigger fires.

No continuous price simulation. No per-tick scanning.

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

## Related specs
- `docs/SPEC_LEDGER.md`
- `docs/SPEC_ASSETS_INSTRUMENTS.md`
- `docs/SPEC_CONTRACTS.md`
- `docs/SPEC_INFORMATION_MODEL.md`
