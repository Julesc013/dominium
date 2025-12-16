/*
FILE: source/domino/struct/compile/dg_struct_occupancy.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / struct/compile/dg_struct_occupancy
RESPONSIBILITY: Defines internal contract for `dg_struct_occupancy`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
/* STRUCT occupancy compilation and chunk-aligned spatial index (C89).
 *
 * Occupancy is a derived cache built from authored volumes. It is NOT
 * authoritative truth and must be rebuildable deterministically under budget.
 */
#ifndef DG_STRUCT_OCCUPANCY_H
#define DG_STRUCT_OCCUPANCY_H

#include "domino/core/types.h"

#include "core/dg_pose.h"
#include "sim/pkt/dg_pkt_common.h"

#include "struct/model/dg_struct_ids.h"
#include "struct/model/dg_struct_instance.h"
#include "struct/model/dg_struct_footprint.h"
#include "struct/model/dg_struct_volume.h"
#include "world/frame/d_world_frame.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dg_struct_aabb {
    dg_vec3_q min;
    dg_vec3_q max;
} dg_struct_aabb;

/* Chunk coordinate triple for indices (canonical lexicographic ordering). */
typedef struct dg_struct_chunk_coord {
    i32 cx;
    i32 cy;
    i32 cz;
} dg_struct_chunk_coord;

typedef struct dg_struct_occ_region {
    dg_struct_occ_region_id id;
    dg_struct_id            struct_id;
    dg_struct_volume_id     volume_id;
    d_bool                  is_void;
    u32                     _pad32;

    dg_struct_aabb bbox_world;
} dg_struct_occ_region;

typedef struct dg_struct_occupancy {
    dg_struct_occ_region *regions; /* sorted by volume_id (authoring order) */
    u32                   region_count;
    u32                   region_capacity;
} dg_struct_occupancy;

typedef struct dg_struct_occ_spatial_entry {
    dg_struct_chunk_coord    chunk;
    dg_struct_id             struct_id;
    dg_struct_occ_region_id  region_id;
    dg_struct_aabb           bbox;
} dg_struct_occ_spatial_entry;

typedef struct dg_struct_occ_spatial_index {
    dg_struct_occ_spatial_entry *entries;
    u32                         count;
    u32                         capacity;
    u32                         probe_refused;
    d_bool                      owns_storage;
} dg_struct_occ_spatial_index;

void dg_struct_occupancy_init(dg_struct_occupancy *o);
void dg_struct_occupancy_free(dg_struct_occupancy *o);
void dg_struct_occupancy_clear(dg_struct_occupancy *o);
int  dg_struct_occupancy_reserve(dg_struct_occupancy *o, u32 region_capacity);

void dg_struct_occ_spatial_index_init(dg_struct_occ_spatial_index *idx);
void dg_struct_occ_spatial_index_free(dg_struct_occ_spatial_index *idx);
int  dg_struct_occ_spatial_index_reserve(dg_struct_occ_spatial_index *idx, u32 capacity);
void dg_struct_occ_spatial_index_clear(dg_struct_occ_spatial_index *idx);

u32 dg_struct_occ_spatial_index_count(const dg_struct_occ_spatial_index *idx);
u32 dg_struct_occ_spatial_index_capacity(const dg_struct_occ_spatial_index *idx);
u32 dg_struct_occ_spatial_index_probe_refused(const dg_struct_occ_spatial_index *idx);

/* Remove all entries associated with the given struct_id. Returns number removed. */
u32 dg_struct_occ_spatial_index_remove_struct(dg_struct_occ_spatial_index *idx, dg_struct_id struct_id);

/* Insert the region into all chunks overlapped by its bbox.
 * chunk_size_q MUST be > 0.
 * Returns 0 on success, >0 if partially refused (capacity), <0 on error.
 */
int dg_struct_occ_spatial_index_add_region(dg_struct_occ_spatial_index *idx, const dg_struct_occ_region *r, dg_q chunk_size_q);

/* Rebuild occupancy for one structure and update the shared spatial index.
 * Returns 0 on success, >0 if spatial insert was partially refused, <0 on error.
 */
int dg_struct_occupancy_rebuild(
    dg_struct_occupancy        *out,
    dg_struct_occ_spatial_index *spatial,
    const dg_struct_instance   *inst,
    dg_struct_id                struct_id,
    const dg_struct_footprint  *footprints,
    u32                         footprint_count,
    const dg_struct_volume     *volumes,
    u32                         volume_count,
    const d_world_frame        *frames,
    dg_tick                     tick,
    dg_q                        chunk_size_q
);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DG_STRUCT_OCCUPANCY_H */

