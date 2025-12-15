#ifndef DG_GRAPH_ADJ_H
#define DG_GRAPH_ADJ_H

/* Deterministic adjacency storage helpers (C89).
 *
 * Adjacency is stored as per-node contiguous arrays, always sorted by:
 *   neighbor_node_id, then edge_id (ascending).
 */

#include "core/graph/dg_graph_node.h"

#ifdef __cplusplus
extern "C" {
#endif

void dg_graph_adj_free(dg_graph_node *n);

/* Insert an adjacency entry, maintaining the sorted invariant.
 * Returns 0 on success.
 */
int dg_graph_adj_insert(dg_graph_node *n, dg_node_id neighbor_id, dg_edge_id edge_id);

/* Remove an adjacency entry, maintaining the sorted invariant.
 * Returns 0 on success, 1 if not found.
 */
int dg_graph_adj_remove(dg_graph_node *n, dg_node_id neighbor_id, dg_edge_id edge_id);

u32 dg_graph_adj_count(const dg_graph_node *n);
dg_node_id dg_graph_adj_neighbor_at(const dg_graph_node *n, u32 index);
dg_edge_id dg_graph_adj_edge_at(const dg_graph_node *n, u32 index);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DG_GRAPH_ADJ_H */

