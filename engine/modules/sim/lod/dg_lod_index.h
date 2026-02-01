/*
FILE: source/domino/sim/lod/dg_lod_index.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / sim/lod/dg_lod_index
RESPONSIBILITY: Defines internal contract for `dg_lod_index`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/specs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/specs/SPEC_*.md` without cross-layer coupling.
*/
/* Chunk-aligned candidate index for deterministic LOD (C89).
 *
 * This module provides bounded, deterministic storage for "objects that may
 * change representation" and supports chunk-local queries without unordered
 * iteration.
 */
#ifndef DG_LOD_INDEX_H
#define DG_LOD_INDEX_H

#include "domino/core/types.h"
#include "domino/core/fixed.h"

#include "sim/pkt/dg_pkt_common.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef u64 dg_lod_class_id;

typedef struct dg_lod_obj_key {
    dg_domain_id domain_id;
    dg_chunk_id  chunk_id;
    dg_entity_id entity_id;
    u64          sub_id;
} dg_lod_obj_key;

typedef struct dg_lod_obj_pos {
    q16_16 x;
    q16_16 y;
    q16_16 z;
} dg_lod_obj_pos;

typedef struct dg_lod_candidate {
    dg_lod_obj_key key;
    dg_lod_obj_pos pos;
    dg_lod_class_id class_id;
} dg_lod_candidate;

typedef struct dg_lod_index_entry {
    dg_chunk_id     chunk_id;
    dg_lod_class_id class_id;
    dg_lod_obj_key  key;
    dg_lod_obj_pos  pos;
} dg_lod_index_entry;

typedef struct dg_lod_index {
    dg_lod_index_entry *entries;
    u32                 count;
    u32                 capacity;
    d_bool              owns_storage;
    u32                 probe_refused; /* insert refusals due to capacity */
} dg_lod_index;

void dg_lod_index_init(dg_lod_index *idx);
void dg_lod_index_free(dg_lod_index *idx);

int dg_lod_index_reserve(dg_lod_index *idx, u32 capacity);
void dg_lod_index_clear(dg_lod_index *idx);

u32 dg_lod_index_count(const dg_lod_index *idx);
u32 dg_lod_index_capacity(const dg_lod_index *idx);
u32 dg_lod_index_probe_refused(const dg_lod_index *idx);

/* Add/update an object entry (deterministic).
 * Returns 0 on success, <0 on error, >0 if updated-in-place.
 */
int dg_lod_index_add(
    dg_lod_index        *idx,
    dg_chunk_id          chunk_id,
    const dg_lod_obj_key *obj_key,
    const dg_lod_obj_pos *obj_pos,
    dg_lod_class_id      class_id
);

/* Remove an object entry. Returns 0 if removed, <0 on error, >0 if not found. */
int dg_lod_index_remove(
    dg_lod_index        *idx,
    dg_chunk_id          chunk_id,
    const dg_lod_obj_key *obj_key,
    dg_lod_class_id      class_id
);

/* Query candidates in a chunk, optionally filtered by class_id.
 * If class_id == 0, returns all classes in the chunk.
 * Returns number written to out_candidates (<= max_out).
 */
u32 dg_lod_index_query(
    const dg_lod_index *idx,
    dg_chunk_id         chunk_id,
    dg_lod_class_id     class_id,
    dg_lod_candidate   *out_candidates,
    u32                 max_out
);

/* Collect unique chunk ids present in the index, in deterministic ascending order.
 * Returns number written (<= max_out).
 */
u32 dg_lod_index_collect_chunks(const dg_lod_index *idx, dg_chunk_id *out_chunks, u32 max_out);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DG_LOD_INDEX_H */

