/*
TEST: dom_market_due_tick_test
PURPOSE: Markets report no due tick when no active orders.
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
    dom_market_order order;
    dom_market_clear_result result;
    dom_act_time_t due = 0;
    int rc;

    if (!reg) {
        return 1;
    }
    memset(&spec, 0, sizeof(spec));
    spec.id = "duecheck";
    spec.id_len = 8u;
    spec.provider_kind = DOM_MARKET_PROVIDER_ORDERBOOK;
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
    rc = dom_market_registry_next_due_tick(reg, market_id, &due);
    if (rc != DOM_MARKET_NOT_FOUND || due != 0) {
        dom_market_registry_destroy(reg);
        return 4;
    }

    memset(&order, 0, sizeof(order));
    order.order_id = 1ull;
    order.account_id = 5ull;
    order.side = DOM_MARKET_SIDE_BUY;
    order.quantity_base = 1;
    order.limit_price = 100;
    order.time_in_force = DOM_MARKET_TIF_IOC;
    order.submit_tick = 7;

    rc = dom_market_registry_submit_order(reg, market_id, &order, 0);
    if (rc != DOM_MARKET_OK) {
        dom_market_registry_destroy(reg);
        return 5;
    }
    rc = dom_market_registry_next_due_tick(reg, market_id, &due);
    if (rc != DOM_MARKET_OK || due != 7) {
        dom_market_registry_destroy(reg);
        return 6;
    }

    rc = dom_market_registry_clear(reg, market_id, 7, &result);
    if (rc != DOM_MARKET_OK) {
        dom_market_registry_destroy(reg);
        return 7;
    }
    rc = dom_market_registry_next_due_tick(reg, market_id, &due);
    if (rc != DOM_MARKET_NOT_FOUND || due != 0) {
        dom_market_registry_destroy(reg);
        return 8;
    }

    dom_market_registry_destroy(reg);
    return 0;
}
