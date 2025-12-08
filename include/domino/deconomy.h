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
