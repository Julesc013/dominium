/*
FILE: source/domino/trans/compile/dg_trans_compile.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / trans/compile/dg_trans_compile
RESPONSIBILITY: Defines internal contract for `dg_trans_compile`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
/* TRANS deterministic compilation pipeline (C89).
 *
 * Authoring model is authoritative; compiled outputs are derived caches.
 * Compilation is incremental, budgeted, and uses deterministic carryover
 * work queues (dg_work_queue) with canonical ordering keys.
 */
#ifndef DG_TRANS_COMPILE_H
#define DG_TRANS_COMPILE_H

#include "domino/core/types.h"

#include "sim/pkt/dg_pkt_common.h"
#include "sim/sched/dg_work_queue.h"

#include "trans/model/dg_trans_alignment.h"
#include "trans/model/dg_trans_section.h"
#include "trans/model/dg_trans_attachment.h"
#include "trans/model/dg_trans_junction.h"

#include "trans/compile/dg_trans_microseg.h"
#include "trans/compile/dg_trans_slotmap.h"
#include "trans/compile/dg_trans_dirty.h"

#ifdef __cplusplus
extern "C" {
#endif

/* Work type taxonomy (dg_work_item.work_type_id) and ordering keys (dg_order_key.type_id). */
#define DG_TRANS_WORK_MICROSEG_RANGE ((dg_type_id)1u)
#define DG_TRANS_WORK_SLOTMAP_RANGE  ((dg_type_id)2u)
#define DG_TRANS_WORK_JUNCTION       ((dg_type_id)3u)

typedef struct dg_trans_compile_input {
    const dg_trans_alignment        *alignments;
    u32                              alignment_count;
    const dg_trans_section_archetype *sections;
    u32                              section_count;
    const dg_trans_attachment       *attachments;
    u32                              attachment_count;
    const dg_trans_junction         *junctions;
    u32                              junction_count;
} dg_trans_compile_input;

typedef struct dg_trans_compiled_alignment {
    dg_trans_alignment_id alignment_id;
    dg_q                  last_length_q;

    dg_trans_microseg         *segs;
    dg_trans_segment_slotmap  *slotmaps;
    u32                        seg_count;
    u32                        seg_capacity;
} dg_trans_compiled_alignment;

typedef struct dg_trans_compiled_junction {
    dg_trans_junction_id junction_id;

    /* Canonical sorted incident list snapshot. */
    dg_trans_junction_incident *incidents;
    u32                         incident_count;
    u32                         incident_capacity;
} dg_trans_compiled_junction;

typedef struct dg_trans_compiled {
    dg_trans_compiled_alignment *alignments; /* sorted by alignment_id */
    u32                         alignment_count;
    u32                         alignment_capacity;

    dg_trans_compiled_junction *junctions; /* sorted by junction_id */
    u32                        junction_count;
    u32                        junction_capacity;

    dg_trans_spatial_index spatial; /* chunk-aligned microsegment index */
} dg_trans_compiled;

typedef struct dg_trans_compiler {
    dg_trans_compiled compiled;
    dg_trans_dirty    dirty;
    dg_work_queue     work_q;

    dg_q microseg_max_len_q; /* max station length per microsegment */
    dg_q chunk_size_q;       /* chunk edge length for spatial index */
} dg_trans_compiler;

void dg_trans_compiler_init(dg_trans_compiler *c);
void dg_trans_compiler_free(dg_trans_compiler *c);

/* Reserve internal deterministic queues/indices. */
int dg_trans_compiler_reserve(dg_trans_compiler *c, u32 work_queue_capacity, u32 spatial_capacity);

/* Set compile parameters (must be > 0). */
int dg_trans_compiler_set_params(dg_trans_compiler *c, dg_q microseg_max_len_q, dg_q chunk_size_q);

/* Synchronize compiled records to the current authoring sets (create missing entries).
 * Destruction is not handled in this prompt (callers keep IDs stable).
 */
int dg_trans_compiler_sync(dg_trans_compiler *c, const dg_trans_compile_input *in);

/* Enqueue work items implied by dirty flags (does not execute). */
int dg_trans_compiler_enqueue_dirty(dg_trans_compiler *c, dg_tick tick);

/* Process queued work items up to budget_units (no skipping; deterministic carryover).
 * Returns number of work items processed.
 */
u32 dg_trans_compiler_process(dg_trans_compiler *c, const dg_trans_compile_input *in, dg_tick tick, u32 budget_units);

u32 dg_trans_compiler_pending_work(const dg_trans_compiler *c);

/* Invariant checks (debug/test helper):
 * Verifies that compiled caches (microsegments/frames/slotmaps/junction snapshots)
 * match a deterministic rebuild from the authoring input under the current
 * compiler parameters.
 *
 * Returns 0 if invariants hold, <0 on mismatch/error.
 */
int dg_trans_compiler_check_invariants(const dg_trans_compiler *c, const dg_trans_compile_input *in);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DG_TRANS_COMPILE_H */
