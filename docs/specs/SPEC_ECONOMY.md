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

DEPENDENCIES (Phase 1 overrides apply):
- Engine -> (no dependencies outside engine/).
- Game -> engine public API only.
- Tools -> engine public API + game public API only.
- Launcher/Setup -> libs/ + schema only (no engine/game dependencies).
--------------------------------
# Economy Scaffolding

- Markets: `Market { id, name, body }` registered via `decon_market_register`.
- Offers: `Offer { id, market, type (BUY/SELL), item, quantity, price_per_unit }` registered via `decon_offer_register`.
- Queries: `decon_find_best_sell_offer(item)` picks the lowest-priced sell offer with quantity > 0; `decon_find_best_buy_offer(item)` picks the highest-priced buy offer. Returns `OfferId` or 0 if none.
- Price is a scalar `Q16.16` per unit; currency and settlement are out of scope in this pass (offers are deterministic quotes only).
- Storage is bounded arrays with sequential IDs; deterministic behavior, no per-tick allocation.

Clarification:
- "Best offer" queries MUST be bounded by market scope or indexed lookups; global
  scans are forbidden. All market access must be event-driven and interest-bounded
  per `docs/SPEC_EVENT_DRIVEN_STEPPING.md` and `docs/NO_GLOBAL_ITERATION_GUIDE.md`.
