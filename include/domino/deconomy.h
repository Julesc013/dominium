/*
FILE: include/domino/deconomy.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / deconomy
RESPONSIBILITY: Defines the public contract for `deconomy` (types/constants/function signatures); does NOT provide implementation.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/SPEC_ABI_TEMPLATES.md` where ABI stability matters.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOMINO_DECONOMY_H
#define DOMINO_DECONOMY_H

#include "dnumeric.h"
#include "dmatter.h"
#include "dorbit.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef uint32_t MarketId;
typedef uint32_t OfferId;

typedef enum {
    OFFER_BUY = 0,
    OFFER_SELL,
} OfferType;

typedef struct {
    MarketId    id;
    const char *name;
    BodyId      body;
} Market;

typedef struct {
    OfferId     id;
    MarketId    market;
    OfferType   type;

    ItemTypeId  item;
    U32         quantity;
    Q16_16      price_per_unit;
} Offer;

MarketId decon_market_register(const Market *def);
Market  *decon_market_get(MarketId id);

OfferId  decon_offer_register(const Offer *def);
Offer   *decon_offer_get(OfferId id);

OfferId  decon_find_best_sell_offer(ItemTypeId item);
OfferId  decon_find_best_buy_offer(ItemTypeId item);

#ifdef __cplusplus
}
#endif

#endif /* DOMINO_DECONOMY_H */
