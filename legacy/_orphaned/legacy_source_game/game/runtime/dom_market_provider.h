/*
FILE: source/dominium/game/runtime/dom_market_provider.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/runtime/market_provider
RESPONSIBILITY: Deterministic market provider interface and shared types.
ALLOWED DEPENDENCIES: `include/domino/**`, `source/dominium/**`, C++98 STL for impl.
FORBIDDEN DEPENDENCIES: OS headers; floating point; nondeterministic inputs.
*/
#ifndef DOM_MARKET_PROVIDER_H
#define DOM_MARKET_PROVIDER_H

#include "domino/core/types.h"
#include "domino/core/dom_time_core.h"
#include "domino/core/dom_ledger.h"

#ifdef __cplusplus
extern "C" {
#endif

enum {
    DOM_MARKET_OK = 0,
    DOM_MARKET_ERR = -1,
    DOM_MARKET_INVALID_ARGUMENT = -2,
    DOM_MARKET_DUPLICATE_ID = -3,
    DOM_MARKET_NOT_FOUND = -4,
    DOM_MARKET_NOT_IMPLEMENTED = -5,
    DOM_MARKET_REFUSED = -6,
    DOM_MARKET_INSUFFICIENT = -7,
    DOM_MARKET_OVERFLOW = -8
};

typedef u64 dom_market_id;
typedef u64 dom_market_order_id;
typedef u64 dom_market_trade_id;

enum {
    DOM_MARKET_SIDE_BUY = 1u,
    DOM_MARKET_SIDE_SELL = 2u
};

enum {
    DOM_MARKET_TIF_GTC = 1u,
    DOM_MARKET_TIF_IOC = 2u,
    DOM_MARKET_TIF_FOK = 3u
};

enum {
    DOM_MARKET_PROVIDER_BARTER = 1u,
    DOM_MARKET_PROVIDER_FIXED_PRICE = 2u,
    DOM_MARKET_PROVIDER_AUCTION = 3u,
    DOM_MARKET_PROVIDER_ORDERBOOK = 4u,
    DOM_MARKET_PROVIDER_CLEARINGHOUSE = 5u
};

typedef struct dom_market_spec {
    const char *id;
    u32 id_len;
    dom_market_id id_hash;
    u32 provider_kind;
    dom_asset_id_t base_asset_id;
    dom_asset_id_t quote_asset_id;
    dom_account_id_t market_account_id;
    u32 price_scale;
    dom_act_time_t clear_interval_ticks;
    i64 fixed_price;
    u32 max_matches_per_clear;
} dom_market_spec;

typedef struct dom_market_order {
    dom_market_order_id order_id;
    dom_account_id_t account_id;
    u64 actor_id;
    u32 side;
    dom_asset_id_t base_asset_id;
    dom_asset_id_t quote_asset_id;
    dom_asset_id_t asset_in;
    dom_asset_id_t asset_out;
    i64 quantity_base;
    i64 quantity_in;
    i64 quantity_out;
    i64 limit_price;
    u32 time_in_force;
    dom_act_time_t submit_tick;
} dom_market_order;

typedef struct dom_market_trade {
    dom_market_trade_id trade_id;
    dom_market_order_id buy_order_id;
    dom_market_order_id sell_order_id;
    dom_account_id_t buy_account_id;
    dom_account_id_t sell_account_id;
    dom_asset_id_t base_asset_id;
    dom_asset_id_t quote_asset_id;
    i64 quantity_base;
    i64 quantity_quote;
    i64 price;
    dom_act_time_t execution_tick;
    dom_act_time_t settlement_tick;
} dom_market_trade;

typedef struct dom_market_quote {
    dom_market_id market_id;
    i64 bid_price;
    i64 ask_price;
    i64 last_price;
    dom_act_time_t quote_tick;
    u32 staleness_ticks;
    u32 resolution_tier;
    u32 uncertainty_flags;
} dom_market_quote;

typedef struct dom_market_clear_result {
    const dom_market_trade *trades;
    u32 trade_count;
    const dom_market_quote *quotes;
    u32 quote_count;
    dom_act_time_t next_due_tick;
} dom_market_clear_result;

typedef struct dom_market_order_ack {
    u32 status;
    dom_market_order_id order_id;
    dom_act_time_t next_due_tick;
} dom_market_order_ack;

typedef struct dom_market_provider_vtbl {
    int (*init)(void *state, const dom_market_spec *spec);
    int (*submit_order)(void *state,
                        const dom_market_order *order,
                        dom_market_order_ack *out_ack);
    int (*cancel_order)(void *state, dom_market_order_id order_id);
    int (*clear)(void *state, dom_act_time_t now, dom_market_clear_result *out_result);
    int (*next_due_tick)(void *state, dom_act_time_t *out_tick);
    void (*destroy)(void *state);
} dom_market_provider_vtbl;

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOM_MARKET_PROVIDER_H */
