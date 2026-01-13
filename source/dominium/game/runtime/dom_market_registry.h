/*
FILE: source/dominium/game/runtime/dom_market_registry.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/runtime/market_registry
RESPONSIBILITY: Deterministic market registry and provider dispatch.
ALLOWED DEPENDENCIES: `include/domino/**`, `source/dominium/**`, C++98 STL.
FORBIDDEN DEPENDENCIES: OS headers; floating point; nondeterministic inputs.
*/
#ifndef DOM_MARKET_REGISTRY_H
#define DOM_MARKET_REGISTRY_H

#include <string>

extern "C" {
#include "domino/core/types.h"
}

#include "runtime/dom_market_provider.h"

typedef struct dom_market_registry dom_market_registry;

dom_market_registry *dom_market_registry_create(void);
void dom_market_registry_destroy(dom_market_registry *registry);

int dom_market_registry_register(dom_market_registry *registry,
                                 const dom_market_spec *spec);
int dom_market_registry_get(const dom_market_registry *registry,
                            dom_market_id id_hash,
                            dom_market_spec *out_spec);

int dom_market_registry_submit_order(dom_market_registry *registry,
                                     dom_market_id market_id,
                                     const dom_market_order *order,
                                     dom_market_order_ack *out_ack);
int dom_market_registry_cancel_order(dom_market_registry *registry,
                                     dom_market_id market_id,
                                     dom_market_order_id order_id);
int dom_market_registry_clear(dom_market_registry *registry,
                              dom_market_id market_id,
                              dom_act_time_t now,
                              dom_market_clear_result *out_result);
int dom_market_registry_next_due_tick(dom_market_registry *registry,
                                      dom_market_id market_id,
                                      dom_act_time_t *out_tick);

int dom_market_registry_next_global_due(dom_market_registry *registry,
                                        dom_act_time_t *out_tick);

int dom_market_registry_settle_trades(dom_market_registry *registry,
                                      dom_ledger *ledger,
                                      const dom_market_trade *trades,
                                      u32 trade_count,
                                      dom_act_time_t act_time);

const char *dom_market_registry_last_error(const dom_market_registry *registry);

#endif /* DOM_MARKET_REGISTRY_H */
