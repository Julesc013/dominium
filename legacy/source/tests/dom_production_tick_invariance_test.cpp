/*
FILE: source/tests/dom_production_tick_invariance_test.cpp
MODULE: Repository
PURPOSE: Ensures production deltas are invariant under tick batching.
*/
#include <cassert>
#include <cstdio>

#include "runtime/dom_station_registry.h"
#include "runtime/dom_production.h"

static i64 station_qty(const dom_station_registry *reg,
                        dom_station_id station_id,
                        dom_resource_id resource_id) {
    i64 qty = 0;
    int rc = dom_station_inventory_get(reg, station_id, resource_id, &qty);
    if (rc != DOM_STATION_REGISTRY_OK) {
        return 0;
    }
    return qty;
}

static void setup(dom_station_registry *reg, dom_production *prod) {
    dom_station_desc s1;
    dom_production_rule_desc rule;
    assert(dom_station_registry_init(reg) == DOM_STATION_REGISTRY_OK);
    assert(dom_production_init(prod) == DOM_PRODUCTION_OK);

    s1.station_id = 1ull;
    s1.body_id = 200ull;
    s1.frame_id = 0ull;
    assert(dom_station_register(reg, &s1) == DOM_STATION_REGISTRY_OK);

    rule.rule_id = 1ull;
    rule.station_id = s1.station_id;
    rule.resource_id = 900ull;
    rule.delta_per_period = 5;
    rule.period_ticks = 4ull;
    assert(dom_production_register(prod, &rule) == DOM_PRODUCTION_OK);
}

int main(void) {
    dom_station_registry *reg_a = dom_station_registry_create();
    dom_station_registry *reg_b = dom_station_registry_create();
    dom_production *prod_a = dom_production_create();
    dom_production *prod_b = dom_production_create();
    i64 qty_a = 0;
    i64 qty_b = 0;

    assert(reg_a && reg_b && prod_a && prod_b);

    setup(reg_a, prod_a);
    setup(reg_b, prod_b);

    for (u64 tick = 1ull; tick <= 12ull; ++tick) {
        assert(dom_production_update(prod_a, reg_a, tick) == DOM_PRODUCTION_OK);
    }
    assert(dom_production_update(prod_b, reg_b, 12ull) == DOM_PRODUCTION_OK);

    qty_a = station_qty(reg_a, 1ull, 900ull);
    qty_b = station_qty(reg_b, 1ull, 900ull);
    assert(qty_a == 15);
    assert(qty_b == 15);

    dom_production_destroy(prod_b);
    dom_production_destroy(prod_a);
    dom_station_registry_destroy(reg_b);
    dom_station_registry_destroy(reg_a);

    std::printf("dom_production_tick_invariance_test: OK\n");
    return 0;
}
