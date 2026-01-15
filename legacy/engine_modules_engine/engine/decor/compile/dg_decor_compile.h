/*
FILE: source/domino/decor/compile/dg_decor_compile.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / decor/compile/dg_decor_compile
RESPONSIBILITY: Defines internal contract for `dg_decor_compile`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
/* DECOR deterministic compilation pipeline (C89).
 *
 * Authoring (rulepacks + overrides + anchors) is the source of truth.
 * Compiled tiles/instances are derived caches, rebuildable under a budget.
 */
#ifndef DG_DECOR_COMPILE_H
#define DG_DECOR_COMPILE_H

#include "domino/core/types.h"

#include "sim/pkt/dg_pkt_common.h"
#include "sim/sched/dg_work_queue.h"

#include "world/frame/d_world_frame.h"

#include "decor/model/dg_decor_rulepack.h"
#include "decor/model/dg_decor_override.h"

#include "decor/compile/dg_decor_dirty.h"
#include "decor/compile/dg_decor_instances.h"
#include "decor/compile/dg_decor_tiles.h"

#ifdef __cplusplus
extern "C" {
#endif

/* Work taxonomy. */
#define DG_DECOR_WORK_HOST        ((dg_type_id)1u)
#define DG_DECOR_WORK_CHUNK_TILES ((dg_type_id)2u)

/* Published host catalog entry (chunk-aligned; renderer-agnostic). */
typedef struct dg_decor_host_desc {
    dg_decor_host host; /* authoring IDs only */

    dg_chunk_id chunk_id;
    dg_frame_id host_frame; /* host frame used for anchor evaluation */

    /* Kind-specific parameter ranges (inclusive; canonicalized so lo<=hi):
     * - TERRAIN_PATCH: primary=(u0,u1), secondary=(v0,v1)
     * - TRANS_SLOT_SURFACE: primary=(s0,s1), secondary unused
     * - STRUCT/ROOM_SURFACE: primary=(u0,u1), secondary=(v0,v1)
     * - SOCKET: primary=(param0,param1), secondary unused
     */
    dg_q primary0;
    dg_q primary1;
    dg_q secondary0;
    dg_q secondary1;
} dg_decor_host_desc;

typedef struct dg_decor_compile_input {
    u64 global_seed;

    const dg_decor_host_desc *hosts;
    u32                       host_count;

    const dg_decor_rulepack  *rulepacks;
    u32                       rulepack_count;

    const dg_decor_override  *overrides;
    u32                       override_count;
} dg_decor_compile_input;

typedef struct dg_decor_compiled_host {
    dg_decor_host_desc desc; /* canonicalized */

    dg_decor_item *items; /* final items for this host (canonical sorted) */
    u32            item_count;
    u32            item_capacity;

    u64 desc_hash;
    d_bool present;
    u32   _pad32;
} dg_decor_compiled_host;

typedef struct dg_decor_compiled_chunk {
    dg_chunk_id chunk_id;
    dg_decor_instances instances;
    dg_decor_tiles     tiles;

    d_bool present;
    u32    _pad32;
} dg_decor_compiled_chunk;

typedef struct dg_decor_rulepack_state {
    dg_decor_rulepack_id id;
    u64                  hash;
    d_bool               present;
    u32                  _pad32;
} dg_decor_rulepack_state;

typedef struct dg_decor_compiler {
    dg_decor_compiled_host  *hosts;  /* sorted by dg_decor_host_cmp */
    u32                      host_count;
    u32                      host_capacity;

    dg_decor_compiled_chunk *chunks; /* sorted by chunk_id */
    u32                      chunk_count;
    u32                      chunk_capacity;

    const dg_decor_rulepack **rulepacks; /* sorted by rulepack_id */
    u32                       rulepack_count;
    u32                       rulepack_capacity;

    const dg_decor_override **overrides; /* sorted by override_id */
    u32                       override_count;
    u32                       override_capacity;

    dg_decor_rulepack_state  *rulepack_state; /* sorted by id */
    u32                       rulepack_state_count;
    u32                       rulepack_state_capacity;

    u64 global_seed;
    u64 overrides_hash;

    dg_decor_dirty dirty;
    dg_work_queue  work_q;
} dg_decor_compiler;

void dg_decor_compiler_init(dg_decor_compiler *c);
void dg_decor_compiler_free(dg_decor_compiler *c);

/* Reserve internal deterministic queues/storage. */
int dg_decor_compiler_reserve(dg_decor_compiler *c, u32 work_queue_capacity);

/* Synchronize internal canonical views and mark dirty sources. */
int dg_decor_compiler_sync(dg_decor_compiler *c, const dg_decor_compile_input *in);

/* Enqueue work implied by dirty flags (does not execute). */
int dg_decor_compiler_enqueue_dirty(dg_decor_compiler *c, dg_tick tick);

/* Process queued work items up to budget_units (no skipping; deterministic carryover).
 * frames is required when host_frame != DG_FRAME_ID_WORLD.
 */
u32 dg_decor_compiler_process(
    dg_decor_compiler      *c,
    const d_world_frame    *frames,
    dg_tick                 tick,
    dg_round_mode           round_mode,
    u32                     budget_units
);

u32 dg_decor_compiler_pending_work(const dg_decor_compiler *c);

/* Accessors (read-only). */
const dg_decor_compiled_chunk *dg_decor_compiler_find_chunk(const dg_decor_compiler *c, dg_chunk_id chunk_id);
const dg_decor_compiled_host  *dg_decor_compiler_find_host(const dg_decor_compiler *c, const dg_decor_host *host);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DG_DECOR_COMPILE_H */

