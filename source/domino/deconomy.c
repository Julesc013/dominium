#include "domino/deconomy.h"

#include <string.h>

#define DECON_MAX_MARKETS 128
#define DECON_MAX_OFFERS  1024

static Market g_markets[DECON_MAX_MARKETS];
static Offer  g_offers[DECON_MAX_OFFERS];
static MarketId g_market_count = 0;
static OfferId  g_offer_count = 0;

MarketId decon_market_register(const Market *def)
{
    Market copy;
    if (!def || !def->name) return 0;
    if (g_market_count >= (MarketId)DECON_MAX_MARKETS) return 0;
    copy = *def;
    if (copy.id == 0) {
        copy.id = (MarketId)(g_market_count + 1);
    }
    g_markets[g_market_count] = copy;
    g_market_count++;
    return copy.id;
}

Market *decon_market_get(MarketId id)
{
    if (id == 0 || id > g_market_count) return 0;
    return &g_markets[id - 1];
}

OfferId decon_offer_register(const Offer *def)
{
    Offer copy;
    if (!def) return 0;
    if (g_offer_count >= (OfferId)DECON_MAX_OFFERS) return 0;
    copy = *def;
    if (copy.id == 0) {
        copy.id = (OfferId)(g_offer_count + 1);
    }
    g_offers[g_offer_count] = copy;
    g_offer_count++;
    return copy.id;
}

Offer *decon_offer_get(OfferId id)
{
    if (id == 0 || id > g_offer_count) return 0;
    return &g_offers[id - 1];
}

OfferId decon_find_best_sell_offer(ItemTypeId item)
{
    OfferId best_id = 0;
    Q16_16 best_price = 0;
    U32 i;
    for (i = 0; i < g_offer_count; ++i) {
        Offer *o = &g_offers[i];
        if (o->item != item) continue;
        if (o->type != OFFER_SELL) continue;
        if (o->quantity == 0) continue;
        if (best_id == 0 || o->price_per_unit < best_price) {
            best_price = o->price_per_unit;
            best_id = o->id;
        }
    }
    return best_id;
}

OfferId decon_find_best_buy_offer(ItemTypeId item)
{
    OfferId best_id = 0;
    Q16_16 best_price = 0;
    U32 i;
    for (i = 0; i < g_offer_count; ++i) {
        Offer *o = &g_offers[i];
        if (o->item != item) continue;
        if (o->type != OFFER_BUY) continue;
        if (o->quantity == 0) continue;
        if (best_id == 0 || o->price_per_unit > best_price) {
            best_price = o->price_per_unit;
            best_id = o->id;
        }
    }
    return best_id;
}
