/*
FILE: source/domino/struct/compile/dg_struct_support_graph.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / struct/compile/dg_struct_support_graph
RESPONSIBILITY: Defines internal contract for `dg_struct_support_graph`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
/* STRUCT support/load graph compilation (C89).
 *
 * Produces a deterministic topology of support nodes/edges and a chunk-aligned
 * index for later load/path systems. No physics solving is performed here.
 */
#ifndef DG_STRUCT_SUPPORT_GRAPH_H
#define DG_STRUCT_SUPPORT_GRAPH_H

#include "domino/core/types.h"

#include "core/dg_pose.h"
#include "struct/model/dg_struct_ids.h"
#include "struct/compile/dg_struct_occupancy.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dg_struct_support_node {
    dg_struct_support_node_id id;
    dg_struct_id              struct_id;
    dg_vec3_q                 pos_world;
    dg_q                      capacity;
} dg_struct_support_node;

typedef struct dg_struct_support_edge {
    dg_struct_support_edge_id id;
    dg_struct_id              struct_id;
    dg_struct_support_node_id a;
    dg_struct_support_node_id b;
    dg_q                      capacity;
} dg_struct_support_edge;

typedef struct dg_struct_support_graph {
    dg_struct_support_node *nodes; /* sorted by node_id */
    u32                     node_count;
    u32                     node_capacity;

    dg_struct_support_edge *edges; /* sorted by edge_id */
    u32                     edge_count;
    u32                     edge_capacity;
} dg_struct_support_graph;

typedef struct dg_struct_support_spatial_entry {
    dg_struct_chunk_coord       chunk;
    dg_struct_id                struct_id;
    dg_struct_support_node_id   node_id;
    dg_vec3_q                   pos_world;
} dg_struct_support_spatial_entry;

typedef struct dg_struct_support_spatial_index {
    dg_struct_support_spatial_entry *entries;
    u32                             count;
    u32                             capacity;
    u32                             probe_refused;
    d_bool                          owns_storage;
} dg_struct_support_spatial_index;

void dg_struct_support_graph_init(dg_struct_support_graph *g);
void dg_struct_support_graph_free(dg_struct_support_graph *g);
void dg_struct_support_graph_clear(dg_struct_support_graph *g);
int  dg_struct_support_graph_reserve(dg_struct_support_graph *g, u32 node_cap, u32 edge_cap);

void dg_struct_support_spatial_index_init(dg_struct_support_spatial_index *idx);
void dg_struct_support_spatial_index_free(dg_struct_support_spatial_index *idx);
int  dg_struct_support_spatial_index_reserve(dg_struct_support_spatial_index *idx, u32 capacity);
void dg_struct_support_spatial_index_clear(dg_struct_support_spatial_index *idx);
u32  dg_struct_support_spatial_index_remove_struct(dg_struct_support_spatial_index *idx, dg_struct_id struct_id);

/* Rebuild support graph for one structure from its occupancy cache.
 * Returns 0 on success, >0 if spatial inserts were partially refused, <0 on error.
 */
int dg_struct_support_graph_rebuild(
    dg_struct_support_graph       *out,
    dg_struct_support_spatial_index *spatial,
    dg_struct_id                   struct_id,
    const dg_struct_occupancy     *occ,
    dg_q                          chunk_size_q
);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DG_STRUCT_SUPPORT_GRAPH_H */

