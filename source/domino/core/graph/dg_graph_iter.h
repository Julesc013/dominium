/*
FILE: source/domino/core/graph/dg_graph_iter.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / core/graph/dg_graph_iter
RESPONSIBILITY: Implements `dg_graph_iter`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DG_GRAPH_ITER_H
#define DG_GRAPH_ITER_H

/* Deterministic traversal helpers (C89).
 *
 * Traversals are deterministic because neighbor iteration order is canonical
 * (sorted adjacency) and queue/stack behavior is fixed.
 */

#include "core/graph/dg_graph.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dg_graph_neighbor {
    dg_node_id neighbor_id;
    dg_edge_id edge_id;
} dg_graph_neighbor;

typedef struct dg_graph_neighbors_iter {
    const dg_graph_node *node;
    u32                  index;
} dg_graph_neighbors_iter;

dg_graph_neighbors_iter dg_graph_neighbors(const dg_graph *g, dg_node_id node_id);
d_bool dg_graph_neighbors_next(dg_graph_neighbors_iter *it, dg_graph_neighbor *out);

typedef void (*dg_graph_visit_fn)(dg_node_id node_id, void *user_ctx);

/* Canonical BFS/DFS from a single start node.
 * Returns 0 on success, 1 if start node missing.
 */
int dg_graph_bfs(const dg_graph *g, dg_node_id start_id, dg_graph_visit_fn fn, void *user_ctx);
int dg_graph_dfs(const dg_graph *g, dg_node_id start_id, dg_graph_visit_fn fn, void *user_ctx);

/* Topological walk helper (if acyclic). Uses edge direction flags:
 * - Directed edges contribute one arc (a->b).
 * - Undirected edges contribute two arcs (a->b and b->a) and will generally
 *   create cycles.
 * Returns 0 on success, 1 if a cycle is detected.
 */
int dg_graph_topo_walk(const dg_graph *g, dg_graph_visit_fn fn, void *user_ctx);

/* Unweighted shortest path scaffolding (BFS). Outputs the path as node IDs
 * from start to goal (inclusive) into out_path.
 * Returns 0 on success, 1 if no path, 2 if start/goal missing.
 */
int dg_graph_shortest_path_unweighted(
    const dg_graph *g,
    dg_node_id      start_id,
    dg_node_id      goal_id,
    dg_node_id     *out_path,
    u32             out_cap,
    u32            *out_len
);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DG_GRAPH_ITER_H */

