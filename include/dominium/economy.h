#ifndef DOMINIUM_ECONOMY_H
#define DOMINIUM_ECONOMY_H

#include <stddef.h>
#include "domino/baseline.h"

#include "domino/core.h"
#include "dominium/world.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dom_economy dom_economy;

typedef uint32_t dom_market_id;
typedef uint32_t dom_company_id;
typedef uint32_t dom_trade_id;

typedef struct dom_economy_desc {
    uint32_t   struct_size;
    uint32_t   struct_version;
    dom_world* world;
} dom_economy_desc;

typedef struct dom_market_desc {
    uint32_t       struct_size;
    uint32_t       struct_version;
    dom_surface_id surface;
    const char*    name;
    uint32_t       flags;
} dom_market_desc;

typedef struct dom_price_quote {
    uint32_t struct_size;
    uint32_t struct_version;
    uint32_t item_type;
    uint32_t unit_price_milli;
    uint32_t available_units;
} dom_price_quote;

typedef struct dom_trade_request {
    uint32_t     struct_size;
    uint32_t     struct_version;
    dom_market_id market;
    uint32_t     item_type;
    uint32_t     quantity;
    uint32_t     flags;
} dom_trade_request;

dom_status dom_economy_create(const dom_economy_desc* desc,
                              dom_economy** out_econ);
void       dom_economy_destroy(dom_economy* econ);
dom_status dom_economy_register_market(dom_economy* econ,
                                       const dom_market_desc* desc,
                                       dom_market_id* out_id);
dom_status dom_economy_get_price(dom_economy* econ,
                                 const dom_trade_request* request,
                                 dom_price_quote* out_quote,
                                 size_t out_quote_size);
dom_status dom_economy_submit_trade(dom_economy* econ,
                                    const dom_trade_request* request,
                                    dom_trade_id* out_id);
dom_status dom_economy_tick(dom_economy* econ, uint32_t dt_millis);

#ifdef __cplusplus
}
#endif

#endif /* DOMINIUM_ECONOMY_H */
