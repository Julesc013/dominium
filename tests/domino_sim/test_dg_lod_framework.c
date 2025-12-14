#include <string.h>

#include "sim/lod/dg_rep.h"
#include "sim/lod/dg_lod_index.h"
#include "sim/lod/dg_interest.h"
#include "sim/lod/dg_promo.h"
#include "sim/lod/dg_stride.h"
#include "sim/lod/dg_accum.h"

#include "core/dg_det_hash.h"

#define TEST_ASSERT(cond) do { if (!(cond)) return __LINE__; } while (0)

typedef struct test_world test_world;

typedef struct test_rep_obj {
    dg_representable rep;
    dg_rep_state     state;
    dg_lod_obj_key   key;
    dg_lod_obj_pos   pos;
    dg_lod_class_id  class_id;
    test_world      *world;
} test_rep_obj;

struct test_world {
    test_rep_obj objs[16];
    u32          obj_count;

    dg_lod_obj_key applied_log[64];
    u32            applied_count;
};

static int test_key_eq(const dg_lod_obj_key *a, const dg_lod_obj_key *b) {
    if (!a || !b) return 0;
    return (a->domain_id == b->domain_id &&
            a->chunk_id == b->chunk_id &&
            a->entity_id == b->entity_id &&
            a->sub_id == b->sub_id) ? 1 : 0;
}

static void test_log_push(test_world *w, const dg_lod_obj_key *k) {
    if (!w || !k) return;
    if (w->applied_count >= (u32)(sizeof(w->applied_log) / sizeof(w->applied_log[0]))) return;
    w->applied_log[w->applied_count++] = *k;
}

static dg_rep_state test_get_rep_state(const dg_representable *self) {
    const test_rep_obj *o;
    if (!self) return DG_REP_R3_DORMANT;
    o = (const test_rep_obj *)self->user;
    if (!o) return DG_REP_R3_DORMANT;
    return o->state;
}

static int test_set_rep_state(dg_representable *self, dg_rep_state new_state) {
    test_rep_obj *o;
    if (!self) return -1;
    o = (test_rep_obj *)self->user;
    if (!o) return -2;
    if (o->state != new_state) {
        o->state = new_state;
        test_log_push(o->world, &o->key);
    }
    return 0;
}

static void test_step_rep(dg_representable *self, dg_phase phase, u32 *budget_units) {
    (void)self;
    (void)phase;
    (void)budget_units;
}

static u32 test_serialize_rep_state(const dg_representable *self, unsigned char *out, u32 out_cap) {
    const test_rep_obj *o;
    if (!self || !out || out_cap < 1u) return 0u;
    o = (const test_rep_obj *)self->user;
    if (!o) return 0u;
    out[0] = (unsigned char)o->state;
    return 1u;
}

static int test_rep_invariants_check(const dg_representable *self) {
    (void)self;
    return 0;
}

static const dg_representable_vtbl TEST_REP_VTBL = {
    test_get_rep_state,
    test_set_rep_state,
    test_step_rep,
    test_serialize_rep_state,
    test_rep_invariants_check
};

static void test_world_init(test_world *w) {
    if (!w) return;
    memset(w, 0, sizeof(*w));
}

static void test_world_add_obj(
    test_world *w,
    dg_domain_id domain_id,
    dg_chunk_id chunk_id,
    dg_entity_id entity_id,
    u64 sub_id,
    dg_lod_obj_pos pos,
    dg_lod_class_id class_id,
    dg_rep_state initial_state
) {
    test_rep_obj *o;
    if (!w) return;
    if (w->obj_count >= (u32)(sizeof(w->objs) / sizeof(w->objs[0]))) return;
    o = &w->objs[w->obj_count++];
    memset(o, 0, sizeof(*o));
    o->world = w;
    o->state = initial_state;
    o->key.domain_id = domain_id;
    o->key.chunk_id = chunk_id;
    o->key.entity_id = entity_id;
    o->key.sub_id = sub_id;
    o->pos = pos;
    o->class_id = class_id;
    dg_representable_init(&o->rep, &TEST_REP_VTBL, o);
}

static dg_representable *test_resolve(void *user_ctx, const dg_lod_obj_key *key, dg_lod_class_id class_id) {
    test_world *w = (test_world *)user_ctx;
    u32 i;
    if (!w || !key) return (dg_representable *)0;
    for (i = 0u; i < w->obj_count; ++i) {
        if (w->objs[i].class_id != class_id) continue;
        if (!test_key_eq(&w->objs[i].key, key)) continue;
        return &w->objs[i].rep;
    }
    return (dg_representable *)0;
}

static void test_interest_source(dg_tick tick, dg_interest_list *out_list, void *user_ctx) {
    dg_interest_volume v;
    (void)tick;
    (void)user_ctx;

    memset(&v, 0, sizeof(v));
    v.type = DG_IV_HAZARD;
    v.shape = DG_IV_SHAPE_SPHERE;
    v.center.x = 0;
    v.center.y = 0;
    v.center.z = 0;
    v.radius = (q16_16)(8 << Q16_16_FRAC_BITS);
    v.weight = 0; /* default weight (2.0) */
    (void)dg_interest_list_push(out_list, &v);

    memset(&v, 0, sizeof(v));
    v.type = DG_IV_PLAYER;
    v.shape = DG_IV_SHAPE_SPHERE;
    v.center.x = (q16_16)(100 << Q16_16_FRAC_BITS);
    v.center.y = 0;
    v.center.z = 0;
    v.radius = (q16_16)(16 << Q16_16_FRAC_BITS);
    v.weight = 0; /* default weight (1.0) */
    (void)dg_interest_list_push(out_list, &v);
}

static int test_transition_eq(const dg_promo_transition *a, const dg_promo_transition *b) {
    if (!a || !b) return 0;
    if (!test_key_eq(&a->key, &b->key)) return 0;
    if (a->class_id != b->class_id) return 0;
    if (a->from_state != b->from_state) return 0;
    if (a->to_state != b->to_state) return 0;
    if (a->score != b->score) return 0;
    if (a->cost_units != b->cost_units) return 0;
    return 1;
}

static int test_promo_stability(void) {
    const dg_lod_class_id CLASS_ENTITY = 1u;
    test_world w1, w2;
    dg_lod_index idx1, idx2;
    dg_interest_ctx interest;
    dg_promo_ctx p1, p2;
    int rc;
    u32 i;

    test_world_init(&w1);
    test_world_init(&w2);

    /* Objects: desired ordering should be A, G, B, E, F, C (see below). */
    {
        dg_lod_obj_pos p_hazard; memset(&p_hazard, 0, sizeof(p_hazard));
        dg_lod_obj_pos p_player; memset(&p_player, 0, sizeof(p_player));
        dg_lod_obj_pos p_player_half; memset(&p_player_half, 0, sizeof(p_player_half));
        p_hazard.x = 0; p_hazard.y = 0; p_hazard.z = 0;
        p_player.x = (q16_16)(100 << Q16_16_FRAC_BITS); p_player.y = 0; p_player.z = 0;
        p_player_half.x = (q16_16)(112 << Q16_16_FRAC_BITS); p_player_half.y = 0; p_player_half.z = 0;

        /* A: hazard => score 2.0 => desired R0 */
        test_world_add_obj(&w1, 1u, 10u, 1u, 1u, p_hazard, CLASS_ENTITY, DG_REP_R3_DORMANT);
        test_world_add_obj(&w2, 1u, 10u, 1u, 1u, p_hazard, CLASS_ENTITY, DG_REP_R3_DORMANT);

        /* G: hazard => score 2.0 => desired R0 */
        test_world_add_obj(&w1, 2u, 1u, 5u, 1u, p_hazard, CLASS_ENTITY, DG_REP_R3_DORMANT);
        test_world_add_obj(&w2, 2u, 1u, 5u, 1u, p_hazard, CLASS_ENTITY, DG_REP_R3_DORMANT);

        /* B,E,F: player center => score 1.0 => desired R1 */
        test_world_add_obj(&w1, 1u, 10u, 2u, 1u, p_player, CLASS_ENTITY, DG_REP_R3_DORMANT);
        test_world_add_obj(&w2, 1u, 10u, 2u, 1u, p_player, CLASS_ENTITY, DG_REP_R3_DORMANT);

        test_world_add_obj(&w1, 1u, 10u, 4u, 1u, p_player, CLASS_ENTITY, DG_REP_R3_DORMANT);
        test_world_add_obj(&w2, 1u, 10u, 4u, 1u, p_player, CLASS_ENTITY, DG_REP_R3_DORMANT);

        test_world_add_obj(&w1, 2u, 5u, 1u, 1u, p_player, CLASS_ENTITY, DG_REP_R3_DORMANT);
        test_world_add_obj(&w2, 2u, 5u, 1u, 1u, p_player, CLASS_ENTITY, DG_REP_R3_DORMANT);

        /* C: player half => score 0.5 => desired R2 */
        test_world_add_obj(&w1, 1u, 20u, 3u, 1u, p_player_half, CLASS_ENTITY, DG_REP_R3_DORMANT);
        test_world_add_obj(&w2, 1u, 20u, 3u, 1u, p_player_half, CLASS_ENTITY, DG_REP_R3_DORMANT);
    }

    dg_lod_index_init(&idx1);
    dg_lod_index_init(&idx2);
    TEST_ASSERT(dg_lod_index_reserve(&idx1, 64u) == 0);
    TEST_ASSERT(dg_lod_index_reserve(&idx2, 64u) == 0);

    /* Insert candidates in different orders. */
    {
        u32 order_a[] = { 5u, 4u, 3u, 2u, 1u, 0u };
        u32 order_b[] = { 0u, 1u, 2u, 3u, 4u, 5u };
        u32 k;
        for (k = 0u; k < 6u; ++k) {
            test_rep_obj *o = &w1.objs[order_a[k]];
            TEST_ASSERT(dg_lod_index_add(&idx1, o->key.chunk_id, &o->key, &o->pos, o->class_id) >= 0);
        }
        for (k = 0u; k < 6u; ++k) {
            test_rep_obj *o = &w2.objs[order_b[k]];
            TEST_ASSERT(dg_lod_index_add(&idx2, o->key.chunk_id, &o->key, &o->pos, o->class_id) >= 0);
        }
    }

    dg_interest_init(&interest);
    TEST_ASSERT(dg_interest_reserve(&interest, 4u) == 0);
    TEST_ASSERT(dg_interest_register_source(&interest, test_interest_source, 0u, (void *)0) == 0);

    dg_promo_init(&p1);
    dg_promo_init(&p2);
    rc = dg_promo_reserve(&p1, 16u, 64u, 64u, 16u);
    TEST_ASSERT(rc == 0);
    rc = dg_promo_reserve(&p2, 16u, 64u, 64u, 16u);
    TEST_ASSERT(rc == 0);
    dg_promo_set_index(&p1, &idx1);
    dg_promo_set_index(&p2, &idx2);
    dg_promo_set_interest(&p1, &interest);
    dg_promo_set_interest(&p2, &interest);
    dg_promo_set_resolver(&p1, test_resolve, &w1);
    dg_promo_set_resolver(&p2, test_resolve, &w2);

    TEST_ASSERT(dg_promo_plan_and_enqueue(&p1, 1u) == 0);
    TEST_ASSERT(dg_promo_plan_and_enqueue(&p2, 1u) == 0);
    TEST_ASSERT(dg_promo_queue_count(&p1) == dg_promo_queue_count(&p2));

    for (i = 0u; i < dg_promo_queue_count(&p1); ++i) {
        const dg_promo_transition *a = dg_promo_queue_at(&p1, i);
        const dg_promo_transition *b = dg_promo_queue_at(&p2, i);
        TEST_ASSERT(test_transition_eq(a, b));
    }

    /* Expected deterministic order by (desired rep, score desc, stable key). */
    {
        const dg_promo_transition *t0 = dg_promo_queue_at(&p1, 0u);
        const dg_promo_transition *t1 = dg_promo_queue_at(&p1, 1u);
        const dg_promo_transition *t2 = dg_promo_queue_at(&p1, 2u);
        const dg_promo_transition *t3 = dg_promo_queue_at(&p1, 3u);
        const dg_promo_transition *t4 = dg_promo_queue_at(&p1, 4u);
        const dg_promo_transition *t5 = dg_promo_queue_at(&p1, 5u);
        TEST_ASSERT(dg_promo_queue_count(&p1) == 6u);
        TEST_ASSERT(t0 && t1 && t2 && t3 && t4 && t5);
        TEST_ASSERT(t0->to_state == DG_REP_R0_FULL);
        TEST_ASSERT(t1->to_state == DG_REP_R0_FULL);
        TEST_ASSERT(t2->to_state == DG_REP_R1_LITE);
        TEST_ASSERT(t3->to_state == DG_REP_R1_LITE);
        TEST_ASSERT(t4->to_state == DG_REP_R1_LITE);
        TEST_ASSERT(t5->to_state == DG_REP_R2_AGG);
        /* R0 group stable-key order: domain 1 before domain 2 */
        TEST_ASSERT(t0->key.domain_id == 1u);
        TEST_ASSERT(t1->key.domain_id == 2u);
        /* Within domain 1/R1: entity 2 before entity 4 */
        TEST_ASSERT(t2->key.domain_id == 1u && t2->key.entity_id == 2u);
        TEST_ASSERT(t3->key.domain_id == 1u && t3->key.entity_id == 4u);
        /* Domain 2/R1 last in that group */
        TEST_ASSERT(t4->key.domain_id == 2u);
        /* R2 candidate */
        TEST_ASSERT(t5->key.domain_id == 1u && t5->key.entity_id == 3u);
    }

    dg_promo_free(&p1);
    dg_promo_free(&p2);
    dg_interest_free(&interest);
    dg_lod_index_free(&idx1);
    dg_lod_index_free(&idx2);
    return 0;
}

static int test_budget_deferral(void) {
    const dg_lod_class_id CLASS_ENTITY = 1u;
    test_world w;
    dg_lod_index idx;
    dg_interest_ctx interest;
    dg_promo_ctx promo;
    dg_budget budget;
    int rc;
    u32 applied;

    test_world_init(&w);

    {
        dg_lod_obj_pos p_hazard; memset(&p_hazard, 0, sizeof(p_hazard));
        dg_lod_obj_pos p_player; memset(&p_player, 0, sizeof(p_player));
        dg_lod_obj_pos p_player_half; memset(&p_player_half, 0, sizeof(p_player_half));
        p_hazard.x = 0; p_hazard.y = 0; p_hazard.z = 0;
        p_player.x = (q16_16)(100 << Q16_16_FRAC_BITS); p_player.y = 0; p_player.z = 0;
        p_player_half.x = (q16_16)(112 << Q16_16_FRAC_BITS); p_player_half.y = 0; p_player_half.z = 0;

        /* Same 6 objects as promo stability test. */
        test_world_add_obj(&w, 1u, 10u, 1u, 1u, p_hazard, CLASS_ENTITY, DG_REP_R3_DORMANT);
        test_world_add_obj(&w, 2u, 1u, 5u, 1u, p_hazard, CLASS_ENTITY, DG_REP_R3_DORMANT);
        test_world_add_obj(&w, 1u, 10u, 2u, 1u, p_player, CLASS_ENTITY, DG_REP_R3_DORMANT);
        test_world_add_obj(&w, 1u, 10u, 4u, 1u, p_player, CLASS_ENTITY, DG_REP_R3_DORMANT);
        test_world_add_obj(&w, 2u, 5u, 1u, 1u, p_player, CLASS_ENTITY, DG_REP_R3_DORMANT);
        test_world_add_obj(&w, 1u, 20u, 3u, 1u, p_player_half, CLASS_ENTITY, DG_REP_R3_DORMANT);
    }

    dg_lod_index_init(&idx);
    TEST_ASSERT(dg_lod_index_reserve(&idx, 64u) == 0);
    {
        u32 i;
        for (i = 0u; i < w.obj_count; ++i) {
            test_rep_obj *o = &w.objs[i];
            TEST_ASSERT(dg_lod_index_add(&idx, o->key.chunk_id, &o->key, &o->pos, o->class_id) >= 0);
        }
    }

    dg_interest_init(&interest);
    TEST_ASSERT(dg_interest_reserve(&interest, 4u) == 0);
    TEST_ASSERT(dg_interest_register_source(&interest, test_interest_source, 0u, (void *)0) == 0);

    dg_promo_init(&promo);
    rc = dg_promo_reserve(&promo, 16u, 64u, 64u, 16u);
    TEST_ASSERT(rc == 0);
    dg_promo_set_index(&promo, &idx);
    dg_promo_set_interest(&promo, &interest);
    dg_promo_set_resolver(&promo, test_resolve, &w);

    TEST_ASSERT(dg_promo_plan_and_enqueue(&promo, 1u) == 0);
    TEST_ASSERT(dg_promo_queue_count(&promo) == 6u);

    dg_budget_init(&budget);
    TEST_ASSERT(dg_budget_reserve(&budget, 32u, 32u) == 0);

    /* Tick 1: allow only 2 cost units globally => only 2 transitions apply. */
    dg_budget_set_limits(&budget, 2u, DG_BUDGET_UNLIMITED, DG_BUDGET_UNLIMITED);
    dg_budget_begin_tick(&budget, 1u);
    applied = dg_promo_apply_transitions_under_budget(&promo, &budget);
    TEST_ASSERT(applied == 2u);
    TEST_ASSERT(dg_promo_queue_pending(&promo) == 4u);

    /* First two transitions are the R0 promotions. */
    TEST_ASSERT(w.objs[0].state == DG_REP_R0_FULL);
    TEST_ASSERT(w.objs[1].state == DG_REP_R0_FULL);
    TEST_ASSERT(w.objs[2].state == DG_REP_R3_DORMANT);

    /* Tick 2: unlimited budget => remaining transitions apply in the same order. */
    dg_budget_set_limits(&budget, DG_BUDGET_UNLIMITED, DG_BUDGET_UNLIMITED, DG_BUDGET_UNLIMITED);
    dg_budget_begin_tick(&budget, 2u);
    applied = dg_promo_apply_transitions_under_budget(&promo, &budget);
    TEST_ASSERT(applied == 4u);
    TEST_ASSERT(dg_promo_queue_pending(&promo) == 0u);

    /* Verify final desired states reached. */
    TEST_ASSERT(w.objs[2].state == DG_REP_R1_LITE);
    TEST_ASSERT(w.objs[3].state == DG_REP_R1_LITE);
    TEST_ASSERT(w.objs[4].state == DG_REP_R1_LITE);
    TEST_ASSERT(w.objs[5].state == DG_REP_R2_AGG);

    /* Verify application order matches planned order. */
    TEST_ASSERT(w.applied_count == 6u);
    {
        const dg_promo_transition *t;
        u32 i;
        for (i = 0u; i < 6u; ++i) {
            t = dg_promo_queue_at(&promo, i);
            /* queue is cleared when drained; use scratch order from known expected sequence via log. */
            (void)t;
        }
    }
    /* Expected order: (1,10,1), (2,1,5), (1,10,2), (1,10,4), (2,5,1), (1,20,3) */
    TEST_ASSERT(w.applied_log[0].domain_id == 1u && w.applied_log[0].chunk_id == 10u && w.applied_log[0].entity_id == 1u);
    TEST_ASSERT(w.applied_log[1].domain_id == 2u && w.applied_log[1].chunk_id == 1u  && w.applied_log[1].entity_id == 5u);
    TEST_ASSERT(w.applied_log[2].domain_id == 1u && w.applied_log[2].chunk_id == 10u && w.applied_log[2].entity_id == 2u);
    TEST_ASSERT(w.applied_log[3].domain_id == 1u && w.applied_log[3].chunk_id == 10u && w.applied_log[3].entity_id == 4u);
    TEST_ASSERT(w.applied_log[4].domain_id == 2u && w.applied_log[4].chunk_id == 5u  && w.applied_log[4].entity_id == 1u);
    TEST_ASSERT(w.applied_log[5].domain_id == 1u && w.applied_log[5].chunk_id == 20u && w.applied_log[5].entity_id == 3u);

    dg_budget_free(&budget);
    dg_promo_free(&promo);
    dg_interest_free(&interest);
    dg_lod_index_free(&idx);
    return 0;
}

static int test_stride_determinism(void) {
    const u64 stable_id = 123456789ULL;
    const u32 stride = 8u;
    u64 h = dg_det_hash_u64(stable_id);
    u32 t;

    TEST_ASSERT(dg_stride_should_run(0u, stable_id, 0u) == D_TRUE);
    TEST_ASSERT(dg_stride_should_run(0u, stable_id, 1u) == D_TRUE);

    for (t = 0u; t < 64u; ++t) {
        d_bool expected = (((((u64)t) + h) % (u64)stride) == 0u) ? D_TRUE : D_FALSE;
        TEST_ASSERT(dg_stride_should_run((dg_tick)t, stable_id, stride) == expected);
    }

    return 0;
}

typedef struct test_accum_ctx {
    q32_32 total;
} test_accum_ctx;

static void test_accum_apply_cb(void *user_ctx, dg_accum_type type, dg_accum_value delta) {
    test_accum_ctx *ctx = (test_accum_ctx *)user_ctx;
    if (!ctx) return;
    if (type == DG_ACCUM_SCALAR_Q32_32) {
        ctx->total = (q32_32)(ctx->total + delta.scalar);
    }
}

static int test_accumulator_integrity(void) {
    dg_accum a_deferred;
    dg_accum a_trickled;
    test_accum_ctx c_deferred, c_trickled;
    dg_accum_value d;
    q32_32 unit_q;
    q32_32 delta_q;
    dg_tick tick;
    u32 budget;
    q32_32 expected_total;

    memset(&c_deferred, 0, sizeof(c_deferred));
    memset(&c_trickled, 0, sizeof(c_trickled));

    unit_q = (q32_32)((i64)1 << (Q32_32_FRAC_BITS - 2));  /* 0.25 */
    delta_q = (q32_32)((i64)1 << (Q32_32_FRAC_BITS - 1)); /* 0.5 */

    dg_accum_init_scalar(&a_deferred, unit_q);
    dg_accum_init_scalar(&a_trickled, unit_q);

    memset(&d, 0, sizeof(d));
    d.scalar = delta_q;

    /* Add 8 deltas. a_trickled applies 1 unit each tick; a_deferred applies nothing. */
    for (tick = 1u; tick <= 8u; ++tick) {
        dg_accum_add(&a_deferred, d, tick);
        dg_accum_add(&a_trickled, d, tick);
        budget = 1u;
        (void)dg_accum_apply(&a_trickled, test_accum_apply_cb, &c_trickled, 1u, &budget);
    }

    /* Drain both with ample budget. */
    budget = 1024u;
    (void)dg_accum_apply(&a_deferred, test_accum_apply_cb, &c_deferred, 1024u, &budget);
    budget = 1024u;
    (void)dg_accum_apply(&a_trickled, test_accum_apply_cb, &c_trickled, 1024u, &budget);

    expected_total = (q32_32)((i64)4 << Q32_32_FRAC_BITS); /* 0.5 * 8 = 4.0 */
    TEST_ASSERT(c_deferred.total == expected_total);
    TEST_ASSERT(c_trickled.total == expected_total);
    TEST_ASSERT(dg_accum_is_empty(&a_deferred) == D_TRUE);
    TEST_ASSERT(dg_accum_is_empty(&a_trickled) == D_TRUE);

    return 0;
}

int main(void) {
    int rc;
    rc = test_promo_stability();
    if (rc != 0) return rc;
    rc = test_budget_deferral();
    if (rc != 0) return rc;
    rc = test_stride_determinism();
    if (rc != 0) return rc;
    rc = test_accumulator_integrity();
    if (rc != 0) return rc;
    return 0;
}

