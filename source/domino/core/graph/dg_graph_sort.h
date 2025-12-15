#ifndef DG_GRAPH_SORT_H
#define DG_GRAPH_SORT_H

/* Deterministic sorting helpers used by graph infrastructure (C89). */

#include "domino/core/types.h"
#include "core/graph/dg_graph_node.h"

#ifdef __cplusplus
extern "C" {
#endif

void dg_graph_sort_u32(u32 *v, u32 n);
void dg_graph_sort_u64(u64 *v, u32 n);

void dg_graph_sort_node_ids(dg_node_id *v, u32 n);
void dg_graph_sort_edge_ids(dg_edge_id *v, u32 n);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DG_GRAPH_SORT_H */

