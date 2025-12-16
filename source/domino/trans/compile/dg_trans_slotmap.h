/*
FILE: source/domino/trans/compile/dg_trans_slotmap.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / trans/compile/dg_trans_slotmap
RESPONSIBILITY: Implements `dg_trans_slotmap`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
/* TRANS slot occupancy compilation (C89).
 *
 * Slot co-location is represented explicitly as multiple occupants in the same
 * section slots for a given corridor microsegment.
 */
#ifndef DG_TRANS_SLOTMAP_H
#define DG_TRANS_SLOTMAP_H

#include "domino/core/types.h"

#include "core/dg_pose.h"
#include "trans/model/dg_trans_ids.h"
#include "trans/model/dg_trans_section.h"
#include "trans/model/dg_trans_attachment.h"
#include "trans/compile/dg_trans_microseg.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dg_trans_slot_occupancy {
    dg_trans_slot_id           slot_id;
    dg_trans_occupant_type_id  occupant_type_id;
    dg_trans_occupant_instance_id occupant_instance_id;

    /* Total offsets in section frame (slot offset + attachment local offsets). */
    dg_q offset_t;
    dg_q offset_h;
} dg_trans_slot_occupancy;

/* Canonical rail coordinate (no baked geometry): (alignment_id, station s, slot_id, local_u).
 * local_u is a param along a microsegment in [0,1] (Q48.16) when used in compiled caches.
 */
typedef struct dg_trans_rail_coord {
    dg_trans_alignment_id alignment_id;
    dg_q                 s;
    dg_trans_slot_id     slot_id;
    dg_q                 local_u;
} dg_trans_rail_coord;

dg_trans_rail_coord dg_trans_rail_coord_make(dg_trans_alignment_id alignment_id, dg_q s, dg_trans_slot_id slot_id, dg_q local_u);

typedef struct dg_trans_segment_slotmap {
    dg_trans_slot_occupancy *items; /* sorted by (slot_id, occupant_instance_id) */
    u32                      count;
    u32                      capacity;
} dg_trans_segment_slotmap;

void dg_trans_segment_slotmap_init(dg_trans_segment_slotmap *m);
void dg_trans_segment_slotmap_free(dg_trans_segment_slotmap *m);
void dg_trans_segment_slotmap_clear(dg_trans_segment_slotmap *m);
int  dg_trans_segment_slotmap_reserve(dg_trans_segment_slotmap *m, u32 capacity);

/* Rebuild slot maps for a segment index range [seg0, seg1] (inclusive).
 * - attachments is the global attachment list; only those with matching alignment_id are considered.
 * - Auto-pack resolver is deterministic and independent of insertion order.
 */
int dg_trans_slotmap_rebuild_range(
    dg_trans_segment_slotmap         *slotmaps,
    u32                               slotmap_count,
    const dg_trans_microseg          *segs,
    u32                               seg_count,
    dg_trans_alignment_id             alignment_id,
    const dg_trans_section_archetype *section,
    const dg_trans_attachment        *attachments,
    u32                               attachment_count,
    u32                               seg0,
    u32                               seg1
);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DG_TRANS_SLOTMAP_H */
