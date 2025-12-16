/*
FILE: source/domino/decor/model/dg_decor_host.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / decor/model/dg_decor_host
RESPONSIBILITY: Implements `dg_decor_host`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
/* DECOR host bindings (C89). */
#include "decor/model/dg_decor_host.h"

#include <string.h>

#include "core/dg_det_hash.h"

void dg_decor_host_clear(dg_decor_host *h) {
    if (!h) return;
    memset(h, 0, sizeof(*h));
}

int dg_decor_host_cmp(const dg_decor_host *a, const dg_decor_host *b) {
    int c;
    if (a == b) return 0;
    if (!a) return -1;
    if (!b) return 1;

    c = D_DET_CMP_I32((i32)a->kind, (i32)b->kind);
    if (c) return c;

    switch (a->kind) {
    case DG_DECOR_HOST_TERRAIN_PATCH:
        return D_DET_CMP_U64((u64)a->u.terrain_patch.chunk_id, (u64)b->u.terrain_patch.chunk_id);
    case DG_DECOR_HOST_TRANS_SLOT_SURFACE:
        c = D_DET_CMP_U64(a->u.trans_slot_surface.alignment_id, b->u.trans_slot_surface.alignment_id);
        if (c) return c;
        c = D_DET_CMP_U32(a->u.trans_slot_surface.segment_index, b->u.trans_slot_surface.segment_index);
        if (c) return c;
        c = D_DET_CMP_U64(a->u.trans_slot_surface.slot_id, b->u.trans_slot_surface.slot_id);
        if (c) return c;
        return 0;
    case DG_DECOR_HOST_STRUCT_SURFACE:
        c = D_DET_CMP_U64(a->u.struct_surface.struct_id, b->u.struct_surface.struct_id);
        if (c) return c;
        c = D_DET_CMP_U64(a->u.struct_surface.surface_id, b->u.struct_surface.surface_id);
        if (c) return c;
        return 0;
    case DG_DECOR_HOST_ROOM_SURFACE:
        c = D_DET_CMP_U64(a->u.room_surface.room_id, b->u.room_surface.room_id);
        if (c) return c;
        c = D_DET_CMP_U64(a->u.room_surface.surface_id, b->u.room_surface.surface_id);
        if (c) return c;
        return 0;
    case DG_DECOR_HOST_SOCKET:
        return D_DET_CMP_U64(a->u.socket.socket_id, b->u.socket.socket_id);
    default:
        return 0;
    }
}

u64 dg_decor_host_stable_id_u64(const dg_decor_host *h) {
    u64 v;
    if (!h) return 0u;

    v = dg_det_hash_u64((u64)h->kind);

    switch (h->kind) {
    case DG_DECOR_HOST_TERRAIN_PATCH:
        v = dg_det_hash_u64(v ^ (u64)h->u.terrain_patch.chunk_id);
        break;
    case DG_DECOR_HOST_TRANS_SLOT_SURFACE:
        v = dg_det_hash_u64(v ^ (u64)h->u.trans_slot_surface.alignment_id);
        v = dg_det_hash_u64(v ^ (u64)h->u.trans_slot_surface.segment_index);
        v = dg_det_hash_u64(v ^ (u64)h->u.trans_slot_surface.slot_id);
        break;
    case DG_DECOR_HOST_STRUCT_SURFACE:
        v = dg_det_hash_u64(v ^ (u64)h->u.struct_surface.struct_id);
        v = dg_det_hash_u64(v ^ (u64)h->u.struct_surface.surface_id);
        break;
    case DG_DECOR_HOST_ROOM_SURFACE:
        v = dg_det_hash_u64(v ^ (u64)h->u.room_surface.room_id);
        v = dg_det_hash_u64(v ^ (u64)h->u.room_surface.surface_id);
        break;
    case DG_DECOR_HOST_SOCKET:
        v = dg_det_hash_u64(v ^ (u64)h->u.socket.socket_id);
        break;
    default:
        break;
    }

    return v;
}

