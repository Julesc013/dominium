/*
FILE: source/domino/struct/compile/dg_struct_compile.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / struct/compile/dg_struct_compile
RESPONSIBILITY: Implements `dg_struct_compile`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
/* STRUCT deterministic compilation pipeline (C89).
 *
 * Authoring model is authoritative; compiled outputs are derived caches.
 * Compilation is incremental, budgeted, and uses deterministic carryover
 * work queues (dg_work_queue) with canonical ordering keys.
 */
#ifndef DG_STRUCT_COMPILE_H
#define DG_STRUCT_COMPILE_H

#include "domino/core/types.h"

#include "sim/pkt/dg_pkt_common.h"
#include "sim/sched/dg_work_queue.h"

#include "struct/model/dg_struct_instance.h"
#include "struct/model/dg_struct_footprint.h"
#include "struct/model/dg_struct_volume.h"
#include "struct/model/dg_struct_enclosure.h"
#include "struct/model/dg_struct_surface.h"
#include "struct/model/dg_struct_socket.h"
#include "struct/model/dg_struct_carrier_intent.h"

#include "struct/compile/dg_struct_occupancy.h"
#include "struct/compile/dg_struct_enclosure_graph.h"
#include "struct/compile/dg_struct_surface_graph.h"
#include "struct/compile/dg_struct_support_graph.h"
#include "struct/compile/dg_struct_carrier_compile.h"
#include "struct/compile/dg_struct_dirty.h"

#ifdef __cplusplus
extern "C" {
#endif

/* Work type taxonomy (dg_work_item.work_type_id) and ordering keys (dg_order_key.type_id). */
#define DG_STRUCT_WORK_OCCUPANCY ((dg_type_id)1u)
#define DG_STRUCT_WORK_ENCLOSURE ((dg_type_id)2u)
#define DG_STRUCT_WORK_SURFACE   ((dg_type_id)3u)
#define DG_STRUCT_WORK_SUPPORT   ((dg_type_id)4u)
#define DG_STRUCT_WORK_CARRIER   ((dg_type_id)5u)

typedef struct dg_struct_compile_input {
    const dg_struct_instance *instances;
    u32                       instance_count;

    const dg_struct_footprint *footprints;
    u32                        footprint_count;

    const dg_struct_volume *volumes;
    u32                    volume_count;

    const dg_struct_enclosure *enclosures;
    u32                       enclosure_count;

    const dg_struct_surface_template *surface_templates;
    u32                              surface_template_count;

    const dg_struct_socket *sockets;
    u32                    socket_count;

    const dg_struct_carrier_intent *carrier_intents;
    u32                            carrier_intent_count;

    const d_world_frame *frames; /* optional; required if anchors reference non-world frames */
} dg_struct_compile_input;

typedef struct dg_struct_compiled_struct {
    dg_struct_id struct_id;

    dg_struct_occupancy       occupancy;
    dg_struct_enclosure_graph enclosures;
    dg_struct_surface_graph   surfaces;
    dg_struct_support_graph   supports;
    dg_struct_carrier_compiled carriers;
} dg_struct_compiled_struct;

typedef struct dg_struct_compiled {
    dg_struct_compiled_struct *structs; /* sorted by struct_id */
    u32                       struct_count;
    u32                       struct_capacity;

    /* Chunk-aligned indices (derived caches). */
    dg_struct_occ_spatial_index      occupancy_spatial;
    dg_struct_room_spatial_index     enclosure_spatial;
    dg_struct_surface_spatial_index  surface_spatial;
    dg_struct_support_spatial_index  support_spatial;
    dg_struct_carrier_spatial_index  carrier_spatial;
} dg_struct_compiled;

typedef struct dg_struct_compiler {
    dg_struct_compiled compiled;
    dg_struct_dirty    dirty;
    dg_work_queue      work_q;

    dg_q chunk_size_q;
} dg_struct_compiler;

void dg_struct_compiler_init(dg_struct_compiler *c);
void dg_struct_compiler_free(dg_struct_compiler *c);

/* Reserve internal deterministic queues/indices. */
int dg_struct_compiler_reserve(dg_struct_compiler *c, u32 work_queue_capacity, u32 spatial_capacity);

/* Set compile parameters (must be > 0). */
int dg_struct_compiler_set_params(dg_struct_compiler *c, dg_q chunk_size_q);

/* Synchronize compiled records to the current authoring sets (create missing entries).
 * Destruction is not handled in this prompt (callers keep IDs stable).
 */
int dg_struct_compiler_sync(dg_struct_compiler *c, const dg_struct_compile_input *in);

/* Enqueue work items implied by dirty flags (does not execute). */
int dg_struct_compiler_enqueue_dirty(dg_struct_compiler *c, dg_tick tick);

/* Process queued work items up to budget_units (no skipping; deterministic carryover).
 * Returns number of work items processed.
 */
u32 dg_struct_compiler_process(dg_struct_compiler *c, const dg_struct_compile_input *in, dg_tick tick, u32 budget_units);

u32 dg_struct_compiler_pending_work(const dg_struct_compiler *c);

/* Invariant checks (debug/test helper). Returns 0 if invariants hold, <0 on mismatch/error. */
int dg_struct_compiler_check_invariants(const dg_struct_compiler *c, const dg_struct_compile_input *in);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DG_STRUCT_COMPILE_H */

