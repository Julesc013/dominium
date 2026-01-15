/*
TEST: dom_market_batch_equivalence_test
PURPOSE: Clearing results are invariant to intermediate empty clears.
*/
#include "runtime/dom_market_registry.h"

#include <string.h>

extern "C" {
#include "domino/core/spacetime.h"
}

static int run_case(int with_intermediate_clear, dom_market_trade *out_trade) {
    dom_market_registry *reg = dom_market_registry_create();
    dom_market_spec spec;
    dom_market_id market_id = 0ull;
    dom_market_order buy;
    dom_market_order sell;
    dom_market_clear_result result;
    int rc;

    if (!reg || !out_trade) {
        return 1;
    }
    memset(&spec, 0, sizeof(spec));
    spec.id = "batch";
    spec.id_len = 5u;
    spec.provider_kind = DOM_MARKET_PROVIDER_ORDERBOOK;
    spec.base_asset_id = 3ull;
    spec.quote_asset_id = 4ull;
    spec.price_scale = 100u;
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
    buy.order_id = 10ull;
    buy.account_id = 100ull;
    buy.side = DOM_MARKET_SIDE_BUY;
    buy.quantity_base = 5;
    buy.limit_price = 150;
    buy.time_in_force = DOM_MARKET_TIF_GTC;
    buy.submit_tick = 1;

    memset(&sell, 0, sizeof(sell));
    sell.order_id = 20ull;
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
    if (with_intermediate_clear) {
        rc = dom_market_registry_clear(reg, market_id, 5, &result);
        if (rc != DOM_MARKET_OK) {
            dom_market_registry_destroy(reg);
            return 5;
        }
    }
    rc = dom_market_registry_submit_order(reg, market_id, &sell, 0);
    if (rc != DOM_MARKET_OK) {
        dom_market_registry_destroy(reg);
        return 6;
    }
    rc = dom_market_registry_clear(reg, market_id, 10, &result);
    if (rc != DOM_MARKET_OK || result.trade_count != 1u) {
        dom_market_registry_destroy(reg);
        return 7;
    }
    *out_trade = result.trades[0];
    dom_market_registry_destroy(reg);
    return 0;
}

int main(void) {
    dom_market_trade trade_a;
    dom_market_trade trade_b;
    int rc;

    rc = run_case(0, &trade_a);
    if (rc != 0) {
        return rc;
    }
    rc = run_case(1, &trade_b);
    if (rc != 0) {
        return rc;
    }
    if (trade_a.buy_order_id != trade_b.buy_order_id ||
        trade_a.sell_order_id != trade_b.sell_order_id ||
        trade_a.quantity_base != trade_b.quantity_base ||
        trade_a.quantity_quote != trade_b.quantity_quote ||
        trade_a.price != trade_b.price) {
        return 10;
    }
    return 0;
}
