/*
FILE: source/dominium/game/runtime/dom_production.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/runtime/production
RESPONSIBILITY: Deterministic production/consumption rules (scheduled deltas).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/dominium/**`, C++98 STL.
FORBIDDEN DEPENDENCIES: OS headers; non-deterministic inputs.
*/
#ifndef DOM_PRODUCTION_H
#define DOM_PRODUCTION_H

#include "domino/core/types.h"
#include "runtime/dom_station_registry.h"

#ifdef __cplusplus
extern "C" {
#endif

enum {
    DOM_PRODUCTION_OK = 0,
    DOM_PRODUCTION_ERR = -1,
    DOM_PRODUCTION_INVALID_ARGUMENT = -2,
    DOM_PRODUCTION_DUPLICATE_ID = -3,
    DOM_PRODUCTION_NOT_FOUND = -4,
    DOM_PRODUCTION_INVALID_DATA = -5,
    DOM_PRODUCTION_INSUFFICIENT = -6,
    DOM_PRODUCTION_OVERFLOW = -7
};

typedef u64 dom_production_rule_id;

typedef struct dom_production_rule_desc {
    dom_production_rule_id rule_id;
    dom_station_id station_id;
    dom_resource_id resource_id;
    i64 delta_per_period;
    u64 period_ticks;
} dom_production_rule_desc;

typedef struct dom_production_rule_info {
    dom_production_rule_id rule_id;
    dom_station_id station_id;
    dom_resource_id resource_id;
    i64 delta_per_period;
    u64 period_ticks;
} dom_production_rule_info;

typedef void (*dom_production_iter_fn)(const dom_production_rule_info *info, void *user);

typedef struct dom_production dom_production;

dom_production *dom_production_create(void);
void dom_production_destroy(dom_production *prod);
int dom_production_init(dom_production *prod);

int dom_production_register(dom_production *prod,
                            const dom_production_rule_desc *desc);
int dom_production_iterate(const dom_production *prod,
                           dom_production_iter_fn fn,
                           void *user);
u32 dom_production_count(const dom_production *prod);

int dom_production_update(dom_production *prod,
                          dom_station_registry *stations,
                          u64 current_tick);
int dom_production_set_last_tick(dom_production *prod, u64 last_tick);
u64 dom_production_last_tick(const dom_production *prod);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOM_PRODUCTION_H */
