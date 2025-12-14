/* STRUCT carrier compilation (C89).
 *
 * Compiles carrier intents (bridge/tunnel/cut/fill) into deterministic
 * parametric artifacts (not baked meshes) and chunk-aligned indices.
 */
#ifndef DG_STRUCT_CARRIER_COMPILE_H
#define DG_STRUCT_CARRIER_COMPILE_H

#include "domino/core/types.h"

#include "core/dg_pose.h"
#include "sim/pkt/dg_pkt_common.h"

#include "struct/model/dg_struct_ids.h"
#include "struct/model/dg_struct_instance.h"
#include "struct/model/dg_struct_carrier_intent.h"
#include "struct/compile/dg_struct_occupancy.h"
#include "world/frame/d_world_frame.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dg_struct_carrier_artifact {
    dg_struct_carrier_artifact_id id;
    dg_struct_id                  struct_id;
    dg_struct_carrier_intent_id   intent_id;
    dg_struct_carrier_kind        kind;
    u32                           _pad32;

    dg_pose a0_world;
    dg_pose a1_world;

    dg_q width;
    dg_q height;
    dg_q depth;

    dg_struct_aabb bbox_world;
} dg_struct_carrier_artifact;

typedef struct dg_struct_carrier_compiled {
    dg_struct_carrier_artifact *items; /* sorted by artifact_id */
    u32                        count;
    u32                        capacity;
} dg_struct_carrier_compiled;

typedef struct dg_struct_carrier_spatial_entry {
    dg_struct_chunk_coord          chunk;
    dg_struct_id                   struct_id;
    dg_struct_carrier_artifact_id  artifact_id;
    dg_struct_aabb                 bbox;
} dg_struct_carrier_spatial_entry;

typedef struct dg_struct_carrier_spatial_index {
    dg_struct_carrier_spatial_entry *entries;
    u32                             count;
    u32                             capacity;
    u32                             probe_refused;
    d_bool                          owns_storage;
} dg_struct_carrier_spatial_index;

void dg_struct_carrier_compiled_init(dg_struct_carrier_compiled *c);
void dg_struct_carrier_compiled_free(dg_struct_carrier_compiled *c);
void dg_struct_carrier_compiled_clear(dg_struct_carrier_compiled *c);
int  dg_struct_carrier_compiled_reserve(dg_struct_carrier_compiled *c, u32 capacity);

void dg_struct_carrier_spatial_index_init(dg_struct_carrier_spatial_index *idx);
void dg_struct_carrier_spatial_index_free(dg_struct_carrier_spatial_index *idx);
int  dg_struct_carrier_spatial_index_reserve(dg_struct_carrier_spatial_index *idx, u32 capacity);
void dg_struct_carrier_spatial_index_clear(dg_struct_carrier_spatial_index *idx);
u32  dg_struct_carrier_spatial_index_remove_struct(dg_struct_carrier_spatial_index *idx, dg_struct_id struct_id);

/* Rebuild carrier artifacts for one structure and update the shared spatial index.
 * Returns 0 on success, >0 if spatial inserts were partially refused, <0 on error.
 */
int dg_struct_carrier_compile_rebuild(
    dg_struct_carrier_compiled      *out,
    dg_struct_carrier_spatial_index *spatial,
    const dg_struct_instance        *inst,
    dg_struct_id                     struct_id,
    const dg_struct_carrier_intent  *intents,
    u32                              intent_count,
    const d_world_frame             *frames,
    dg_tick                          tick,
    dg_q                             chunk_size_q
);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DG_STRUCT_CARRIER_COMPILE_H */

