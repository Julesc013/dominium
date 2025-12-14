/* Parametric anchors (C89). */
#include "world/frame/dg_anchor.h"

#include <string.h>

#include "core/det_invariants.h"

void dg_anchor_clear(dg_anchor *a) {
    if (!a) return;
    memset(a, 0, sizeof(*a));
}

static int dg_cmp_q(dg_q a, dg_q b) { return D_DET_CMP_I64((i64)a, (i64)b); }

int dg_anchor_cmp(const dg_anchor *a, const dg_anchor *b) {
    int c;
    if (a == b) return 0;
    if (!a) return -1;
    if (!b) return 1;

    c = D_DET_CMP_U64((u64)a->host_frame, (u64)b->host_frame);
    if (c) return c;
    c = D_DET_CMP_I32((i32)a->kind, (i32)b->kind);
    if (c) return c;

    switch (a->kind) {
    case DG_ANCHOR_TERRAIN:
        c = dg_cmp_q(a->u.terrain.u, b->u.terrain.u); if (c) return c;
        c = dg_cmp_q(a->u.terrain.v, b->u.terrain.v); if (c) return c;
        c = dg_cmp_q(a->u.terrain.h, b->u.terrain.h); if (c) return c;
        return 0;
    case DG_ANCHOR_CORRIDOR_TRANS:
        c = D_DET_CMP_U64(a->u.corridor.alignment_id, b->u.corridor.alignment_id); if (c) return c;
        c = dg_cmp_q(a->u.corridor.s, b->u.corridor.s); if (c) return c;
        c = dg_cmp_q(a->u.corridor.t, b->u.corridor.t); if (c) return c;
        c = dg_cmp_q(a->u.corridor.h, b->u.corridor.h); if (c) return c;
        c = dg_cmp_q(a->u.corridor.roll, b->u.corridor.roll); if (c) return c;
        return 0;
    case DG_ANCHOR_STRUCT_SURFACE:
        c = D_DET_CMP_U64(a->u.struct_surface.structure_id, b->u.struct_surface.structure_id); if (c) return c;
        c = D_DET_CMP_U64(a->u.struct_surface.surface_id, b->u.struct_surface.surface_id); if (c) return c;
        c = dg_cmp_q(a->u.struct_surface.u, b->u.struct_surface.u); if (c) return c;
        c = dg_cmp_q(a->u.struct_surface.v, b->u.struct_surface.v); if (c) return c;
        c = dg_cmp_q(a->u.struct_surface.offset, b->u.struct_surface.offset); if (c) return c;
        return 0;
    case DG_ANCHOR_ROOM_SURFACE:
        c = D_DET_CMP_U64(a->u.room_surface.room_id, b->u.room_surface.room_id); if (c) return c;
        c = D_DET_CMP_U64(a->u.room_surface.surface_id, b->u.room_surface.surface_id); if (c) return c;
        c = dg_cmp_q(a->u.room_surface.u, b->u.room_surface.u); if (c) return c;
        c = dg_cmp_q(a->u.room_surface.v, b->u.room_surface.v); if (c) return c;
        c = dg_cmp_q(a->u.room_surface.offset, b->u.room_surface.offset); if (c) return c;
        return 0;
    case DG_ANCHOR_SOCKET:
        c = D_DET_CMP_U64(a->u.socket.socket_id, b->u.socket.socket_id); if (c) return c;
        c = dg_cmp_q(a->u.socket.param, b->u.socket.param); if (c) return c;
        return 0;
    default:
        return 0;
    }
}

static dg_pose dg_anchor_local_pose(const dg_anchor *a) {
    dg_pose p = dg_pose_identity();
    if (!a) return p;

    switch (a->kind) {
    case DG_ANCHOR_TERRAIN:
        p.pos.x = a->u.terrain.u;
        p.pos.y = a->u.terrain.v;
        p.pos.z = a->u.terrain.h;
        break;
    case DG_ANCHOR_CORRIDOR_TRANS:
        p.pos.x = a->u.corridor.s;
        p.pos.y = a->u.corridor.t;
        p.pos.z = a->u.corridor.h;
        p.roll = a->u.corridor.roll;
        break;
    case DG_ANCHOR_STRUCT_SURFACE:
        p.pos.x = a->u.struct_surface.u;
        p.pos.y = a->u.struct_surface.v;
        p.pos.z = a->u.struct_surface.offset;
        break;
    case DG_ANCHOR_ROOM_SURFACE:
        p.pos.x = a->u.room_surface.u;
        p.pos.y = a->u.room_surface.v;
        p.pos.z = a->u.room_surface.offset;
        break;
    case DG_ANCHOR_SOCKET:
        p.pos.x = a->u.socket.param;
        p.pos.y = 0;
        p.pos.z = 0;
        break;
    default:
        break;
    }

    return p;
}

int dg_anchor_eval(
    const dg_anchor     *anchor,
    const d_world_frame *frames,
    dg_tick              tick,
    dg_round_mode        round_mode,
    dg_pose             *out_pose
) {
    dg_pose host_to_world;
    dg_pose local_to_host;

    if (!out_pose) return -1;
    *out_pose = dg_pose_identity();
    if (!anchor) return -2;

    local_to_host = dg_anchor_local_pose(anchor);

    if (anchor->host_frame == DG_FRAME_ID_WORLD) {
        host_to_world = dg_pose_identity();
    } else {
        if (!frames) return -3;
        if (d_world_frame_eval_to_world(frames, anchor->host_frame, tick, round_mode, &host_to_world) != 0) {
            return -4;
        }
    }

    *out_pose = dg_pose_compose(&host_to_world, &local_to_host, round_mode);
    return 0;
}

