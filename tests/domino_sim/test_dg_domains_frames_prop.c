#include <string.h>

#include "core/dg_det_hash.h"

#include "sim/lod/dg_accum.h"
#include "sim/prop/dg_prop.h"
#include "sim/sched/dg_budget.h"

#include "world/domain/dg_domain.h"
#include "world/domain/dg_domain_registry.h"

#include "world/frame/dg_frame_eval.h"
#include "world/frame/dg_frame_graph.h"

#define TEST_ASSERT(cond) do { if (!(cond)) return __LINE__; } while (0)

/* ----------------------------- Domain ordering ----------------------------- */

typedef struct test_domain_ctx {
    dg_domain_id step_log[8];
    u32          step_count;
    dg_domain_id hash_log[8];
    u32          hash_count;
} test_domain_ctx;

typedef struct test_domain {
    dg_domain       d;
    test_domain_ctx *ctx;
    u64             hash_value;
} test_domain;

static void test_domain_step_phase(struct dg_domain *self, dg_phase phase, dg_budget *budget) {
    test_domain *td;
    (void)phase;
    (void)budget;
    if (!self) return;
    td = (test_domain *)self->user;
    if (!td || !td->ctx) return;
    if (td->ctx->step_count >= (u32)(sizeof(td->ctx->step_log) / sizeof(td->ctx->step_log[0]))) return;
    td->ctx->step_log[td->ctx->step_count++] = self->domain_id;
}

static int test_domain_query(
    const struct dg_domain *self,
    const dg_domain_query_desc *desc,
    const void *observer_ctx,
    dg_domain_query_results *out_results
) {
    (void)self;
    (void)desc;
    (void)observer_ctx;
    (void)out_results;
    return 0;
}

static u32 test_domain_serialize(const struct dg_domain *self, unsigned char *out, u32 out_cap) {
    (void)self;
    (void)out;
    (void)out_cap;
    return 0u;
}

static u64 test_domain_hash(const struct dg_domain *self) {
    test_domain *td;
    if (!self) return 0u;
    td = (test_domain *)self->user;
    if (!td || !td->ctx) return 0u;
    if (td->ctx->hash_count < (u32)(sizeof(td->ctx->hash_log) / sizeof(td->ctx->hash_log[0]))) {
        td->ctx->hash_log[td->ctx->hash_count++] = self->domain_id;
    }
    return td->hash_value;
}

static const dg_domain_vtbl TEST_DOMAIN_VTBL = {
    test_domain_step_phase,
    test_domain_query,
    test_domain_serialize,
    test_domain_hash
};

static void test_domain_init(test_domain *td, dg_domain_id id, test_domain_ctx *ctx, u64 hash_value) {
    if (!td) return;
    memset(td, 0, sizeof(*td));
    td->ctx = ctx;
    td->hash_value = hash_value;
    dg_domain_init(&td->d, id, &TEST_DOMAIN_VTBL, td);
}

static int test_domain_ordering(void) {
    dg_domain_registry reg;
    dg_budget budget;
    test_domain_ctx ctx;
    test_domain d3, d1, d2;
    u64 h_expected;
    u64 h_actual;

    memset(&ctx, 0, sizeof(ctx));

    dg_domain_registry_init(&reg);
    dg_budget_init(&budget);
    dg_budget_set_limits(&budget, DG_BUDGET_UNLIMITED, DG_BUDGET_UNLIMITED, DG_BUDGET_UNLIMITED);
    dg_budget_begin_tick(&budget, 1u);

    test_domain_init(&d3, 3u, &ctx, 0x0303u);
    test_domain_init(&d1, 1u, &ctx, 0x0101u);
    test_domain_init(&d2, 2u, &ctx, 0x0202u);

    TEST_ASSERT(dg_domain_registry_add(&reg, &d3.d) == 0);
    TEST_ASSERT(dg_domain_registry_add(&reg, &d1.d) == 0);
    TEST_ASSERT(dg_domain_registry_add(&reg, &d2.d) == 0);

    dg_domain_registry_step_phase(&reg, DG_PH_TOPOLOGY, &budget);
    TEST_ASSERT(ctx.step_count == 3u);
    TEST_ASSERT(ctx.step_log[0] == 1u);
    TEST_ASSERT(ctx.step_log[1] == 2u);
    TEST_ASSERT(ctx.step_log[2] == 3u);

    h_actual = dg_domain_registry_hash_state(&reg);
    TEST_ASSERT(ctx.hash_count == 3u);
    TEST_ASSERT(ctx.hash_log[0] == 1u);
    TEST_ASSERT(ctx.hash_log[1] == 2u);
    TEST_ASSERT(ctx.hash_log[2] == 3u);

    h_expected = 0xD06A1D0D06A1D0D1ULL;
    h_expected = dg_det_hash_u64(h_expected ^ (u64)3u);
    h_expected = dg_det_hash_u64(h_expected ^ (u64)1u);
    h_expected = dg_det_hash_u64(h_expected ^ (u64)d1.hash_value);
    h_expected = dg_det_hash_u64(h_expected ^ (u64)2u);
    h_expected = dg_det_hash_u64(h_expected ^ (u64)d2.hash_value);
    h_expected = dg_det_hash_u64(h_expected ^ (u64)3u);
    h_expected = dg_det_hash_u64(h_expected ^ (u64)d3.hash_value);
    TEST_ASSERT(h_actual == h_expected);

    dg_budget_free(&budget);
    dg_domain_registry_free(&reg);
    return 0;
}

/* ------------------------ Frame evaluation determinism --------------------- */

static int test_pose_eq(const dg_pose *a, const dg_pose *b) {
    if (!a || !b) return 0;
    return (a->pos.x == b->pos.x &&
            a->pos.y == b->pos.y &&
            a->pos.z == b->pos.z &&
            a->rot.x == b->rot.x &&
            a->rot.y == b->rot.y &&
            a->rot.z == b->rot.z &&
            a->rot.w == b->rot.w &&
            a->incline == b->incline &&
            a->roll == b->roll) ? 1 : 0;
}

static dg_pose test_expected_frame_pose(dg_tick tick) {
    dg_pose p;
    i64 t = (i64)tick;
    p = dg_pose_identity();
    p.pos.x = (dg_q)d_q48_16_from_int((i64)10 + t);
    p.pos.y = (dg_q)d_q48_16_from_int((i64)5 + (i64)2 * t);
    p.pos.z = (dg_q)d_q48_16_from_int((i64)7 + (i64)3 * t);
    p.incline = (dg_q)d_q48_16_from_int((i64)3 + t);
    p.roll = 0;
    return p;
}

static int test_frame_eval_determinism(void) {
    dg_frame_node storage[8];
    dg_frame_graph g;
    dg_frame_node n;
    dg_pose out_a, out_b, expected;
    dg_tick ticks[4];
    u32 i;

    ticks[0] = 0u;
    ticks[1] = 1u;
    ticks[2] = 2u;
    ticks[3] = 10u;

    dg_frame_graph_init(&g, storage, (u32)(sizeof(storage) / sizeof(storage[0])));

    memset(&n, 0, sizeof(n));
    n.id = 1u;
    n.parent_id = DG_FRAME_ID_WORLD;
    n.to_parent_base = dg_pose_identity();
    n.to_parent_base.pos.x = (dg_q)d_q48_16_from_int(10);
    n.to_parent_base.incline = (dg_q)d_q48_16_from_int(1);
    n.vel_pos_per_tick.x = (dg_q)d_q48_16_from_int(1);
    (void)dg_frame_graph_add(&g, &n);

    memset(&n, 0, sizeof(n));
    n.id = 2u;
    n.parent_id = 1u;
    n.to_parent_base = dg_pose_identity();
    n.to_parent_base.pos.y = (dg_q)d_q48_16_from_int(5);
    n.vel_pos_per_tick.y = (dg_q)d_q48_16_from_int(2);
    n.vel_incline_per_tick = (dg_q)d_q48_16_from_int(1);
    (void)dg_frame_graph_add(&g, &n);

    memset(&n, 0, sizeof(n));
    n.id = 3u;
    n.parent_id = 2u;
    n.to_parent_base = dg_pose_identity();
    n.to_parent_base.pos.z = (dg_q)d_q48_16_from_int(7);
    n.to_parent_base.incline = (dg_q)d_q48_16_from_int(2);
    n.vel_pos_per_tick.z = (dg_q)d_q48_16_from_int(3);
    (void)dg_frame_graph_add(&g, &n);

    for (i = 0u; i < (u32)(sizeof(ticks) / sizeof(ticks[0])); ++i) {
        TEST_ASSERT(dg_frame_eval(&g, 3u, ticks[i], DG_ROUND_NEAR, &out_a) == 0);
        TEST_ASSERT(dg_frame_eval(&g, 3u, ticks[i], DG_ROUND_NEAR, &out_b) == 0);
        TEST_ASSERT(test_pose_eq(&out_a, &out_b) == 1);

        expected = test_expected_frame_pose(ticks[i]);
        TEST_ASSERT(test_pose_eq(&out_a, &expected) == 1);
    }

    return 0;
}

/* --------------------------- Propagator deferral --------------------------- */

typedef struct test_prop_state {
    i64     value;
    dg_accum accum;
} test_prop_state;

typedef struct test_prop {
    dg_prop        p;
    test_prop_state s;
} test_prop;

static void test_prop_apply(void *user_ctx, dg_accum_type type, dg_accum_value delta) {
    test_prop_state *s = (test_prop_state *)user_ctx;
    if (!s) return;
    if (type == DG_ACCUM_COUNT_I64) {
        s->value = (i64)(s->value + delta.count);
    }
}

static void test_prop_step(struct dg_prop *self, dg_tick tick, dg_budget *budget) {
    test_prop *tp;
    dg_accum_value d;
    dg_budget_scope scope;
    u32 rem;
    u32 budget_units;
    u32 used_units;

    if (!self) return;
    tp = (test_prop *)self->user;
    if (!tp) return;

    memset(&d, 0, sizeof(d));
    d.count = 1;
    dg_accum_add(&tp->s.accum, d, tick);

    if (!budget) return;
    scope = dg_budget_scope_global();
    rem = dg_budget_remaining(budget, &scope);
    if (rem == 0u) return;

    budget_units = rem;
    used_units = dg_accum_apply(&tp->s.accum, test_prop_apply, &tp->s, rem, &budget_units);
    (void)dg_budget_try_consume(budget, &scope, used_units);
}

static int test_prop_sample(const struct dg_prop *self, dg_tick tick, const void *query, void *out) {
    (void)self;
    (void)tick;
    (void)query;
    (void)out;
    return 0;
}

static u32 test_prop_serialize(const struct dg_prop *self, unsigned char *out, u32 out_cap) {
    (void)self;
    (void)out;
    (void)out_cap;
    return 0u;
}

static u64 test_prop_hash(const struct dg_prop *self) {
    const test_prop *tp;
    if (!self) return 0u;
    tp = (const test_prop *)self->user;
    if (!tp) return 0u;
    return (u64)tp->s.value;
}

static const dg_prop_vtbl TEST_PROP_VTBL = {
    test_prop_step,
    test_prop_sample,
    test_prop_serialize,
    test_prop_hash
};

static void test_prop_init(test_prop *tp, dg_prop_id id) {
    if (!tp) return;
    memset(tp, 0, sizeof(*tp));
    dg_prop_init(&tp->p, 0u, id, &TEST_PROP_VTBL, tp);
    dg_accum_init_count(&tp->s.accum, 1);
}

static int test_prop_deferral(void) {
    dg_budget budget;
    test_prop uninterrupted;
    test_prop deferred;
    dg_tick tick;
    u32 budgets[5];

    budgets[0] = 0u;
    budgets[1] = 0u;
    budgets[2] = 1u;
    budgets[3] = 0u;
    budgets[4] = 10u;

    dg_budget_init(&budget);
    test_prop_init(&uninterrupted, 1u);
    test_prop_init(&deferred, 2u);

    for (tick = 1u; tick <= 5u; ++tick) {
        dg_budget_set_limits(&budget, DG_BUDGET_UNLIMITED, DG_BUDGET_UNLIMITED, DG_BUDGET_UNLIMITED);
        dg_budget_begin_tick(&budget, tick);
        dg_prop_step(&uninterrupted.p, tick, &budget);
    }

    for (tick = 1u; tick <= 5u; ++tick) {
        dg_budget_set_limits(&budget, budgets[(u32)tick - 1u], DG_BUDGET_UNLIMITED, DG_BUDGET_UNLIMITED);
        dg_budget_begin_tick(&budget, tick);
        dg_prop_step(&deferred.p, tick, &budget);
    }

    TEST_ASSERT(uninterrupted.s.value == 5);
    TEST_ASSERT(deferred.s.value == 5);
    TEST_ASSERT(dg_accum_is_empty(&uninterrupted.s.accum) == D_TRUE);
    TEST_ASSERT(dg_accum_is_empty(&deferred.s.accum) == D_TRUE);

    dg_budget_free(&budget);
    return 0;
}

int main(void) {
    int rc;
    rc = test_domain_ordering();
    if (rc != 0) return rc;
    rc = test_frame_eval_determinism();
    if (rc != 0) return rc;
    rc = test_prop_deferral();
    if (rc != 0) return rc;
    return 0;
}

