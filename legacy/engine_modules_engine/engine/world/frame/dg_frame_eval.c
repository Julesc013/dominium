/*
FILE: source/domino/world/frame/dg_frame_eval.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / world/frame/dg_frame_eval
RESPONSIBILITY: Implements `dg_frame_eval`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include <string.h>

#include "world/frame/dg_frame_eval.h"

#include "domino/core/fixed.h"

static i64 dg_tick_clamp_to_i64(dg_tick t) {
    const u64 max_i64 = 0x7FFFFFFFFFFFFFFFULL;
    if (t > max_i64) {
        return (i64)max_i64;
    }
    return (i64)t;
}

static dg_pose dg_frame_eval_to_parent_at_tick(const dg_frame_node *node, dg_tick tick) {
    dg_pose p;
    q48_16 tick_q48;
    q48_16 dx, dy, dz;
    q48_16 di, dr;
    i64 tick_i64;

    if (!node) {
        return dg_pose_identity();
    }

    p = node->to_parent_base;

    tick_i64 = dg_tick_clamp_to_i64(tick);
    tick_q48 = d_q48_16_from_int(tick_i64);

    dx = d_q48_16_mul((q48_16)node->vel_pos_per_tick.x, tick_q48);
    dy = d_q48_16_mul((q48_16)node->vel_pos_per_tick.y, tick_q48);
    dz = d_q48_16_mul((q48_16)node->vel_pos_per_tick.z, tick_q48);

    p.pos.x = (dg_q)d_q48_16_add((q48_16)p.pos.x, dx);
    p.pos.y = (dg_q)d_q48_16_add((q48_16)p.pos.y, dy);
    p.pos.z = (dg_q)d_q48_16_add((q48_16)p.pos.z, dz);

    di = d_q48_16_mul((q48_16)node->vel_incline_per_tick, tick_q48);
    dr = d_q48_16_mul((q48_16)node->vel_roll_per_tick, tick_q48);
    p.incline = (dg_q)d_q48_16_add((q48_16)p.incline, di);
    p.roll = (dg_q)d_q48_16_add((q48_16)p.roll, dr);

    return p;
}

int dg_frame_eval(
    const dg_frame_graph *g,
    dg_frame_id           id,
    dg_tick               tick,
    dg_round_mode         round_mode,
    dg_pose              *out_transform
) {
    dg_pose chain[DG_FRAME_MAX_DEPTH];
    u32 depth;
    dg_frame_id cur;
    dg_pose accum;
    u32 i;

    if (!out_transform) return -1;
    *out_transform = dg_pose_identity();
    if (id == DG_FRAME_ID_WORLD) return 0;
    if (!g || !g->nodes) return -2;

    depth = 0u;
    cur = id;
    while (cur != DG_FRAME_ID_WORLD && depth < DG_FRAME_MAX_DEPTH) {
        dg_frame_node node;
        if (dg_frame_graph_find(g, cur, &node) != 0) {
            return -3;
        }
        chain[depth] = dg_frame_eval_to_parent_at_tick(&node, tick);
        depth += 1u;
        cur = node.parent_id;
    }
    if (cur != DG_FRAME_ID_WORLD) {
        return -4; /* cycle or depth overflow */
    }

    accum = dg_pose_identity();
    for (i = depth; i > 0u; --i) {
        accum = dg_pose_compose(&accum, &chain[i - 1u], round_mode);
    }
    *out_transform = accum;
    return 0;
}

