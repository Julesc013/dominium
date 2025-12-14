#include <string.h>

#include "core/dg_det_hash.h"

#include "decor/model/dg_decor_rulepack.h"
#include "decor/model/dg_decor_override.h"

#include "decor/compile/dg_decor_compile.h"
#include "decor/compile/dg_decor_promote.h"

#define TEST_ASSERT(cond) do { if (!(cond)) return __LINE__; } while (0)

#define QONE ((dg_q)((i64)1 << 16))
static dg_q q_int(i64 v) { return (dg_q)(v * (i64)QONE); }

static u64 hash_step_u64(u64 h, u64 v) { return dg_det_hash_u64(h ^ v); }
static u64 hash_step_i64(u64 h, i64 v) { return dg_det_hash_u64(h ^ (u64)v); }
static u64 hash_step_u32(u64 h, u32 v) { return dg_det_hash_u64(h ^ (u64)v); }
static u64 hash_step_i32(u64 h, i32 v) { return dg_det_hash_u64(h ^ (u64)(u32)v); }

static u64 hash_pose(u64 h, const dg_pose *p) {
    if (!p) return h;
    h = hash_step_i64(h, (i64)p->pos.x);
    h = hash_step_i64(h, (i64)p->pos.y);
    h = hash_step_i64(h, (i64)p->pos.z);
    h = hash_step_i64(h, (i64)p->rot.x);
    h = hash_step_i64(h, (i64)p->rot.y);
    h = hash_step_i64(h, (i64)p->rot.z);
    h = hash_step_i64(h, (i64)p->rot.w);
    h = hash_step_i64(h, (i64)p->incline);
    h = hash_step_i64(h, (i64)p->roll);
    return h;
}

static u64 hash_anchor(u64 h, const dg_anchor *a) {
    if (!a) return h;
    h = hash_step_i32(h, (i32)a->kind);
    h = hash_step_u64(h, (u64)a->host_frame);
    switch (a->kind) {
    case DG_ANCHOR_TERRAIN:
        h = hash_step_i64(h, (i64)a->u.terrain.u);
        h = hash_step_i64(h, (i64)a->u.terrain.v);
        h = hash_step_i64(h, (i64)a->u.terrain.h);
        break;
    case DG_ANCHOR_CORRIDOR_TRANS:
        h = hash_step_u64(h, (u64)a->u.corridor.alignment_id);
        h = hash_step_i64(h, (i64)a->u.corridor.s);
        h = hash_step_i64(h, (i64)a->u.corridor.t);
        h = hash_step_i64(h, (i64)a->u.corridor.h);
        h = hash_step_i64(h, (i64)a->u.corridor.roll);
        break;
    case DG_ANCHOR_STRUCT_SURFACE:
        h = hash_step_u64(h, (u64)a->u.struct_surface.structure_id);
        h = hash_step_u64(h, (u64)a->u.struct_surface.surface_id);
        h = hash_step_i64(h, (i64)a->u.struct_surface.u);
        h = hash_step_i64(h, (i64)a->u.struct_surface.v);
        h = hash_step_i64(h, (i64)a->u.struct_surface.offset);
        break;
    case DG_ANCHOR_ROOM_SURFACE:
        h = hash_step_u64(h, (u64)a->u.room_surface.room_id);
        h = hash_step_u64(h, (u64)a->u.room_surface.surface_id);
        h = hash_step_i64(h, (i64)a->u.room_surface.u);
        h = hash_step_i64(h, (i64)a->u.room_surface.v);
        h = hash_step_i64(h, (i64)a->u.room_surface.offset);
        break;
    case DG_ANCHOR_SOCKET:
        h = hash_step_u64(h, (u64)a->u.socket.socket_id);
        h = hash_step_i64(h, (i64)a->u.socket.param);
        break;
    default:
        break;
    }
    return h;
}

static u64 hash_host_items(const dg_decor_compiler *c) {
    u64 h = 0xDEC0DEC0DEC0DEC0ULL;
    u32 hi;
    if (!c) return 0u;

    h = hash_step_u32(h, c->host_count);
    for (hi = 0u; hi < c->host_count; ++hi) {
        const dg_decor_compiled_host *host = &c->hosts[hi];
        u32 ii;
        h = hash_step_i32(h, (i32)host->desc.host.kind);
        h = hash_step_u64(h, (u64)host->desc.chunk_id);
        h = hash_step_u64(h, (u64)host->desc.host_frame);
        h = hash_step_i64(h, (i64)host->desc.primary0);
        h = hash_step_i64(h, (i64)host->desc.primary1);

        h = hash_step_u32(h, host->item_count);
        for (ii = 0u; ii < host->item_count; ++ii) {
            const dg_decor_item *it = &host->items[ii];
            h = hash_step_u64(h, (u64)it->decor_id);
            h = hash_step_u64(h, (u64)it->decor_type_id);
            h = hash_step_u32(h, it->flags);
            h = hash_anchor(h, &it->anchor);
            h = hash_pose(h, &it->local_offset);
        }
    }
    return h;
}

static u64 hash_compiled_chunks(const dg_decor_compiler *c) {
    u64 h = 0xA11CEDEC0D0C0A11ULL;
    u32 ci;
    if (!c) return 0u;

    h = hash_step_u32(h, c->chunk_count);
    for (ci = 0u; ci < c->chunk_count; ++ci) {
        const dg_decor_compiled_chunk *ch = &c->chunks[ci];
        const dg_decor_instances *ins = &ch->instances;
        const dg_decor_tiles *tiles = &ch->tiles;
        u32 i;

        h = hash_step_u64(h, (u64)ch->chunk_id);

        h = hash_step_u32(h, ins->count);
        for (i = 0u; i < ins->count; ++i) {
            const dg_decor_instance *inst = &ins->items[i];
            h = hash_step_u64(h, (u64)inst->decor_id);
            h = hash_step_u64(h, (u64)inst->decor_type_id);
            h = hash_step_u32(h, inst->flags);
            h = hash_pose(h, &inst->world_pose);
        }

        h = hash_step_u32(h, tiles->tile_count);
        h = hash_step_u32(h, tiles->index_count);
        for (i = 0u; i < tiles->tile_count; ++i) {
            const dg_decor_tile *t = &tiles->tiles[i];
            h = hash_step_u64(h, (u64)t->chunk_id);
            h = hash_step_u64(h, (u64)t->decor_type_id);
            h = hash_step_u32(h, t->index_offset);
            h = hash_step_u32(h, t->index_count);
        }
        for (i = 0u; i < tiles->index_count; ++i) {
            h = hash_step_u32(h, tiles->indices[i]);
        }
    }
    return h;
}

static void compile_until_done(dg_decor_compiler *c, dg_tick tick0, u32 budget_units) {
    dg_tick t = tick0;
    u32 guard = 0u;
    while (dg_decor_compiler_pending_work(c) != 0u) {
        (void)dg_decor_compiler_process(c, (const d_world_frame *)0, t, DG_ROUND_NEAR, budget_units);
        t += 1u;
        guard += 1u;
        if (guard > 1024u) break;
    }
}

static void build_host_trans(dg_decor_host_desc *out, dg_chunk_id chunk_id, u64 alignment_id, u32 segment_index, u64 slot_id, dg_q s0, dg_q s1) {
    dg_decor_host_desc h;
    memset(&h, 0, sizeof(h));
    dg_decor_host_clear(&h.host);
    h.host.kind = DG_DECOR_HOST_TRANS_SLOT_SURFACE;
    h.host.u.trans_slot_surface.alignment_id = alignment_id;
    h.host.u.trans_slot_surface.segment_index = segment_index;
    h.host.u.trans_slot_surface.slot_id = slot_id;
    h.chunk_id = chunk_id;
    h.host_frame = DG_FRAME_ID_WORLD;
    h.primary0 = s0;
    h.primary1 = s1;
    h.secondary0 = 0;
    h.secondary1 = 0;
    *out = h;
}

static void build_host_struct_surface(dg_decor_host_desc *out, dg_chunk_id chunk_id, u64 struct_id, u64 surface_id, dg_q u0, dg_q u1, dg_q v0, dg_q v1) {
    dg_decor_host_desc h;
    memset(&h, 0, sizeof(h));
    dg_decor_host_clear(&h.host);
    h.host.kind = DG_DECOR_HOST_STRUCT_SURFACE;
    h.host.u.struct_surface.struct_id = struct_id;
    h.host.u.struct_surface.surface_id = surface_id;
    h.chunk_id = chunk_id;
    h.host_frame = DG_FRAME_ID_WORLD;
    h.primary0 = u0;
    h.primary1 = u1;
    h.secondary0 = v0;
    h.secondary1 = v1;
    *out = h;
}

static void build_rulepack_for_host(dg_decor_rulepack *out, dg_decor_rulepack_id id, const dg_decor_host *host, dg_decor_type_id type_id, dg_q interval, u32 flags) {
    dg_decor_spawn_template st;
    dg_decor_rulepack_init(out);
    out->id = id;
    out->selector.host_kind = host->kind;
    out->selector.match_all_of_kind = D_FALSE;
    out->selector.exact = *host;
    out->interval_q = interval;
    out->start_q = 0;

    memset(&st, 0, sizeof(st));
    st.decor_type_id = type_id;
    st.flags = flags;
    st.local_offset = dg_pose_identity();
    st.params.ptr = (const unsigned char *)0;
    st.params.len = 0u;
    (void)dg_decor_rulepack_set_spawn(out, &st);
}

static void build_override_pin(dg_decor_override *out, dg_decor_override_id id, const dg_decor_host *host, dg_decor_id decor_id, dg_decor_type_id type_id, dg_q s) {
    dg_decor_override o;
    dg_decor_item_clear(&o.u.pin.item);
    dg_decor_override_clear(&o);
    o.id = id;
    o.op = DG_DECOR_OVERRIDE_PIN;
    o.u.pin.item.decor_id = decor_id;
    o.u.pin.item.decor_type_id = type_id;
    o.u.pin.item.flags = DG_DECOR_ITEM_F_PROMOTABLE;
    o.u.pin.item.host = *host;
    dg_anchor_clear(&o.u.pin.item.anchor);
    o.u.pin.item.anchor.kind = DG_ANCHOR_CORRIDOR_TRANS;
    o.u.pin.item.anchor.host_frame = DG_FRAME_ID_WORLD;
    o.u.pin.item.anchor.u.corridor.alignment_id = host->u.trans_slot_surface.alignment_id;
    o.u.pin.item.anchor.u.corridor.s = s;
    o.u.pin.item.anchor.u.corridor.t = 0;
    o.u.pin.item.anchor.u.corridor.h = 0;
    o.u.pin.item.anchor.u.corridor.roll = 0;
    o.u.pin.item.local_offset = dg_pose_identity();
    o.u.pin.item.params.ptr = (const unsigned char *)0;
    o.u.pin.item.params.len = 0u;
    *out = o;
}

static void build_override_move(dg_decor_override *out, dg_decor_override_id id, dg_decor_id target, dg_q new_s) {
    dg_decor_override o;
    dg_decor_override_clear(&o);
    o.id = id;
    o.op = DG_DECOR_OVERRIDE_MOVE;
    o.u.move.target_decor_id = target;
    o.u.move.has_anchor = D_TRUE;
    o.u.move.has_local_offset = D_FALSE;
    dg_anchor_clear(&o.u.move.new_anchor);
    o.u.move.new_anchor.kind = DG_ANCHOR_CORRIDOR_TRANS;
    o.u.move.new_anchor.host_frame = DG_FRAME_ID_WORLD;
    o.u.move.new_anchor.u.corridor.alignment_id = 10u;
    o.u.move.new_anchor.u.corridor.s = new_s;
    o.u.move.new_anchor.u.corridor.t = 0;
    o.u.move.new_anchor.u.corridor.h = 0;
    o.u.move.new_anchor.u.corridor.roll = 0;
    o.u.move.new_local_offset = dg_pose_identity();
    *out = o;
}

static void build_override_replace(dg_decor_override *out, dg_decor_override_id id, dg_decor_id target, dg_decor_type_id new_type) {
    dg_decor_override o;
    dg_decor_override_clear(&o);
    o.id = id;
    o.op = DG_DECOR_OVERRIDE_REPLACE;
    o.u.replace.target_decor_id = target;
    o.u.replace.new_decor_type_id = new_type;
    o.u.replace.new_params.ptr = (const unsigned char *)0;
    o.u.replace.new_params.len = 0u;
    o.u.replace.new_flags_mask = 0u;
    o.u.replace.new_flags_value = 0u;
    *out = o;
}

static void build_override_suppress(dg_decor_override *out, dg_decor_override_id id, const dg_decor_host *host, dg_q s0, dg_q s1) {
    dg_decor_override o;
    dg_decor_override_clear(&o);
    o.id = id;
    o.op = DG_DECOR_OVERRIDE_SUPPRESS;
    o.u.suppress.region.host = *host;
    o.u.suppress.region.s0 = s0;
    o.u.suppress.region.s1 = s1;
    *out = o;
}

static u32 count_dirty_hosts(const dg_decor_dirty *d) {
    u32 i;
    u32 n = 0u;
    for (i = 0u; i < d->host_count; ++i) {
        if (d->hosts[i].dirty) n += 1u;
    }
    return n;
}

static u32 count_dirty_chunks(const dg_decor_dirty *d) {
    u32 i;
    u32 n = 0u;
    for (i = 0u; i < d->chunk_count; ++i) {
        if (d->chunks[i].dirty) n += 1u;
    }
    return n;
}

static int test_baseline_determinism(void) {
    dg_decor_host_desc hosts1[2];
    dg_decor_host_desc hosts2[2];
    dg_decor_rulepack rps1[2];
    dg_decor_rulepack rps2[2];
    dg_decor_compile_input in1;
    dg_decor_compile_input in2;
    dg_decor_compiler c1;
    dg_decor_compiler c2;
    u64 h_items1;
    u64 h_items2;

    build_host_trans(&hosts1[0], 1u, 10u, 0u, 5u, q_int(0), q_int(10));
    build_host_struct_surface(&hosts1[1], 2u, 20u, 2u, q_int(0), q_int(8), q_int(0), q_int(2));

    /* Reordered insertion. */
    hosts2[0] = hosts1[1];
    hosts2[1] = hosts1[0];

    build_rulepack_for_host(&rps1[0], 100u, &hosts1[0].host, 1000u, q_int(2), 0u);
    build_rulepack_for_host(&rps1[1], 200u, &hosts1[1].host, 2000u, q_int(3), 0u);

    /* Same rulepacks, different insertion order (separate storage). */
    build_rulepack_for_host(&rps2[0], 200u, &hosts1[1].host, 2000u, q_int(3), 0u);
    build_rulepack_for_host(&rps2[1], 100u, &hosts1[0].host, 1000u, q_int(2), 0u);

    memset(&in1, 0, sizeof(in1));
    in1.global_seed = 12345u;
    in1.hosts = hosts1;
    in1.host_count = 2u;
    in1.rulepacks = rps1;
    in1.rulepack_count = 2u;
    in1.overrides = (const dg_decor_override *)0;
    in1.override_count = 0u;

    memset(&in2, 0, sizeof(in2));
    in2.global_seed = 12345u;
    in2.hosts = hosts2;
    in2.host_count = 2u;
    in2.rulepacks = rps2;
    in2.rulepack_count = 2u;
    in2.overrides = (const dg_decor_override *)0;
    in2.override_count = 0u;

    dg_decor_compiler_init(&c1);
    dg_decor_compiler_init(&c2);
    TEST_ASSERT(dg_decor_compiler_reserve(&c1, 64u) == 0);
    TEST_ASSERT(dg_decor_compiler_reserve(&c2, 64u) == 0);

    TEST_ASSERT(dg_decor_compiler_sync(&c1, &in1) == 0);
    TEST_ASSERT(dg_decor_compiler_sync(&c2, &in2) == 0);
    TEST_ASSERT(dg_decor_compiler_enqueue_dirty(&c1, 1u) == 0);
    TEST_ASSERT(dg_decor_compiler_enqueue_dirty(&c2, 1u) == 0);

    compile_until_done(&c1, 1u, 0xFFFFFFFFu);
    compile_until_done(&c2, 1u, 0xFFFFFFFFu);

    h_items1 = hash_host_items(&c1);
    h_items2 = hash_host_items(&c2);
    TEST_ASSERT(h_items1 == h_items2);

    dg_decor_compiler_free(&c1);
    dg_decor_compiler_free(&c2);
    dg_decor_rulepack_free(&rps1[0]);
    dg_decor_rulepack_free(&rps1[1]);
    dg_decor_rulepack_free(&rps2[0]);
    dg_decor_rulepack_free(&rps2[1]);
    return 0;
}

static int test_override_determinism(void) {
    dg_decor_host_desc hosts[1];
    dg_decor_rulepack rps[1];
    dg_decor_override ov1[4];
    dg_decor_override ov2[4];
    dg_decor_compile_input in1;
    dg_decor_compile_input in2;
    dg_decor_compiler c1;
    dg_decor_compiler c2;
    u64 h1;
    u64 h2;
    const dg_decor_id pinned_id = 42u;

    build_host_trans(&hosts[0], 1u, 10u, 0u, 5u, q_int(0), q_int(10));
    build_rulepack_for_host(&rps[0], 100u, &hosts[0].host, 1000u, q_int(2), 0u);

    build_override_suppress(&ov1[0], 10u, &hosts[0].host, q_int(0), q_int(4));
    build_override_replace(&ov1[1], 12u, pinned_id, 9001u);
    build_override_move(&ov1[2], 15u, pinned_id, q_int(7));
    build_override_pin(&ov1[3], 20u, &hosts[0].host, pinned_id, 9000u, q_int(3));

    /* Reordered insertion. */
    ov2[0] = ov1[3];
    ov2[1] = ov1[1];
    ov2[2] = ov1[0];
    ov2[3] = ov1[2];

    memset(&in1, 0, sizeof(in1));
    in1.global_seed = 12345u;
    in1.hosts = hosts;
    in1.host_count = 1u;
    in1.rulepacks = rps;
    in1.rulepack_count = 1u;
    in1.overrides = ov1;
    in1.override_count = 4u;

    memset(&in2, 0, sizeof(in2));
    in2.global_seed = 12345u;
    in2.hosts = hosts;
    in2.host_count = 1u;
    in2.rulepacks = rps;
    in2.rulepack_count = 1u;
    in2.overrides = ov2;
    in2.override_count = 4u;

    dg_decor_compiler_init(&c1);
    dg_decor_compiler_init(&c2);
    TEST_ASSERT(dg_decor_compiler_reserve(&c1, 64u) == 0);
    TEST_ASSERT(dg_decor_compiler_reserve(&c2, 64u) == 0);

    TEST_ASSERT(dg_decor_compiler_sync(&c1, &in1) == 0);
    TEST_ASSERT(dg_decor_compiler_sync(&c2, &in2) == 0);
    TEST_ASSERT(dg_decor_compiler_enqueue_dirty(&c1, 1u) == 0);
    TEST_ASSERT(dg_decor_compiler_enqueue_dirty(&c2, 1u) == 0);

    compile_until_done(&c1, 1u, 0xFFFFFFFFu);
    compile_until_done(&c2, 1u, 0xFFFFFFFFu);

    h1 = hash_host_items(&c1);
    h2 = hash_host_items(&c2);
    TEST_ASSERT(h1 == h2);

    dg_decor_compiler_free(&c1);
    dg_decor_compiler_free(&c2);
    dg_decor_rulepack_free(&rps[0]);
    return 0;
}

static int test_dirty_rebuild_budgeted(void) {
    dg_decor_host_desc hosts[2];
    dg_decor_rulepack rps[2];
    dg_decor_compile_input in;
    dg_decor_compile_input in_mod;
    dg_decor_compiler partial;
    dg_decor_compiler full;
    u32 dirty_hosts;
    u32 dirty_chunks;
    u64 h_partial;
    u64 h_full;

    build_host_trans(&hosts[0], 1u, 10u, 0u, 5u, q_int(0), q_int(10));
    build_host_struct_surface(&hosts[1], 2u, 20u, 2u, q_int(0), q_int(8), q_int(0), q_int(2));

    build_rulepack_for_host(&rps[0], 100u, &hosts[0].host, 1000u, q_int(2), 0u);
    build_rulepack_for_host(&rps[1], 200u, &hosts[1].host, 2000u, q_int(3), 0u);

    memset(&in, 0, sizeof(in));
    in.global_seed = 12345u;
    in.hosts = hosts;
    in.host_count = 2u;
    in.rulepacks = rps;
    in.rulepack_count = 2u;
    in.overrides = (const dg_decor_override *)0;
    in.override_count = 0u;

    dg_decor_compiler_init(&partial);
    TEST_ASSERT(dg_decor_compiler_reserve(&partial, 64u) == 0);
    TEST_ASSERT(dg_decor_compiler_sync(&partial, &in) == 0);
    TEST_ASSERT(dg_decor_compiler_enqueue_dirty(&partial, 1u) == 0);
    compile_until_done(&partial, 1u, 0xFFFFFFFFu);

    /* Modify rulepack affecting only hosts[0]. */
    rps[0].interval_q = q_int(3);

    in_mod = in;
    TEST_ASSERT(dg_decor_compiler_sync(&partial, &in_mod) == 0);

    dirty_hosts = count_dirty_hosts(&partial.dirty);
    dirty_chunks = count_dirty_chunks(&partial.dirty);
    TEST_ASSERT(dirty_hosts == 1u);
    TEST_ASSERT(dirty_chunks == 1u);

    TEST_ASSERT(dg_decor_compiler_enqueue_dirty(&partial, 2u) == 0);
    /* Budgeted resume: 1 work item per tick. */
    compile_until_done(&partial, 2u, 1u);
    h_partial = hash_compiled_chunks(&partial);

    /* Full rebuild from scratch must match. */
    dg_decor_compiler_init(&full);
    TEST_ASSERT(dg_decor_compiler_reserve(&full, 64u) == 0);
    TEST_ASSERT(dg_decor_compiler_sync(&full, &in_mod) == 0);
    TEST_ASSERT(dg_decor_compiler_enqueue_dirty(&full, 1u) == 0);
    compile_until_done(&full, 1u, 0xFFFFFFFFu);
    h_full = hash_compiled_chunks(&full);
    TEST_ASSERT(h_partial == h_full);

    dg_decor_compiler_free(&partial);
    dg_decor_compiler_free(&full);
    dg_decor_rulepack_free(&rps[0]);
    dg_decor_rulepack_free(&rps[1]);
    return 0;
}

static int test_promotion_hook_stability(void) {
    dg_decor_host_desc hosts1[1];
    dg_decor_host_desc hosts2[1];
    dg_decor_rulepack rps1[1];
    dg_decor_rulepack rps2[1];
    dg_decor_compile_input in1;
    dg_decor_compile_input in2;
    dg_decor_compiler c1;
    dg_decor_compiler c2;
    const dg_decor_compiled_chunk *ch1;
    const dg_decor_compiled_chunk *ch2;
    dg_decor_promotion_list p1;
    dg_decor_promotion_list p2;
    u64 hk1;
    u64 hk2;
    u32 i;

    build_host_trans(&hosts1[0], 1u, 10u, 0u, 5u, q_int(0), q_int(10));
    hosts2[0] = hosts1[0];

    build_rulepack_for_host(&rps1[0], 100u, &hosts1[0].host, 1000u, q_int(2), DG_DECOR_ITEM_F_PROMOTABLE);
    build_rulepack_for_host(&rps2[0], 100u, &hosts2[0].host, 1000u, q_int(2), DG_DECOR_ITEM_F_PROMOTABLE);

    memset(&in1, 0, sizeof(in1));
    in1.global_seed = 777u;
    in1.hosts = hosts1;
    in1.host_count = 1u;
    in1.rulepacks = rps1;
    in1.rulepack_count = 1u;
    in1.overrides = (const dg_decor_override *)0;
    in1.override_count = 0u;

    memset(&in2, 0, sizeof(in2));
    in2.global_seed = 777u;
    in2.hosts = hosts2;
    in2.host_count = 1u;
    in2.rulepacks = rps2;
    in2.rulepack_count = 1u;
    in2.overrides = (const dg_decor_override *)0;
    in2.override_count = 0u;

    dg_decor_compiler_init(&c1);
    dg_decor_compiler_init(&c2);
    TEST_ASSERT(dg_decor_compiler_reserve(&c1, 64u) == 0);
    TEST_ASSERT(dg_decor_compiler_reserve(&c2, 64u) == 0);
    TEST_ASSERT(dg_decor_compiler_sync(&c1, &in1) == 0);
    TEST_ASSERT(dg_decor_compiler_sync(&c2, &in2) == 0);
    TEST_ASSERT(dg_decor_compiler_enqueue_dirty(&c1, 1u) == 0);
    TEST_ASSERT(dg_decor_compiler_enqueue_dirty(&c2, 1u) == 0);
    compile_until_done(&c1, 1u, 0xFFFFFFFFu);
    compile_until_done(&c2, 1u, 0xFFFFFFFFu);

    ch1 = dg_decor_compiler_find_chunk(&c1, 1u);
    ch2 = dg_decor_compiler_find_chunk(&c2, 1u);
    TEST_ASSERT(ch1 != (const dg_decor_compiled_chunk *)0);
    TEST_ASSERT(ch2 != (const dg_decor_compiled_chunk *)0);

    dg_decor_promotion_list_init(&p1);
    dg_decor_promotion_list_init(&p2);
    TEST_ASSERT(dg_decor_promote_collect(&p1, &ch1->instances, 1u, 0u) == 0);
    TEST_ASSERT(dg_decor_promote_collect(&p2, &ch2->instances, 1u, 0u) == 0);

    TEST_ASSERT(p1.count == p2.count);
    hk1 = 0xA5A5A5A5A5A5A5A5ULL;
    hk2 = 0xA5A5A5A5A5A5A5A5ULL;
    for (i = 0u; i < p1.count; ++i) {
        hk1 = hash_step_u64(hk1, (u64)p1.items[i].key.chunk_id);
        hk1 = hash_step_u64(hk1, (u64)p1.items[i].key.entity_id);
        hk2 = hash_step_u64(hk2, (u64)p2.items[i].key.chunk_id);
        hk2 = hash_step_u64(hk2, (u64)p2.items[i].key.entity_id);
        if (i > 0u) {
            TEST_ASSERT(dg_order_key_cmp(&p1.items[i - 1u].key, &p1.items[i].key) <= 0);
        }
    }
    TEST_ASSERT(hk1 == hk2);

    dg_decor_promotion_list_free(&p1);
    dg_decor_promotion_list_free(&p2);
    dg_decor_compiler_free(&c1);
    dg_decor_compiler_free(&c2);
    dg_decor_rulepack_free(&rps1[0]);
    dg_decor_rulepack_free(&rps2[0]);
    return 0;
}

int main(void) {
    int rc;
    rc = test_baseline_determinism();
    if (rc != 0) return rc;
    rc = test_override_determinism();
    if (rc != 0) return rc;
    rc = test_dirty_rebuild_budgeted();
    if (rc != 0) return rc;
    rc = test_promotion_hook_stability();
    if (rc != 0) return rc;
    return 0;
}
