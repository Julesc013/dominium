/*
FILE: source/dominium/game/runtime/dom_market_auction.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/runtime/market_auction
RESPONSIBILITY: Deterministic auction market provider (single-price clears).
*/
#include "runtime/dom_market_provider_impl.h"

#include <algorithm>
#include <vector>

#include "runtime/dom_market_quote_stream.h"

namespace {

struct AuctionState {
    dom_market_spec spec;
    std::vector<dom_market_order> orders;
    std::vector<dom_market_trade> trades;
    std::vector<dom_market_quote> quotes;
    dom_market_quote_stream quote_stream;
    dom_market_order_id next_order_id;
    dom_market_trade_id next_trade_id;
    dom_act_time_t next_due;
    dom_act_time_t last_clear;
};

static bool order_buy_less(const dom_market_order &a, const dom_market_order &b) {
    if (a.limit_price != b.limit_price) {
        return a.limit_price > b.limit_price;
    }
    return a.order_id < b.order_id;
}

static bool order_sell_less(const dom_market_order &a, const dom_market_order &b) {
    if (a.limit_price != b.limit_price) {
        return a.limit_price < b.limit_price;
    }
    return a.order_id < b.order_id;
}

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

static void filter_fok(std::vector<dom_market_order> &buys,
                       std::vector<dom_market_order> &sells) {
    size_t i;
    size_t j;
    for (i = 0u; i < buys.size(); ++i) {
        dom_market_order &buy = buys[i];
        if (buy.time_in_force != DOM_MARKET_TIF_FOK) {
            continue;
        }
        {
            i64 available = 0;
            for (j = 0u; j < sells.size(); ++j) {
                if (sells[j].limit_price <= buy.limit_price) {
                    available += sells[j].quantity_base;
                }
            }
            if (available < buy.quantity_base) {
                buy.quantity_base = 0;
            }
        }
    }
    for (i = 0u; i < sells.size(); ++i) {
        dom_market_order &sell = sells[i];
        if (sell.time_in_force != DOM_MARKET_TIF_FOK) {
            continue;
        }
        {
            i64 available = 0;
            for (j = 0u; j < buys.size(); ++j) {
                if (buys[j].limit_price >= sell.limit_price) {
                    available += buys[j].quantity_base;
                }
            }
            if (available < sell.quantity_base) {
                sell.quantity_base = 0;
            }
        }
    }
}

static int auction_init(void *state, const dom_market_spec *spec) {
    AuctionState *s = (AuctionState *)state;
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
    s->last_clear = 0;
    return DOM_MARKET_OK;
}

static int auction_submit(void *state,
                          const dom_market_order *order,
                          dom_market_order_ack *out_ack) {
    AuctionState *s = (AuctionState *)state;
    dom_market_order tmp;
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
    if (tmp.quantity_base <= 0 || tmp.limit_price <= 0) {
        if (out_ack) out_ack->status = 0u;
        return DOM_MARKET_REFUSED;
    }
    tmp.base_asset_id = s->spec.base_asset_id;
    tmp.quote_asset_id = s->spec.quote_asset_id;
    s->orders.push_back(tmp);
    if (out_ack) {
        out_ack->status = 1u;
        out_ack->order_id = tmp.order_id;
        out_ack->next_due_tick = tmp.submit_tick + s->spec.clear_interval_ticks;
    }
    if (s->next_due == 0 || tmp.submit_tick + s->spec.clear_interval_ticks < s->next_due) {
        s->next_due = tmp.submit_tick + s->spec.clear_interval_ticks;
    }
    return DOM_MARKET_OK;
}

static int auction_cancel(void *state, dom_market_order_id order_id) {
    AuctionState *s = (AuctionState *)state;
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

static int auction_clear(void *state,
                         dom_act_time_t now,
                         dom_market_clear_result *out_result) {
    AuctionState *s = (AuctionState *)state;
    std::vector<dom_market_order> buys;
    std::vector<dom_market_order> sells;
    std::vector<dom_market_order> remaining;
    size_t i;
    size_t bi = 0u;
    size_t si = 0u;
    if (!s || !out_result) {
        return DOM_MARKET_INVALID_ARGUMENT;
    }
    if (s->spec.clear_interval_ticks == 0) {
        s->next_due = now;
    }
    if (s->next_due != 0 && now < s->next_due) {
        out_result->trades = 0;
        out_result->trade_count = 0u;
        out_result->quotes = 0;
        out_result->quote_count = 0u;
        out_result->next_due_tick = s->next_due;
        return DOM_MARKET_OK;
    }

    s->trades.clear();
    s->quotes.clear();
    buys.reserve(s->orders.size());
    sells.reserve(s->orders.size());
    for (i = 0u; i < s->orders.size(); ++i) {
        if (s->orders[i].side == DOM_MARKET_SIDE_BUY) {
            buys.push_back(s->orders[i]);
        } else {
            sells.push_back(s->orders[i]);
        }
    }
    filter_fok(buys, sells);
    std::sort(buys.begin(), buys.end(), order_buy_less);
    std::sort(sells.begin(), sells.end(), order_sell_less);

    while (bi < buys.size() && si < sells.size()) {
        dom_market_order &buy = buys[bi];
        dom_market_order &sell = sells[si];
        i64 price = 0;
        i64 qty_quote = 0;
        i64 qty_base = 0;

        if (buy.quantity_base <= 0) {
            bi++;
            continue;
        }
        if (sell.quantity_base <= 0) {
            si++;
            continue;
        }
        if (buy.limit_price < sell.limit_price) {
            break;
        }
        price = sell.limit_price;
        qty_base = (buy.quantity_base < sell.quantity_base) ? buy.quantity_base : sell.quantity_base;
        if (!compute_quote(qty_base, price, s->spec.price_scale, qty_quote)) {
            return DOM_MARKET_OVERFLOW;
        }

        {
            dom_market_trade tr;
            tr.trade_id = s->next_trade_id++;
            tr.buy_order_id = buy.order_id;
            tr.sell_order_id = sell.order_id;
            tr.buy_account_id = buy.account_id;
            tr.sell_account_id = sell.account_id;
            tr.base_asset_id = s->spec.base_asset_id;
            tr.quote_asset_id = s->spec.quote_asset_id;
            tr.quantity_base = qty_base;
            tr.quantity_quote = qty_quote;
            tr.price = price;
            tr.execution_tick = now;
            tr.settlement_tick = now;
            s->trades.push_back(tr);
        }
        dom_market_quote_stream_set_last(&s->quote_stream, price);
        buy.quantity_base -= qty_base;
        sell.quantity_base -= qty_base;
        if (buy.quantity_base == 0) {
            bi++;
        }
        if (sell.quantity_base == 0) {
            si++;
        }
        if (s->spec.max_matches_per_clear > 0u &&
            s->trades.size() >= s->spec.max_matches_per_clear) {
            break;
        }
    }

    remaining.reserve(s->orders.size());
    for (i = 0u; i < buys.size(); ++i) {
        dom_market_order &ord = buys[i];
        if (ord.quantity_base > 0 && ord.time_in_force == DOM_MARKET_TIF_GTC) {
            remaining.push_back(ord);
        }
    }
    for (i = 0u; i < sells.size(); ++i) {
        dom_market_order &ord = sells[i];
        if (ord.quantity_base > 0 && ord.time_in_force == DOM_MARKET_TIF_GTC) {
            remaining.push_back(ord);
        }
    }
    s->orders.swap(remaining);

    if (!buys.empty()) {
        dom_market_quote_stream_set_bid_ask(&s->quote_stream,
                                            buys[0].limit_price,
                                            sells.empty() ? 0 : sells[0].limit_price);
    }
    s->quotes.resize(1u);
    if (dom_market_quote_stream_emit(&s->quote_stream, now, &s->quotes[0], 1u) == 0u) {
        s->quotes.clear();
    }

    out_result->trades = s->trades.empty() ? 0 : &s->trades[0];
    out_result->trade_count = (u32)s->trades.size();
    out_result->quotes = s->quotes.empty() ? 0 : &s->quotes[0];
    out_result->quote_count = (u32)s->quotes.size();
    s->last_clear = now;
    if (s->spec.clear_interval_ticks > 0) {
        s->next_due = now + s->spec.clear_interval_ticks;
    } else {
        s->next_due = s->orders.empty() ? 0 : now;
    }
    out_result->next_due_tick = s->next_due;
    return DOM_MARKET_OK;
}

static int auction_next_due(void *state, dom_act_time_t *out_tick) {
    AuctionState *s = (AuctionState *)state;
    if (!s || !out_tick) {
        return DOM_MARKET_INVALID_ARGUMENT;
    }
    *out_tick = s->next_due;
    return s->next_due ? DOM_MARKET_OK : DOM_MARKET_NOT_FOUND;
}

static void auction_destroy(void *state) {
    AuctionState *s = (AuctionState *)state;
    if (!s) {
        return;
    }
    delete s;
}

} // namespace

int dom_market_provider_create_auction(dom_market_provider_vtbl *out_vtbl, void **out_state) {
    if (!out_vtbl || !out_state) {
        return DOM_MARKET_INVALID_ARGUMENT;
    }
    AuctionState *state = new AuctionState();
    out_vtbl->init = auction_init;
    out_vtbl->submit_order = auction_submit;
    out_vtbl->cancel_order = auction_cancel;
    out_vtbl->clear = auction_clear;
    out_vtbl->next_due_tick = auction_next_due;
    out_vtbl->destroy = auction_destroy;
    *out_state = state;
    return DOM_MARKET_OK;
}
