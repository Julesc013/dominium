/*
FILE: source/domino/sim/lod/dg_interest.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / sim/lod/dg_interest
RESPONSIBILITY: Implements `dg_interest`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
/* Deterministic interest volumes (C89).
 *
 * Interest volumes are lockstep-derived regions used for deterministic LOD
 * selection. They are NOT camera frusta and MUST NOT depend on UI state.
 *
 * All positions/extents are fixed-point and quantized to deterministic quanta.
 */
#ifndef DG_INTEREST_H
#define DG_INTEREST_H

#include "domino/core/types.h"
#include "domino/core/fixed.h"

#include "sim/pkt/dg_pkt_common.h"
#include "sim/lod/dg_lod_index.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum dg_interest_volume_type {
    DG_IV_PLAYER = 1,
    DG_IV_OWNERSHIP = 2,
    DG_IV_HAZARD = 3,
    DG_IV_ACTIVITY = 4,
    DG_IV_CRITICAL_INFRA = 5
} dg_interest_volume_type;

typedef enum dg_interest_shape {
    DG_IV_SHAPE_SPHERE = 1,
    DG_IV_SHAPE_AABB = 2
} dg_interest_shape;

typedef struct dg_interest_volume {
    dg_interest_volume_type type;
    dg_interest_shape       shape;

    /* Optional stable provenance (for determinism/debug; may be 0). */
    dg_domain_id domain_id;
    dg_entity_id src_entity;

    /* Shape parameters (q16_16). */
    dg_lod_obj_pos center;

    q16_16         radius;       /* sphere */
    dg_lod_obj_pos half_extents; /* aabb */

    /* Weight in q16_16 (default weights are engine-level; sources may override). */
    q16_16 weight;
} dg_interest_volume;

typedef struct dg_interest_list {
    dg_interest_volume *volumes;
    u32                count;
    u32                capacity;
    d_bool             owns_storage;
    u32                probe_refused;
} dg_interest_list;

void dg_interest_list_init(dg_interest_list *l);
void dg_interest_list_free(dg_interest_list *l);
int  dg_interest_list_reserve(dg_interest_list *l, u32 capacity);
void dg_interest_list_clear(dg_interest_list *l);
u32  dg_interest_list_count(const dg_interest_list *l);
u32  dg_interest_list_probe_refused(const dg_interest_list *l);

/* Adds a volume (will be quantized). Returns 0 on success. */
int dg_interest_list_push(dg_interest_list *l, const dg_interest_volume *v);

typedef void (*dg_interest_source_fn)(dg_tick tick, dg_interest_list *out_list, void *user_ctx);

typedef struct dg_interest_source {
    dg_interest_source_fn fn;
    void                *user_ctx;
    u64                  priority_key;
    u32                  insert_index;
} dg_interest_source;

typedef struct dg_interest_ctx {
    dg_interest_source *sources;
    u32                count;
    u32                capacity;
    u32                next_insert_index;
    u32                probe_refused;
} dg_interest_ctx;

void dg_interest_init(dg_interest_ctx *ic);
void dg_interest_free(dg_interest_ctx *ic);
int  dg_interest_reserve(dg_interest_ctx *ic, u32 capacity);

/* Register a deterministic interest source (sorted by priority_key then stable). */
int dg_interest_register_source(dg_interest_ctx *ic, dg_interest_source_fn fn, u64 priority_key, void *user_ctx);
u32 dg_interest_probe_refused(const dg_interest_ctx *ic);

/* Gather interest volumes deterministically (calls registered sources, then canonicalizes). */
int dg_interest_collect(dg_interest_ctx *ic, dg_tick tick, dg_interest_list *out_list);

/* Deterministic inclusion test. */
d_bool dg_interest_contains(const dg_lod_obj_pos *obj_pos, const dg_interest_volume *v);

/* Deterministic fixed-point interest score (q16_16). */
q16_16 dg_interest_score_object(const dg_lod_obj_key *obj_key, const dg_lod_obj_pos *obj_pos, dg_lod_class_id class_id, const dg_interest_list *volumes);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DG_INTEREST_H */

