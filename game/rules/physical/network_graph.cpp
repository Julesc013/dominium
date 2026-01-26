/*
FILE: game/rules/physical/network_graph.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Game / physical
RESPONSIBILITY: Implements a unified network graph model for infrastructure.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Network operations are deterministic for identical inputs.
*/
#include "dominium/physical/network_graph.h"

#include <string.h>

void dom_network_graph_init(dom_network_graph* graph,
                            u32 type,
                            dom_network_node* nodes,
                            u32 node_capacity,
                            dom_network_edge* edges,
                            u32 edge_capacity)
{
    if (!graph) {
        return;
    }
    graph->type = type;
    graph->nodes = nodes;
    graph->node_count = 0u;
    graph->node_capacity = node_capacity;
    graph->edges = edges;
    graph->edge_count = 0u;
    graph->edge_capacity = edge_capacity;
    if (nodes && node_capacity > 0u) {
        memset(nodes, 0, sizeof(dom_network_node) * (size_t)node_capacity);
    }
    if (edges && edge_capacity > 0u) {
        memset(edges, 0, sizeof(dom_network_edge) * (size_t)edge_capacity);
    }
}

dom_network_node* dom_network_add_node(dom_network_graph* graph,
                                       u64 node_id,
                                       i32 capacity_q16)
{
    dom_network_node* node;
    if (!graph || !graph->nodes || graph->node_count >= graph->node_capacity) {
        return 0;
    }
    node = &graph->nodes[graph->node_count++];
    memset(node, 0, sizeof(*node));
    node->node_id = node_id;
    node->status = DOM_NETWORK_OK;
    node->capacity_q16 = capacity_q16;
    node->stored_q16 = 0;
    node->loss_q16 = 0;
    node->min_required_q16 = 0;
    return node;
}

dom_network_edge* dom_network_add_edge(dom_network_graph* graph,
                                       u64 edge_id,
                                       u64 a,
                                       u64 b,
                                       i32 capacity_q16,
                                       i32 loss_q16)
{
    dom_network_edge* edge;
    if (!graph || !graph->edges || graph->edge_count >= graph->edge_capacity) {
        return 0;
    }
    edge = &graph->edges[graph->edge_count++];
    memset(edge, 0, sizeof(*edge));
    edge->edge_id = edge_id;
    edge->a = a;
    edge->b = b;
    edge->status = DOM_NETWORK_OK;
    edge->capacity_q16 = capacity_q16;
    edge->loss_q16 = loss_q16;
    return edge;
}

dom_network_node* dom_network_find_node(dom_network_graph* graph,
                                        u64 node_id)
{
    u32 i;
    if (!graph || !graph->nodes) {
        return 0;
    }
    for (i = 0u; i < graph->node_count; ++i) {
        if (graph->nodes[i].node_id == node_id) {
            return &graph->nodes[i];
        }
    }
    return 0;
}

dom_network_edge* dom_network_find_edge(dom_network_graph* graph,
                                        u64 edge_id)
{
    u32 i;
    if (!graph || !graph->edges) {
        return 0;
    }
    for (i = 0u; i < graph->edge_count; ++i) {
        if (graph->edges[i].edge_id == edge_id) {
            return &graph->edges[i];
        }
    }
    return 0;
}

static dom_network_edge* dom_network_find_direct(dom_network_graph* graph,
                                                 u64 a,
                                                 u64 b)
{
    u32 i;
    if (!graph || !graph->edges) {
        return 0;
    }
    for (i = 0u; i < graph->edge_count; ++i) {
        dom_network_edge* edge = &graph->edges[i];
        if ((edge->a == a && edge->b == b) || (edge->a == b && edge->b == a)) {
            return edge;
        }
    }
    return 0;
}

int dom_network_route_flow(dom_network_graph* graph,
                           u64 from_node,
                           u64 to_node,
                           i32 amount_q16,
                           dom_physical_audit_log* audit,
                           dom_act_time_t now_act)
{
    dom_network_edge* edge;
    if (!graph) {
        return -1;
    }
    edge = dom_network_find_direct(graph, from_node, to_node);
    if (!edge) {
        return -2;
    }
    if (edge->status == DOM_NETWORK_FAILED) {
        return -3;
    }
    if (amount_q16 > edge->capacity_q16) {
        edge->status = DOM_NETWORK_FAILED;
        if (audit) {
            dom_physical_audit_set_context(audit, now_act, 0u);
            dom_physical_audit_record(audit,
                                      from_node,
                                      DOM_PHYS_EVENT_NETWORK_OVERLOAD,
                                      edge->edge_id,
                                      to_node,
                                      (i64)amount_q16);
            dom_physical_audit_record(audit,
                                      from_node,
                                      DOM_PHYS_EVENT_NETWORK_FAIL,
                                      edge->edge_id,
                                      to_node,
                                      (i64)amount_q16);
        }
        return -4;
    }
    if (audit) {
        dom_physical_audit_set_context(audit, now_act, 0u);
        dom_physical_audit_record(audit,
                                  from_node,
                                  DOM_PHYS_EVENT_NETWORK_CONNECT,
                                  edge->edge_id,
                                  to_node,
                                  (i64)amount_q16);
    }
    return 0;
}

int dom_network_store(dom_network_graph* graph,
                      u64 node_id,
                      i32 amount_q16,
                      dom_physical_audit_log* audit,
                      dom_act_time_t now_act)
{
    dom_network_node* node;
    if (!graph || amount_q16 <= 0) {
        return -1;
    }
    node = dom_network_find_node(graph, node_id);
    if (!node) {
        return -2;
    }
    if (node->status == DOM_NETWORK_FAILED) {
        return -3;
    }
    if (node->capacity_q16 > 0 && node->stored_q16 + amount_q16 > node->capacity_q16) {
        node->status = DOM_NETWORK_FAILED;
        if (audit) {
            dom_physical_audit_set_context(audit, now_act, 0u);
            dom_physical_audit_record(audit,
                                      node_id,
                                      DOM_PHYS_EVENT_NETWORK_OVERLOAD,
                                      node_id,
                                      0u,
                                      (i64)(node->stored_q16 + amount_q16));
            dom_physical_audit_record(audit,
                                      node_id,
                                      DOM_PHYS_EVENT_NETWORK_FAIL,
                                      node_id,
                                      0u,
                                      (i64)(node->stored_q16 + amount_q16));
        }
        return -4;
    }
    node->stored_q16 += amount_q16;
    if (audit) {
        dom_physical_audit_set_context(audit, now_act, 0u);
        dom_physical_audit_record(audit,
                                  node_id,
                                  DOM_PHYS_EVENT_NETWORK_CONNECT,
                                  node_id,
                                  0u,
                                  (i64)amount_q16);
    }
    return 0;
}

int dom_network_withdraw(dom_network_graph* graph,
                         u64 node_id,
                         i32 amount_q16,
                         dom_physical_audit_log* audit,
                         dom_act_time_t now_act)
{
    dom_network_node* node;
    if (!graph || amount_q16 <= 0) {
        return -1;
    }
    node = dom_network_find_node(graph, node_id);
    if (!node) {
        return -2;
    }
    if (node->status == DOM_NETWORK_FAILED) {
        return -3;
    }
    if (node->stored_q16 < amount_q16) {
        node->status = DOM_NETWORK_FAILED;
        if (audit) {
            dom_physical_audit_set_context(audit, now_act, 0u);
            dom_physical_audit_record(audit,
                                      node_id,
                                      DOM_PHYS_EVENT_NETWORK_FAIL,
                                      node_id,
                                      0u,
                                      (i64)node->stored_q16);
        }
        return -4;
    }
    node->stored_q16 -= amount_q16;
    return 0;
}

int dom_network_transfer(dom_network_graph* graph,
                         u64 from_node,
                         u64 to_node,
                         i32 amount_q16,
                         dom_physical_audit_log* audit,
                         dom_act_time_t now_act)
{
    dom_network_edge* edge;
    i32 loss_q16 = 0;
    i32 delivered_q16;
    if (!graph || amount_q16 <= 0) {
        return -1;
    }
    edge = dom_network_find_direct(graph, from_node, to_node);
    if (!edge) {
        return -2;
    }
    if (edge->status == DOM_NETWORK_FAILED) {
        return -3;
    }
    if (amount_q16 > edge->capacity_q16) {
        edge->status = DOM_NETWORK_FAILED;
        if (audit) {
            dom_physical_audit_set_context(audit, now_act, 0u);
            dom_physical_audit_record(audit,
                                      from_node,
                                      DOM_PHYS_EVENT_NETWORK_OVERLOAD,
                                      edge->edge_id,
                                      to_node,
                                      (i64)amount_q16);
            dom_physical_audit_record(audit,
                                      from_node,
                                      DOM_PHYS_EVENT_NETWORK_FAIL,
                                      edge->edge_id,
                                      to_node,
                                      (i64)amount_q16);
        }
        return -4;
    }
    if (edge->loss_q16 > 0) {
        loss_q16 = (i32)(((i64)amount_q16 * (i64)edge->loss_q16) >> 16);
    }
    delivered_q16 = amount_q16 - loss_q16;
    if (delivered_q16 < 0) {
        delivered_q16 = 0;
    }
    if (dom_network_withdraw(graph, from_node, amount_q16, audit, now_act) != 0) {
        return -5;
    }
    if (dom_network_store(graph, to_node, delivered_q16, audit, now_act) != 0) {
        return -6;
    }
    if (audit) {
        dom_physical_audit_set_context(audit, now_act, 0u);
        dom_physical_audit_record(audit,
                                  from_node,
                                  DOM_PHYS_EVENT_NETWORK_CONNECT,
                                  edge->edge_id,
                                  to_node,
                                  (i64)amount_q16);
    }
    return 0;
}

int dom_network_tick(dom_network_graph* graph,
                     dom_physical_audit_log* audit,
                     dom_act_time_t now_act)
{
    u32 i;
    if (!graph) {
        return -1;
    }
    for (i = 0u; i < graph->node_count; ++i) {
        dom_network_node* node = &graph->nodes[i];
        if (node->status == DOM_NETWORK_FAILED) {
            continue;
        }
        if (node->loss_q16 > 0 && node->stored_q16 > 0) {
            node->stored_q16 -= node->loss_q16;
            if (node->stored_q16 < 0) {
                node->stored_q16 = 0;
            }
        }
        if (node->min_required_q16 > 0 && node->stored_q16 < node->min_required_q16) {
            node->status = DOM_NETWORK_FAILED;
            if (audit) {
                dom_physical_audit_set_context(audit, now_act, 0u);
                dom_physical_audit_record(audit,
                                          node->node_id,
                                          DOM_PHYS_EVENT_NETWORK_FAIL,
                                          node->node_id,
                                          0u,
                                          (i64)node->stored_q16);
            }
        }
    }
    for (i = 0u; i < graph->edge_count; ++i) {
        dom_network_edge* edge = &graph->edges[i];
        dom_network_node* a = dom_network_find_node(graph, edge->a);
        dom_network_node* b = dom_network_find_node(graph, edge->b);
        if (edge->status == DOM_NETWORK_FAILED) {
            continue;
        }
        if ((a && a->status == DOM_NETWORK_FAILED) ||
            (b && b->status == DOM_NETWORK_FAILED)) {
            edge->status = DOM_NETWORK_FAILED;
            if (audit) {
                dom_physical_audit_set_context(audit, now_act, 0u);
                dom_physical_audit_record(audit,
                                          0u,
                                          DOM_PHYS_EVENT_NETWORK_FAIL,
                                          edge->edge_id,
                                          0u,
                                          0);
            }
        }
    }
    return 0;
}

int dom_network_fail_edge(dom_network_graph* graph,
                          u64 edge_id,
                          dom_physical_audit_log* audit,
                          dom_act_time_t now_act)
{
    dom_network_edge* edge = dom_network_find_edge(graph, edge_id);
    if (!edge) {
        return -1;
    }
    edge->status = DOM_NETWORK_FAILED;
    if (audit) {
        dom_physical_audit_set_context(audit, now_act, 0u);
        dom_physical_audit_record(audit,
                                  0u,
                                  DOM_PHYS_EVENT_NETWORK_FAIL,
                                  edge_id,
                                  0u,
                                  0);
    }
    return 0;
}

int dom_network_repair_edge(dom_network_graph* graph,
                            u64 edge_id)
{
    dom_network_edge* edge = dom_network_find_edge(graph, edge_id);
    if (!edge) {
        return -1;
    }
    edge->status = DOM_NETWORK_OK;
    return 0;
}
