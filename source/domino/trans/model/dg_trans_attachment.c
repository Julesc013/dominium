/* TRANS attachments / occupants (slot co-location) (C89). */
#include "trans/model/dg_trans_attachment.h"

#include <string.h>

#include "core/det_invariants.h"

void dg_trans_attachment_clear(dg_trans_attachment *a) {
    if (!a) return;
    memset(a, 0, sizeof(*a));
    a->slot.kind = DG_TRANS_SLOT_ASSIGN_AUTO;
}

static int dg_cmp_q(dg_q a, dg_q b) { return D_DET_CMP_I64((i64)a, (i64)b); }

int dg_trans_attachment_cmp(const dg_trans_attachment *a, const dg_trans_attachment *b) {
    int c;
    if (a == b) return 0;
    if (!a) return -1;
    if (!b) return 1;

    c = D_DET_CMP_U64(a->alignment_id, b->alignment_id); if (c) return c;
    c = D_DET_CMP_I32((i32)a->slot.kind, (i32)b->slot.kind); if (c) return c;
    c = D_DET_CMP_U64(a->slot.slot_id, b->slot.slot_id); if (c) return c;
    c = D_DET_CMP_U64(a->occupant_type_id, b->occupant_type_id); if (c) return c;
    c = D_DET_CMP_U64(a->occupant_instance_id, b->occupant_instance_id); if (c) return c;
    c = dg_cmp_q(a->s0, b->s0); if (c) return c;
    c = dg_cmp_q(a->s1, b->s1); if (c) return c;
    c = dg_cmp_q(a->local_t, b->local_t); if (c) return c;
    c = dg_cmp_q(a->local_h, b->local_h); if (c) return c;
    c = D_DET_CMP_U32(a->params.len, b->params.len); if (c) return c;
    return 0;
}

int dg_trans_attachment_overlaps(const dg_trans_attachment *a, dg_q s0, dg_q s1) {
    dg_q a0;
    dg_q a1;
    if (!a) return 0;
    a0 = a->s0;
    a1 = a->s1;
    if (a1 < a0) {
        dg_q t = a0;
        a0 = a1;
        a1 = t;
    }
    if (s1 < s0) {
        dg_q t2 = s0;
        s0 = s1;
        s1 = t2;
    }
    if (a1 < s0) return 0;
    if (s1 < a0) return 0;
    return 1;
}

