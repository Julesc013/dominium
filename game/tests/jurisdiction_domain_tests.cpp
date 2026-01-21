/*
Jurisdiction domain resolution tests (DOMAIN2).
*/
#include "game/core/law/jurisdiction_resolver.h"

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
} test_sdf_ctx;

static q16_16 test_abs_q16_16(q16_16 v)
{
    return (v < 0) ? (q16_16)-v : v;
}

static q16_16 test_sdf_l1_sphere(const void* ctx, const dom_domain_point* p)
{
    const test_sdf_ctx* c = (const test_sdf_ctx*)ctx;
    q16_16 dx = (q16_16)(p->x - c->center.x);
    q16_16 dy = (q16_16)(p->y - c->center.y);
    q16_16 dz = (q16_16)(p->z - c->center.z);
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
                              dom_domain_id domain_id,
                              dom_domain_sdf_source* source)
{
    dom_domain_volume_init(volume);
    volume->domain_id = domain_id;
    dom_domain_volume_set_authoring_version(volume, 1u);
    dom_domain_volume_set_state(volume, DOM_DOMAIN_EXISTENCE_REALIZED, DOM_DOMAIN_ARCHIVAL_LIVE);
    dom_domain_volume_set_source(volume, source);
}

static int list_contains(const dom_jurisdiction_list* list, dom_jurisdiction_id id)
{
    u32 i;
    if (!list) {
        return 0;
    }
    for (i = 0u; i < list->count; ++i) {
        if (list->ids[i] == id) {
            return 1;
        }
    }
    return 0;
}

static int list_equal(const dom_jurisdiction_list* a, const dom_jurisdiction_list* b)
{
    u32 i;
    if (!a || !b) {
        return 0;
    }
    if (a->count != b->count) {
        return 0;
    }
    for (i = 0u; i < a->count; ++i) {
        if (a->ids[i] != b->ids[i]) {
            return 0;
        }
    }
    return 1;
}

static int test_nested_domain_resolution(void)
{
    test_sdf_ctx outer_ctx;
    test_sdf_ctx inner_ctx;
    dom_domain_sdf_source outer_source;
    dom_domain_sdf_source inner_source;
    dom_domain_volume outer_volume;
    dom_domain_volume inner_volume;
    dom_domain_jurisdiction_binding outer_bindings[] = { { 100u, 1u } };
    dom_domain_jurisdiction_binding inner_bindings[] = { { 101u, 1u } };
    dom_domain_jurisdiction_entry domains[2];
    dom_domain_point p;
    dom_domain_budget budget;
    dom_jurisdiction_resolution res;

    memset(&outer_ctx, 0, sizeof(outer_ctx));
    memset(&inner_ctx, 0, sizeof(inner_ctx));
    outer_ctx.center = test_point_i32(0, 0, 0);
    outer_ctx.radius = d_q16_16_from_int(8);
    inner_ctx.center = test_point_i32(0, 0, 0);
    inner_ctx.radius = d_q16_16_from_int(3);

    test_setup_source(&outer_source, &outer_ctx, 16);
    test_setup_source(&inner_source, &inner_ctx, 16);
    test_setup_volume(&outer_volume, 10u, &outer_source);
    test_setup_volume(&inner_volume, 11u, &inner_source);

    domains[0].domain_id = 10u;
    domains[0].parent_domain_id = 0u;
    domains[0].domain_precedence = 1u;
    domains[0].volume = &outer_volume;
    domains[0].bindings = outer_bindings;
    domains[0].binding_count = 1u;

    domains[1].domain_id = 11u;
    domains[1].parent_domain_id = 10u;
    domains[1].domain_precedence = 1u;
    domains[1].volume = &inner_volume;
    domains[1].bindings = inner_bindings;
    domains[1].binding_count = 1u;

    p = test_point_i32(1, 0, 0);
    dom_domain_budget_init(&budget, 10000u);
    dom_jurisdiction_resolution_init(&res);
    EXPECT(dom_jurisdiction_resolve_point(domains, 2u, 0, &p, &budget,
                                          200u, 201u, 999u, &res) == 0,
           "nested resolve");
    EXPECT(res.ordered.count >= 2u, "nested count");
    EXPECT(res.ordered.ids[0] == 101u, "nested smallest domain first");
    EXPECT(res.ordered.ids[1] == 100u, "nested outer second");
    EXPECT(list_contains(&res.ordered, 200u), "world default present");
    EXPECT(list_contains(&res.ordered, 201u), "server default present");
    EXPECT(list_contains(&res.ordered, 999u), "fallback present");
    return 0;
}

static int test_overlap_precedence(void)
{
    test_sdf_ctx a_ctx;
    test_sdf_ctx b_ctx;
    dom_domain_sdf_source a_source;
    dom_domain_sdf_source b_source;
    dom_domain_volume a_volume;
    dom_domain_volume b_volume;
    dom_domain_jurisdiction_binding a_bindings[] = { { 300u, 1u } };
    dom_domain_jurisdiction_binding b_bindings[] = { { 301u, 1u } };
    dom_domain_jurisdiction_entry domains[2];
    dom_domain_point p;
    dom_domain_budget budget;
    dom_jurisdiction_resolution res;

    memset(&a_ctx, 0, sizeof(a_ctx));
    memset(&b_ctx, 0, sizeof(b_ctx));
    a_ctx.center = test_point_i32(0, 0, 0);
    a_ctx.radius = d_q16_16_from_int(5);
    b_ctx.center = test_point_i32(1, 0, 0);
    b_ctx.radius = d_q16_16_from_int(5);

    test_setup_source(&a_source, &a_ctx, 16);
    test_setup_source(&b_source, &b_ctx, 16);
    test_setup_volume(&a_volume, 20u, &a_source);
    test_setup_volume(&b_volume, 21u, &b_source);

    domains[0].domain_id = 20u;
    domains[0].parent_domain_id = 0u;
    domains[0].domain_precedence = 1u;
    domains[0].volume = &a_volume;
    domains[0].bindings = a_bindings;
    domains[0].binding_count = 1u;

    domains[1].domain_id = 21u;
    domains[1].parent_domain_id = 0u;
    domains[1].domain_precedence = 5u;
    domains[1].volume = &b_volume;
    domains[1].bindings = b_bindings;
    domains[1].binding_count = 1u;

    p = test_point_i32(0, 0, 0);
    dom_domain_budget_init(&budget, 10000u);
    dom_jurisdiction_resolution_init(&res);
    EXPECT(dom_jurisdiction_resolve_point(domains, 2u, 0, &p, &budget,
                                          0u, 0u, 0u, &res) == 0,
           "overlap resolve");
    EXPECT(res.ordered.count >= 2u, "overlap count");
    EXPECT(res.ordered.ids[0] == 300u, "overlap smallest first");
    EXPECT(res.ordered.ids[1] == 301u, "overlap higher precedence next");
    return 0;
}

static int test_boundary_difference(void)
{
    test_sdf_ctx ctx;
    dom_domain_sdf_source source;
    dom_domain_volume volume;
    dom_domain_jurisdiction_binding bindings[] = { { 400u, 1u } };
    dom_domain_jurisdiction_entry domain;
    dom_domain_budget budget;
    dom_domain_point inside_p;
    dom_domain_point outside_p;
    dom_jurisdiction_resolution inside_res;
    dom_jurisdiction_resolution outside_res;

    memset(&ctx, 0, sizeof(ctx));
    ctx.center = test_point_i32(0, 0, 0);
    ctx.radius = d_q16_16_from_int(2);
    test_setup_source(&source, &ctx, 8);
    test_setup_volume(&volume, 30u, &source);

    domain.domain_id = 30u;
    domain.parent_domain_id = 0u;
    domain.domain_precedence = 1u;
    domain.volume = &volume;
    domain.bindings = bindings;
    domain.binding_count = 1u;

    inside_p = test_point_i32(1, 0, 0);
    dom_domain_budget_init(&budget, 10000u);
    dom_jurisdiction_resolution_init(&inside_res);
    dom_jurisdiction_resolve_point(&domain, 1u, 0, &inside_p, &budget,
                                   0u, 0u, 0u, &inside_res);
    EXPECT(list_contains(&inside_res.ordered, 400u), "inside contains jurisdiction");

    outside_p = test_point_i32(5, 0, 0);
    dom_domain_budget_init(&budget, 10000u);
    dom_jurisdiction_resolution_init(&outside_res);
    dom_jurisdiction_resolve_point(&domain, 1u, 0, &outside_p, &budget,
                                   0u, 0u, 0u, &outside_res);
    EXPECT(!list_contains(&outside_res.ordered, 400u), "outside excludes jurisdiction");
    return 0;
}

static int test_travel_path_resolution(void)
{
    test_sdf_ctx ctx;
    dom_domain_sdf_source source;
    dom_domain_volume volume;
    dom_domain_jurisdiction_binding bindings[] = { { 500u, 1u } };
    dom_domain_jurisdiction_entry domain;
    dom_domain_budget budget;
    dom_domain_point points[3];
    dom_jurisdiction_resolution res;

    memset(&ctx, 0, sizeof(ctx));
    ctx.center = test_point_i32(0, 0, 0);
    ctx.radius = d_q16_16_from_int(2);
    test_setup_source(&source, &ctx, 8);
    test_setup_volume(&volume, 40u, &source);

    domain.domain_id = 40u;
    domain.parent_domain_id = 0u;
    domain.domain_precedence = 1u;
    domain.volume = &volume;
    domain.bindings = bindings;
    domain.binding_count = 1u;

    points[0] = test_point_i32(-5, 0, 0);
    points[1] = test_point_i32(0, 0, 0);
    points[2] = test_point_i32(5, 0, 0);

    dom_domain_budget_init(&budget, 10000u);
    dom_jurisdiction_resolution_init(&res);
    dom_jurisdiction_resolve_multi(&domain, 1u, 0, points, 3u, &budget,
                                   0u, 0u, 0u, &res);
    EXPECT(list_contains(&res.ordered, 500u), "path includes restrictive jurisdiction");
    return 0;
}

static int test_deterministic_ordering(void)
{
    test_sdf_ctx ctx_a;
    test_sdf_ctx ctx_b;
    dom_domain_sdf_source src_a;
    dom_domain_sdf_source src_b;
    dom_domain_volume vol_a;
    dom_domain_volume vol_b;
    dom_domain_jurisdiction_binding bind_a[] = { { 600u, 1u } };
    dom_domain_jurisdiction_binding bind_b[] = { { 601u, 1u } };
    dom_domain_jurisdiction_entry domains_a[2];
    dom_domain_jurisdiction_entry domains_b[2];
    dom_domain_point p;
    dom_domain_budget budget;
    dom_jurisdiction_resolution res_a;
    dom_jurisdiction_resolution res_b;

    memset(&ctx_a, 0, sizeof(ctx_a));
    memset(&ctx_b, 0, sizeof(ctx_b));
    ctx_a.center = test_point_i32(0, 0, 0);
    ctx_a.radius = d_q16_16_from_int(4);
    ctx_b.center = test_point_i32(1, 0, 0);
    ctx_b.radius = d_q16_16_from_int(4);
    test_setup_source(&src_a, &ctx_a, 8);
    test_setup_source(&src_b, &ctx_b, 8);
    test_setup_volume(&vol_a, 50u, &src_a);
    test_setup_volume(&vol_b, 51u, &src_b);

    domains_a[0].domain_id = 50u;
    domains_a[0].parent_domain_id = 0u;
    domains_a[0].domain_precedence = 2u;
    domains_a[0].volume = &vol_a;
    domains_a[0].bindings = bind_a;
    domains_a[0].binding_count = 1u;
    domains_a[1].domain_id = 51u;
    domains_a[1].parent_domain_id = 0u;
    domains_a[1].domain_precedence = 3u;
    domains_a[1].volume = &vol_b;
    domains_a[1].bindings = bind_b;
    domains_a[1].binding_count = 1u;

    domains_b[0] = domains_a[1];
    domains_b[1] = domains_a[0];

    p = test_point_i32(0, 0, 0);
    dom_domain_budget_init(&budget, 10000u);
    dom_jurisdiction_resolution_init(&res_a);
    dom_jurisdiction_resolve_point(domains_a, 2u, 0, &p, &budget,
                                   0u, 0u, 0u, &res_a);

    dom_domain_budget_init(&budget, 10000u);
    dom_jurisdiction_resolution_init(&res_b);
    dom_jurisdiction_resolve_point(domains_b, 2u, 0, &p, &budget,
                                   0u, 0u, 0u, &res_b);

    EXPECT(list_equal(&res_a.ordered, &res_b.ordered), "deterministic regardless of input order");
    return 0;
}

int main(void)
{
    if (test_nested_domain_resolution() != 0) return 1;
    if (test_overlap_precedence() != 0) return 1;
    if (test_boundary_difference() != 0) return 1;
    if (test_travel_path_resolution() != 0) return 1;
    if (test_deterministic_ordering() != 0) return 1;
    return 0;
}
