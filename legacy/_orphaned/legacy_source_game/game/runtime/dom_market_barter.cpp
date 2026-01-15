/*
FILE: source/dominium/game/runtime/dom_market_barter.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/runtime/market_barter
RESPONSIBILITY: Deterministic barter market provider.
*/
#include "runtime/dom_market_provider_impl.h"

#include <algorithm>
#include <vector>

#include "runtime/dom_market_quote_stream.h"

namespace {

struct BarterState {
    dom_market_spec spec;
    std::vector<dom_market_order> orders;
    std::vector<dom_market_trade> trades;
    std::vector<dom_market_quote> quotes;
    dom_market_quote_stream quote_stream;
    dom_market_order_id next_order_id;
    dom_market_trade_id next_trade_id;
    dom_act_time_t next_due;
};

static bool order_less(const dom_market_order &a, const dom_market_order &b) {
    return a.order_id < b.order_id;
}

static bool compute_price_from_qty(i64 qty_base,
                                   i64 qty_quote,
                                   u32 scale,
                                   i64 &out_price) {
    if (qty_base <= 0 || qty_quote <= 0 || scale == 0u) {
        return false;
    }
    if (qty_quote > DOM_LEDGER_AMOUNT_MAX / (i64)scale) {
        return false;
    }
    {
        i64 numer = qty_quote * (i64)scale;
        out_price = numer / qty_base;
    }
    return true;
}

static int barter_init(void *state, const dom_market_spec *spec) {
    BarterState *s = (BarterState *)state;
    if (!s || !spec) {
        return DOM_MARKET_INVALID_ARGUMENT;
    }
    s->spec = *spec;
    s->orders.clear();
    s->trades.clear();
    s->quotes.clear();
    dom_market_quote_stream_init(&s->quote_stream, spec->id_hash);
    s->next_order_id = 1ull;
    s->next_trade_id = 1ull;
    s->next_due = 0;
    return DOM_MARKET_OK;
}

static int barter_submit(void *state,
                         const dom_market_order *order,
                         dom_market_order_ack *out_ack) {
    BarterState *s = (BarterState *)state;
    dom_market_order tmp;
    if (!s || !order) {
        return DOM_MARKET_INVALID_ARGUMENT;
    }
    tmp = *order;
    if (tmp.order_id == 0ull) {
        tmp.order_id = s->next_order_id++;
    }
    if (tmp.asset_in == 0ull || tmp.asset_out == 0ull ||
        tmp.quantity_in <= 0 || tmp.quantity_out <= 0) {
        if (out_ack) {
            out_ack->status = 0u;
        }
        return DOM_MARKET_REFUSED;
    }
    if (!((tmp.asset_in == s->spec.quote_asset_id && tmp.asset_out == s->spec.base_asset_id) ||
          (tmp.asset_in == s->spec.base_asset_id && tmp.asset_out == s->spec.quote_asset_id))) {
        if (out_ack) {
            out_ack->status = 0u;
        }
        return DOM_MARKET_REFUSED;
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

static int barter_cancel(void *state, dom_market_order_id order_id) {
    BarterState *s = (BarterState *)state;
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

static int barter_clear(void *state,
                        dom_act_time_t now,
                        dom_market_clear_result *out_result) {
    BarterState *s = (BarterState *)state;
    std::vector<dom_market_order> remaining;
    size_t i;
    if (!s || !out_result) {
        return DOM_MARKET_INVALID_ARGUMENT;
    }
    s->trades.clear();
    s->quotes.clear();
    if (s->orders.empty()) {
        out_result->trades = 0;
        out_result->trade_count = 0u;
        out_result->quotes = 0;
        out_result->quote_count = 0u;
        out_result->next_due_tick = 0;
        return DOM_MARKET_OK;
    }

    std::sort(s->orders.begin(), s->orders.end(), order_less);
    remaining.reserve(s->orders.size());

    for (i = 0u; i < s->orders.size(); ++i) {
        dom_market_order &a = s->orders[i];
        size_t j;
        if (a.quantity_in <= 0 || a.quantity_out <= 0) {
            continue;
        }
        for (j = i + 1u; j < s->orders.size(); ++j) {
            dom_market_order &b = s->orders[j];
            if (b.quantity_in <= 0 || b.quantity_out <= 0) {
                continue;
            }
            if (a.asset_in == b.asset_out &&
                a.asset_out == b.asset_in &&
                a.quantity_in == b.quantity_out &&
                a.quantity_out == b.quantity_in) {
                dom_market_trade tr;
                i64 price = 0;
                dom_market_order *buy = 0;
                dom_market_order *sell = 0;
                if (a.asset_out == s->spec.base_asset_id) {
                    buy = &a;
                    sell = &b;
                } else if (b.asset_out == s->spec.base_asset_id) {
                    buy = &b;
                    sell = &a;
                }
                if (!buy || !sell) {
                    continue;
                }
                if (!compute_price_from_qty(buy->quantity_out, buy->quantity_in,
                                            s->spec.price_scale, price)) {
                    price = 0;
                }
                tr.trade_id = s->next_trade_id++;
                tr.buy_order_id = buy->order_id;
                tr.sell_order_id = sell->order_id;
                tr.buy_account_id = buy->account_id;
                tr.sell_account_id = sell->account_id;
                tr.base_asset_id = s->spec.base_asset_id;
                tr.quote_asset_id = s->spec.quote_asset_id;
                tr.quantity_base = buy->quantity_out;
                tr.quantity_quote = buy->quantity_in;
                tr.price = price;
                tr.execution_tick = now;
                tr.settlement_tick = now;
                s->trades.push_back(tr);
                a.quantity_in = 0;
                a.quantity_out = 0;
                b.quantity_in = 0;
                b.quantity_out = 0;
                dom_market_quote_stream_set_last(&s->quote_stream, price);
                break;
            }
        }
        if (a.quantity_in > 0 && a.quantity_out > 0) {
            if (a.time_in_force == DOM_MARKET_TIF_GTC) {
                remaining.push_back(a);
            }
        }
    }
    s->orders.swap(remaining);
    s->quotes.resize(1u);
    if (!s->trades.empty()) {
        u32 count = dom_market_quote_stream_emit(&s->quote_stream, now,
                                                 &s->quotes[0], 1u);
        if (count == 0u) {
            s->quotes.clear();
        }
    } else {
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

static int barter_next_due(void *state, dom_act_time_t *out_tick) {
    BarterState *s = (BarterState *)state;
    if (!s || !out_tick) {
        return DOM_MARKET_INVALID_ARGUMENT;
    }
    *out_tick = s->next_due;
    return s->next_due ? DOM_MARKET_OK : DOM_MARKET_NOT_FOUND;
}

static void barter_destroy(void *state) {
    BarterState *s = (BarterState *)state;
    if (!s) {
        return;
    }
    delete s;
}

} // namespace

int dom_market_provider_create_barter(dom_market_provider_vtbl *out_vtbl, void **out_state) {
    if (!out_vtbl || !out_state) {
        return DOM_MARKET_INVALID_ARGUMENT;
    }
    BarterState *state = new BarterState();
    out_vtbl->init = barter_init;
    out_vtbl->submit_order = barter_submit;
    out_vtbl->cancel_order = barter_cancel;
    out_vtbl->clear = barter_clear;
    out_vtbl->next_due_tick = barter_next_due;
    out_vtbl->destroy = barter_destroy;
    *out_state = state;
    return DOM_MARKET_OK;
}
