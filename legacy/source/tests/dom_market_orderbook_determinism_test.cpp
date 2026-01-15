/*
TEST: dom_market_orderbook_determinism_test
PURPOSE: Orderbook matching is deterministic across order submission sequences.
*/
#include "runtime/dom_market_registry.h"

#include <string.h>

extern "C" {
#include "domino/core/spacetime.h"
}

struct TradeSig {
    u32 trade_count;
    dom_market_order_id buy_order_id;
    dom_market_order_id sell_order_id;
    i64 quantity_base;
    i64 quantity_quote;
    i64 price;
};

static int run_case(const dom_market_order *orders, u32 count, const u32 *seq, u32 seq_count, TradeSig *out_sig) {
    dom_market_registry *reg = dom_market_registry_create();
    dom_market_spec spec;
    dom_market_id market_id = 0ull;
    dom_market_clear_result result;
    u32 i;
    int rc;

    if (!reg || !out_sig) {
        return 1;
    }
    memset(&spec, 0, sizeof(spec));
    spec.id = "orderbook";
    spec.id_len = 9u;
    spec.provider_kind = DOM_MARKET_PROVIDER_ORDERBOOK;
    spec.base_asset_id = 1ull;
    spec.quote_asset_id = 2ull;
    spec.price_scale = 100u;
    spec.max_matches_per_clear = 0u;
    if (dom_id_hash64(spec.id, spec.id_len, &market_id) != DOM_SPACETIME_OK) {
        dom_market_registry_destroy(reg);
        return 2;
    }
    rc = dom_market_registry_register(reg, &spec);
    if (rc != DOM_MARKET_OK) {
        dom_market_registry_destroy(reg);
        return 3;
    }

    for (i = 0u; i < seq_count; ++i) {
        const dom_market_order *ord = &orders[seq[i]];
        dom_market_order_ack ack;
        rc = dom_market_registry_submit_order(reg, market_id, ord, &ack);
        if (rc != DOM_MARKET_OK || ack.status == 0u) {
            dom_market_registry_destroy(reg);
            return 4;
        }
    }

    rc = dom_market_registry_clear(reg, market_id, 10, &result);
    if (rc != DOM_MARKET_OK) {
        dom_market_registry_destroy(reg);
        return 5;
    }
    if (result.trade_count != 1u) {
        dom_market_registry_destroy(reg);
        return 6;
    }
    out_sig->trade_count = result.trade_count;
    out_sig->buy_order_id = result.trades[0].buy_order_id;
    out_sig->sell_order_id = result.trades[0].sell_order_id;
    out_sig->quantity_base = result.trades[0].quantity_base;
    out_sig->quantity_quote = result.trades[0].quantity_quote;
    out_sig->price = result.trades[0].price;

    dom_market_registry_destroy(reg);
    return 0;
}

int main(void) {
    dom_market_order orders[3];
    TradeSig sig_a;
    TradeSig sig_b;
    u32 seq_a[3] = {0u, 1u, 2u};
    u32 seq_b[3] = {2u, 1u, 0u};
    int rc;

    memset(orders, 0, sizeof(orders));
    orders[0].order_id = 100ull;
    orders[0].account_id = 10ull;
    orders[0].side = DOM_MARKET_SIDE_BUY;
    orders[0].quantity_base = 10;
    orders[0].limit_price = 120;
    orders[0].time_in_force = DOM_MARKET_TIF_GTC;
    orders[0].submit_tick = 5;

    orders[1].order_id = 101ull;
    orders[1].account_id = 11ull;
    orders[1].side = DOM_MARKET_SIDE_BUY;
    orders[1].quantity_base = 8;
    orders[1].limit_price = 110;
    orders[1].time_in_force = DOM_MARKET_TIF_GTC;
    orders[1].submit_tick = 6;

    orders[2].order_id = 200ull;
    orders[2].account_id = 20ull;
    orders[2].side = DOM_MARKET_SIDE_SELL;
    orders[2].quantity_base = 6;
    orders[2].limit_price = 100;
    orders[2].time_in_force = DOM_MARKET_TIF_GTC;
    orders[2].submit_tick = 7;

    rc = run_case(orders, 3u, seq_a, 3u, &sig_a);
    if (rc != 0) {
        return rc;
    }
    rc = run_case(orders, 3u, seq_b, 3u, &sig_b);
    if (rc != 0) {
        return rc;
    }

    if (sig_a.trade_count != sig_b.trade_count ||
        sig_a.buy_order_id != sig_b.buy_order_id ||
        sig_a.sell_order_id != sig_b.sell_order_id ||
        sig_a.quantity_base != sig_b.quantity_base ||
        sig_a.quantity_quote != sig_b.quantity_quote ||
        sig_a.price != sig_b.price) {
        return 10;
    }

    if (sig_a.buy_order_id != 100ull || sig_a.sell_order_id != 200ull) {
        return 11;
    }
    if (sig_a.quantity_base != 6 || sig_a.quantity_quote != 6 || sig_a.price != 100) {
        return 12;
    }
    return 0;
}
