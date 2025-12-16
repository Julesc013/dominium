/*
FILE: tests/domino_sim/test_dg_pose_anchor_quant.c
MODULE: Repository
LAYER / SUBSYSTEM: tests/domino_sim
RESPONSIBILITY: Owns documentation for this translation unit.
ALLOWED DEPENDENCIES: Project-local headers; C89/C++98 standard headers.
FORBIDDEN DEPENDENCIES: N/A.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include <string.h>

#include "core/dg_quant.h"
#include "world/frame/d_world_frame.h"
#include "world/frame/dg_anchor.h"

#include "core/dg_det_hash.h"

#define TEST_ASSERT(cond) do { if (!(cond)) return __LINE__; } while (0)

#define QONE ((dg_q)((i64)1 << 16))

static int pose_eq(const dg_pose *a, const dg_pose *b) {
    if (!a || !b) return 0;
    if (a->pos.x != b->pos.x) return 0;
    if (a->pos.y != b->pos.y) return 0;
    if (a->pos.z != b->pos.z) return 0;
    if (a->rot.x != b->rot.x) return 0;
    if (a->rot.y != b->rot.y) return 0;
    if (a->rot.z != b->rot.z) return 0;
    if (a->rot.w != b->rot.w) return 0;
    if (a->incline != b->incline) return 0;
    if (a->roll != b->roll) return 0;
    return 1;
}

static int anchor_eq(const dg_anchor *a, const dg_anchor *b) {
    return (dg_anchor_cmp(a, b) == 0) ? 1 : 0;
}

static dg_pose quant_pose(dg_pose p) {
    p.pos.x = dg_quant_pos(p.pos.x, DG_QUANT_POS_DEFAULT_Q);
    p.pos.y = dg_quant_pos(p.pos.y, DG_QUANT_POS_DEFAULT_Q);
    p.pos.z = dg_quant_pos(p.pos.z, DG_QUANT_POS_DEFAULT_Q);

    p.rot.x = dg_quant_param(p.rot.x, DG_QUANT_PARAM_DEFAULT_Q);
    p.rot.y = dg_quant_param(p.rot.y, DG_QUANT_PARAM_DEFAULT_Q);
    p.rot.z = dg_quant_param(p.rot.z, DG_QUANT_PARAM_DEFAULT_Q);
    p.rot.w = dg_quant_param(p.rot.w, DG_QUANT_PARAM_DEFAULT_Q);

    p.incline = dg_quant_angle(p.incline, DG_QUANT_ANGLE_DEFAULT_Q);
    p.roll = dg_quant_angle(p.roll, DG_QUANT_ANGLE_DEFAULT_Q);
    return p;
}

static dg_anchor quant_anchor(dg_anchor a) {
    switch (a.kind) {
    case DG_ANCHOR_TERRAIN:
        a.u.terrain.u = dg_quant_param(a.u.terrain.u, DG_QUANT_PARAM_DEFAULT_Q);
        a.u.terrain.v = dg_quant_param(a.u.terrain.v, DG_QUANT_PARAM_DEFAULT_Q);
        a.u.terrain.h = dg_quant_param(a.u.terrain.h, DG_QUANT_PARAM_DEFAULT_Q);
        break;
    case DG_ANCHOR_CORRIDOR_TRANS:
        a.u.corridor.s = dg_quant_param(a.u.corridor.s, DG_QUANT_PARAM_DEFAULT_Q);
        a.u.corridor.t = dg_quant_param(a.u.corridor.t, DG_QUANT_PARAM_DEFAULT_Q);
        a.u.corridor.h = dg_quant_param(a.u.corridor.h, DG_QUANT_PARAM_DEFAULT_Q);
        a.u.corridor.roll = dg_quant_angle(a.u.corridor.roll, DG_QUANT_ANGLE_DEFAULT_Q);
        break;
    case DG_ANCHOR_STRUCT_SURFACE:
        a.u.struct_surface.u = dg_quant_param(a.u.struct_surface.u, DG_QUANT_PARAM_DEFAULT_Q);
        a.u.struct_surface.v = dg_quant_param(a.u.struct_surface.v, DG_QUANT_PARAM_DEFAULT_Q);
        a.u.struct_surface.offset = dg_quant_param(a.u.struct_surface.offset, DG_QUANT_PARAM_DEFAULT_Q);
        break;
    case DG_ANCHOR_ROOM_SURFACE:
        a.u.room_surface.u = dg_quant_param(a.u.room_surface.u, DG_QUANT_PARAM_DEFAULT_Q);
        a.u.room_surface.v = dg_quant_param(a.u.room_surface.v, DG_QUANT_PARAM_DEFAULT_Q);
        a.u.room_surface.offset = dg_quant_param(a.u.room_surface.offset, DG_QUANT_PARAM_DEFAULT_Q);
        break;
    case DG_ANCHOR_SOCKET:
        a.u.socket.param = dg_quant_param(a.u.socket.param, DG_QUANT_PARAM_DEFAULT_Q);
        break;
    default:
        break;
    }
    a._pad32 = 0u;
    return a;
}

static void frame_graph_make(d_world_frame *g, d_world_frame_node *storage, u32 cap) {
    d_world_frame_node n;
    dg_pose p;
    (void)cap;

    d_world_frame_init(g, storage, cap);
    d_world_frame_clear(g);

    /* Frame 10: parent=world. Translate (10m,0,0) and rotate 180° about Z. */
    memset(&n, 0, sizeof(n));
    n.id = 10u;
    n.parent_id = DG_FRAME_ID_WORLD;
    p = dg_pose_identity();
    p.pos.x = (dg_q)((i64)10 * (i64)QONE);
    p.rot.x = 0;
    p.rot.y = 0;
    p.rot.z = QONE;
    p.rot.w = 0;
    n.to_parent = quant_pose(p);
    (void)d_world_frame_add(g, &n);

    /* Frame 11: parent=10. Translate (0, 5m, 0), identity rotation. */
    memset(&n, 0, sizeof(n));
    n.id = 11u;
    n.parent_id = 10u;
    p = dg_pose_identity();
    p.pos.y = (dg_q)((i64)5 * (i64)QONE);
    n.to_parent = quant_pose(p);
    (void)d_world_frame_add(g, &n);
}

static int test_quantization_determinism(void) {
    dg_anchor a0, a1;
    dg_pose p0, p1;

    memset(&a0, 0, sizeof(a0));
    memset(&a1, 0, sizeof(a1));
    a0.kind = DG_ANCHOR_SOCKET;
    a0.host_frame = 10u;
    a0.u.socket.socket_id = 99u;
    a0.u.socket.param = (dg_q)(1000 * DG_QUANT_PARAM_DEFAULT_Q + 1);

    a1 = a0;
    a1.u.socket.param = (dg_q)(1000 * DG_QUANT_PARAM_DEFAULT_Q + 2);

    memset(&p0, 0, sizeof(p0));
    memset(&p1, 0, sizeof(p1));
    p0 = dg_pose_identity();
    p1 = dg_pose_identity();
    p0.pos.x = (dg_q)(2000 * DG_QUANT_POS_DEFAULT_Q + 3);
    p1.pos.x = (dg_q)(2000 * DG_QUANT_POS_DEFAULT_Q + 4);
    p0.incline = (dg_q)(123 * DG_QUANT_ANGLE_DEFAULT_Q + 1);
    p1.incline = (dg_q)(123 * DG_QUANT_ANGLE_DEFAULT_Q + 2);

    a0 = quant_anchor(a0);
    a1 = quant_anchor(a1);
    p0 = quant_pose(p0);
    p1 = quant_pose(p1);

    TEST_ASSERT(anchor_eq(&a0, &a1));
    TEST_ASSERT(pose_eq(&p0, &p1));
    return 0;
}

static int test_anchor_stability(void) {
    d_world_frame g1, g2;
    d_world_frame_node nodes1[8];
    d_world_frame_node nodes2[8];
    dg_anchor a;
    dg_pose p_tick1, p_tick2;
    dg_pose p_rebuild;
    int rc;

    frame_graph_make(&g1, nodes1, 8u);
    frame_graph_make(&g2, nodes2, 8u); /* mock "rebuild" of derived artifacts */

    memset(&a, 0, sizeof(a));
    a.kind = DG_ANCHOR_SOCKET;
    a.host_frame = 10u;
    a.u.socket.socket_id = 7u;
    a.u.socket.param = (dg_q)((i64)1 * (i64)QONE); /* 1m along local +X */
    a = quant_anchor(a);

    memset(&p_tick1, 0, sizeof(p_tick1));
    memset(&p_tick2, 0, sizeof(p_tick2));
    rc = dg_anchor_eval(&a, &g1, 1u, DG_ROUND_NEAR, &p_tick1);
    TEST_ASSERT(rc == 0);
    rc = dg_anchor_eval(&a, &g1, 999u, DG_ROUND_NEAR, &p_tick2);
    TEST_ASSERT(rc == 0);
    TEST_ASSERT(pose_eq(&p_tick1, &p_tick2));

    rc = dg_anchor_eval(&a, &g2, 1u, DG_ROUND_NEAR, &p_rebuild);
    TEST_ASSERT(rc == 0);
    TEST_ASSERT(pose_eq(&p_tick1, &p_rebuild));
    return 0;
}

typedef struct test_pair {
    dg_anchor a;
    dg_pose   p;
} test_pair;

static void pairs_insertion_sort(test_pair *pairs, u32 count) {
    u32 i;
    if (!pairs || count < 2u) return;
    for (i = 1u; i < count; ++i) {
        test_pair key = pairs[i];
        u32 j = i;
        while (j > 0u && dg_anchor_cmp(&key.a, &pairs[j - 1u].a) < 0) {
            pairs[j] = pairs[j - 1u];
            j -= 1u;
        }
        pairs[j] = key;
    }
}

static void shuffle_u32(u32 *idx, u32 n, u64 seed) {
    u32 i;
    if (!idx || n < 2u) return;
    for (i = n - 1u; i > 0u; --i) {
        u64 h = dg_det_hash_u64(seed ^ (u64)i);
        u32 j = (u32)(h % (u64)(i + 1u));
        u32 tmp = idx[i];
        idx[i] = idx[j];
        idx[j] = tmp;
    }
}

static int test_ordering(void) {
    d_world_frame g;
    d_world_frame_node nodes[8];
    dg_anchor anchors[5];
    test_pair base[5];
    test_pair shuffled[5];
    u32 order[5];
    u32 i;
    int rc;

    frame_graph_make(&g, nodes, 8u);

    memset(anchors, 0, sizeof(anchors));

    anchors[0].kind = DG_ANCHOR_TERRAIN;
    anchors[0].host_frame = DG_FRAME_ID_WORLD;
    anchors[0].u.terrain.u = (dg_q)(10 * DG_QUANT_PARAM_DEFAULT_Q);
    anchors[0].u.terrain.v = (dg_q)(20 * DG_QUANT_PARAM_DEFAULT_Q);
    anchors[0].u.terrain.h = (dg_q)(0);

    anchors[1].kind = DG_ANCHOR_SOCKET;
    anchors[1].host_frame = 10u;
    anchors[1].u.socket.socket_id = 1u;
    anchors[1].u.socket.param = (dg_q)(2 * DG_QUANT_PARAM_DEFAULT_Q);

    anchors[2].kind = DG_ANCHOR_STRUCT_SURFACE;
    anchors[2].host_frame = 11u;
    anchors[2].u.struct_surface.structure_id = 123u;
    anchors[2].u.struct_surface.surface_id = 4u;
    anchors[2].u.struct_surface.u = (dg_q)(3 * DG_QUANT_PARAM_DEFAULT_Q);
    anchors[2].u.struct_surface.v = (dg_q)(1 * DG_QUANT_PARAM_DEFAULT_Q);
    anchors[2].u.struct_surface.offset = (dg_q)(0);

    anchors[3].kind = DG_ANCHOR_CORRIDOR_TRANS;
    anchors[3].host_frame = 11u;
    anchors[3].u.corridor.alignment_id = 777u;
    anchors[3].u.corridor.s = (dg_q)(5 * DG_QUANT_PARAM_DEFAULT_Q);
    anchors[3].u.corridor.t = (dg_q)(0);
    anchors[3].u.corridor.h = (dg_q)(0);
    anchors[3].u.corridor.roll = (dg_q)(2 * DG_QUANT_ANGLE_DEFAULT_Q);

    anchors[4].kind = DG_ANCHOR_ROOM_SURFACE;
    anchors[4].host_frame = 10u;
    anchors[4].u.room_surface.room_id = 9u;
    anchors[4].u.room_surface.surface_id = 2u;
    anchors[4].u.room_surface.u = (dg_q)(8 * DG_QUANT_PARAM_DEFAULT_Q);
    anchors[4].u.room_surface.v = (dg_q)(7 * DG_QUANT_PARAM_DEFAULT_Q);
    anchors[4].u.room_surface.offset = (dg_q)(0);

    for (i = 0u; i < 5u; ++i) {
        anchors[i] = quant_anchor(anchors[i]);
    }

    memset(base, 0, sizeof(base));
    for (i = 0u; i < 5u; ++i) {
        base[i].a = anchors[i];
        rc = dg_anchor_eval(&base[i].a, &g, 42u, DG_ROUND_NEAR, &base[i].p);
        TEST_ASSERT(rc == 0);
    }
    pairs_insertion_sort(base, 5u);

    for (i = 0u; i < 5u; ++i) order[i] = i;
    shuffle_u32(order, 5u, 0xC0FFEEu);

    memset(shuffled, 0, sizeof(shuffled));
    for (i = 0u; i < 5u; ++i) {
        shuffled[i].a = anchors[order[i]];
        rc = dg_anchor_eval(&shuffled[i].a, &g, 42u, DG_ROUND_NEAR, &shuffled[i].p);
        TEST_ASSERT(rc == 0);
    }
    pairs_insertion_sort(shuffled, 5u);

    for (i = 0u; i < 5u; ++i) {
        TEST_ASSERT(anchor_eq(&base[i].a, &shuffled[i].a));
        TEST_ASSERT(pose_eq(&base[i].p, &shuffled[i].p));
    }

    return 0;
}

int main(void) {
    int rc;
    rc = test_quantization_determinism();
    if (rc != 0) return rc;
    rc = test_anchor_stability();
    if (rc != 0) return rc;
    rc = test_ordering();
    if (rc != 0) return rc;
    return 0;
}

