/*
FILE: source/dominium/game/runtime/dom_market_clearinghouse.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/runtime/market_clearinghouse
RESPONSIBILITY: Deterministic clearinghouse provider stub (not implemented).
*/
#include "runtime/dom_market_provider_impl.h"

namespace {

struct ClearinghouseState {
    dom_market_spec spec;
    dom_act_time_t next_due;
};

static int ch_init(void *state, const dom_market_spec *spec) {
    ClearinghouseState *s = (ClearinghouseState *)state;
    if (!s || !spec) {
        return DOM_MARKET_INVALID_ARGUMENT;
    }
    s->spec = *spec;
    s->next_due = 0;
    return DOM_MARKET_OK;
}

static int ch_submit(void *state,
                     const dom_market_order *order,
                     dom_market_order_ack *out_ack) {
    (void)state;
    (void)order;
    if (out_ack) {
        out_ack->status = 0u;
        out_ack->order_id = 0ull;
        out_ack->next_due_tick = 0;
    }
    return DOM_MARKET_NOT_IMPLEMENTED;
}

static int ch_cancel(void *state, dom_market_order_id order_id) {
    (void)state;
    (void)order_id;
    return DOM_MARKET_NOT_IMPLEMENTED;
}

static int ch_clear(void *state,
                    dom_act_time_t now,
                    dom_market_clear_result *out_result) {
    (void)state;
    (void)now;
    if (!out_result) {
        return DOM_MARKET_INVALID_ARGUMENT;
    }
    out_result->trades = 0;
    out_result->trade_count = 0u;
    out_result->quotes = 0;
    out_result->quote_count = 0u;
    out_result->next_due_tick = 0;
    return DOM_MARKET_NOT_IMPLEMENTED;
}

static int ch_next_due(void *state, dom_act_time_t *out_tick) {
    ClearinghouseState *s = (ClearinghouseState *)state;
    if (!s || !out_tick) {
        return DOM_MARKET_INVALID_ARGUMENT;
    }
    *out_tick = s->next_due;
    return s->next_due ? DOM_MARKET_OK : DOM_MARKET_NOT_FOUND;
}

static void ch_destroy(void *state) {
    ClearinghouseState *s = (ClearinghouseState *)state;
    if (!s) {
        return;
    }
    delete s;
}

} // namespace

int dom_market_provider_create_clearinghouse(dom_market_provider_vtbl *out_vtbl, void **out_state) {
    if (!out_vtbl || !out_state) {
        return DOM_MARKET_INVALID_ARGUMENT;
    }
    ClearinghouseState *state = new ClearinghouseState();
    out_vtbl->init = ch_init;
    out_vtbl->submit_order = ch_submit;
    out_vtbl->cancel_order = ch_cancel;
    out_vtbl->clear = ch_clear;
    out_vtbl->next_due_tick = ch_next_due;
    out_vtbl->destroy = ch_destroy;
    *out_state = state;
    return DOM_MARKET_OK;
}
