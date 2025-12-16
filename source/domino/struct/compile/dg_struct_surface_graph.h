/*
FILE: source/domino/struct/compile/dg_struct_surface_graph.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / struct/compile/dg_struct_surface_graph
RESPONSIBILITY: Implements `dg_struct_surface_graph`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
/* STRUCT surface graph compilation (C89).
 *
 * Compiles authored surface templates + sockets into a stable surface graph
 * with parameterization frames (u,v) and chunk-aligned spatial indices.
 */
#ifndef DG_STRUCT_SURFACE_GRAPH_H
#define DG_STRUCT_SURFACE_GRAPH_H

#include "domino/core/types.h"

#include "core/dg_pose.h"
#include "sim/pkt/dg_pkt_common.h"

#include "struct/model/dg_struct_ids.h"
#include "struct/model/dg_struct_instance.h"
#include "struct/model/dg_struct_surface.h"
#include "struct/model/dg_struct_socket.h"
#include "struct/model/dg_struct_footprint.h"
#include "struct/model/dg_struct_volume.h"
#include "struct/compile/dg_struct_occupancy.h"
#include "world/frame/d_world_frame.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dg_struct_compiled_surface {
    dg_struct_surface_id          id;
    dg_struct_id                  struct_id;
    dg_struct_surface_template_id template_id;

    dg_struct_volume_id           volume_id;
    dg_struct_enclosure_id        enclosure_id;
    dg_struct_volume_face_kind    face_kind;
    u32                           face_index;

    /* Parameterization: world-space origin + basis vectors spanning the surface.
     * u_vec_world and v_vec_world include extents (not unit length).
     */
    dg_vec3_q origin_world;
    dg_vec3_q u_vec_world;
    dg_vec3_q v_vec_world;
    dg_q      u_len;
    dg_q      v_len;

    dg_struct_aabb bbox_world;
} dg_struct_compiled_surface;

typedef struct dg_struct_compiled_socket {
    dg_struct_socket_id  id;
    dg_struct_id         struct_id;
    dg_struct_surface_id surface_id;
    dg_q                 u;
    dg_q                 v;
    dg_q                 offset;
} dg_struct_compiled_socket;

typedef struct dg_struct_surface_graph {
    dg_struct_compiled_surface *surfaces; /* sorted by surface_id */
    u32                        surface_count;
    u32                        surface_capacity;

    dg_struct_compiled_socket *sockets; /* sorted by socket_id */
    u32                       socket_count;
    u32                       socket_capacity;
} dg_struct_surface_graph;

typedef struct dg_struct_surface_spatial_entry {
    dg_struct_chunk_coord chunk;
    dg_struct_id          struct_id;
    dg_struct_surface_id  surface_id;
    dg_struct_aabb        bbox;
} dg_struct_surface_spatial_entry;

typedef struct dg_struct_surface_spatial_index {
    dg_struct_surface_spatial_entry *entries;
    u32                             count;
    u32                             capacity;
    u32                             probe_refused;
    d_bool                          owns_storage;
} dg_struct_surface_spatial_index;

void dg_struct_surface_graph_init(dg_struct_surface_graph *g);
void dg_struct_surface_graph_free(dg_struct_surface_graph *g);
void dg_struct_surface_graph_clear(dg_struct_surface_graph *g);
int  dg_struct_surface_graph_reserve(dg_struct_surface_graph *g, u32 surface_cap, u32 socket_cap);

void dg_struct_surface_spatial_index_init(dg_struct_surface_spatial_index *idx);
void dg_struct_surface_spatial_index_free(dg_struct_surface_spatial_index *idx);
int  dg_struct_surface_spatial_index_reserve(dg_struct_surface_spatial_index *idx, u32 capacity);
void dg_struct_surface_spatial_index_clear(dg_struct_surface_spatial_index *idx);
u32  dg_struct_surface_spatial_index_remove_struct(dg_struct_surface_spatial_index *idx, dg_struct_id struct_id);

/* Rebuild surfaces + sockets for one structure and update the shared spatial index.
 * Returns 0 on success, >0 if spatial inserts were partially refused, <0 on error.
 */
int dg_struct_surface_graph_rebuild(
    dg_struct_surface_graph        *out,
    dg_struct_surface_spatial_index *spatial,
    const dg_struct_instance       *inst,
    dg_struct_id                    struct_id,
    const dg_struct_surface_template *templates,
    u32                             template_count,
    const dg_struct_socket          *sockets,
    u32                             socket_count,
    const dg_struct_footprint       *footprints,
    u32                             footprint_count,
    const dg_struct_volume          *volumes,
    u32                             volume_count,
    const d_world_frame             *frames,
    dg_tick                         tick,
    dg_q                            chunk_size_q
);

/* Deterministic stable surface_id derivation used by sockets and anchors. */
dg_struct_surface_id dg_struct_surface_id_make(dg_struct_id struct_id, dg_struct_surface_template_id template_id);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DG_STRUCT_SURFACE_GRAPH_H */

