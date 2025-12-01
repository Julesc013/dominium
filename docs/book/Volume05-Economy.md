```markdown
// docs/book/Volume05-Economy.md
# Dominium Design Book v3.0
## Volume 05 — Economy

### Overview
The economy is a deterministic multi-layer model covering goods, services, markets, finance, logistics, and company operations. All values use integer or fixed-point currency; supply/demand, contracts, and markets run on tick-driven logic without randomness.

### Requirements (MUST)
- Represent goods as item stacks with stable item_id and integer quantities; services priced per tick or job.
- Currency uses 64-bit integer microcredits; no floating currency math.
- Support markets: spot, futures, options; local property markets and global/universe markets; deterministic pricing.
- Model companies with cash/assets/liabilities/shares; support stock exchange listings, trading, portfolios.
- Account for logistics pricing (TEU containers, conveyors, vehicles, routes) and tariffs/fees.
- Integrate labor costs (wages for humans, capital/maintenance for robots) and construction/maintenance costs.
- Preserve determinism across multiplayer and replays; no random market events.

### Recommendations (SHOULD)
- Base prices on realistic industrial costs and dynamic supply/demand.
- Use contracts and interproperty trade for predictable flows.
- Link research/technology progression to production efficiency and market access.
- Store quantities in smallest indivisible units to avoid rounding.

### Prohibitions (MUST NOT)
- No stochastic economic events or random price fluctuations.
- No floating-point pricing or platform-dependent rounding.
- No magic resources or fantasy tech affecting economy (unless DLC explicitly adds).
- No item spam; logistics uses inventories/containers, not free-floating items.

### Detailed Sections
#### 5.1 — Economic Primitives
- Goods: ores, energy (electrical kJ), components, fuel, food, chemicals, robots, machine parts stored as ItemStack {item_id, qty}.
- Services: construction, repair, training, transport, research, logistics, maintenance, medical, electricity delivery.
- Money: microcredits (int64); 1 credit = 1,000,000 microcredits.

#### 5.2 — Markets and Transactions
- Local property markets and global/universe markets; deterministic supply/demand curves.
- Spot/futures/options supported; tariffs/fees configurable per property/universe.
- Contracts and interproperty trade allowed; AI/company transactions follow same deterministic rules.

#### 5.3 — Companies and Finance
- Each property belongs to a company with cash/assets/liabilities/shares_outstanding.
- Support stock exchange for listings/trading; portfolios represented deterministically.
- Bankruptcy/overload states surfaced via alerts; no random bailouts.

#### 5.4 — Logistics Cost Model
- TEU-based logistics for container flows; conveyors/loaders/vehicles/trains/ships/aircraft priced deterministically.
- Items live in inventories/slots/streams; conveyors/vehicles carry stacks, not per-item entities.
- Integration with transportation networks for route costs and capacity limits.

#### 5.5 — Research and Production Coupling
- Science data as packets over data network; production-based research (no idle magic points).
- Machine tiers and tech unlocks influence production efficiency and market competitiveness.
- Realistic engineering focus; no fantasy tech without DLC.

### Cross-References
- Volume 02 — Simulation (tick-driven updates, determinism)
- Volume 03 — World (resource locations, property assets)
- Volume 04 — Networks (logistics, power/fuel/data costs)
- Volume 06 — Climate (environmental impacts on production)
- Volume 07 — UIUX (market interfaces, alerts)
- Volume 08 — Engine (persistence of economic state)
- Volume 09 — Modding (data definitions for goods/companies/markets)
```
