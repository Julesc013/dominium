/*
TEST: dom_market_barter_determinism_test
PURPOSE: Barter matching is deterministic with reciprocal orders.
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
    dom_market_order a;
    dom_market_order b;
    dom_market_clear_result result;
    int rc;

    if (!reg) {
        return 1;
    }
    memset(&spec, 0, sizeof(spec));
    spec.id = "barter";
    spec.id_len = 6u;
    spec.provider_kind = DOM_MARKET_PROVIDER_BARTER;
    spec.base_asset_id = 1ull;
    spec.quote_asset_id = 2ull;
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

    memset(&a, 0, sizeof(a));
    a.order_id = 1ull;
    a.account_id = 10ull;
    a.asset_in = 2ull;
    a.asset_out = 1ull;
    a.quantity_in = 500;
    a.quantity_out = 5;
    a.time_in_force = DOM_MARKET_TIF_GTC;
    a.submit_tick = 2;

    memset(&b, 0, sizeof(b));
    b.order_id = 2ull;
    b.account_id = 11ull;
    b.asset_in = 1ull;
    b.asset_out = 2ull;
    b.quantity_in = 5;
    b.quantity_out = 500;
    b.time_in_force = DOM_MARKET_TIF_GTC;
    b.submit_tick = 3;

    rc = dom_market_registry_submit_order(reg, market_id, &a, 0);
    if (rc != DOM_MARKET_OK) {
        dom_market_registry_destroy(reg);
        return 4;
    }
    rc = dom_market_registry_submit_order(reg, market_id, &b, 0);
    if (rc != DOM_MARKET_OK) {
        dom_market_registry_destroy(reg);
        return 5;
    }

    rc = dom_market_registry_clear(reg, market_id, 5, &result);
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
        result.trades[0].quantity_base != 5 ||
        result.trades[0].quantity_quote != 500) {
        dom_market_registry_destroy(reg);
        return 8;
    }

    dom_market_registry_destroy(reg);
    return 0;
}
