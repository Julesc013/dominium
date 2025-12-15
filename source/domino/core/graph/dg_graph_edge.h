#ifndef DG_GRAPH_EDGE_H
#define DG_GRAPH_EDGE_H

/* Canonical deterministic graph edge identity (C89). */

#include "core/graph/dg_graph_node.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef u32 dg_edge_flags;

#define DG_EDGE_FLAG_NONE     0u
#define DG_EDGE_FLAG_DIRECTED 1u /* interpret (a -> b) */

typedef struct dg_graph_edge {
    dg_edge_id    id;
    dg_node_id    a;
    dg_node_id    b;
    dg_edge_flags flags;
} dg_graph_edge;

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DG_GRAPH_EDGE_H */

