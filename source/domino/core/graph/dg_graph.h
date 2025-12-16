/*
FILE: source/domino/core/graph/dg_graph.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / core/graph/dg_graph
RESPONSIBILITY: Implements `dg_graph`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DG_GRAPH_H
#define DG_GRAPH_H

/* Canonical deterministic graph storage (C89).
 *
 * - Nodes and edges have stable numeric IDs (0 is invalid).
 * - Adjacency is stored as per-node contiguous arrays sorted by:
 *     (neighbor_node_id, edge_id) ascending.
 * - Graph-wide node/edge tables are stored sorted by ID.
 */

#include "domino/core/types.h"

#include "core/graph/dg_graph_node.h"
#include "core/graph/dg_graph_edge.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dg_graph {
    dg_graph_node *nodes; /* sorted by node_id */
    u32            node_count;
    u32            node_capacity;

    dg_graph_edge *edges; /* sorted by edge_id */
    u32            edge_count;
    u32            edge_capacity;

    dg_node_id next_node_id; /* deterministic allocator state */
    dg_edge_id next_edge_id; /* deterministic allocator state */
} dg_graph;

void dg_graph_init(dg_graph *g);
void dg_graph_free(dg_graph *g);

/* Ensure capacities are at least the requested values (preserves contents). */
int dg_graph_reserve(dg_graph *g, u32 node_capacity, u32 edge_capacity);

u32 dg_graph_node_count(const dg_graph *g);
u32 dg_graph_edge_count(const dg_graph *g);

const dg_graph_node *dg_graph_node_at(const dg_graph *g, u32 index);
const dg_graph_edge *dg_graph_edge_at(const dg_graph *g, u32 index);

/* Find by ID (canonical tables are sorted). Returns NULL if absent. */
const dg_graph_node *dg_graph_find_node(const dg_graph *g, dg_node_id id);
const dg_graph_edge *dg_graph_find_edge(const dg_graph *g, dg_edge_id id);

/* Find by ID, returning the canonical index on success.
 * Returns 0 if found, 1 if not found, <0 on error.
 */
int dg_graph_find_node_index(const dg_graph *g, dg_node_id id, u32 *out_index);
int dg_graph_find_edge_index(const dg_graph *g, dg_edge_id id, u32 *out_index);

/* Add a node. If 'id' is DG_NODE_ID_INVALID, a deterministic ID is allocated.
 * Returns 0 on success.
 */
int dg_graph_add_node(dg_graph *g, dg_node_id id, dg_node_id *out_id);

/* Add an undirected edge between a and b.
 * If 'id' is DG_EDGE_ID_INVALID, a deterministic ID is allocated.
 * Returns 0 on success.
 */
int dg_graph_add_edge(dg_graph *g, dg_edge_id id, dg_node_id a, dg_node_id b, dg_edge_id *out_id);

/* Add a directed edge a->b (adjacency stored only on a). */
int dg_graph_add_edge_dir(dg_graph *g, dg_edge_id id, dg_node_id a, dg_node_id b, dg_edge_id *out_id);

/* Remove an edge by ID (removes its adjacency entries). Returns 0 on success,
 * 1 if not found.
 */
int dg_graph_remove_edge(dg_graph *g, dg_edge_id id);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DG_GRAPH_H */

