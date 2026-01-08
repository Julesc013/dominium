/*
FILE: source/dominium/game/runtime/dom_route_graph.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/runtime/route_graph
RESPONSIBILITY: Deterministic route registry for scheduled transfers.
ALLOWED DEPENDENCIES: `include/domino/**`, `source/dominium/**`, C++98 STL.
FORBIDDEN DEPENDENCIES: OS headers; non-deterministic inputs.
*/
#ifndef DOM_ROUTE_GRAPH_H
#define DOM_ROUTE_GRAPH_H

#include "domino/core/types.h"
#include "runtime/dom_station_registry.h"

#ifdef __cplusplus
extern "C" {
#endif

enum {
    DOM_ROUTE_GRAPH_OK = 0,
    DOM_ROUTE_GRAPH_ERR = -1,
    DOM_ROUTE_GRAPH_INVALID_ARGUMENT = -2,
    DOM_ROUTE_GRAPH_DUPLICATE_ID = -3,
    DOM_ROUTE_GRAPH_NOT_FOUND = -4,
    DOM_ROUTE_GRAPH_INVALID_DATA = -5
};

typedef u64 dom_route_id;

typedef struct dom_route_desc {
    dom_route_id route_id;
    dom_station_id src_station_id;
    dom_station_id dst_station_id;
    u64 duration_ticks;
    u64 capacity_units;
} dom_route_desc;

typedef struct dom_route_info {
    dom_route_id route_id;
    dom_station_id src_station_id;
    dom_station_id dst_station_id;
    u64 duration_ticks;
    u64 capacity_units;
} dom_route_info;

typedef void (*dom_route_iter_fn)(const dom_route_info *info, void *user);

typedef struct dom_route_graph dom_route_graph;

dom_route_graph *dom_route_graph_create(void);
void dom_route_graph_destroy(dom_route_graph *graph);
int dom_route_graph_init(dom_route_graph *graph);

int dom_route_graph_register(dom_route_graph *graph, const dom_route_desc *desc);
int dom_route_graph_get(const dom_route_graph *graph,
                        dom_route_id route_id,
                        dom_route_info *out_info);
int dom_route_graph_iterate(const dom_route_graph *graph,
                            dom_route_iter_fn fn,
                            void *user);
u32 dom_route_graph_count(const dom_route_graph *graph);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOM_ROUTE_GRAPH_H */
