#include "dominium/economy.h"

dom_status dom_economy_create(const dom_economy_desc* desc,
                              dom_economy** out_econ)
{
    (void)desc;
    (void)out_econ;
    return DOM_STATUS_UNSUPPORTED;
}

void dom_economy_destroy(dom_economy* econ)
{
    (void)econ;
}

dom_status dom_economy_register_market(dom_economy* econ,
                                       const dom_market_desc* desc,
                                       dom_market_id* out_id)
{
    (void)econ;
    (void)desc;
    if (out_id) {
        *out_id = 0;
    }
    return DOM_STATUS_UNSUPPORTED;
}

dom_status dom_economy_get_price(dom_economy* econ,
                                 const dom_trade_request* request,
                                 dom_price_quote* out_quote,
                                 size_t out_quote_size)
{
    (void)econ;
    (void)request;
    if (out_quote && out_quote_size >= sizeof(dom_price_quote)) {
        out_quote->struct_size     = (uint32_t)sizeof(dom_price_quote);
        out_quote->struct_version  = 0;
        out_quote->item_type       = 0;
        out_quote->unit_price_milli = 0;
        out_quote->available_units = 0;
    }
    return DOM_STATUS_UNSUPPORTED;
}

dom_status dom_economy_submit_trade(dom_economy* econ,
                                    const dom_trade_request* request,
                                    dom_trade_id* out_id)
{
    (void)econ;
    (void)request;
    if (out_id) {
        *out_id = 0;
    }
    return DOM_STATUS_UNSUPPORTED;
}

dom_status dom_economy_tick(dom_economy* econ, uint32_t dt_millis)
{
    (void)econ;
    (void)dt_millis;
    return DOM_STATUS_UNSUPPORTED;
}
