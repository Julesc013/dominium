/*
FILE: source/domino/struct/compile/dg_struct_enclosure_graph.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / struct/compile/dg_struct_enclosure_graph
RESPONSIBILITY: Implements `dg_struct_enclosure_graph`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
/* STRUCT enclosure graph compilation (C89).
 *
 * Compiles authored enclosures into a stable room graph with aperture edges,
 * plus a chunk-aligned spatial index over room bounding boxes.
 */
#ifndef DG_STRUCT_ENCLOSURE_GRAPH_H
#define DG_STRUCT_ENCLOSURE_GRAPH_H

#include "domino/core/types.h"

#include "core/dg_pose.h"
#include "sim/pkt/dg_pkt_common.h"

#include "struct/model/dg_struct_ids.h"
#include "struct/model/dg_struct_instance.h"
#include "struct/model/dg_struct_enclosure.h"
#include "struct/compile/dg_struct_occupancy.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dg_struct_room_node {
    dg_struct_room_id      id;
    dg_struct_id           struct_id;
    dg_struct_enclosure_id enclosure_id;
    dg_struct_aabb         bbox_world; /* derived (union of referenced volumes) */
} dg_struct_room_node;

typedef struct dg_struct_room_edge {
    u64                    id; /* stable edge id */
    dg_struct_room_id      room_a;
    dg_struct_room_id      room_b; /* 0 allowed for exterior */
    dg_struct_aperture_kind kind;
    u32                    _pad32;
} dg_struct_room_edge;

typedef struct dg_struct_enclosure_graph {
    dg_struct_room_node *rooms; /* sorted by room_id */
    u32                  room_count;
    u32                  room_capacity;

    dg_struct_room_edge *edges; /* sorted by (room_a, room_b, kind, id) */
    u32                  edge_count;
    u32                  edge_capacity;
} dg_struct_enclosure_graph;

typedef struct dg_struct_room_spatial_entry {
    dg_struct_chunk_coord chunk;
    dg_struct_id          struct_id;
    dg_struct_room_id     room_id;
    dg_struct_aabb        bbox;
} dg_struct_room_spatial_entry;

typedef struct dg_struct_room_spatial_index {
    dg_struct_room_spatial_entry *entries;
    u32                          count;
    u32                          capacity;
    u32                          probe_refused;
    d_bool                       owns_storage;
} dg_struct_room_spatial_index;

void dg_struct_enclosure_graph_init(dg_struct_enclosure_graph *g);
void dg_struct_enclosure_graph_free(dg_struct_enclosure_graph *g);
void dg_struct_enclosure_graph_clear(dg_struct_enclosure_graph *g);
int  dg_struct_enclosure_graph_reserve(dg_struct_enclosure_graph *g, u32 room_cap, u32 edge_cap);

void dg_struct_room_spatial_index_init(dg_struct_room_spatial_index *idx);
void dg_struct_room_spatial_index_free(dg_struct_room_spatial_index *idx);
int  dg_struct_room_spatial_index_reserve(dg_struct_room_spatial_index *idx, u32 capacity);
void dg_struct_room_spatial_index_clear(dg_struct_room_spatial_index *idx);
u32  dg_struct_room_spatial_index_remove_struct(dg_struct_room_spatial_index *idx, dg_struct_id struct_id);

/* Rebuild room nodes and aperture edges for one structure.
 * Requires an up-to-date occupancy cache for referenced volume bboxes.
 *
 * Returns 0 on success, >0 if room spatial inserts were partially refused, <0 on error.
 */
int dg_struct_enclosure_graph_rebuild(
    dg_struct_enclosure_graph   *out,
    dg_struct_room_spatial_index *spatial,
    const dg_struct_instance    *inst,
    dg_struct_id                 struct_id,
    const dg_struct_enclosure   *enclosures,
    u32                          enclosure_count,
    const dg_struct_occupancy   *occ,
    dg_q                         chunk_size_q
);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DG_STRUCT_ENCLOSURE_GRAPH_H */

