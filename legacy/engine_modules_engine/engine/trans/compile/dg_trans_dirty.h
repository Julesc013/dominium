/*
FILE: source/domino/trans/compile/dg_trans_dirty.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / trans/compile/dg_trans_dirty
RESPONSIBILITY: Defines internal contract for `dg_trans_dirty`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
/* TRANS incremental dirty tracking (C89). */
#ifndef DG_TRANS_DIRTY_H
#define DG_TRANS_DIRTY_H

#include "domino/core/types.h"

#include "core/dg_pose.h"
#include "trans/model/dg_trans_ids.h"

#ifdef __cplusplus
extern "C" {
#endif

/* Dirty station ranges are represented as [s0, s1] in Q48.16.
 * Canonicalization ensures s0 <= s1.
 */
typedef struct dg_trans_dirty_range {
    d_bool dirty;
    dg_q   s0;
    dg_q   s1;
} dg_trans_dirty_range;

typedef struct dg_trans_dirty_alignment {
    dg_trans_alignment_id alignment_id;
    dg_trans_dirty_range  microseg;
    dg_trans_dirty_range  slotmap;
} dg_trans_dirty_alignment;

typedef struct dg_trans_dirty_junction {
    dg_trans_junction_id junction_id;
    d_bool               dirty;
} dg_trans_dirty_junction;

typedef struct dg_trans_dirty {
    dg_trans_dirty_alignment *alignments; /* sorted by alignment_id */
    u32                      alignment_count;
    u32                      alignment_capacity;

    dg_trans_dirty_junction *junctions; /* sorted by junction_id */
    u32                     junction_count;
    u32                     junction_capacity;
} dg_trans_dirty;

void dg_trans_dirty_init(dg_trans_dirty *d);
void dg_trans_dirty_free(dg_trans_dirty *d);
void dg_trans_dirty_clear(dg_trans_dirty *d);

int dg_trans_dirty_reserve_alignments(dg_trans_dirty *d, u32 capacity);
int dg_trans_dirty_reserve_junctions(dg_trans_dirty *d, u32 capacity);

/* Mark alignment dirty in station range (merged). */
void dg_trans_dirty_mark_alignment_microseg(dg_trans_dirty *d, dg_trans_alignment_id alignment_id, dg_q s0, dg_q s1);
void dg_trans_dirty_mark_alignment_slotmap(dg_trans_dirty *d, dg_trans_alignment_id alignment_id, dg_q s0, dg_q s1);

/* Mark junction dirty. */
void dg_trans_dirty_mark_junction(dg_trans_dirty *d, dg_trans_junction_id junction_id);

/* Query (returns 1 if found, 0 if not). */
int dg_trans_dirty_get_alignment(const dg_trans_dirty *d, dg_trans_alignment_id alignment_id, dg_trans_dirty_alignment *out);
int dg_trans_dirty_get_junction(const dg_trans_dirty *d, dg_trans_junction_id junction_id, dg_trans_dirty_junction *out);

/* Clear dirty flags for a specific alignment/junction (no-op if absent). */
void dg_trans_dirty_clear_alignment(dg_trans_dirty *d, dg_trans_alignment_id alignment_id);
void dg_trans_dirty_clear_junction(dg_trans_dirty *d, dg_trans_junction_id junction_id);

/* Convert a station range to an inclusive segment index span.
 * microseg_max_len_q MUST be > 0.
 * Returns 0 on success, <0 on error.
 */
int dg_trans_dirty_range_to_seg_span(dg_q s0, dg_q s1, dg_q microseg_max_len_q, u32 *out_seg0, u32 *out_seg1);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DG_TRANS_DIRTY_H */

