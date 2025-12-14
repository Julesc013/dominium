/* STRUCT incremental dirty tracking (C89).
 *
 * Tracks dirtiness per-structure plus an optional chunk-aligned affected region.
 * Dirty sets are stored in canonical sorted order by struct_id.
 */
#ifndef DG_STRUCT_DIRTY_H
#define DG_STRUCT_DIRTY_H

#include "domino/core/types.h"

#include "struct/model/dg_struct_ids.h"

#ifdef __cplusplus
extern "C" {
#endif

/* Dirty flags for per-structure compilation stages. */
#define DG_STRUCT_DIRTY_FOOTPRINT ((u32)0x00000001u)
#define DG_STRUCT_DIRTY_VOLUME    ((u32)0x00000002u)
#define DG_STRUCT_DIRTY_ENCLOSURE ((u32)0x00000004u)
#define DG_STRUCT_DIRTY_SURFACE   ((u32)0x00000008u)
#define DG_STRUCT_DIRTY_CARRIER   ((u32)0x00000010u)
#define DG_STRUCT_DIRTY_SUPPORT   ((u32)0x00000020u)

typedef struct dg_struct_dirty_chunk_aabb {
    d_bool dirty;
    i32    cx0;
    i32    cy0;
    i32    cz0;
    i32    cx1;
    i32    cy1;
    i32    cz1;
} dg_struct_dirty_chunk_aabb;

typedef struct dg_struct_dirty_record {
    dg_struct_id              struct_id;
    u32                      dirty_flags;
    dg_struct_dirty_chunk_aabb chunks; /* conservative union */
} dg_struct_dirty_record;

typedef struct dg_struct_dirty {
    dg_struct_dirty_record *items; /* sorted by struct_id */
    u32                    count;
    u32                    capacity;
} dg_struct_dirty;

void dg_struct_dirty_init(dg_struct_dirty *d);
void dg_struct_dirty_free(dg_struct_dirty *d);
void dg_struct_dirty_clear(dg_struct_dirty *d);

int dg_struct_dirty_reserve(dg_struct_dirty *d, u32 capacity);

/* Mark a structure dirty with optional affected chunk AABB (inclusive). */
void dg_struct_dirty_mark(dg_struct_dirty *d, dg_struct_id struct_id, u32 dirty_flags);
void dg_struct_dirty_mark_chunks(
    dg_struct_dirty *d,
    dg_struct_id     struct_id,
    u32             dirty_flags,
    i32              cx0, i32 cy0, i32 cz0,
    i32              cx1, i32 cy1, i32 cz1
);

/* Query (returns 1 if found, 0 if not). */
int dg_struct_dirty_get(const dg_struct_dirty *d, dg_struct_id struct_id, dg_struct_dirty_record *out);

/* Clear dirty bits (mask) and chunk flag (if any bits cleared to zero). */
void dg_struct_dirty_clear_flags(dg_struct_dirty *d, dg_struct_id struct_id, u32 clear_mask);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DG_STRUCT_DIRTY_H */

