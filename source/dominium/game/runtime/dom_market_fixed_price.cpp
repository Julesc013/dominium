/*
FILE: source/dominium/game/runtime/dom_market_fixed_price.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/runtime/market_fixed_price
RESPONSIBILITY: Deterministic fixed-price market provider.
*/
#include "runtime/dom_market_provider_impl.h"

#include <vector>

#include "runtime/dom_market_quote_stream.h"

namespace {

struct FixedPriceState {
    dom_market_spec spec;
    std::vector<dom_market_order> orders;
    std::vector<dom_market_trade> trades;
    std::vector<dom_market_quote> quotes;
    dom_market_quote_stream quote_stream;
    dom_market_order_id next_order_id;
    dom_market_trade_id next_trade_id;
    dom_act_time_t next_due;
};

static bool compute_quote(i64 qty_base, i64 price, u32 scale, i64 &out_quote) {
    if (qty_base <= 0 || price <= 0 || scale == 0u) {
        return false;
    }
    if (qty_base > DOM_LEDGER_AMOUNT_MAX / price) {
        return false;
    }
    {
        i64 prod = qty_base * price;
        out_quote = prod / (i64)scale;
    }
    return true;
}

static int fixed_init(void *state, const dom_market_spec *spec) {
    FixedPriceState *s = (FixedPriceState *)state;
    if (!s || !spec) {
        return DOM_MARKET_INVALID_ARGUMENT;
    }
    s->spec = *spec;
    s->orders.clear();
    s->trades.clear();
    s->quotes.clear();
    dom_market_quote_stream_init(&s->quote_stream, spec->id_hash);
    dom_market_quote_stream_set_bid_ask(&s->quote_stream, spec->fixed_price, spec->fixed_price);
    s->next_order_id = 1ull;
    s->next_trade_id = 1ull;
    s->next_due = 0;
    return DOM_MARKET_OK;
}

static int fixed_submit(void *state,
                        const dom_market_order *order,
                        dom_market_order_ack *out_ack) {
    FixedPriceState *s = (FixedPriceState *)state;
    dom_market_order tmp;
    i64 quote_qty = 0;
    if (!s || !order) {
        return DOM_MARKET_INVALID_ARGUMENT;
    }
    tmp = *order;
    if (tmp.order_id == 0ull) {
        tmp.order_id = s->next_order_id++;
    }
    if (tmp.side != DOM_MARKET_SIDE_BUY && tmp.side != DOM_MARKET_SIDE_SELL) {
        if (out_ack) out_ack->status = 0u;
        return DOM_MARKET_REFUSED;
    }
    if (tmp.quantity_base <= 0) {
        if (out_ack) out_ack->status = 0u;
        return DOM_MARKET_REFUSED;
    }
    if (!compute_quote(tmp.quantity_base, s->spec.fixed_price, s->spec.price_scale, quote_qty)) {
        if (out_ack) out_ack->status = 0u;
        return DOM_MARKET_OVERFLOW;
    }
    tmp.limit_price = s->spec.fixed_price;
    if (tmp.side == DOM_MARKET_SIDE_BUY) {
        tmp.asset_in = s->spec.quote_asset_id;
        tmp.asset_out = s->spec.base_asset_id;
        tmp.quantity_in = quote_qty;
        tmp.quantity_out = tmp.quantity_base;
    } else {
        tmp.asset_in = s->spec.base_asset_id;
        tmp.asset_out = s->spec.quote_asset_id;
        tmp.quantity_in = tmp.quantity_base;
        tmp.quantity_out = quote_qty;
    }
    s->orders.push_back(tmp);
    if (out_ack) {
        out_ack->status = 1u;
        out_ack->order_id = tmp.order_id;
        out_ack->next_due_tick = tmp.submit_tick;
    }
    s->next_due = tmp.submit_tick;
    return DOM_MARKET_OK;
}

static int fixed_cancel(void *state, dom_market_order_id order_id) {
    FixedPriceState *s = (FixedPriceState *)state;
    size_t i;
    if (!s || order_id == 0ull) {
        return DOM_MARKET_INVALID_ARGUMENT;
    }
    for (i = 0u; i < s->orders.size(); ++i) {
        if (s->orders[i].order_id == order_id) {
            s->orders.erase(s->orders.begin() + (std::vector<dom_market_order>::difference_type)i);
            return DOM_MARKET_OK;
        }
    }
    return DOM_MARKET_NOT_FOUND;
}

static int fixed_clear(void *state,
                       dom_act_time_t now,
                       dom_market_clear_result *out_result) {
    FixedPriceState *s = (FixedPriceState *)state;
    size_t i;
    if (!s || !out_result) {
        return DOM_MARKET_INVALID_ARGUMENT;
    }
    s->trades.clear();
    s->quotes.clear();

    if (s->spec.market_account_id == 0ull) {
        out_result->trades = 0;
        out_result->trade_count = 0u;
        out_result->quotes = 0;
        out_result->quote_count = 0u;
        out_result->next_due_tick = 0;
        return DOM_MARKET_REFUSED;
    }

    for (i = 0u; i < s->orders.size(); ++i) {
        const dom_market_order &ord = s->orders[i];
        dom_market_trade tr;
        tr.trade_id = s->next_trade_id++;
        tr.price = s->spec.fixed_price;
        tr.base_asset_id = s->spec.base_asset_id;
        tr.quote_asset_id = s->spec.quote_asset_id;
        tr.quantity_base = ord.quantity_base;
        tr.execution_tick = now;
        tr.settlement_tick = now;
        if (ord.side == DOM_MARKET_SIDE_BUY) {
            tr.buy_order_id = ord.order_id;
            tr.sell_order_id = 0ull;
            tr.buy_account_id = ord.account_id;
            tr.sell_account_id = s->spec.market_account_id;
            tr.quantity_quote = ord.quantity_in;
        } else {
            tr.buy_order_id = 0ull;
            tr.sell_order_id = ord.order_id;
            tr.buy_account_id = s->spec.market_account_id;
            tr.sell_account_id = ord.account_id;
            tr.quantity_quote = ord.quantity_out;
        }
        s->trades.push_back(tr);
    }

    s->orders.clear();
    s->quotes.resize(1u);
    dom_market_quote_stream_set_last(&s->quote_stream, s->spec.fixed_price);
    if (dom_market_quote_stream_emit(&s->quote_stream, now, &s->quotes[0], 1u) == 0u) {
        s->quotes.clear();
    }

    out_result->trades = s->trades.empty() ? 0 : &s->trades[0];
    out_result->trade_count = (u32)s->trades.size();
    out_result->quotes = s->quotes.empty() ? 0 : &s->quotes[0];
    out_result->quote_count = (u32)s->quotes.size();
    out_result->next_due_tick = s->orders.empty() ? 0 : now;
    s->next_due = out_result->next_due_tick;
    return DOM_MARKET_OK;
}

static int fixed_next_due(void *state, dom_act_time_t *out_tick) {
    FixedPriceState *s = (FixedPriceState *)state;
    if (!s || !out_tick) {
        return DOM_MARKET_INVALID_ARGUMENT;
    }
    *out_tick = s->next_due;
    return s->next_due ? DOM_MARKET_OK : DOM_MARKET_NOT_FOUND;
}

static void fixed_destroy(void *state) {
    FixedPriceState *s = (FixedPriceState *)state;
    if (!s) {
        return;
    }
    delete s;
}

} // namespace

int dom_market_provider_create_fixed_price(dom_market_provider_vtbl *out_vtbl, void **out_state) {
    if (!out_vtbl || !out_state) {
        return DOM_MARKET_INVALID_ARGUMENT;
    }
    FixedPriceState *state = new FixedPriceState();
    out_vtbl->init = fixed_init;
    out_vtbl->submit_order = fixed_submit;
    out_vtbl->cancel_order = fixed_cancel;
    out_vtbl->clear = fixed_clear;
    out_vtbl->next_due_tick = fixed_next_due;
    out_vtbl->destroy = fixed_destroy;
    *out_state = state;
    return DOM_MARKET_OK;
}
