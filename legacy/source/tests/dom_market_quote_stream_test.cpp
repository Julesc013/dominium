/*
TEST: dom_market_quote_stream_test
PURPOSE: Quote stream emits deterministic snapshot values.
*/
#include "runtime/dom_market_quote_stream.h"

int main(void) {
    dom_market_quote_stream stream;
    dom_market_quote quotes[1];
    u32 count = 0;

    dom_market_quote_stream_init(&stream, 123ull);
    dom_market_quote_stream_set_bid_ask(&stream, 100, 110);
    dom_market_quote_stream_set_last(&stream, 105);

    count = dom_market_quote_stream_emit(&stream, 50, quotes, 1u);
    if (count != 1u) {
        return 1;
    }
    if (quotes[0].market_id != 123ull ||
        quotes[0].bid_price != 100 ||
        quotes[0].ask_price != 110 ||
        quotes[0].last_price != 105 ||
        quotes[0].quote_tick != 50) {
        return 2;
    }
    return 0;
}
