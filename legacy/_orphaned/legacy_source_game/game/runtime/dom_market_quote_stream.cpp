/*
FILE: source/dominium/game/runtime/dom_market_quote_stream.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/runtime/market_quote_stream
RESPONSIBILITY: Deterministic quote snapshot helper for market providers.
*/
#include "runtime/dom_market_quote_stream.h"

void dom_market_quote_stream_init(dom_market_quote_stream *stream, dom_market_id market_id) {
    if (!stream) {
        return;
    }
    stream->market_id = market_id;
    stream->bid_price = 0;
    stream->ask_price = 0;
    stream->last_price = 0;
    stream->resolution_tier = 0u;
    stream->uncertainty_flags = 0u;
    stream->staleness_ticks = 0u;
    stream->have_bid = 0;
    stream->have_ask = 0;
    stream->have_last = 0;
}

void dom_market_quote_stream_set_bid_ask(dom_market_quote_stream *stream, i64 bid, i64 ask) {
    if (!stream) {
        return;
    }
    stream->bid_price = bid;
    stream->ask_price = ask;
    stream->have_bid = 1;
    stream->have_ask = 1;
}

void dom_market_quote_stream_set_last(dom_market_quote_stream *stream, i64 last) {
    if (!stream) {
        return;
    }
    stream->last_price = last;
    stream->have_last = 1;
}

u32 dom_market_quote_stream_emit(dom_market_quote_stream *stream,
                                 dom_act_time_t now,
                                 dom_market_quote *out_quotes,
                                 u32 quote_capacity) {
    dom_market_quote q;
    if (!stream || !out_quotes || quote_capacity == 0u) {
        return 0u;
    }
    if (!stream->have_bid && !stream->have_ask && !stream->have_last) {
        return 0u;
    }
    q.market_id = stream->market_id;
    q.bid_price = stream->have_bid ? stream->bid_price : 0;
    q.ask_price = stream->have_ask ? stream->ask_price : 0;
    q.last_price = stream->have_last ? stream->last_price : 0;
    q.quote_tick = now;
    q.staleness_ticks = stream->staleness_ticks;
    q.resolution_tier = stream->resolution_tier;
    q.uncertainty_flags = stream->uncertainty_flags;
    out_quotes[0] = q;
    return 1u;
}
