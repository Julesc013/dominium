/*
FILE: include/dominium/physical/network_graph.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / physical
RESPONSIBILITY: Defines a unified network graph model for infrastructure.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Network operations are deterministic for identical inputs.
*/
#ifndef DOMINIUM_PHYSICAL_NETWORK_GRAPH_H
#define DOMINIUM_PHYSICAL_NETWORK_GRAPH_H

#include "domino/core/types.h"
#include "dominium/physical/physical_audit.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum dom_network_type {
    DOM_NETWORK_ELECTRICAL = 1,
    DOM_NETWORK_THERMAL = 2,
    DOM_NETWORK_FLUID = 3,
    DOM_NETWORK_LOGISTICS = 4,
    DOM_NETWORK_DATA = 5
} dom_network_type;

typedef enum dom_network_status {
    DOM_NETWORK_OK = 0,
    DOM_NETWORK_FAILED = 1
} dom_network_status;

typedef struct dom_network_node {
    u64 node_id;
    u32 status;
    i32 capacity_q16;
    i32 stored_q16;
    i32 loss_q16;
    i32 min_required_q16;
} dom_network_node;

typedef struct dom_network_edge {
    u64 edge_id;
    u64 a;
    u64 b;
    u32 status;
    i32 capacity_q16;
    i32 loss_q16;
} dom_network_edge;

typedef struct dom_network_graph {
    u32 type;
    dom_network_node* nodes;
    u32 node_count;
    u32 node_capacity;
    dom_network_edge* edges;
    u32 edge_count;
    u32 edge_capacity;
} dom_network_graph;

void dom_network_graph_init(dom_network_graph* graph,
                            u32 type,
                            dom_network_node* nodes,
                            u32 node_capacity,
                            dom_network_edge* edges,
                            u32 edge_capacity);
dom_network_node* dom_network_add_node(dom_network_graph* graph,
                                       u64 node_id,
                                       i32 capacity_q16);
dom_network_edge* dom_network_add_edge(dom_network_graph* graph,
                                       u64 edge_id,
                                       u64 a,
                                       u64 b,
                                       i32 capacity_q16,
                                       i32 loss_q16);
dom_network_node* dom_network_find_node(dom_network_graph* graph,
                                        u64 node_id);
dom_network_edge* dom_network_find_edge(dom_network_graph* graph,
                                        u64 edge_id);

int dom_network_route_flow(dom_network_graph* graph,
                           u64 from_node,
                           u64 to_node,
                           i32 amount_q16,
                           dom_physical_audit_log* audit,
                           dom_act_time_t now_act);
int dom_network_store(dom_network_graph* graph,
                      u64 node_id,
                      i32 amount_q16,
                      dom_physical_audit_log* audit,
                      dom_act_time_t now_act);
int dom_network_withdraw(dom_network_graph* graph,
                         u64 node_id,
                         i32 amount_q16,
                         dom_physical_audit_log* audit,
                         dom_act_time_t now_act);
int dom_network_transfer(dom_network_graph* graph,
                         u64 from_node,
                         u64 to_node,
                         i32 amount_q16,
                         dom_physical_audit_log* audit,
                         dom_act_time_t now_act);
int dom_network_tick(dom_network_graph* graph,
                     dom_physical_audit_log* audit,
                     dom_act_time_t now_act);
int dom_network_fail_edge(dom_network_graph* graph,
                          u64 edge_id,
                          dom_physical_audit_log* audit,
                          dom_act_time_t now_act);
int dom_network_repair_edge(dom_network_graph* graph,
                            u64 edge_id);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_PHYSICAL_NETWORK_GRAPH_H */
