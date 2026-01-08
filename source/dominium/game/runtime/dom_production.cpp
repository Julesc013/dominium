/*
FILE: source/dominium/game/runtime/dom_production.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/runtime/production
RESPONSIBILITY: Deterministic production/consumption rules (scheduled deltas).
*/
#include "runtime/dom_production.h"

#include <vector>
#include <climits>

namespace {

struct ProductionRule {
    dom_production_rule_id rule_id;
    dom_station_id station_id;
    dom_resource_id resource_id;
    i64 delta_per_period;
    u64 period_ticks;
};

static int find_rule_index(const std::vector<ProductionRule> &list,
                           dom_production_rule_id rule_id) {
    size_t i;
    for (i = 0u; i < list.size(); ++i) {
        if (list[i].rule_id == rule_id) {
            return (int)i;
        }
    }
    return -1;
}

static void insert_rule_sorted(std::vector<ProductionRule> &list,
                               const ProductionRule &rule) {
    size_t i = 0u;
    while (i < list.size() && list[i].rule_id < rule.rule_id) {
        ++i;
    }
    list.insert(list.begin() + (std::vector<ProductionRule>::difference_type)i, rule);
}

static int validate_rule_desc(const dom_production_rule_desc *desc) {
    if (!desc) {
        return DOM_PRODUCTION_INVALID_ARGUMENT;
    }
    if (desc->rule_id == 0ull ||
        desc->station_id == 0ull ||
        desc->resource_id == 0ull) {
        return DOM_PRODUCTION_INVALID_DATA;
    }
    if (desc->delta_per_period == 0) {
        return DOM_PRODUCTION_INVALID_DATA;
    }
    if (desc->period_ticks == 0ull) {
        return DOM_PRODUCTION_INVALID_DATA;
    }
    return DOM_PRODUCTION_OK;
}

} // namespace

struct dom_production {
    std::vector<ProductionRule> rules;
    u64 last_tick;
};

dom_production *dom_production_create(void) {
    dom_production *prod = new dom_production();
    if (!prod) {
        return 0;
    }
    (void)dom_production_init(prod);
    return prod;
}

void dom_production_destroy(dom_production *prod) {
    if (!prod) {
        return;
    }
    delete prod;
}

int dom_production_init(dom_production *prod) {
    if (!prod) {
        return DOM_PRODUCTION_INVALID_ARGUMENT;
    }
    prod->rules.clear();
    prod->last_tick = 0ull;
    return DOM_PRODUCTION_OK;
}

int dom_production_register(dom_production *prod,
                            const dom_production_rule_desc *desc) {
    ProductionRule rule;
    int rc;
    if (!prod || !desc) {
        return DOM_PRODUCTION_INVALID_ARGUMENT;
    }
    rc = validate_rule_desc(desc);
    if (rc != DOM_PRODUCTION_OK) {
        return rc;
    }
    if (find_rule_index(prod->rules, desc->rule_id) >= 0) {
        return DOM_PRODUCTION_DUPLICATE_ID;
    }
    rule.rule_id = desc->rule_id;
    rule.station_id = desc->station_id;
    rule.resource_id = desc->resource_id;
    rule.delta_per_period = desc->delta_per_period;
    rule.period_ticks = desc->period_ticks;
    insert_rule_sorted(prod->rules, rule);
    return DOM_PRODUCTION_OK;
}

int dom_production_iterate(const dom_production *prod,
                           dom_production_iter_fn fn,
                           void *user) {
    size_t i;
    if (!prod || !fn) {
        return DOM_PRODUCTION_INVALID_ARGUMENT;
    }
    for (i = 0u; i < prod->rules.size(); ++i) {
        const ProductionRule &rule = prod->rules[i];
        dom_production_rule_info info;
        info.rule_id = rule.rule_id;
        info.station_id = rule.station_id;
        info.resource_id = rule.resource_id;
        info.delta_per_period = rule.delta_per_period;
        info.period_ticks = rule.period_ticks;
        fn(&info, user);
    }
    return DOM_PRODUCTION_OK;
}

u32 dom_production_count(const dom_production *prod) {
    if (!prod) {
        return 0u;
    }
    return (u32)prod->rules.size();
}

int dom_production_update(dom_production *prod,
                          dom_station_registry *stations,
                          u64 current_tick) {
    if (!prod || !stations) {
        return DOM_PRODUCTION_INVALID_ARGUMENT;
    }
    if (current_tick <= prod->last_tick) {
        prod->last_tick = current_tick;
        return DOM_PRODUCTION_OK;
    }

    for (size_t i = 0u; i < prod->rules.size(); ++i) {
        const ProductionRule &rule = prod->rules[i];
        const u64 period = rule.period_ticks;
        const u64 prev_bucket = (period > 0ull) ? (prod->last_tick / period) : 0ull;
        const u64 curr_bucket = current_tick / period;
        u64 ticks_to_apply = (curr_bucket > prev_bucket) ? (curr_bucket - prev_bucket) : 0ull;

        if (ticks_to_apply == 0ull) {
            continue;
        }

        i64 delta = rule.delta_per_period;
        i64 total_delta = 0;
        if (delta > 0) {
            if (ticks_to_apply > (u64)(LLONG_MAX / delta)) {
                return DOM_PRODUCTION_OVERFLOW;
            }
            total_delta = (i64)ticks_to_apply * delta;
            if (dom_station_inventory_add(stations,
                                          rule.station_id,
                                          rule.resource_id,
                                          total_delta) != DOM_STATION_REGISTRY_OK) {
                return DOM_PRODUCTION_ERR;
            }
        } else {
            i64 magnitude = -delta;
            if (ticks_to_apply > (u64)(LLONG_MAX / magnitude)) {
                return DOM_PRODUCTION_OVERFLOW;
            }
            total_delta = (i64)ticks_to_apply * magnitude;
            if (dom_station_inventory_remove(stations,
                                             rule.station_id,
                                             rule.resource_id,
                                             total_delta) != DOM_STATION_REGISTRY_OK) {
                return DOM_PRODUCTION_INSUFFICIENT;
            }
        }
    }

    prod->last_tick = current_tick;
    return DOM_PRODUCTION_OK;
}

int dom_production_set_last_tick(dom_production *prod, u64 last_tick) {
    if (!prod) {
        return DOM_PRODUCTION_INVALID_ARGUMENT;
    }
    prod->last_tick = last_tick;
    return DOM_PRODUCTION_OK;
}

u64 dom_production_last_tick(const dom_production *prod) {
    if (!prod) {
        return 0ull;
    }
    return prod->last_tick;
}
