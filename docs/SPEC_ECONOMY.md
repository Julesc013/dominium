# Economy Scaffolding

- Markets: `Market { id, name, body }` registered via `decon_market_register`.
- Offers: `Offer { id, market, type (BUY/SELL), item, quantity, price_per_unit }` registered via `decon_offer_register`.
- Queries: `decon_find_best_sell_offer(item)` picks the lowest-priced sell offer with quantity > 0; `decon_find_best_buy_offer(item)` picks the highest-priced buy offer. Returns `OfferId` or 0 if none.
- Price is a scalar `Q16.16` per unit; currency and settlement are out of scope in this pass (offers are deterministic quotes only).
- Storage is bounded arrays with sequential IDs; deterministic behavior, no per-tick allocation.
