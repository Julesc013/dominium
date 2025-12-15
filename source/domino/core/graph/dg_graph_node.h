#ifndef DG_GRAPH_NODE_H
#define DG_GRAPH_NODE_H

/* Canonical deterministic graph node identity (C89).
 *
 * Node/edge IDs are stable fixed-size integers. ID value 0 is reserved as an
 * invalid/sentinel identifier.
 */

#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef u32 dg_node_id;
typedef u32 dg_edge_id;

#define DG_NODE_ID_INVALID ((dg_node_id)0u)
#define DG_EDGE_ID_INVALID ((dg_edge_id)0u)

typedef struct dg_graph_node {
    dg_node_id id;

    /* Adjacency is stored as per-node contiguous SoA arrays, kept sorted by:
     *   (neighbor_node_id, edge_id) ascending.
     */
    dg_node_id *neighbor_ids;
    dg_edge_id *edge_ids;
    u32         adj_count;
    u32         adj_capacity;
} dg_graph_node;

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DG_GRAPH_NODE_H */

