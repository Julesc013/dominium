/*
FILE: source/dominium/game/runtime/dom_macro_economy.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/runtime/macro_economy
RESPONSIBILITY: Deterministic macro economy aggregates (system/galaxy scopes).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/dominium/**`, C++98 STL.
FORBIDDEN DEPENDENCIES: OS headers; non-deterministic inputs.
*/
#ifndef DOM_MACRO_ECONOMY_H
#define DOM_MACRO_ECONOMY_H

#include "domino/core/types.h"
#include "runtime/dom_station_registry.h"

#ifdef __cplusplus
extern "C" {
#endif

enum {
    DOM_MACRO_ECONOMY_OK = 0,
    DOM_MACRO_ECONOMY_ERR = -1,
    DOM_MACRO_ECONOMY_INVALID_ARGUMENT = -2,
    DOM_MACRO_ECONOMY_DUPLICATE_ID = -3,
    DOM_MACRO_ECONOMY_NOT_FOUND = -4,
    DOM_MACRO_ECONOMY_INVALID_DATA = -5,
    DOM_MACRO_ECONOMY_OVERFLOW = -6
};

enum dom_macro_scope_kind {
    DOM_MACRO_SCOPE_SYSTEM = 1u,
    DOM_MACRO_SCOPE_GALAXY = 2u
};

typedef struct dom_macro_rate_entry {
    dom_resource_id resource_id;
    i64 rate_per_tick;
} dom_macro_rate_entry;

typedef struct dom_macro_stock_entry {
    dom_resource_id resource_id;
    i64 quantity;
} dom_macro_stock_entry;

typedef struct dom_macro_scope_info {
    u32 scope_kind;
    u64 scope_id;
    u32 flags;
    u32 production_count;
    u32 demand_count;
    u32 stockpile_count;
} dom_macro_scope_info;

typedef void (*dom_macro_scope_iter_fn)(const dom_macro_scope_info *info, void *user);

typedef struct dom_macro_economy dom_macro_economy;

dom_macro_economy *dom_macro_economy_create(void);
void dom_macro_economy_destroy(dom_macro_economy *econ);
int dom_macro_economy_init(dom_macro_economy *econ);

int dom_macro_economy_register_system(dom_macro_economy *econ, u64 system_id);
int dom_macro_economy_register_galaxy(dom_macro_economy *econ, u64 galaxy_id);

int dom_macro_economy_get_scope(const dom_macro_economy *econ,
                                u32 scope_kind,
                                u64 scope_id,
                                dom_macro_scope_info *out_info);
int dom_macro_economy_list_scopes(const dom_macro_economy *econ,
                                  u32 scope_kind,
                                  dom_macro_scope_info *out_infos,
                                  u32 max_infos,
                                  u32 *out_count);
int dom_macro_economy_iterate(const dom_macro_economy *econ,
                              u32 scope_kind,
                              dom_macro_scope_iter_fn fn,
                              void *user);

int dom_macro_economy_rate_get(const dom_macro_economy *econ,
                               u32 scope_kind,
                               u64 scope_id,
                               dom_resource_id resource_id,
                               i64 *out_production_rate,
                               i64 *out_demand_rate);
int dom_macro_economy_rate_set(dom_macro_economy *econ,
                               u32 scope_kind,
                               u64 scope_id,
                               dom_resource_id resource_id,
                               i64 production_rate,
                               i64 demand_rate);
int dom_macro_economy_rate_delta(dom_macro_economy *econ,
                                 u32 scope_kind,
                                 u64 scope_id,
                                 dom_resource_id resource_id,
                                 i64 production_delta,
                                 i64 demand_delta);
int dom_macro_economy_list_production(const dom_macro_economy *econ,
                                      u32 scope_kind,
                                      u64 scope_id,
                                      dom_macro_rate_entry *out_entries,
                                      u32 max_entries,
                                      u32 *out_count);
int dom_macro_economy_list_demand(const dom_macro_economy *econ,
                                  u32 scope_kind,
                                  u64 scope_id,
                                  dom_macro_rate_entry *out_entries,
                                  u32 max_entries,
                                  u32 *out_count);

int dom_macro_economy_stockpile_get(const dom_macro_economy *econ,
                                    u32 scope_kind,
                                    u64 scope_id,
                                    dom_resource_id resource_id,
                                    i64 *out_quantity);
int dom_macro_economy_stockpile_set(dom_macro_economy *econ,
                                    u32 scope_kind,
                                    u64 scope_id,
                                    dom_resource_id resource_id,
                                    i64 quantity);
int dom_macro_economy_stockpile_delta(dom_macro_economy *econ,
                                      u32 scope_kind,
                                      u64 scope_id,
                                      dom_resource_id resource_id,
                                      i64 delta);
int dom_macro_economy_list_stockpile(const dom_macro_economy *econ,
                                     u32 scope_kind,
                                     u64 scope_id,
                                     dom_macro_stock_entry *out_entries,
                                     u32 max_entries,
                                     u32 *out_count);

int dom_macro_economy_flags_apply(dom_macro_economy *econ,
                                  u32 scope_kind,
                                  u64 scope_id,
                                  u32 flags_set,
                                  u32 flags_clear);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOM_MACRO_ECONOMY_H */
