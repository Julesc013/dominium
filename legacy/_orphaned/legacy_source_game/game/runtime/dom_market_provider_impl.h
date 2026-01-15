/*
FILE: source/dominium/game/runtime/dom_market_provider_impl.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/runtime/market_provider_impl
RESPONSIBILITY: Internal provider factory hooks for market registry.
*/
#ifndef DOM_MARKET_PROVIDER_IMPL_H
#define DOM_MARKET_PROVIDER_IMPL_H

#include "runtime/dom_market_provider.h"

int dom_market_provider_create_barter(dom_market_provider_vtbl *out_vtbl, void **out_state);
int dom_market_provider_create_fixed_price(dom_market_provider_vtbl *out_vtbl, void **out_state);
int dom_market_provider_create_auction(dom_market_provider_vtbl *out_vtbl, void **out_state);
int dom_market_provider_create_orderbook(dom_market_provider_vtbl *out_vtbl, void **out_state);
int dom_market_provider_create_clearinghouse(dom_market_provider_vtbl *out_vtbl, void **out_state);

#endif /* DOM_MARKET_PROVIDER_IMPL_H */
