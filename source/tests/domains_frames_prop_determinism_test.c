#include <string.h>

#include "core/dg_pose.h"

#include "world/domain/dg_domain.h"
#include "world/domain/dg_domain_registry.h"

#include "world/frame/dg_frame_graph.h"
#include "world/frame/dg_frame_eval.h"

#include "sim/prop/dg_prop.h"

#include "sim/lod/dg_accum.h"
#include "sim/sched/dg_budget.h"

#define TEST_ASSERT(cond) do { if (!(cond)) return __LINE__; } while (0)

#define QONE ((dg_q)((i64)1 << 16))

static dg_q q_int(i64 v) { return (dg_q)(v * (i64)QONE); }

/* --------------------------- Domain ordering --------------------------- */

typedef struct test_domain_ctx {
    dg_domain_id step_order[8];
    u32          step_count;
    dg_domain_id hash_order[8];
    u32          hash_count;
} test_domain_ctx;

typedef struct test_domain {
    dg_domain       dom;
    test_domain_ctx *ctx;
} test_domain;

static void test_domain_step_phase(dg_domain *self, dg_phase phase, dg_budget *budget) {
    test_domain *d;
    (void)phase;
    (void)budget;
    if (!self) return;
    d = (test_domain *)self->user;
    if (!d || !d->ctx) return;
    if (d->ctx->step_count >= (u32)(sizeof(d->ctx->step_order) / sizeof(d->ctx->step_order[0]))) return;
    d->ctx->step_order[d->ctx->step_count++] = self->domain_id;
}

static int test_domain_query_stub(
    const dg_domain *self,
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

static u32 test_domain_serialize_stub(const dg_domain *self, unsigned char *out, u32 out_cap) {
    (void)self;
    (void)out;
    (void)out_cap;
    return 0u;
}

static u64 test_domain_hash_state(const dg_domain *self) {
    test_domain *d;
    if (!self) return 0u;
    d = (test_domain *)self->user;
    if (d && d->ctx) {
        if (d->ctx->hash_count < (u32)(sizeof(d->ctx->hash_order) / sizeof(d->ctx->hash_order[0]))) {
            d->ctx->hash_order[d->ctx->hash_count++] = self->domain_id;
        }
    }
    return (u64)self->domain_id;
}

static const dg_domain_vtbl TEST_DOMAIN_VTBL = {
    test_domain_step_phase,
    test_domain_query_stub,
    test_domain_serialize_stub,
    test_domain_hash_state
};

static void test_domain_init(test_domain *d, test_domain_ctx *ctx, dg_domain_id id) {
    if (!d) return;
    memset(d, 0, sizeof(*d));
    d->ctx = ctx;
    dg_domain_init(&d->dom, id, &TEST_DOMAIN_VTBL, d);
}

static int test_domain_ordering(void) {
    dg_domain_registry reg;
    dg_budget budget;
    test_domain_ctx ctx;
    test_domain d10, d2, d7, d1;

    memset(&ctx, 0, sizeof(ctx));
    dg_domain_registry_init(&reg);

    dg_budget_init(&budget);
    TEST_ASSERT(dg_budget_reserve(&budget, 8u, 0u) == 0);
    dg_budget_set_limits(&budget, DG_BUDGET_UNLIMITED, DG_BUDGET_UNLIMITED, DG_BUDGET_UNLIMITED);
    dg_budget_begin_tick(&budget, 1u);

    test_domain_init(&d10, &ctx, 10u);
    test_domain_init(&d2, &ctx, 2u);
    test_domain_init(&d7, &ctx, 7u);
    test_domain_init(&d1, &ctx, 1u);

    /* Shuffled insertion order must not affect canonical iteration. */
    TEST_ASSERT(dg_domain_registry_add(&reg, &d7.dom) == 0);
    TEST_ASSERT(dg_domain_registry_add(&reg, &d1.dom) == 0);
    TEST_ASSERT(dg_domain_registry_add(&reg, &d10.dom) == 0);
    TEST_ASSERT(dg_domain_registry_add(&reg, &d2.dom) == 0);

    dg_domain_registry_step_phase(&reg, DG_PH_TOPOLOGY, &budget);
    TEST_ASSERT(ctx.step_count == 4u);
    TEST_ASSERT(ctx.step_order[0] == 1u);
    TEST_ASSERT(ctx.step_order[1] == 2u);
    TEST_ASSERT(ctx.step_order[2] == 7u);
    TEST_ASSERT(ctx.step_order[3] == 10u);

    (void)dg_domain_registry_hash_state(&reg);
    TEST_ASSERT(ctx.hash_count == 4u);
    TEST_ASSERT(ctx.hash_order[0] == 1u);
    TEST_ASSERT(ctx.hash_order[1] == 2u);
    TEST_ASSERT(ctx.hash_order[2] == 7u);
    TEST_ASSERT(ctx.hash_order[3] == 10u);

    dg_budget_free(&budget);
    dg_domain_registry_free(&reg);
    return 0;
}

/* ------------------------ Frame eval determinism ----------------------- */

static dg_pose pose_translate(dg_q x, dg_q y, dg_q z) {
    dg_pose p = dg_pose_identity();
    p.pos.x = x;
    p.pos.y = y;
    p.pos.z = z;
    return p;
}

static dg_vec3_q v3(dg_q x, dg_q y, dg_q z) {
    dg_vec3_q v;
    v.x = x;
    v.y = y;
    v.z = z;
    return v;
}

static int test_frame_eval_determinism(void) {
    dg_frame_node storage[8];
    dg_frame_graph g;
    dg_frame_node n1, n2, n3;
    dg_pose out;
    const dg_tick ticks[4] = { 0u, 1u, 2u, 10u };
    u32 ti;
    int rc;

    dg_frame_graph_init(&g, storage, 8u);

    memset(&n1, 0, sizeof(n1));
    n1.id = 1u;
    n1.parent_id = DG_FRAME_ID_WORLD;
    n1.to_parent_base = pose_translate(q_int(1), 0, 0);
    n1.vel_pos_per_tick = v3(q_int(1), 0, 0);

    memset(&n2, 0, sizeof(n2));
    n2.id = 2u;
    n2.parent_id = 1u;
    n2.to_parent_base = pose_translate(0, q_int(2), 0);
    n2.vel_pos_per_tick = v3(0, q_int(1), 0);

    memset(&n3, 0, sizeof(n3));
    n3.id = 3u;
    n3.parent_id = 2u;
    n3.to_parent_base = pose_translate(0, 0, q_int(3));
    n3.vel_pos_per_tick = v3(0, 0, q_int(1));

    /* Shuffled insertion; eval must remain deterministic. */
    TEST_ASSERT(dg_frame_graph_add(&g, &n2) == 0);
    TEST_ASSERT(dg_frame_graph_add(&g, &n3) == 0);
    TEST_ASSERT(dg_frame_graph_add(&g, &n1) == 0);

    /* Evaluate at several ticks and verify expected fixed-point results. */
    for (ti = 0u; ti < 4u; ++ti) {
        dg_tick tick = ticks[ti];
        dg_q ex = q_int(1 + (i64)tick);
        dg_q ey = q_int(2 + (i64)tick);
        dg_q ez = q_int(3 + (i64)tick);

        rc = dg_frame_eval(&g, 3u, tick, DG_ROUND_NEAR, &out);
        TEST_ASSERT(rc == 0);
        TEST_ASSERT(out.pos.x == ex);
        TEST_ASSERT(out.pos.y == ey);
        TEST_ASSERT(out.pos.z == ez);
        TEST_ASSERT(out.rot.x == 0 && out.rot.y == 0 && out.rot.z == 0 && out.rot.w == QONE);
        TEST_ASSERT(out.incline == 0 && out.roll == 0);
    }

    return 0;
}

/* ----------------------- Propagator deferral --------------------------- */

typedef struct test_prop {
    dg_prop  prop;
    dg_accum owed;
    i64      applied;
    i64      per_tick;
    int      fail_line;
} test_prop;

static void test_prop_apply_cb(void *user_ctx, dg_accum_type type, dg_accum_value delta) {
    test_prop *p = (test_prop *)user_ctx;
    if (!p) return;
    if (type != DG_ACCUM_COUNT_I64) return;
    p->applied = (i64)(p->applied + delta.count);
}

static void test_prop_step(dg_prop *self, dg_tick tick, dg_budget *budget) {
    test_prop *p;
    dg_accum_value d;
    dg_budget_scope scope;
    u32 rem;
    u32 local_budget;
    u32 used_units;

    if (!self || !budget) return;
    p = (test_prop *)self->user;
    if (!p) return;

    memset(&d, 0, sizeof(d));
    d.count = p->per_tick;
    dg_accum_add(&p->owed, d, tick);

    scope = dg_budget_scope_domain(self->domain_id);
    rem = dg_budget_remaining(budget, &scope);
    local_budget = rem;
    used_units = dg_accum_apply(&p->owed, test_prop_apply_cb, p, rem, &local_budget);
    if (used_units > 0u) {
        if (dg_budget_try_consume(budget, &scope, used_units) != D_TRUE) {
            p->fail_line = __LINE__;
        }
    }
}

static int test_prop_sample_stub(const dg_prop *self, dg_tick tick, const void *query, void *out) {
    (void)self;
    (void)tick;
    (void)query;
    (void)out;
    return 0;
}

static u32 test_prop_serialize_stub(const dg_prop *self, unsigned char *out, u32 out_cap) {
    (void)self;
    (void)out;
    (void)out_cap;
    return 0u;
}

static u64 test_prop_hash_state(const dg_prop *self) {
    const test_prop *p;
    if (!self) return 0u;
    p = (const test_prop *)self->user;
    if (!p) return 0u;
    return (u64)p->applied ^ (u64)p->owed.owed.count;
}

static const dg_prop_vtbl TEST_PROP_VTBL = {
    test_prop_step,
    test_prop_sample_stub,
    test_prop_serialize_stub,
    test_prop_hash_state
};

static void test_prop_init(test_prop *p, dg_domain_id domain_id, dg_prop_id prop_id, i64 per_tick) {
    if (!p) return;
    memset(p, 0, sizeof(*p));
    p->per_tick = per_tick;
    dg_accum_init_count(&p->owed, 1);
    dg_prop_init(&p->prop, domain_id, prop_id, &TEST_PROP_VTBL, p);
}

static int test_prop_deferral(void) {
    dg_budget budget_full;
    dg_budget budget_limited;
    test_prop full;
    test_prop limited;
    dg_tick tick;

    test_prop_init(&full, 1u, 1u, 10);
    test_prop_init(&limited, 1u, 2u, 10);

    dg_budget_init(&budget_full);
    dg_budget_init(&budget_limited);
    TEST_ASSERT(dg_budget_reserve(&budget_full, 8u, 0u) == 0);
    TEST_ASSERT(dg_budget_reserve(&budget_limited, 8u, 0u) == 0);

    for (tick = 1u; tick <= 8u; ++tick) {
        i64 expected = (i64)(full.per_tick * (i64)tick);

        dg_budget_set_limits(&budget_full, DG_BUDGET_UNLIMITED, DG_BUDGET_UNLIMITED, DG_BUDGET_UNLIMITED);
        dg_budget_begin_tick(&budget_full, tick);
        dg_prop_step(&full.prop, tick, &budget_full);
        if (full.fail_line != 0) return full.fail_line;

        dg_budget_set_limits(&budget_limited, 3u, 3u, DG_BUDGET_UNLIMITED);
        dg_budget_begin_tick(&budget_limited, tick);
        dg_prop_step(&limited.prop, tick, &budget_limited);
        if (limited.fail_line != 0) return limited.fail_line;

        TEST_ASSERT(full.applied == expected);
        TEST_ASSERT((limited.applied + limited.owed.owed.count) == expected);
    }

    /* Deferral must have actually occurred (limited applied cannot keep up). */
    TEST_ASSERT(limited.applied < full.applied);
    TEST_ASSERT(limited.owed.owed.count > 0);

    dg_budget_free(&budget_full);
    dg_budget_free(&budget_limited);
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
