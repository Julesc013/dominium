/*
FILE: source/tests/dom_logistics_schedule_determinism_test.cpp
MODULE: Repository
PURPOSE: Ensures transfer arrivals are deterministic under tick batching.
*/
#include <cassert>
#include <cstdio>

#include "runtime/dom_station_registry.h"
#include "runtime/dom_route_graph.h"
#include "runtime/dom_transfer_scheduler.h"

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

static void setup_baseline(dom_station_registry *reg,
                           dom_route_graph *graph,
                           dom_transfer_scheduler *sched) {
    dom_station_desc s1;
    dom_station_desc s2;
    dom_route_desc route;

    assert(dom_station_registry_init(reg) == DOM_STATION_REGISTRY_OK);
    assert(dom_route_graph_init(graph) == DOM_ROUTE_GRAPH_OK);
    assert(dom_transfer_scheduler_init(sched) == DOM_TRANSFER_OK);

    s1.station_id = 1ull;
    s1.body_id = 100ull;
    s1.frame_id = 0ull;
    s2.station_id = 2ull;
    s2.body_id = 100ull;
    s2.frame_id = 0ull;
    assert(dom_station_register(reg, &s1) == DOM_STATION_REGISTRY_OK);
    assert(dom_station_register(reg, &s2) == DOM_STATION_REGISTRY_OK);
    assert(dom_station_inventory_add(reg, s1.station_id, 500ull, 50) == DOM_STATION_REGISTRY_OK);

    route.route_id = 10ull;
    route.src_station_id = s1.station_id;
    route.dst_station_id = s2.station_id;
    route.duration_ticks = 5ull;
    route.capacity_units = 50ull;
    assert(dom_route_graph_register(graph, &route) == DOM_ROUTE_GRAPH_OK);
}

int main(void) {
    dom_station_registry *reg_a = dom_station_registry_create();
    dom_station_registry *reg_b = dom_station_registry_create();
    dom_route_graph *graph_a = dom_route_graph_create();
    dom_route_graph *graph_b = dom_route_graph_create();
    dom_transfer_scheduler *sched_a = dom_transfer_scheduler_create();
    dom_transfer_scheduler *sched_b = dom_transfer_scheduler_create();
    dom_transfer_entry entry;
    dom_transfer_id out_id = 0ull;

    assert(reg_a && reg_b && graph_a && graph_b && sched_a && sched_b);

    setup_baseline(reg_a, graph_a, sched_a);
    setup_baseline(reg_b, graph_b, sched_b);

    entry.resource_id = 500ull;
    entry.quantity = 20;
    assert(dom_transfer_schedule(sched_a, graph_a, reg_a, 10ull, &entry, 1u, 1ull, &out_id) == DOM_TRANSFER_OK);
    assert(dom_transfer_schedule(sched_b, graph_b, reg_b, 10ull, &entry, 1u, 1ull, &out_id) == DOM_TRANSFER_OK);

    for (u64 tick = 1ull; tick <= 6ull; ++tick) {
        assert(dom_transfer_update(sched_a, graph_a, reg_a, tick) == DOM_TRANSFER_OK);
    }
    assert(dom_transfer_update(sched_b, graph_b, reg_b, 6ull) == DOM_TRANSFER_OK);

    assert(station_qty(reg_a, 1ull, 500ull) == station_qty(reg_b, 1ull, 500ull));
    assert(station_qty(reg_a, 2ull, 500ull) == station_qty(reg_b, 2ull, 500ull));

    dom_transfer_scheduler_destroy(sched_b);
    dom_transfer_scheduler_destroy(sched_a);
    dom_route_graph_destroy(graph_b);
    dom_route_graph_destroy(graph_a);
    dom_station_registry_destroy(reg_b);
    dom_station_registry_destroy(reg_a);

    std::printf("dom_logistics_schedule_determinism_test: OK\n");
    return 0;
}
