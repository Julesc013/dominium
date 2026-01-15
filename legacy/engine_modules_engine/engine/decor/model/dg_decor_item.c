/*
FILE: source/domino/decor/model/dg_decor_item.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / decor/model/dg_decor_item
RESPONSIBILITY: Implements `dg_decor_item`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
/* DECOR items (C89). */
#include "decor/model/dg_decor_item.h"

#include <string.h>

#include "core/det_invariants.h"

void dg_decor_item_clear(dg_decor_item *it) {
    if (!it) return;
    memset(it, 0, sizeof(*it));
    it->local_offset = dg_pose_identity();
}

int dg_decor_item_cmp(const dg_decor_item *a, const dg_decor_item *b) {
    int c;
    if (a == b) return 0;
    if (!a) return -1;
    if (!b) return 1;

    c = dg_decor_host_cmp(&a->host, &b->host);
    if (c) return c;

    c = D_DET_CMP_U64(a->decor_type_id, b->decor_type_id);
    if (c) return c;

    c = D_DET_CMP_U64(a->decor_id, b->decor_id);
    if (c) return c;

    c = D_DET_CMP_U32(a->flags, b->flags);
    if (c) return c;

    c = dg_anchor_cmp(&a->anchor, &b->anchor);
    if (c) return c;

    c = D_DET_CMP_I64((i64)a->local_offset.pos.x, (i64)b->local_offset.pos.x); if (c) return c;
    c = D_DET_CMP_I64((i64)a->local_offset.pos.y, (i64)b->local_offset.pos.y); if (c) return c;
    c = D_DET_CMP_I64((i64)a->local_offset.pos.z, (i64)b->local_offset.pos.z); if (c) return c;
    c = D_DET_CMP_I64((i64)a->local_offset.rot.x, (i64)b->local_offset.rot.x); if (c) return c;
    c = D_DET_CMP_I64((i64)a->local_offset.rot.y, (i64)b->local_offset.rot.y); if (c) return c;
    c = D_DET_CMP_I64((i64)a->local_offset.rot.z, (i64)b->local_offset.rot.z); if (c) return c;
    c = D_DET_CMP_I64((i64)a->local_offset.rot.w, (i64)b->local_offset.rot.w); if (c) return c;
    c = D_DET_CMP_I64((i64)a->local_offset.incline, (i64)b->local_offset.incline); if (c) return c;
    c = D_DET_CMP_I64((i64)a->local_offset.roll, (i64)b->local_offset.roll); if (c) return c;

    /* Params last: compare by (len, bytes) to avoid pointer-identity ordering. */
    if (a->params.len != b->params.len) return D_DET_CMP_U32(a->params.len, b->params.len);
    if (a->params.ptr != b->params.ptr && a->params.len != 0u) {
        u32 i;
        const unsigned char *ap = a->params.ptr;
        const unsigned char *bp = b->params.ptr;
        if (!ap && bp) return -1;
        if (ap && !bp) return 1;
        for (i = 0u; i < a->params.len; ++i) {
            if (ap[i] < bp[i]) return -1;
            if (ap[i] > bp[i]) return 1;
        }
    }

    return 0;
}

int dg_decor_item_eval_pose(
    const dg_decor_item *it,
    const d_world_frame *frames,
    dg_tick              tick,
    dg_round_mode        round_mode,
    dg_pose             *out_pose
) {
    dg_pose anchor_pose;
    if (!out_pose) return -1;
    *out_pose = dg_pose_identity();
    if (!it) return -2;

    if (dg_anchor_eval(&it->anchor, frames, tick, round_mode, &anchor_pose) != 0) {
        return -3;
    }

    *out_pose = dg_pose_compose(&anchor_pose, &it->local_offset, round_mode);
    return 0;
}
