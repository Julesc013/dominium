/*
FILE: source/dominium/game/runtime/dom_route_graph.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/runtime/route_graph
RESPONSIBILITY: Deterministic route registry for scheduled transfers.
*/
#include "runtime/dom_route_graph.h"

#include <vector>

namespace {

struct RouteEntry {
    dom_route_id route_id;
    dom_station_id src_station_id;
    dom_station_id dst_station_id;
    u64 duration_ticks;
    u64 capacity_units;
};

static int find_route_index(const std::vector<RouteEntry> &list,
                            dom_route_id route_id) {
    size_t i;
    for (i = 0u; i < list.size(); ++i) {
        if (list[i].route_id == route_id) {
            return (int)i;
        }
    }
    return -1;
}

static void insert_route_sorted(std::vector<RouteEntry> &list,
                                const RouteEntry &entry) {
    size_t i = 0u;
    while (i < list.size() && list[i].route_id < entry.route_id) {
        ++i;
    }
    list.insert(list.begin() + (std::vector<RouteEntry>::difference_type)i, entry);
}

static int validate_route_desc(const dom_route_desc *desc) {
    if (!desc) {
        return DOM_ROUTE_GRAPH_INVALID_ARGUMENT;
    }
    if (desc->route_id == 0ull ||
        desc->src_station_id == 0ull ||
        desc->dst_station_id == 0ull) {
        return DOM_ROUTE_GRAPH_INVALID_DATA;
    }
    if (desc->duration_ticks == 0ull || desc->capacity_units == 0ull) {
        return DOM_ROUTE_GRAPH_INVALID_DATA;
    }
    return DOM_ROUTE_GRAPH_OK;
}

} // namespace

struct dom_route_graph {
    std::vector<RouteEntry> routes;
};

dom_route_graph *dom_route_graph_create(void) {
    dom_route_graph *graph = new dom_route_graph();
    if (!graph) {
        return 0;
    }
    (void)dom_route_graph_init(graph);
    return graph;
}

void dom_route_graph_destroy(dom_route_graph *graph) {
    if (!graph) {
        return;
    }
    delete graph;
}

int dom_route_graph_init(dom_route_graph *graph) {
    if (!graph) {
        return DOM_ROUTE_GRAPH_INVALID_ARGUMENT;
    }
    graph->routes.clear();
    return DOM_ROUTE_GRAPH_OK;
}

int dom_route_graph_register(dom_route_graph *graph, const dom_route_desc *desc) {
    RouteEntry entry;
    int rc;
    if (!graph || !desc) {
        return DOM_ROUTE_GRAPH_INVALID_ARGUMENT;
    }
    rc = validate_route_desc(desc);
    if (rc != DOM_ROUTE_GRAPH_OK) {
        return rc;
    }
    if (find_route_index(graph->routes, desc->route_id) >= 0) {
        return DOM_ROUTE_GRAPH_DUPLICATE_ID;
    }
    entry.route_id = desc->route_id;
    entry.src_station_id = desc->src_station_id;
    entry.dst_station_id = desc->dst_station_id;
    entry.duration_ticks = desc->duration_ticks;
    entry.capacity_units = desc->capacity_units;
    insert_route_sorted(graph->routes, entry);
    return DOM_ROUTE_GRAPH_OK;
}

int dom_route_graph_get(const dom_route_graph *graph,
                        dom_route_id route_id,
                        dom_route_info *out_info) {
    int idx;
    if (!graph || !out_info) {
        return DOM_ROUTE_GRAPH_INVALID_ARGUMENT;
    }
    idx = find_route_index(graph->routes, route_id);
    if (idx < 0) {
        return DOM_ROUTE_GRAPH_NOT_FOUND;
    }
    {
        const RouteEntry &entry = graph->routes[(size_t)idx];
        out_info->route_id = entry.route_id;
        out_info->src_station_id = entry.src_station_id;
        out_info->dst_station_id = entry.dst_station_id;
        out_info->duration_ticks = entry.duration_ticks;
        out_info->capacity_units = entry.capacity_units;
    }
    return DOM_ROUTE_GRAPH_OK;
}

int dom_route_graph_iterate(const dom_route_graph *graph,
                            dom_route_iter_fn fn,
                            void *user) {
    size_t i;
    if (!graph || !fn) {
        return DOM_ROUTE_GRAPH_INVALID_ARGUMENT;
    }
    for (i = 0u; i < graph->routes.size(); ++i) {
        const RouteEntry &entry = graph->routes[i];
        dom_route_info info;
        info.route_id = entry.route_id;
        info.src_station_id = entry.src_station_id;
        info.dst_station_id = entry.dst_station_id;
        info.duration_ticks = entry.duration_ticks;
        info.capacity_units = entry.capacity_units;
        fn(&info, user);
    }
    return DOM_ROUTE_GRAPH_OK;
}

u32 dom_route_graph_count(const dom_route_graph *graph) {
    if (!graph) {
        return 0u;
    }
    return (u32)graph->routes.size();
}
