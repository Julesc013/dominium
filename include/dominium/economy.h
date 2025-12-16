/*
FILE: include/dominium/economy.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / economy
RESPONSIBILITY: Defines the public contract for `economy` (types/constants/function signatures); does NOT provide implementation.
ALLOWED DEPENDENCIES: `include/dominium/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/SPEC_ABI_TEMPLATES.md` where ABI stability matters.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOMINIUM_ECONOMY_H
#define DOMINIUM_ECONOMY_H

#include <stddef.h>
#include "domino/baseline.h"

#include "domino/core.h"
#include "dominium/world.h"

#ifdef __cplusplus
extern "C" {
#endif

/* dom_economy: Public type used by `economy`. */
typedef struct dom_economy dom_economy;

/* dom_market_id: Public type used by `economy`. */
typedef uint32_t dom_market_id;
/* dom_company_id: Public type used by `economy`. */
typedef uint32_t dom_company_id;
/* dom_trade_id: Public type used by `economy`. */
typedef uint32_t dom_trade_id;

/* dom_economy_desc: Public type used by `economy`. */
typedef struct dom_economy_desc {
    uint32_t   struct_size;
    uint32_t   struct_version;
    dom_world* world;
} dom_economy_desc;

/* dom_market_desc: Public type used by `economy`. */
typedef struct dom_market_desc {
    uint32_t       struct_size;
    uint32_t       struct_version;
    dom_surface_id surface;
    const char*    name;
    uint32_t       flags;
} dom_market_desc;

/* dom_price_quote: Public type used by `economy`. */
typedef struct dom_price_quote {
    uint32_t struct_size;
    uint32_t struct_version;
    uint32_t item_type;
    uint32_t unit_price_milli;
    uint32_t available_units;
} dom_price_quote;

/* dom_trade_request: Public type used by `economy`. */
typedef struct dom_trade_request {
    uint32_t     struct_size;
    uint32_t     struct_version;
    dom_market_id market;
    uint32_t     item_type;
    uint32_t     quantity;
    uint32_t     flags;
} dom_trade_request;

/* Purpose: Create economy.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/CONTRACTS.md#Return Values / Errors`.
 */
dom_status dom_economy_create(const dom_economy_desc* desc,
                              dom_economy** out_econ);
/* Purpose: Destroy economy.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 */
void       dom_economy_destroy(dom_economy* econ);
/* Purpose: Register market.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/CONTRACTS.md#Return Values / Errors`.
 */
dom_status dom_economy_register_market(dom_economy* econ,
                                       const dom_market_desc* desc,
                                       dom_market_id* out_id);
/* Purpose: Get price.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/CONTRACTS.md#Return Values / Errors`.
 */
dom_status dom_economy_get_price(dom_economy* econ,
                                 const dom_trade_request* request,
                                 dom_price_quote* out_quote,
                                 size_t out_quote_size);
/* Purpose: Submit trade.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/CONTRACTS.md#Return Values / Errors`.
 */
dom_status dom_economy_submit_trade(dom_economy* econ,
                                    const dom_trade_request* request,
                                    dom_trade_id* out_id);
/* Purpose: Tick economy.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/CONTRACTS.md#Return Values / Errors`.
 */
dom_status dom_economy_tick(dom_economy* econ, uint32_t dt_millis);

#ifdef __cplusplus
}
#endif

#endif /* DOMINIUM_ECONOMY_H */
