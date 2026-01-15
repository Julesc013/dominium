/*
FILE: source/dominium/game/rules/economy.c
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/rules/economy
RESPONSIBILITY: Implements `economy`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
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
