/*
FILE: tests/domino_struct/test_dg_struct_compile_determinism.c
MODULE: Repository
LAYER / SUBSYSTEM: tests/domino_struct
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

#include "core/dg_det_hash.h"

#include "struct/model/dg_struct_instance.h"
#include "struct/model/dg_struct_footprint.h"
#include "struct/model/dg_struct_volume.h"
#include "struct/model/dg_struct_enclosure.h"
#include "struct/model/dg_struct_surface.h"
#include "struct/model/dg_struct_socket.h"
#include "struct/model/dg_struct_carrier_intent.h"

#include "struct/compile/dg_struct_compile.h"

#define TEST_ASSERT(cond) do { if (!(cond)) return __LINE__; } while (0)

#define QONE ((dg_q)((i64)1 << 16))

static dg_q q_int(i64 v) { return (dg_q)(v * (i64)QONE); }

static u64 hash_step_u64(u64 h, u64 v) { return dg_det_hash_u64(h ^ v); }
static u64 hash_step_i64(u64 h, i64 v) { return dg_det_hash_u64(h ^ (u64)v); }
static u64 hash_step_i32(u64 h, i32 v) { return dg_det_hash_u64(h ^ (u64)(u32)v); }

static u64 hash_vec3(u64 h, dg_vec3_q v) {
    h = hash_step_i64(h, (i64)v.x);
    h = hash_step_i64(h, (i64)v.y);
    h = hash_step_i64(h, (i64)v.z);
    return h;
}

static u64 hash_aabb(u64 h, const dg_struct_aabb *b) {
    if (!b) return h;
    h = hash_vec3(h, b->min);
    h = hash_vec3(h, b->max);
    return h;
}

static u64 hash_compiled(const dg_struct_compiler *c) {
    u64 h = 0xD6E8FEB86659FD93ULL;
    u32 i;
    if (!c) return 0u;

    h = hash_step_u64(h, (u64)c->compiled.struct_count);
    for (i = 0u; i < c->compiled.struct_count; ++i) {
        const dg_struct_compiled_struct *s = &c->compiled.structs[i];
        u32 j;

        h = hash_step_u64(h, (u64)s->struct_id);

        h = hash_step_u64(h, (u64)s->occupancy.region_count);
        for (j = 0u; j < s->occupancy.region_count; ++j) {
            const dg_struct_occ_region *r = &s->occupancy.regions[j];
            h = hash_step_u64(h, (u64)r->id);
            h = hash_step_u64(h, (u64)r->struct_id);
            h = hash_step_u64(h, (u64)r->volume_id);
            h = hash_step_u64(h, (u64)(r->is_void ? 1u : 0u));
            h = hash_aabb(h, &r->bbox_world);
        }

        h = hash_step_u64(h, (u64)s->enclosures.room_count);
        h = hash_step_u64(h, (u64)s->enclosures.edge_count);
        for (j = 0u; j < s->enclosures.room_count; ++j) {
            const dg_struct_room_node *n = &s->enclosures.rooms[j];
            h = hash_step_u64(h, (u64)n->id);
            h = hash_step_u64(h, (u64)n->struct_id);
            h = hash_step_u64(h, (u64)n->enclosure_id);
            h = hash_aabb(h, &n->bbox_world);
        }
        for (j = 0u; j < s->enclosures.edge_count; ++j) {
            const dg_struct_room_edge *e = &s->enclosures.edges[j];
            h = hash_step_u64(h, (u64)e->id);
            h = hash_step_u64(h, (u64)e->room_a);
            h = hash_step_u64(h, (u64)e->room_b);
            h = hash_step_i32(h, (i32)e->kind);
        }

        h = hash_step_u64(h, (u64)s->surfaces.surface_count);
        h = hash_step_u64(h, (u64)s->surfaces.socket_count);
        for (j = 0u; j < s->surfaces.surface_count; ++j) {
            const dg_struct_compiled_surface *sf = &s->surfaces.surfaces[j];
            h = hash_step_u64(h, (u64)sf->id);
            h = hash_step_u64(h, (u64)sf->template_id);
            h = hash_step_u64(h, (u64)sf->volume_id);
            h = hash_step_u64(h, (u64)sf->enclosure_id);
            h = hash_step_i32(h, (i32)sf->face_kind);
            h = hash_step_u64(h, (u64)sf->face_index);
            h = hash_vec3(h, sf->origin_world);
            h = hash_vec3(h, sf->u_vec_world);
            h = hash_vec3(h, sf->v_vec_world);
            h = hash_step_i64(h, (i64)sf->u_len);
            h = hash_step_i64(h, (i64)sf->v_len);
            h = hash_aabb(h, &sf->bbox_world);
        }
        for (j = 0u; j < s->surfaces.socket_count; ++j) {
            const dg_struct_compiled_socket *so = &s->surfaces.sockets[j];
            h = hash_step_u64(h, (u64)so->id);
            h = hash_step_u64(h, (u64)so->surface_id);
            h = hash_step_i64(h, (i64)so->u);
            h = hash_step_i64(h, (i64)so->v);
            h = hash_step_i64(h, (i64)so->offset);
        }

        h = hash_step_u64(h, (u64)s->supports.node_count);
        h = hash_step_u64(h, (u64)s->supports.edge_count);
        for (j = 0u; j < s->supports.node_count; ++j) {
            const dg_struct_support_node *n = &s->supports.nodes[j];
            h = hash_step_u64(h, (u64)n->id);
            h = hash_vec3(h, n->pos_world);
            h = hash_step_i64(h, (i64)n->capacity);
        }
        for (j = 0u; j < s->supports.edge_count; ++j) {
            const dg_struct_support_edge *e = &s->supports.edges[j];
            h = hash_step_u64(h, (u64)e->id);
            h = hash_step_u64(h, (u64)e->a);
            h = hash_step_u64(h, (u64)e->b);
            h = hash_step_i64(h, (i64)e->capacity);
        }

        h = hash_step_u64(h, (u64)s->carriers.count);
        for (j = 0u; j < s->carriers.count; ++j) {
            const dg_struct_carrier_artifact *a = &s->carriers.items[j];
            h = hash_step_u64(h, (u64)a->id);
            h = hash_step_u64(h, (u64)a->intent_id);
            h = hash_step_i32(h, (i32)a->kind);
            h = hash_vec3(h, a->a0_world.pos);
            h = hash_vec3(h, a->a1_world.pos);
            h = hash_step_i64(h, (i64)a->width);
            h = hash_step_i64(h, (i64)a->height);
            h = hash_step_i64(h, (i64)a->depth);
            h = hash_aabb(h, &a->bbox_world);
        }
    }

    h = hash_step_u64(h, (u64)c->compiled.occupancy_spatial.count);
    for (i = 0u; i < c->compiled.occupancy_spatial.count; ++i) {
        const dg_struct_occ_spatial_entry *e = &c->compiled.occupancy_spatial.entries[i];
        h = hash_step_i32(h, e->chunk.cx);
        h = hash_step_i32(h, e->chunk.cy);
        h = hash_step_i32(h, e->chunk.cz);
        h = hash_step_u64(h, (u64)e->struct_id);
        h = hash_step_u64(h, (u64)e->region_id);
        h = hash_aabb(h, &e->bbox);
    }

    h = hash_step_u64(h, (u64)c->compiled.enclosure_spatial.count);
    for (i = 0u; i < c->compiled.enclosure_spatial.count; ++i) {
        const dg_struct_room_spatial_entry *e = &c->compiled.enclosure_spatial.entries[i];
        h = hash_step_i32(h, e->chunk.cx);
        h = hash_step_i32(h, e->chunk.cy);
        h = hash_step_i32(h, e->chunk.cz);
        h = hash_step_u64(h, (u64)e->struct_id);
        h = hash_step_u64(h, (u64)e->room_id);
        h = hash_aabb(h, &e->bbox);
    }

    h = hash_step_u64(h, (u64)c->compiled.surface_spatial.count);
    for (i = 0u; i < c->compiled.surface_spatial.count; ++i) {
        const dg_struct_surface_spatial_entry *e = &c->compiled.surface_spatial.entries[i];
        h = hash_step_i32(h, e->chunk.cx);
        h = hash_step_i32(h, e->chunk.cy);
        h = hash_step_i32(h, e->chunk.cz);
        h = hash_step_u64(h, (u64)e->struct_id);
        h = hash_step_u64(h, (u64)e->surface_id);
        h = hash_aabb(h, &e->bbox);
    }

    h = hash_step_u64(h, (u64)c->compiled.support_spatial.count);
    for (i = 0u; i < c->compiled.support_spatial.count; ++i) {
        const dg_struct_support_spatial_entry *e = &c->compiled.support_spatial.entries[i];
        h = hash_step_i32(h, e->chunk.cx);
        h = hash_step_i32(h, e->chunk.cy);
        h = hash_step_i32(h, e->chunk.cz);
        h = hash_step_u64(h, (u64)e->struct_id);
        h = hash_step_u64(h, (u64)e->node_id);
        h = hash_vec3(h, e->pos_world);
    }

    h = hash_step_u64(h, (u64)c->compiled.carrier_spatial.count);
    for (i = 0u; i < c->compiled.carrier_spatial.count; ++i) {
        const dg_struct_carrier_spatial_entry *e = &c->compiled.carrier_spatial.entries[i];
        h = hash_step_i32(h, e->chunk.cx);
        h = hash_step_i32(h, e->chunk.cy);
        h = hash_step_i32(h, e->chunk.cz);
        h = hash_step_u64(h, (u64)e->struct_id);
        h = hash_step_u64(h, (u64)e->artifact_id);
        h = hash_aabb(h, &e->bbox);
    }

    return h;
}

static void build_square_footprint(dg_struct_footprint *fp, dg_struct_footprint_id id, dg_q x0, dg_q y0, dg_q x1, dg_q y1) {
    dg_struct_footprint_init(fp);
    fp->id = id;
    (void)dg_struct_footprint_set_ring(fp, 0u, D_FALSE);
    (void)dg_struct_footprint_set_vertex(fp, 0u, 0u, x0, y0);
    (void)dg_struct_footprint_set_vertex(fp, 0u, 1u, x1, y0);
    (void)dg_struct_footprint_set_vertex(fp, 0u, 2u, x1, y1);
    (void)dg_struct_footprint_set_vertex(fp, 0u, 3u, x0, y1);
    (void)dg_struct_footprint_canon_winding(fp);
}

static void build_extrude_volume(dg_struct_volume *v, dg_struct_volume_id id, dg_struct_footprint_id fp_id, dg_q base_z, dg_q height, d_bool is_void) {
    dg_struct_volume_init(v);
    v->id = id;
    (void)dg_struct_volume_set_extrude(v, fp_id, base_z, height, is_void);
}

static void build_enclosure_one(dg_struct_enclosure *e, dg_struct_enclosure_id id, dg_struct_volume_id vol_id) {
    dg_struct_aperture ap;
    dg_struct_enclosure_init(e);
    e->id = id;
    (void)dg_struct_enclosure_add_volume(e, vol_id);
    memset(&ap, 0, sizeof(ap));
    ap.aperture_id = 1u;
    ap.to_enclosure_id = 0u;
    ap.kind = DG_STRUCT_APERTURE_DOOR;
    (void)dg_struct_enclosure_set_aperture(e, &ap);
}

static void build_surface_template_vol_face(dg_struct_surface_template *t, dg_struct_surface_template_id id, dg_struct_volume_id vol_id, dg_struct_volume_face_kind face_kind, u32 face_index) {
    dg_struct_surface_template_clear(t);
    t->id = id;
    t->kind = DG_STRUCT_SURF_TMPL_VOLUME_FACE;
    t->volume_id = vol_id;
    t->face_kind = face_kind;
    t->face_index = face_index;
}

static void build_socket(dg_struct_socket *s, dg_struct_socket_id id, dg_struct_surface_template_id surface_template_id, dg_q u, dg_q v, dg_q offset) {
    dg_struct_socket_clear(s);
    s->id = id;
    s->surface_template_id = surface_template_id;
    s->u = u;
    s->v = v;
    s->offset = offset;
}

static void build_instance_basic(dg_struct_instance *inst, dg_struct_id id, dg_struct_footprint_id fp_id, dg_struct_volume_id v0, dg_struct_volume_id v1, dg_struct_enclosure_id enc_id, dg_struct_surface_template_id st0, dg_struct_surface_template_id st1, dg_struct_socket_id sock_id) {
    dg_struct_instance_init(inst);
    inst->id = id;
    inst->footprint_id = fp_id;

    dg_anchor_clear(&inst->anchor);
    inst->anchor.kind = DG_ANCHOR_TERRAIN;
    inst->anchor.host_frame = DG_FRAME_ID_WORLD;
    inst->anchor.u.terrain.u = q_int(100);
    inst->anchor.u.terrain.v = q_int(200);
    inst->anchor.u.terrain.h = 0;

    inst->local_pose = dg_pose_identity();
    inst->local_pose.rot.x = 0;
    inst->local_pose.rot.y = 0;
    inst->local_pose.rot.z = (dg_q)46340; /* sin(pi/4) in Q16 */
    inst->local_pose.rot.w = (dg_q)46340; /* cos(pi/4) in Q16 */

    (void)dg_struct_instance_add_volume(inst, v0);
    (void)dg_struct_instance_add_volume(inst, v1);
    (void)dg_struct_instance_add_enclosure(inst, enc_id);
    (void)dg_struct_instance_add_surface_template(inst, st0);
    (void)dg_struct_instance_add_surface_template(inst, st1);
    (void)dg_struct_instance_add_socket(inst, sock_id);
}

static void compile_until_done(dg_struct_compiler *c, const dg_struct_compile_input *in, u32 budget_units) {
    while (dg_struct_compiler_pending_work(c) != 0u) {
        (void)dg_struct_compiler_process(c, in, 1u, budget_units);
    }
}

static int test_struct_compilation_determinism(void) {
    dg_struct_footprint fps_base[2];
    dg_struct_volume vols_base[2];
    dg_struct_enclosure enc_base[1];
    dg_struct_surface_template st_base[2];
    dg_struct_socket sock_base[1];
    dg_struct_instance inst_base[1];

    dg_struct_footprint fps_rev[2];
    dg_struct_volume vols_rev[2];
    dg_struct_surface_template st_rev[2];
    dg_struct_socket sock_rev[1];
    dg_struct_instance inst_rev[1];

    dg_struct_compile_input in_a;
    dg_struct_compile_input in_b;

    dg_struct_compiler ca;
    dg_struct_compiler cb;
    u64 ha;
    u64 hb;
    const dg_struct_id sid = 100u;

    build_square_footprint(&fps_base[0], 10u, 0, 0, q_int(10), q_int(10));
    build_square_footprint(&fps_base[1], 11u, q_int(2), q_int(2), q_int(8), q_int(8));

    build_extrude_volume(&vols_base[0], 20u, fps_base[0].id, 0, q_int(6), D_FALSE);
    build_extrude_volume(&vols_base[1], 21u, fps_base[1].id, 0, q_int(5), D_TRUE);

    build_enclosure_one(&enc_base[0], 30u, vols_base[1].id);

    build_surface_template_vol_face(&st_base[0], 40u, vols_base[0].id, DG_STRUCT_VOL_FACE_TOP, 0u);
    build_surface_template_vol_face(&st_base[1], 41u, vols_base[0].id, DG_STRUCT_VOL_FACE_SIDE, 0u);

    build_socket(&sock_base[0], 50u, st_base[1].id, q_int(1), q_int(2), q_int(0));

    build_instance_basic(&inst_base[0], sid, fps_base[0].id, vols_base[0].id, vols_base[1].id, enc_base[0].id, st_base[0].id, st_base[1].id, sock_base[0].id);

    /* Reordered insertion views (shallow copies). */
    fps_rev[0] = fps_base[1];
    fps_rev[1] = fps_base[0];
    vols_rev[0] = vols_base[1];
    vols_rev[1] = vols_base[0];
    st_rev[0] = st_base[1];
    st_rev[1] = st_base[0];
    sock_rev[0] = sock_base[0];
    inst_rev[0] = inst_base[0];

    memset(&in_a, 0, sizeof(in_a));
    in_a.instances = inst_base;
    in_a.instance_count = 1u;
    in_a.footprints = fps_base;
    in_a.footprint_count = 2u;
    in_a.volumes = vols_base;
    in_a.volume_count = 2u;
    in_a.enclosures = enc_base;
    in_a.enclosure_count = 1u;
    in_a.surface_templates = st_base;
    in_a.surface_template_count = 2u;
    in_a.sockets = sock_base;
    in_a.socket_count = 1u;
    in_a.carrier_intents = (const dg_struct_carrier_intent *)0;
    in_a.carrier_intent_count = 0u;
    in_a.frames = (const d_world_frame *)0;

    memset(&in_b, 0, sizeof(in_b));
    in_b.instances = inst_rev;
    in_b.instance_count = 1u;
    in_b.footprints = fps_rev;
    in_b.footprint_count = 2u;
    in_b.volumes = vols_rev;
    in_b.volume_count = 2u;
    in_b.enclosures = enc_base;
    in_b.enclosure_count = 1u;
    in_b.surface_templates = st_rev;
    in_b.surface_template_count = 2u;
    in_b.sockets = sock_rev;
    in_b.socket_count = 1u;
    in_b.carrier_intents = (const dg_struct_carrier_intent *)0;
    in_b.carrier_intent_count = 0u;
    in_b.frames = (const d_world_frame *)0;

    dg_struct_compiler_init(&ca);
    dg_struct_compiler_init(&cb);
    TEST_ASSERT(dg_struct_compiler_reserve(&ca, 64u, 1024u) == 0);
    TEST_ASSERT(dg_struct_compiler_reserve(&cb, 64u, 1024u) == 0);
    TEST_ASSERT(dg_struct_compiler_set_params(&ca, q_int(16)) == 0);
    TEST_ASSERT(dg_struct_compiler_set_params(&cb, q_int(16)) == 0);
    TEST_ASSERT(dg_struct_compiler_sync(&ca, &in_a) == 0);
    TEST_ASSERT(dg_struct_compiler_sync(&cb, &in_b) == 0);

    dg_struct_dirty_mark(&ca.dirty, sid, DG_STRUCT_DIRTY_FOOTPRINT | DG_STRUCT_DIRTY_VOLUME | DG_STRUCT_DIRTY_ENCLOSURE | DG_STRUCT_DIRTY_SURFACE);
    dg_struct_dirty_mark(&cb.dirty, sid, DG_STRUCT_DIRTY_FOOTPRINT | DG_STRUCT_DIRTY_VOLUME | DG_STRUCT_DIRTY_ENCLOSURE | DG_STRUCT_DIRTY_SURFACE);
    TEST_ASSERT(dg_struct_compiler_enqueue_dirty(&ca, 1u) == 0);
    TEST_ASSERT(dg_struct_compiler_enqueue_dirty(&cb, 1u) == 0);
    compile_until_done(&ca, &in_a, 0xFFFFFFFFu);
    compile_until_done(&cb, &in_b, 0xFFFFFFFFu);
    TEST_ASSERT(dg_struct_compiler_check_invariants(&ca, &in_a) == 0);
    TEST_ASSERT(dg_struct_compiler_check_invariants(&cb, &in_b) == 0);

    ha = hash_compiled(&ca);
    hb = hash_compiled(&cb);
    TEST_ASSERT(ha == hb);

    dg_struct_compiler_free(&ca);
    dg_struct_compiler_free(&cb);

    dg_struct_instance_free(&inst_base[0]);
    dg_struct_enclosure_free(&enc_base[0]);
    dg_struct_footprint_free(&fps_base[0]);
    dg_struct_footprint_free(&fps_base[1]);
    dg_struct_volume_free(&vols_base[0]);
    dg_struct_volume_free(&vols_base[1]);
    return 0;
}

static int test_struct_dirty_rebuild(void) {
    dg_struct_footprint fps[2];
    dg_struct_volume vols[2];
    dg_struct_enclosure enc[1];
    dg_struct_surface_template st[2];
    dg_struct_socket sock[1];
    dg_struct_instance inst[1];
    dg_struct_compile_input in;

    dg_struct_compiler partial;
    dg_struct_compiler full;
    dg_struct_dirty_record dr;
    u64 h_partial;
    u64 h_full;
    const dg_struct_id sid = 200u;

    build_square_footprint(&fps[0], 10u, 0, 0, q_int(10), q_int(10));
    build_square_footprint(&fps[1], 11u, q_int(2), q_int(2), q_int(8), q_int(8));
    build_extrude_volume(&vols[0], 20u, fps[0].id, 0, q_int(6), D_FALSE);
    build_extrude_volume(&vols[1], 21u, fps[1].id, 0, q_int(5), D_TRUE);
    build_enclosure_one(&enc[0], 30u, vols[1].id);
    build_surface_template_vol_face(&st[0], 40u, vols[0].id, DG_STRUCT_VOL_FACE_TOP, 0u);
    build_surface_template_vol_face(&st[1], 41u, vols[0].id, DG_STRUCT_VOL_FACE_SIDE, 0u);
    build_socket(&sock[0], 50u, st[1].id, q_int(1), q_int(2), q_int(0));
    build_instance_basic(&inst[0], sid, fps[0].id, vols[0].id, vols[1].id, enc[0].id, st[0].id, st[1].id, sock[0].id);

    memset(&in, 0, sizeof(in));
    in.instances = inst;
    in.instance_count = 1u;
    in.footprints = fps;
    in.footprint_count = 2u;
    in.volumes = vols;
    in.volume_count = 2u;
    in.enclosures = enc;
    in.enclosure_count = 1u;
    in.surface_templates = st;
    in.surface_template_count = 2u;
    in.sockets = sock;
    in.socket_count = 1u;
    in.carrier_intents = (const dg_struct_carrier_intent *)0;
    in.carrier_intent_count = 0u;
    in.frames = (const d_world_frame *)0;

    dg_struct_compiler_init(&partial);
    TEST_ASSERT(dg_struct_compiler_reserve(&partial, 64u, 1024u) == 0);
    TEST_ASSERT(dg_struct_compiler_set_params(&partial, q_int(16)) == 0);
    TEST_ASSERT(dg_struct_compiler_sync(&partial, &in) == 0);

    /* Initial full compile. */
    dg_struct_dirty_mark(&partial.dirty, sid, DG_STRUCT_DIRTY_FOOTPRINT | DG_STRUCT_DIRTY_VOLUME | DG_STRUCT_DIRTY_ENCLOSURE | DG_STRUCT_DIRTY_SURFACE);
    TEST_ASSERT(dg_struct_compiler_enqueue_dirty(&partial, 1u) == 0);
    compile_until_done(&partial, &in, 0xFFFFFFFFu);
    TEST_ASSERT(dg_struct_compiler_check_invariants(&partial, &in) == 0);

    /* Mutate a single enclosure: change aperture kind. */
    enc[0].apertures[0].kind = DG_STRUCT_APERTURE_VENT;

    dg_struct_dirty_mark(&partial.dirty, sid, DG_STRUCT_DIRTY_ENCLOSURE);
    TEST_ASSERT(dg_struct_dirty_get(&partial.dirty, sid, &dr) == 1);
    TEST_ASSERT(dr.dirty_flags == (DG_STRUCT_DIRTY_ENCLOSURE | DG_STRUCT_DIRTY_SURFACE));

    TEST_ASSERT(dg_struct_compiler_enqueue_dirty(&partial, 2u) == 0);
    /* Constrained budget: should take multiple ticks, but must converge deterministically. */
    compile_until_done(&partial, &in, 4u);
    TEST_ASSERT(dg_struct_compiler_check_invariants(&partial, &in) == 0);

    /* Full rebuild from scratch must match. */
    dg_struct_compiler_init(&full);
    TEST_ASSERT(dg_struct_compiler_reserve(&full, 64u, 1024u) == 0);
    TEST_ASSERT(dg_struct_compiler_set_params(&full, q_int(16)) == 0);
    TEST_ASSERT(dg_struct_compiler_sync(&full, &in) == 0);
    dg_struct_dirty_mark(&full.dirty, sid, DG_STRUCT_DIRTY_FOOTPRINT | DG_STRUCT_DIRTY_VOLUME | DG_STRUCT_DIRTY_ENCLOSURE | DG_STRUCT_DIRTY_SURFACE);
    TEST_ASSERT(dg_struct_compiler_enqueue_dirty(&full, 1u) == 0);
    compile_until_done(&full, &in, 0xFFFFFFFFu);
    TEST_ASSERT(dg_struct_compiler_check_invariants(&full, &in) == 0);

    h_partial = hash_compiled(&partial);
    h_full = hash_compiled(&full);
    TEST_ASSERT(h_partial == h_full);

    dg_struct_compiler_free(&partial);
    dg_struct_compiler_free(&full);

    dg_struct_instance_free(&inst[0]);
    dg_struct_enclosure_free(&enc[0]);
    dg_struct_footprint_free(&fps[0]);
    dg_struct_footprint_free(&fps[1]);
    dg_struct_volume_free(&vols[0]);
    dg_struct_volume_free(&vols[1]);
    return 0;
}

static void build_carrier_bridge(dg_struct_carrier_intent *c, dg_struct_carrier_intent_id id) {
    dg_struct_carrier_intent_init(c);
    c->id = id;
    c->kind = DG_STRUCT_CARRIER_BRIDGE;

    dg_anchor_clear(&c->a0);
    c->a0.kind = DG_ANCHOR_TERRAIN;
    c->a0.host_frame = DG_FRAME_ID_WORLD;
    c->a0.u.terrain.u = q_int(0);
    c->a0.u.terrain.v = q_int(0);
    c->a0.u.terrain.h = q_int(0);

    dg_anchor_clear(&c->a1);
    c->a1.kind = DG_ANCHOR_TERRAIN;
    c->a1.host_frame = DG_FRAME_ID_WORLD;
    c->a1.u.terrain.u = q_int(32);
    c->a1.u.terrain.v = q_int(0);
    c->a1.u.terrain.h = q_int(0);

    c->width = q_int(6);
    c->height = q_int(2);
    c->depth = q_int(0);
}

static int test_struct_carrier_determinism(void) {
    dg_struct_carrier_intent carrier[1];
    dg_struct_instance inst[1];
    dg_struct_compile_input in;
    dg_struct_compiler c1;
    dg_struct_compiler c2;
    u64 h1;
    u64 h2;
    const dg_struct_id sid = 300u;

    build_carrier_bridge(&carrier[0], 500u);

    dg_struct_instance_init(&inst[0]);
    inst[0].id = sid;
    dg_anchor_clear(&inst[0].anchor);
    inst[0].anchor.kind = DG_ANCHOR_TERRAIN;
    inst[0].anchor.host_frame = DG_FRAME_ID_WORLD;
    inst[0].anchor.u.terrain.u = q_int(0);
    inst[0].anchor.u.terrain.v = q_int(0);
    inst[0].anchor.u.terrain.h = q_int(0);
    inst[0].local_pose = dg_pose_identity();
    (void)dg_struct_instance_add_carrier_intent(&inst[0], carrier[0].id);

    memset(&in, 0, sizeof(in));
    in.instances = inst;
    in.instance_count = 1u;
    in.footprints = (const dg_struct_footprint *)0;
    in.footprint_count = 0u;
    in.volumes = (const dg_struct_volume *)0;
    in.volume_count = 0u;
    in.enclosures = (const dg_struct_enclosure *)0;
    in.enclosure_count = 0u;
    in.surface_templates = (const dg_struct_surface_template *)0;
    in.surface_template_count = 0u;
    in.sockets = (const dg_struct_socket *)0;
    in.socket_count = 0u;
    in.carrier_intents = carrier;
    in.carrier_intent_count = 1u;
    in.frames = (const d_world_frame *)0;

    dg_struct_compiler_init(&c1);
    dg_struct_compiler_init(&c2);
    TEST_ASSERT(dg_struct_compiler_reserve(&c1, 64u, 1024u) == 0);
    TEST_ASSERT(dg_struct_compiler_reserve(&c2, 64u, 1024u) == 0);
    TEST_ASSERT(dg_struct_compiler_set_params(&c1, q_int(16)) == 0);
    TEST_ASSERT(dg_struct_compiler_set_params(&c2, q_int(16)) == 0);
    TEST_ASSERT(dg_struct_compiler_sync(&c1, &in) == 0);
    TEST_ASSERT(dg_struct_compiler_sync(&c2, &in) == 0);

    dg_struct_dirty_mark(&c1.dirty, sid, DG_STRUCT_DIRTY_CARRIER);
    dg_struct_dirty_mark(&c2.dirty, sid, DG_STRUCT_DIRTY_CARRIER);
    TEST_ASSERT(dg_struct_compiler_enqueue_dirty(&c1, 1u) == 0);
    TEST_ASSERT(dg_struct_compiler_enqueue_dirty(&c2, 1u) == 0);
    compile_until_done(&c1, &in, 0xFFFFFFFFu);
    compile_until_done(&c2, &in, 0xFFFFFFFFu);
    TEST_ASSERT(dg_struct_compiler_check_invariants(&c1, &in) == 0);
    TEST_ASSERT(dg_struct_compiler_check_invariants(&c2, &in) == 0);

    h1 = hash_compiled(&c1);
    h2 = hash_compiled(&c2);
    TEST_ASSERT(h1 == h2);

    dg_struct_compiler_free(&c1);
    dg_struct_compiler_free(&c2);
    dg_struct_instance_free(&inst[0]);
    dg_struct_carrier_intent_free(&carrier[0]);
    return 0;
}

int main(void) {
    int rc;
    rc = test_struct_compilation_determinism();
    if (rc != 0) return rc;
    rc = test_struct_dirty_rebuild();
    if (rc != 0) return rc;
    rc = test_struct_carrier_determinism();
    if (rc != 0) return rc;
    return 0;
}

