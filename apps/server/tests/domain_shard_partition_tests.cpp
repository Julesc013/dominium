/*
Domain shard partitioning tests (DOMAIN3).
*/
#include "shard/domain_shard_mapper.h"
#include "shard/shard_domain_index.h"

#include <stdio.h>
#include <string.h>

#define EXPECT(cond, msg) do { \
    if (!(cond)) { \
        fprintf(stderr, "FAIL: %s\n", msg); \
        return 1; \
    } \
} while (0)

typedef struct test_sdf_sphere_ctx {
    dom_domain_point center;
    q16_16 radius;
} test_sdf_sphere_ctx;

typedef struct test_sdf_union_ctx {
    test_sdf_sphere_ctx a;
    test_sdf_sphere_ctx b;
} test_sdf_union_ctx;

typedef struct test_sdf_slab_ctx {
    q16_16 half_thickness;
    q16_16 half_span;
} test_sdf_slab_ctx;

static q16_16 test_abs_q16_16(q16_16 v)
{
    return (v < 0) ? (q16_16)-v : v;
}

static q16_16 test_max_q16_16(q16_16 a, q16_16 b)
{
    return (a > b) ? a : b;
}

static q16_16 test_sdf_l1_sphere(const void* ctx, const dom_domain_point* p)
{
    const test_sdf_sphere_ctx* c = (const test_sdf_sphere_ctx*)ctx;
    q16_16 dx = (q16_16)(p->x - c->center.x);
    q16_16 dy = (q16_16)(p->y - c->center.y);
    q16_16 dz = (q16_16)(p->z - c->center.z);
    dx = test_abs_q16_16(dx);
    dy = test_abs_q16_16(dy);
    dz = test_abs_q16_16(dz);
    return (q16_16)((dx + dy + dz) - c->radius);
}

static q16_16 test_sdf_union(const void* ctx, const dom_domain_point* p)
{
    const test_sdf_union_ctx* c = (const test_sdf_union_ctx*)ctx;
    q16_16 da = test_sdf_l1_sphere(&c->a, p);
    q16_16 db = test_sdf_l1_sphere(&c->b, p);
    return (da < db) ? da : db;
}

static q16_16 test_sdf_slab(const void* ctx, const dom_domain_point* p)
{
    const test_sdf_slab_ctx* c = (const test_sdf_slab_ctx*)ctx;
    q16_16 dx = (q16_16)(test_abs_q16_16(p->x) - c->half_thickness);
    q16_16 dy = (q16_16)(test_abs_q16_16(p->y) - c->half_span);
    q16_16 dz = (q16_16)(test_abs_q16_16(p->z) - c->half_span);
    return test_max_q16_16(dx, test_max_q16_16(dy, dz));
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
                              dom_domain_sdf_eval_fn eval,
                              void* ctx,
                              i32 bounds_extent)
{
    memset(source, 0, sizeof(*source));
    source->eval = eval;
    source->analytic_eval = eval;
    source->ctx = ctx;
    source->has_analytic = 1u;
    source->bounds.min = test_point_i32(-bounds_extent, -bounds_extent, -bounds_extent);
    source->bounds.max = test_point_i32(bounds_extent, bounds_extent, bounds_extent);
}

static void test_setup_volume(dom_domain_volume* volume,
                              dom_domain_sdf_source* source,
                              dom_domain_id id,
                              u32 version,
                              const dom_domain_policy* policy,
                              u32 existence_state,
                              u32 archival_state)
{
    dom_domain_volume_init(volume);
    volume->domain_id = id;
    dom_domain_volume_set_authoring_version(volume, version);
    dom_domain_volume_set_state(volume, existence_state, archival_state);
    dom_domain_volume_set_source(volume, source);
    if (policy) {
        dom_domain_volume_set_policy(volume, policy);
    }
}

static u32 test_count_domain(const dom_shard_domain_index* index, dom_domain_id domain_id)
{
    u32 i;
    u32 count = 0u;
    for (i = 0u; i < index->count; ++i) {
        if (index->assignments[i].domain_id == domain_id) {
            count += 1u;
        }
    }
    return count;
}

static int test_partition_deterministic(void)
{
    test_sdf_sphere_ctx ctx;
    dom_domain_sdf_source source;
    dom_domain_volume volume;
    dom_domain_policy policy;
    dom_domain_partition_params params;
    dom_domain_shard_input input;
    dom_shard_domain_assignment storage_a[256];
    dom_shard_domain_assignment storage_b[256];
    dom_shard_domain_index index_a;
    dom_shard_domain_index index_b;
    u32 i;
    int res_a;
    int res_b;

    ctx.center = test_point_i32(0, 0, 0);
    ctx.radius = d_q16_16_from_int(6);
    test_setup_source(&source, test_sdf_l1_sphere, &ctx, 16);

    dom_domain_policy_init(&policy);
    policy.tile_size = d_q16_16_from_int(4);
    test_setup_volume(&volume, &source, 101u, 1u, &policy,
                      DOM_DOMAIN_EXISTENCE_REALIZED, DOM_DOMAIN_ARCHIVAL_LIVE);

    input.domain_id = volume.domain_id;
    input.volume = &volume;
    input.flags = DOM_DOMAIN_SHARD_FLAG_ALLOW_SPLIT |
                  DOM_DOMAIN_SHARD_FLAG_ALLOW_STREAMING |
                  DOM_DOMAIN_SHARD_FLAG_ALLOW_SIMULATION;

    dom_domain_partition_params_init(&params);
    params.shard_count = 4u;
    params.allow_split = 1u;
    params.resolution = DOM_DOMAIN_RES_COARSE;
    params.max_tiles_per_domain = 0u;
    params.budget_units = 100000u;
    params.global_seed = 42u;

    dom_shard_domain_index_init(&index_a, storage_a, 256u);
    dom_shard_domain_index_init(&index_b, storage_b, 256u);

    res_a = dom_domain_shard_map(&input, 1u, &params, &index_a);
    res_b = dom_domain_shard_map(&input, 1u, &params, &index_b);

    EXPECT(res_a == 0 && res_b == 0, "partition should succeed");
    EXPECT(index_a.count == index_b.count, "deterministic count");
    EXPECT(index_a.uncertain == index_b.uncertain, "deterministic uncertain");
    for (i = 0u; i < index_a.count; ++i) {
        const dom_shard_domain_assignment* a = &index_a.assignments[i];
        const dom_shard_domain_assignment* b = &index_b.assignments[i];
        EXPECT(a->domain_id == b->domain_id, "domain id deterministic");
        EXPECT(a->tile_id == b->tile_id, "tile id deterministic");
        EXPECT(a->shard_id == b->shard_id, "shard id deterministic");
        EXPECT(a->flags == b->flags, "flags deterministic");
    }

    dom_domain_volume_free(&volume);
    return 0;
}

static int test_arbitrary_shapes(void)
{
    test_sdf_union_ctx union_ctx;
    test_sdf_slab_ctx slab_ctx;
    test_sdf_sphere_ctx outer_ctx;
    test_sdf_sphere_ctx inner_ctx;
    dom_domain_sdf_source union_source;
    dom_domain_sdf_source slab_source;
    dom_domain_sdf_source outer_source;
    dom_domain_sdf_source inner_source;
    dom_domain_volume volumes[4];
    dom_domain_policy policy;
    dom_domain_shard_input inputs[4];
    dom_domain_partition_params params;
    dom_shard_domain_assignment storage[512];
    dom_shard_domain_index index;
    u32 count_union;
    u32 count_slab;
    u32 count_outer;
    u32 count_inner;

    union_ctx.a.center = test_point_i32(-3, 0, 0);
    union_ctx.a.radius = d_q16_16_from_int(3);
    union_ctx.b.center = test_point_i32(3, 0, 0);
    union_ctx.b.radius = d_q16_16_from_int(3);
    slab_ctx.half_thickness = d_q16_16_from_int(1);
    slab_ctx.half_span = d_q16_16_from_int(6);
    outer_ctx.center = test_point_i32(0, 0, 0);
    outer_ctx.radius = d_q16_16_from_int(6);
    inner_ctx.center = test_point_i32(0, 0, 0);
    inner_ctx.radius = d_q16_16_from_int(3);

    test_setup_source(&union_source, test_sdf_union, &union_ctx, 8);
    test_setup_source(&slab_source, test_sdf_slab, &slab_ctx, 8);
    test_setup_source(&outer_source, test_sdf_l1_sphere, &outer_ctx, 8);
    test_setup_source(&inner_source, test_sdf_l1_sphere, &inner_ctx, 8);

    dom_domain_policy_init(&policy);
    policy.tile_size = d_q16_16_from_int(2);

    test_setup_volume(&volumes[0], &union_source, 201u, 1u, &policy,
                      DOM_DOMAIN_EXISTENCE_REALIZED, DOM_DOMAIN_ARCHIVAL_LIVE);
    test_setup_volume(&volumes[1], &slab_source, 202u, 1u, &policy,
                      DOM_DOMAIN_EXISTENCE_REALIZED, DOM_DOMAIN_ARCHIVAL_LIVE);
    test_setup_volume(&volumes[2], &outer_source, 203u, 1u, &policy,
                      DOM_DOMAIN_EXISTENCE_REALIZED, DOM_DOMAIN_ARCHIVAL_LIVE);
    test_setup_volume(&volumes[3], &inner_source, 204u, 1u, &policy,
                      DOM_DOMAIN_EXISTENCE_REALIZED, DOM_DOMAIN_ARCHIVAL_LIVE);

    inputs[0].domain_id = volumes[0].domain_id;
    inputs[0].volume = &volumes[0];
    inputs[0].flags = DOM_DOMAIN_SHARD_FLAG_ALLOW_SPLIT | DOM_DOMAIN_SHARD_FLAG_ALLOW_SIMULATION;
    inputs[1].domain_id = volumes[1].domain_id;
    inputs[1].volume = &volumes[1];
    inputs[1].flags = DOM_DOMAIN_SHARD_FLAG_ALLOW_SPLIT | DOM_DOMAIN_SHARD_FLAG_ALLOW_SIMULATION;
    inputs[2].domain_id = volumes[2].domain_id;
    inputs[2].volume = &volumes[2];
    inputs[2].flags = DOM_DOMAIN_SHARD_FLAG_ALLOW_SPLIT | DOM_DOMAIN_SHARD_FLAG_ALLOW_SIMULATION;
    inputs[3].domain_id = volumes[3].domain_id;
    inputs[3].volume = &volumes[3];
    inputs[3].flags = DOM_DOMAIN_SHARD_FLAG_ALLOW_SPLIT | DOM_DOMAIN_SHARD_FLAG_ALLOW_SIMULATION;

    dom_domain_partition_params_init(&params);
    params.shard_count = 3u;
    params.allow_split = 1u;
    params.resolution = DOM_DOMAIN_RES_COARSE;
    params.max_tiles_per_domain = 0u;
    params.budget_units = 100000u;
    params.global_seed = 7u;

    dom_shard_domain_index_init(&index, storage, 512u);

    EXPECT(dom_domain_shard_map(inputs, 4u, &params, &index) == 0, "map shapes");
    EXPECT(index.count > 0u, "index populated");

    count_union = test_count_domain(&index, volumes[0].domain_id);
    count_slab = test_count_domain(&index, volumes[1].domain_id);
    count_outer = test_count_domain(&index, volumes[2].domain_id);
    count_inner = test_count_domain(&index, volumes[3].domain_id);
    EXPECT(count_union > 0u, "non-convex domain mapped");
    EXPECT(count_slab > 0u, "thin domain mapped");
    EXPECT(count_outer > 0u, "outer domain mapped");
    EXPECT(count_inner > 0u, "inner domain mapped");

    dom_domain_volume_free(&volumes[0]);
    dom_domain_volume_free(&volumes[1]);
    dom_domain_volume_free(&volumes[2]);
    dom_domain_volume_free(&volumes[3]);
    return 0;
}

static int test_ownership_exclusivity(void)
{
    test_sdf_sphere_ctx ctx;
    dom_domain_sdf_source source;
    dom_domain_volume volume;
    dom_domain_policy policy;
    dom_domain_shard_input input;
    dom_domain_partition_params params;
    dom_shard_domain_assignment storage[256];
    dom_shard_domain_index index;
    u32 i;
    u32 j;

    ctx.center = test_point_i32(0, 0, 0);
    ctx.radius = d_q16_16_from_int(6);
    test_setup_source(&source, test_sdf_l1_sphere, &ctx, 16);

    dom_domain_policy_init(&policy);
    policy.tile_size = d_q16_16_from_int(4);
    test_setup_volume(&volume, &source, 301u, 1u, &policy,
                      DOM_DOMAIN_EXISTENCE_REALIZED, DOM_DOMAIN_ARCHIVAL_LIVE);

    input.domain_id = volume.domain_id;
    input.volume = &volume;
    input.flags = DOM_DOMAIN_SHARD_FLAG_ALLOW_SPLIT | DOM_DOMAIN_SHARD_FLAG_ALLOW_SIMULATION;

    dom_domain_partition_params_init(&params);
    params.shard_count = 4u;
    params.allow_split = 1u;
    params.resolution = DOM_DOMAIN_RES_COARSE;
    params.max_tiles_per_domain = 0u;
    params.budget_units = 100000u;
    params.global_seed = 11u;

    dom_shard_domain_index_init(&index, storage, 256u);
    EXPECT(dom_domain_shard_map(&input, 1u, &params, &index) == 0, "map domain");

    for (i = 0u; i < index.count; ++i) {
        for (j = i + 1u; j < index.count; ++j) {
            const dom_shard_domain_assignment* a = &index.assignments[i];
            const dom_shard_domain_assignment* b = &index.assignments[j];
            if (a->domain_id == b->domain_id && a->tile_id == b->tile_id) {
                EXPECT(a->shard_id == b->shard_id, "duplicate tile ownership");
            }
        }
    }

    dom_domain_volume_free(&volume);
    return 0;
}

static int test_streaming_restriction(void)
{
    test_sdf_sphere_ctx ctx;
    dom_domain_sdf_source source;
    dom_domain_volume live_volume;
    dom_domain_volume frozen_volume;
    dom_domain_policy policy;
    dom_domain_shard_input inputs[2];
    dom_domain_partition_params params;
    dom_shard_domain_assignment storage[256];
    dom_shard_domain_index index;
    u32 i;
    u32 live_ok = 0u;
    u32 frozen_stream = 0u;
    u32 frozen_sim = 0u;

    ctx.center = test_point_i32(0, 0, 0);
    ctx.radius = d_q16_16_from_int(6);
    test_setup_source(&source, test_sdf_l1_sphere, &ctx, 16);

    dom_domain_policy_init(&policy);
    policy.tile_size = d_q16_16_from_int(4);
    test_setup_volume(&live_volume, &source, 401u, 1u, &policy,
                      DOM_DOMAIN_EXISTENCE_REALIZED, DOM_DOMAIN_ARCHIVAL_LIVE);
    test_setup_volume(&frozen_volume, &source, 402u, 1u, &policy,
                      DOM_DOMAIN_EXISTENCE_REALIZED, DOM_DOMAIN_ARCHIVAL_FROZEN);

    inputs[0].domain_id = live_volume.domain_id;
    inputs[0].volume = &live_volume;
    inputs[0].flags = DOM_DOMAIN_SHARD_FLAG_ALLOW_SPLIT |
                      DOM_DOMAIN_SHARD_FLAG_ALLOW_STREAMING |
                      DOM_DOMAIN_SHARD_FLAG_ALLOW_SIMULATION;
    inputs[1].domain_id = frozen_volume.domain_id;
    inputs[1].volume = &frozen_volume;
    inputs[1].flags = DOM_DOMAIN_SHARD_FLAG_ALLOW_SPLIT |
                      DOM_DOMAIN_SHARD_FLAG_ALLOW_STREAMING |
                      DOM_DOMAIN_SHARD_FLAG_ALLOW_SIMULATION;

    dom_domain_partition_params_init(&params);
    params.shard_count = 2u;
    params.allow_split = 1u;
    params.resolution = DOM_DOMAIN_RES_COARSE;
    params.max_tiles_per_domain = 0u;
    params.budget_units = 100000u;
    params.global_seed = 9u;

    dom_shard_domain_index_init(&index, storage, 256u);
    EXPECT(dom_domain_shard_map(inputs, 2u, &params, &index) == 0, "map streaming restriction");

    for (i = 0u; i < index.count; ++i) {
        const dom_shard_domain_assignment* assignment = &index.assignments[i];
        if (assignment->domain_id == live_volume.domain_id) {
            if (assignment->flags & DOM_SHARD_DOMAIN_FLAG_STREAMING_ALLOWED) {
                live_ok += 1u;
            }
        } else if (assignment->domain_id == frozen_volume.domain_id) {
            if (assignment->flags & DOM_SHARD_DOMAIN_FLAG_STREAMING_ALLOWED) {
                frozen_stream += 1u;
            }
            if (assignment->flags & DOM_SHARD_DOMAIN_FLAG_SIMULATION_ALLOWED) {
                frozen_sim += 1u;
            }
        }
    }

    EXPECT(live_ok > 0u, "live domain streaming allowed");
    EXPECT(frozen_stream == 0u, "frozen domain streaming denied");
    EXPECT(frozen_sim == 0u, "frozen domain simulation denied");

    dom_domain_volume_free(&live_volume);
    dom_domain_volume_free(&frozen_volume);
    return 0;
}

int main(void)
{
    if (test_partition_deterministic() != 0) return 1;
    if (test_arbitrary_shapes() != 0) return 1;
    if (test_ownership_exclusivity() != 0) return 1;
    if (test_streaming_restriction() != 0) return 1;
    return 0;
}
