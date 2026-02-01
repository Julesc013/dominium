Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Logistics and Markets Baseline (ECON0)

Status: binding for T20 baseline.  
Scope: logistics, markets, and exchange as deterministic, local systems.

## What exists in T20
- Goods move **physically** via containers, storage, transport, and jobs.
- Markets are **local** and **fragmented**; they do not share a global ledger.
- Prices emerge from scarcity, risk, trust, and information delays.
- Matching and fulfillment are **process-driven** and deterministic.

## Logistics primitives
- Containers: capacity, contents, integrity (no teleportation).
- Storage: capacity and spoilage/decay constraints.
- Transport: vehicle + route + travel cost (from T8).
- Jobs: task graphs consuming time, energy, and skill (T18).

All numeric values are unit-tagged per `docs/architecture/UNIT_SYSTEM_POLICY.md`.

## Markets (local and imperfect)
- Offers and bids are posted at market places.
- Matching is deterministic and interest-bounded.
- Information latency is explicit; no omniscient price discovery.

## Medium of exchange (optional)
Coins, notes, tokens, and commodity money are **assemblies**.  
Acceptance depends on trust, institutions, and law; no universal currency exists.

## Failures and crises
- Shortages and hoarding emerge from transport limits and delays.
- Black markets appear when law and legitimacy diverge.
- Supply shocks are local, not global by default.

## What is NOT included yet
- No global currencies or magic money.
- No per-tick market clearing or equilibrium pricing.
- No automated factories, batch production, or economic AI.

## Collapse/expand compatibility
Collapsed domains store:
- total goods per domain (coarse)
- price distribution histograms
- transaction volume summaries

Expanded domains rehydrate deterministically and locally.

## Maturity labels
- Logistics primitives: **BOUNDED**
- Market matching and transactions: **BOUNDED**
- Exchange media: **PARAMETRIC**

## See also
- `docs/architecture/ECONOMIC_MODEL.md`
- `docs/architecture/SCALING_MODEL.md`
- `docs/architecture/COLLAPSE_EXPAND_CONTRACT.md`