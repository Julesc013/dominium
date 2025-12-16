/*
FILE: source/domino/trans/model/dg_trans_attachment.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / trans/model/dg_trans_attachment
RESPONSIBILITY: Defines internal contract for `dg_trans_attachment`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
/* TRANS attachments / occupants (slot co-location) (C89). */
#ifndef DG_TRANS_ATTACHMENT_H
#define DG_TRANS_ATTACHMENT_H

#include "domino/core/types.h"

#include "core/dg_pose.h"
#include "core/d_tlv.h"
#include "trans/model/dg_trans_ids.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum dg_trans_slot_assign_kind {
    DG_TRANS_SLOT_ASSIGN_EXPLICIT = 0,
    DG_TRANS_SLOT_ASSIGN_AUTO = 1
} dg_trans_slot_assign_kind;

typedef struct dg_trans_slot_assign {
    dg_trans_slot_assign_kind kind;
    dg_trans_slot_id          slot_id; /* only used when kind==EXPLICIT */
} dg_trans_slot_assign;

typedef struct dg_trans_attachment {
    dg_trans_alignment_id         alignment_id;
    dg_trans_occupant_type_id     occupant_type_id;
    dg_trans_occupant_instance_id occupant_instance_id;

    dg_trans_slot_assign slot;

    /* Longitudinal range along the corridor spine: [s0, s1]. */
    dg_q s0;
    dg_q s1;

    /* Local offsets applied in the section frame in addition to slot offset. */
    dg_q local_t;
    dg_q local_h;

    /* Optional per-occupant parameters (TLV). */
    d_tlv_blob params;
} dg_trans_attachment;

void dg_trans_attachment_clear(dg_trans_attachment *a);

/* Canonical total order comparator for attachments (alignment_id, slot, occupant_instance_id). */
int dg_trans_attachment_cmp(const dg_trans_attachment *a, const dg_trans_attachment *b);

/* Returns nonzero if attachment overlaps the station interval [s0, s1]. */
int dg_trans_attachment_overlaps(const dg_trans_attachment *a, dg_q s0, dg_q s1);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DG_TRANS_ATTACHMENT_H */

