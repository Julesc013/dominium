# Economic Model (ECON0)

Status: binding.  
Scope: logistics, markets, and exchange primitives for deterministic economy.

## Core invariant
Economy emerges from constrained exchange of **matter, energy, labor, risk, and information**.  
There is no global ledger, no universal currency, and no free exchange.

## Determinism and process-only mutation
- All logistics and market changes occur via **Processes**.
- No per-tick global market clearing or simulation.
- Ordering is deterministic and follows `docs/architecture/DETERMINISTIC_ORDERING_POLICY.md`.
- Authoritative logic uses fixed-point only (see `docs/architecture/FLOAT_POLICY.md`).

## Logistics primitives (authoritative data)
Logistics are modeled as **containers**, **storage**, **transport**, and **jobs**:
- Containers and storage describe **capacity**, **contents**, and **integrity**.
- Transport references vehicles and routes and consumes travel cost from T8.
- Jobs are task graphs that consume time, energy, and skill (T18).

Schemas:
- `schema/logistics.container.schema`
- `schema/logistics.storage.schema`
- `schema/logistics.transport.schema`
- `schema/logistics.job.schema`

## Markets (local and fragmented)
Markets are **places**, not global systems:
- Offers and bids are posted locally.
- Matching is process-driven and interest-bounded.
- Information is delayed and incomplete.
- Prices are **local**, symbolic, and data-defined.

Schemas:
- `schema/market.place.schema`
- `schema/market.offer.schema`
- `schema/market.bid.schema`
- `schema/market.transaction.schema`

## Medium of exchange (optional)
Exchange media are **assemblies** (coins, notes, tokens, commodities).  
Acceptance is local and depends on **trust**, **law**, and **institutions**.

## Failures and crises
Shortages, hoarding, black markets, and supply shocks emerge from:
- transport limits (T8)
- risk profiles (T16)
- information delays (T14)
- enforcement and legitimacy (T19)

No scripted crashes or global equilibrium logic exist at this layer.

## Collapse/expand compatibility
Macro capsules store:
- total goods per domain (coarse)
- price distributions (coarse)
- transaction volume summaries
- RNG cursor continuity (if used)

Expanded domains reconstruct local state deterministically.

## Save/load/replay
- Only data + process events are saved.
- No cached paths or market clears are persisted.
- Replays reproduce transactions deterministically.

## See also
- `docs/architecture/PROCESS_ONLY_MUTATION.md`
- `docs/architecture/SCALING_MODEL.md`
- `docs/architecture/COLLAPSE_EXPAND_CONTRACT.md`
- `docs/architecture/UNIT_SYSTEM_POLICY.md`
