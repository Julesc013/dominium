/* TRANS microsegment model + chunk-aligned spatial index (C89). */
#ifndef DG_TRANS_MICROSEG_H
#define DG_TRANS_MICROSEG_H

#include "domino/core/types.h"

#include "core/dg_pose.h"
#include "trans/model/dg_trans_ids.h"
#include "trans/compile/dg_trans_frame.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dg_trans_aabb {
    dg_vec3_q min;
    dg_vec3_q max;
} dg_trans_aabb;

typedef struct dg_trans_microseg {
    dg_trans_segment_id id;
    dg_q                s_begin;
    dg_q                s_end;
    dg_trans_aabb       bbox;
    dg_trans_frame      frame0; /* local frame at s_begin */
} dg_trans_microseg;

/* Chunk coordinate triple for indices (canonical lexicographic ordering). */
typedef struct dg_trans_chunk_coord {
    i32 cx;
    i32 cy;
    i32 cz;
} dg_trans_chunk_coord;

typedef struct dg_trans_spatial_entry {
    dg_trans_chunk_coord chunk;
    dg_trans_segment_id  seg_id;
    dg_trans_aabb        bbox;
} dg_trans_spatial_entry;

typedef struct dg_trans_spatial_index {
    dg_trans_spatial_entry *entries;
    u32                     count;
    u32                     capacity;
    u32                     probe_refused;
    d_bool                  owns_storage;
} dg_trans_spatial_index;

void dg_trans_spatial_index_init(dg_trans_spatial_index *idx);
void dg_trans_spatial_index_free(dg_trans_spatial_index *idx);
int  dg_trans_spatial_index_reserve(dg_trans_spatial_index *idx, u32 capacity);
void dg_trans_spatial_index_clear(dg_trans_spatial_index *idx);

u32 dg_trans_spatial_index_count(const dg_trans_spatial_index *idx);
u32 dg_trans_spatial_index_capacity(const dg_trans_spatial_index *idx);
u32 dg_trans_spatial_index_probe_refused(const dg_trans_spatial_index *idx);

/* Remove all entries associated with the given segment id. Returns number removed. */
u32 dg_trans_spatial_index_remove_segment(dg_trans_spatial_index *idx, const dg_trans_segment_id *seg_id);

/* Insert the segment into all chunks overlapped by its bbox.
 * chunk_size_q MUST be > 0.
 * Returns 0 on success, >0 if partially refused (capacity), <0 on error.
 */
int dg_trans_spatial_index_add_segment(dg_trans_spatial_index *idx, const dg_trans_microseg *seg, dg_q chunk_size_q);

/* Query entries in the chunk containing 'pos'. Returns number written. */
u32 dg_trans_spatial_query_pos(
    const dg_trans_spatial_index *idx,
    dg_vec3_q                     pos,
    dg_q                          chunk_size_q,
    dg_trans_segment_id          *out_seg_ids,
    u32                           max_out
);

/* Query entries overlapping an AABB by visiting all overlapped chunks. */
u32 dg_trans_spatial_query_aabb(
    const dg_trans_spatial_index *idx,
    const dg_trans_aabb          *query,
    dg_q                          chunk_size_q,
    dg_trans_segment_id          *out_seg_ids,
    u32                           max_out
);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DG_TRANS_MICROSEG_H */

