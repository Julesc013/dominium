/*
Domain volume runtime tests (DOMAIN1).
*/
#include "domino/world/domain_query.h"
#include "domino/world/domain_cache.h"

#include <stdio.h>
#include <string.h>

#define EXPECT(cond, msg) do { \
    if (!(cond)) { \
        fprintf(stderr, "FAIL: %s\n", msg); \
        return 1; \
    } \
} while (0)

typedef struct test_sdf_ctx {
    dom_domain_point center;
    q16_16 radius;
    u32 eval_count;
} test_sdf_ctx;

static q16_16 test_abs_q16_16(q16_16 v)
{
    return (v < 0) ? (q16_16)-v : v;
}

static q16_16 test_sdf_l1_sphere(const void* ctx, const dom_domain_point* p)
{
    test_sdf_ctx* c = (test_sdf_ctx*)ctx;
    q16_16 dx = (q16_16)(p->x - c->center.x);
    q16_16 dy = (q16_16)(p->y - c->center.y);
    q16_16 dz = (q16_16)(p->z - c->center.z);
    if (c) {
        c->eval_count += 1u;
    }
    dx = test_abs_q16_16(dx);
    dy = test_abs_q16_16(dy);
    dz = test_abs_q16_16(dz);
    return (q16_16)((dx + dy + dz) - c->radius);
}

static dom_domain_point test_point_i32(i32 x, i32 y, i32 z)
{
    dom_domain_point p;
    p.x = d_q16_16_from_int(x);
    p.y = d_q16_16_from_int(y);
    p.z = d_q16_16_from_int(z);
    return p;
}

static void test_setup_source(dom_domain_sdf_source* source,
                              test_sdf_ctx* ctx,
                              i32 bounds_extent)
{
    memset(source, 0, sizeof(*source));
    source->eval = test_sdf_l1_sphere;
    source->analytic_eval = test_sdf_l1_sphere;
    source->ctx = ctx;
    source->has_analytic = 1u;
    source->bounds.min = test_point_i32(-bounds_extent, -bounds_extent, -bounds_extent);
    source->bounds.max = test_point_i32(bounds_extent, bounds_extent, bounds_extent);
}

static void test_setup_volume(dom_domain_volume* volume,
                              dom_domain_sdf_source* source,
                              dom_domain_id id,
                              u32 version,
                              const dom_domain_policy* policy)
{
    dom_domain_volume_init(volume);
    volume->domain_id = id;
    dom_domain_volume_set_authoring_version(volume, version);
    dom_domain_volume_set_state(volume, DOM_DOMAIN_EXISTENCE_REALIZED, DOM_DOMAIN_ARCHIVAL_LIVE);
    dom_domain_volume_set_source(volume, source);
    if (policy) {
        dom_domain_volume_set_policy(volume, policy);
    }
}

static int test_contains_deterministic(void)
{
    test_sdf_ctx ctx;
    dom_domain_sdf_source source;
    dom_domain_volume volume;
    dom_domain_budget budget;
    dom_domain_query_meta meta_a;
    dom_domain_query_meta meta_b;
    dom_domain_point p;
    d_bool a;
    d_bool b;

    memset(&ctx, 0, sizeof(ctx));
    ctx.center = test_point_i32(0, 0, 0);
    ctx.radius = d_q16_16_from_int(4);
    test_setup_source(&source, &ctx, 16);

    test_setup_volume(&volume, &source, 1u, 1u, NULL);

    dom_domain_budget_init(&budget, 1000u);
    p = test_point_i32(1, 1, 1);
    a = dom_domain_contains(&volume, &p, &budget, &meta_a);

    dom_domain_budget_init(&budget, 1000u);
    b = dom_domain_contains(&volume, &p, &budget, &meta_b);

    EXPECT(a == b, "contains deterministic");
    EXPECT(meta_a.status == meta_b.status, "meta status deterministic");
    EXPECT(meta_a.resolution == meta_b.resolution, "meta resolution deterministic");
    EXPECT(meta_a.confidence == meta_b.confidence, "meta confidence deterministic");
    EXPECT(meta_a.refusal_reason == meta_b.refusal_reason, "meta refusal deterministic");
    EXPECT(meta_a.cost_units == meta_b.cost_units, "meta cost deterministic");

    dom_domain_volume_free(&volume);
    return 0;
}

static int test_distance_deterministic(void)
{
    test_sdf_ctx ctx;
    dom_domain_sdf_source source;
    dom_domain_volume volume;
    dom_domain_budget budget;
    dom_domain_point p;
    dom_domain_distance_result res;

    memset(&ctx, 0, sizeof(ctx));
    ctx.center = test_point_i32(0, 0, 0);
    ctx.radius = d_q16_16_from_int(4);
    test_setup_source(&source, &ctx, 16);

    test_setup_volume(&volume, &source, 2u, 1u, NULL);
    dom_domain_budget_init(&budget, 1000u);

    p = test_point_i32(6, 0, 0);
    res = dom_domain_distance(&volume, &p, &budget);
    EXPECT(res.meta.status == DOM_DOMAIN_QUERY_OK, "distance query ok");
    EXPECT(res.meta.confidence == DOM_DOMAIN_CONFIDENCE_EXACT, "distance exact");
    EXPECT(res.distance == d_q16_16_from_int(2), "distance expected");

    dom_domain_volume_free(&volume);
    return 0;
}

static int test_cache_reuse(void)
{
    test_sdf_ctx ctx;
    dom_domain_sdf_source source;
    dom_domain_volume volume;
    dom_domain_cache cache;
    dom_domain_policy policy;
    dom_domain_budget budget;
    dom_domain_point p1;
    dom_domain_point p2;
    u32 count_after_first;

    memset(&ctx, 0, sizeof(ctx));
    ctx.center = test_point_i32(0, 0, 0);
    ctx.radius = d_q16_16_from_int(4);
    test_setup_source(&source, &ctx, 16);

    dom_domain_policy_init(&policy);
    policy.max_resolution = DOM_DOMAIN_RES_MEDIUM;

    dom_domain_cache_init(&cache);
    dom_domain_cache_reserve(&cache, 4u);

    test_setup_volume(&volume, &source, 3u, 1u, &policy);
    dom_domain_volume_set_cache(&volume, &cache);

    dom_domain_budget_init(&budget, 10000u);
    p1 = test_point_i32(1, 1, 1);
    (void)dom_domain_distance(&volume, &p1, &budget);
    count_after_first = ctx.eval_count;
    EXPECT(count_after_first > 0u, "eval count after first query");

    dom_domain_budget_init(&budget, 10000u);
    p2 = test_point_i32(2, 1, 1);
    (void)dom_domain_distance(&volume, &p2, &budget);
    EXPECT(ctx.eval_count == count_after_first, "cache reuse avoids rebuild");

    dom_domain_volume_free(&volume);
    dom_domain_cache_free(&cache);
    return 0;
}

static int test_budget_degradation(void)
{
    test_sdf_ctx ctx;
    dom_domain_sdf_source source;
    dom_domain_volume volume;
    dom_domain_policy policy;
    dom_domain_budget budget;
    dom_domain_query_meta meta;
    dom_domain_point p;
    d_bool inside;

    memset(&ctx, 0, sizeof(ctx));
    ctx.center = test_point_i32(0, 0, 0);
    ctx.radius = d_q16_16_from_int(4);
    test_setup_source(&source, &ctx, 16);

    dom_domain_policy_init(&policy);
    policy.max_resolution = DOM_DOMAIN_RES_FULL;
    policy.cost_full = 100u;
    policy.cost_medium = 90u;
    policy.tile_build_cost_medium = 90u;
    policy.cost_coarse = 5u;
    policy.tile_build_cost_coarse = 5u;

    test_setup_volume(&volume, &source, 4u, 1u, &policy);

    dom_domain_budget_init(&budget, 10u);
    p = test_point_i32(1, 0, 0);
    inside = dom_domain_contains(&volume, &p, &budget, &meta);
    EXPECT(inside == D_FALSE, "contains conservatively false under coarse");
    EXPECT(meta.status == DOM_DOMAIN_QUERY_OK, "coarse query ok");
    EXPECT(meta.resolution == DOM_DOMAIN_RES_COARSE, "coarse resolution selected");
    EXPECT(meta.confidence == DOM_DOMAIN_CONFIDENCE_LOWER_BOUND, "coarse lower bound");

    dom_domain_volume_free(&volume);
    return 0;
}

static int test_nested_and_overlap(void)
{
    test_sdf_ctx outer_ctx;
    test_sdf_ctx inner_ctx;
    test_sdf_ctx overlap_ctx;
    dom_domain_sdf_source outer_source;
    dom_domain_sdf_source inner_source;
    dom_domain_sdf_source overlap_source;
    dom_domain_volume outer;
    dom_domain_volume inner;
    dom_domain_volume overlap;
    dom_domain_budget budget;
    dom_domain_query_meta meta;
    dom_domain_point p;
    d_bool in_outer;
    d_bool in_inner;
    d_bool in_overlap;

    memset(&outer_ctx, 0, sizeof(outer_ctx));
    memset(&inner_ctx, 0, sizeof(inner_ctx));
    memset(&overlap_ctx, 0, sizeof(overlap_ctx));

    outer_ctx.center = test_point_i32(0, 0, 0);
    outer_ctx.radius = d_q16_16_from_int(8);
    inner_ctx.center = test_point_i32(0, 0, 0);
    inner_ctx.radius = d_q16_16_from_int(3);
    overlap_ctx.center = test_point_i32(2, 0, 0);
    overlap_ctx.radius = d_q16_16_from_int(3);

    test_setup_source(&outer_source, &outer_ctx, 16);
    test_setup_source(&inner_source, &inner_ctx, 16);
    test_setup_source(&overlap_source, &overlap_ctx, 16);

    test_setup_volume(&outer, &outer_source, 5u, 1u, NULL);
    test_setup_volume(&inner, &inner_source, 6u, 1u, NULL);
    test_setup_volume(&overlap, &overlap_source, 7u, 1u, NULL);

    dom_domain_budget_init(&budget, 1000u);
    p = test_point_i32(1, 0, 0);
    in_outer = dom_domain_contains(&outer, &p, &budget, &meta);
    dom_domain_budget_init(&budget, 1000u);
    in_inner = dom_domain_contains(&inner, &p, &budget, &meta);
    dom_domain_budget_init(&budget, 1000u);
    in_overlap = dom_domain_contains(&overlap, &p, &budget, &meta);
    EXPECT(in_outer == D_TRUE, "nested outer contains");
    EXPECT(in_inner == D_TRUE, "nested inner contains");
    EXPECT(in_overlap == D_TRUE, "overlap contains");

    dom_domain_budget_init(&budget, 1000u);
    p = test_point_i32(7, 0, 0);
    in_outer = dom_domain_contains(&outer, &p, &budget, &meta);
    dom_domain_budget_init(&budget, 1000u);
    in_inner = dom_domain_contains(&inner, &p, &budget, &meta);
    EXPECT(in_outer == D_TRUE, "outer contains far point");
    EXPECT(in_inner == D_FALSE, "inner excludes far point");

    dom_domain_volume_free(&outer);
    dom_domain_volume_free(&inner);
    dom_domain_volume_free(&overlap);
    return 0;
}

static int test_large_scale_queries(void)
{
    test_sdf_ctx ctx;
    dom_domain_sdf_source source;
    dom_domain_volume volume;
    dom_domain_budget budget;
    dom_domain_point p;
    i64 sum_a;
    i64 sum_b;
    i32 i;

    memset(&ctx, 0, sizeof(ctx));
    ctx.center = test_point_i32(0, 0, 0);
    ctx.radius = d_q16_16_from_int(10000);
    test_setup_source(&source, &ctx, 20000);

    test_setup_volume(&volume, &source, 8u, 1u, NULL);

    sum_a = 0;
    dom_domain_budget_init(&budget, 1000000u);
    for (i = 0; i < 256; ++i) {
        p = test_point_i32(15000 + (i % 64), 14900 + (i % 64), 14800 + (i % 64));
        sum_a += dom_domain_distance(&volume, &p, &budget).distance;
    }

    sum_b = 0;
    dom_domain_budget_init(&budget, 1000000u);
    for (i = 0; i < 256; ++i) {
        p = test_point_i32(15000 + (i % 64), 14900 + (i % 64), 14800 + (i % 64));
        sum_b += dom_domain_distance(&volume, &p, &budget).distance;
    }

    EXPECT(sum_a == sum_b, "large-scale queries deterministic");
    dom_domain_volume_free(&volume);
    return 0;
}

int main(void)
{
    if (test_contains_deterministic() != 0) return 1;
    if (test_distance_deterministic() != 0) return 1;
    if (test_cache_reuse() != 0) return 1;
    if (test_budget_degradation() != 0) return 1;
    if (test_nested_and_overlap() != 0) return 1;
    if (test_large_scale_queries() != 0) return 1;
    return 0;
}
