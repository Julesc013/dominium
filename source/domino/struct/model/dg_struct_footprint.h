/* STRUCT footprint authoring model (C89).
 *
 * A footprint is a parametric polygon defined in the local structure frame:
 * - vertices are fixed-point (dg_q == Q48.16)
 * - no axis alignment assumptions
 * - holes are represented as additional rings
 * - winding is canonicalized deterministically:
 *     outer rings: CCW (positive signed area)
 *     hole rings : CW  (negative signed area)
 */
#ifndef DG_STRUCT_FOOTPRINT_H
#define DG_STRUCT_FOOTPRINT_H

#include "domino/core/types.h"

#include "core/dg_pose.h"
#include "struct/model/dg_struct_ids.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dg_struct_footprint_vertex {
    u32  vertex_index; /* local ordering key (monotonic by convention) */
    dg_q x;
    dg_q y;
} dg_struct_footprint_vertex;

typedef struct dg_struct_footprint_ring {
    u32    ring_index; /* 0 = outer ring by convention */
    d_bool is_hole;
    u32    _pad32;

    dg_struct_footprint_vertex *verts; /* sorted by vertex_index */
    u32                         vert_count;
    u32                         vert_capacity;
} dg_struct_footprint_ring;

typedef struct dg_struct_footprint_aabb2 {
    dg_q min_x;
    dg_q min_y;
    dg_q max_x;
    dg_q max_y;
} dg_struct_footprint_aabb2;

typedef struct dg_struct_footprint {
    dg_struct_footprint_id id;

    dg_struct_footprint_ring *rings; /* sorted by ring_index */
    u32                       ring_count;
    u32                       ring_capacity;
} dg_struct_footprint;

void dg_struct_footprint_init(dg_struct_footprint *fp);
void dg_struct_footprint_free(dg_struct_footprint *fp);

int dg_struct_footprint_reserve_rings(dg_struct_footprint *fp, u32 capacity);
int dg_struct_footprint_set_ring(dg_struct_footprint *fp, u32 ring_index, d_bool is_hole);
int dg_struct_footprint_reserve_ring_verts(dg_struct_footprint *fp, u32 ring_index, u32 capacity);
int dg_struct_footprint_set_vertex(dg_struct_footprint *fp, u32 ring_index, u32 vertex_index, dg_q x, dg_q y);

dg_struct_footprint_ring *dg_struct_footprint_find_ring(dg_struct_footprint *fp, u32 ring_index);
const dg_struct_footprint_ring *dg_struct_footprint_find_ring_const(const dg_struct_footprint *fp, u32 ring_index);

/* Canonicalize winding in-place (see header rules). Returns 0 on success. */
int dg_struct_footprint_canon_winding(dg_struct_footprint *fp);

/* Validate structural and winding invariants. Returns 0 if valid, <0 otherwise. */
int dg_struct_footprint_validate(const dg_struct_footprint *fp);

/* Compute a local-space AABB over all rings. Returns 0 on success. */
int dg_struct_footprint_get_aabb2(const dg_struct_footprint *fp, dg_struct_footprint_aabb2 *out);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DG_STRUCT_FOOTPRINT_H */
