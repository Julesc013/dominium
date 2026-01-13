/*
FILE: source/dominium/game/runtime/dom_market_quote_stream.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/runtime/market_quote_stream
RESPONSIBILITY: Deterministic quote snapshot helper for market providers.
*/
#ifndef DOM_MARKET_QUOTE_STREAM_H
#define DOM_MARKET_QUOTE_STREAM_H

#include "runtime/dom_market_provider.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dom_market_quote_stream {
    dom_market_id market_id;
    i64 bid_price;
    i64 ask_price;
    i64 last_price;
    u32 resolution_tier;
    u32 uncertainty_flags;
    u32 staleness_ticks;
    int have_bid;
    int have_ask;
    int have_last;
} dom_market_quote_stream;

void dom_market_quote_stream_init(dom_market_quote_stream *stream, dom_market_id market_id);
void dom_market_quote_stream_set_bid_ask(dom_market_quote_stream *stream, i64 bid, i64 ask);
void dom_market_quote_stream_set_last(dom_market_quote_stream *stream, i64 last);
u32 dom_market_quote_stream_emit(dom_market_quote_stream *stream,
                                 dom_act_time_t now,
                                 dom_market_quote *out_quotes,
                                 u32 quote_capacity);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOM_MARKET_QUOTE_STREAM_H */
