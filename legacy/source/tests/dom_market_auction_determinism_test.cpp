/*
TEST: dom_market_auction_determinism_test
PURPOSE: Auction clearing is deterministic and uses stable tie-breaks.
*/
#include "runtime/dom_market_registry.h"

#include <string.h>

extern "C" {
#include "domino/core/spacetime.h"
}

int main(void) {
    dom_market_registry *reg = dom_market_registry_create();
    dom_market_spec spec;
    dom_market_id market_id = 0ull;
    dom_market_order buy;
    dom_market_order sell;
    dom_market_clear_result result;
    int rc;

    if (!reg) {
        return 1;
    }
    memset(&spec, 0, sizeof(spec));
    spec.id = "auction";
    spec.id_len = 7u;
    spec.provider_kind = DOM_MARKET_PROVIDER_AUCTION;
    spec.base_asset_id = 10ull;
    spec.quote_asset_id = 20ull;
    spec.price_scale = 100u;
    spec.clear_interval_ticks = 10;
    if (dom_id_hash64(spec.id, spec.id_len, &market_id) != DOM_SPACETIME_OK) {
        dom_market_registry_destroy(reg);
        return 2;
    }
    rc = dom_market_registry_register(reg, &spec);
    if (rc != DOM_MARKET_OK) {
        dom_market_registry_destroy(reg);
        return 3;
    }

    memset(&buy, 0, sizeof(buy));
    buy.order_id = 1ull;
    buy.account_id = 100ull;
    buy.side = DOM_MARKET_SIDE_BUY;
    buy.quantity_base = 5;
    buy.limit_price = 120;
    buy.time_in_force = DOM_MARKET_TIF_GTC;
    buy.submit_tick = 1;

    memset(&sell, 0, sizeof(sell));
    sell.order_id = 2ull;
    sell.account_id = 200ull;
    sell.side = DOM_MARKET_SIDE_SELL;
    sell.quantity_base = 5;
    sell.limit_price = 100;
    sell.time_in_force = DOM_MARKET_TIF_GTC;
    sell.submit_tick = 2;

    rc = dom_market_registry_submit_order(reg, market_id, &buy, 0);
    if (rc != DOM_MARKET_OK) {
        dom_market_registry_destroy(reg);
        return 4;
    }
    rc = dom_market_registry_submit_order(reg, market_id, &sell, 0);
    if (rc != DOM_MARKET_OK) {
        dom_market_registry_destroy(reg);
        return 5;
    }

    rc = dom_market_registry_clear(reg, market_id, 10, &result);
    if (rc != DOM_MARKET_OK) {
        dom_market_registry_destroy(reg);
        return 6;
    }
    if (result.trade_count != 1u) {
        dom_market_registry_destroy(reg);
        return 7;
    }
    if (result.trades[0].buy_order_id != 1ull ||
        result.trades[0].sell_order_id != 2ull ||
        result.trades[0].price != 100) {
        dom_market_registry_destroy(reg);
        return 8;
    }
    if (result.next_due_tick != 20) {
        dom_market_registry_destroy(reg);
        return 9;
    }

    dom_market_registry_destroy(reg);
    return 0;
}
