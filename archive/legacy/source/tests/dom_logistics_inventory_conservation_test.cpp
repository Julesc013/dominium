/*
FILE: source/tests/dom_logistics_inventory_conservation_test.cpp
MODULE: Repository
PURPOSE: Ensures transfers conserve inventory exactly.
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

int main(void) {
    dom_station_registry *reg = dom_station_registry_create();
    dom_route_graph *graph = dom_route_graph_create();
    dom_transfer_scheduler *sched = dom_transfer_scheduler_create();
    dom_station_desc s1;
    dom_station_desc s2;
    dom_route_desc route;
    dom_transfer_entry entry;
    dom_transfer_id out_id = 0ull;

    assert(reg && graph && sched);
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
    assert(dom_station_inventory_add(reg, s1.station_id, 700ull, 30) == DOM_STATION_REGISTRY_OK);

    route.route_id = 10ull;
    route.src_station_id = s1.station_id;
    route.dst_station_id = s2.station_id;
    route.duration_ticks = 3ull;
    route.capacity_units = 50ull;
    assert(dom_route_graph_register(graph, &route) == DOM_ROUTE_GRAPH_OK);

    entry.resource_id = 700ull;
    entry.quantity = 10;
    assert(dom_transfer_schedule(sched, graph, reg, route.route_id, &entry, 1u, 1ull, &out_id) == DOM_TRANSFER_OK);

    assert(station_qty(reg, s1.station_id, 700ull) == 20);
    assert(station_qty(reg, s2.station_id, 700ull) == 0);

    assert(dom_transfer_update(sched, graph, reg, 4ull) == DOM_TRANSFER_OK);
    assert(station_qty(reg, s1.station_id, 700ull) == 20);
    assert(station_qty(reg, s2.station_id, 700ull) == 10);
    assert(station_qty(reg, s1.station_id, 700ull) + station_qty(reg, s2.station_id, 700ull) == 30);

    dom_transfer_scheduler_destroy(sched);
    dom_route_graph_destroy(graph);
    dom_station_registry_destroy(reg);

    std::printf("dom_logistics_inventory_conservation_test: OK\n");
    return 0;
}
