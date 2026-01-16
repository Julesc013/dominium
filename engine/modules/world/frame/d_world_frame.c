/*
FILE: source/domino/world/frame/d_world_frame.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / world/frame/d_world_frame
RESPONSIBILITY: Implements `d_world_frame`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
/* World frame graph (C89). */
#include "world/frame/d_world_frame.h"

#include <string.h>

void d_world_frame_init(d_world_frame *g, d_world_frame_node *storage, u32 capacity) {
    if (!g) return;
    g->nodes = storage;
    g->count = 0u;
    g->capacity = capacity;
}

void d_world_frame_clear(d_world_frame *g) {
    if (!g) return;
    g->count = 0u;
}

int d_world_frame_add(d_world_frame *g, const d_world_frame_node *node) {
    u32 i;
    if (!g || !node) return -1;
    if (!g->nodes || g->capacity == 0u) return -2;
    if (node->id == DG_FRAME_ID_WORLD) return -3;
    if (g->count >= g->capacity) return -4;

    for (i = 0u; i < g->count; ++i) {
        if (g->nodes[i].id == node->id) {
            return -5; /* duplicate */
        }
    }

    g->nodes[g->count] = *node;
    g->count += 1u;
    return 0;
}

int d_world_frame_find(const d_world_frame *g, dg_frame_id id, d_world_frame_node *out_node) {
    u32 i;
    if (!g || !out_node) return -1;
    if (id == DG_FRAME_ID_WORLD) return -2;
    if (!g->nodes) return -3;
    for (i = 0u; i < g->count; ++i) {
        if (g->nodes[i].id == id) {
            *out_node = g->nodes[i];
            return 0;
        }
    }
    return -4;
}

int d_world_frame_eval_to_world(
    const d_world_frame *g,
    dg_frame_id          id,
    dg_tick              tick,
    dg_round_mode        round_mode,
    dg_pose             *out_pose
) {
    dg_pose chain[D_WORLD_FRAME_MAX_DEPTH];
    u32 depth;
    dg_frame_id cur;
    dg_pose accum;
    u32 i;
    (void)tick;

    if (!out_pose) return -1;
    *out_pose = dg_pose_identity();
    if (id == DG_FRAME_ID_WORLD) return 0;
    if (!g || !g->nodes) return -2;

    depth = 0u;
    cur = id;
    while (cur != DG_FRAME_ID_WORLD && depth < D_WORLD_FRAME_MAX_DEPTH) {
        d_world_frame_node node;
        if (d_world_frame_find(g, cur, &node) != 0) {
            return -3;
        }
        chain[depth] = node.to_parent;
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
    *out_pose = accum;
    return 0;
}

