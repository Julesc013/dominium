/*
FILE: source/domino/world/domain_query.cpp
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / world/domain_query
RESPONSIBILITY: Implements deterministic domain queries with budgeted degradation.
ALLOWED DEPENDENCIES: `include/domino/**` and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: Engine private headers outside world.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: Fixed-point math, deterministic ladder.
*/
#include "domino/world/domain_query.h"
#include "domino/world/domain_cache.h"

#include <string.h>

static d_bool dom_domain_volume_is_active(const dom_domain_volume* volume)
{
    if (!volume) {
        return D_FALSE;
    }
    if (volume->existence_state == DOM_DOMAIN_EXISTENCE_NONEXISTENT ||
        volume->existence_state == DOM_DOMAIN_EXISTENCE_DECLARED) {
        return D_FALSE;
    }
    return D_TRUE;
}

void dom_domain_budget_init(dom_domain_budget* budget, u32 max_units)
{
    if (!budget) {
        return;
    }
    budget->max_units = max_units;
    budget->used_units = 0u;
}

d_bool dom_domain_budget_consume(dom_domain_budget* budget, u32 cost_units)
{
    u64 remaining;
    if (!budget) {
        return D_TRUE;
    }
    if (budget->used_units > budget->max_units) {
        return D_FALSE;
    }
    remaining = (u64)budget->max_units - (u64)budget->used_units;
    if ((u64)cost_units > remaining) {
        return D_FALSE;
    }
    budget->used_units += cost_units;
    return D_TRUE;
}

static void dom_domain_query_meta_refused(dom_domain_query_meta* meta,
                                          u32 reason,
                                          const dom_domain_budget* budget)
{
    if (!meta) {
        return;
    }
    memset(meta, 0, sizeof(*meta));
    meta->status = DOM_DOMAIN_QUERY_REFUSED;
    meta->resolution = DOM_DOMAIN_RES_REFUSED;
    meta->confidence = DOM_DOMAIN_CONFIDENCE_UNKNOWN;
    meta->refusal_reason = reason;
    if (budget) {
        meta->budget_used = budget->used_units;
        meta->budget_max = budget->max_units;
    }
}

static void dom_domain_query_meta_ok(dom_domain_query_meta* meta,
                                     u32 resolution,
                                     u32 confidence,
                                     u32 cost_units,
                                     const dom_domain_budget* budget)
{
    if (!meta) {
        return;
    }
    memset(meta, 0, sizeof(*meta));
    meta->status = DOM_DOMAIN_QUERY_OK;
    meta->resolution = resolution;
    meta->confidence = confidence;
    meta->refusal_reason = DOM_DOMAIN_REFUSE_NONE;
    meta->cost_units = cost_units;
    if (budget) {
        meta->budget_used = budget->used_units;
        meta->budget_max = budget->max_units;
    }
}

static d_bool dom_domain_resolution_allowed(u32 max_resolution, u32 resolution)
{
    if (max_resolution == DOM_DOMAIN_RES_FULL) {
        return D_TRUE;
    }
    if (max_resolution == DOM_DOMAIN_RES_MEDIUM) {
        return resolution != DOM_DOMAIN_RES_FULL;
    }
    if (max_resolution == DOM_DOMAIN_RES_COARSE) {
        return resolution == DOM_DOMAIN_RES_COARSE || resolution == DOM_DOMAIN_RES_ANALYTIC;
    }
    if (max_resolution == DOM_DOMAIN_RES_ANALYTIC) {
        return resolution == DOM_DOMAIN_RES_ANALYTIC;
    }
    return resolution == DOM_DOMAIN_RES_ANALYTIC;
}

static u32 dom_domain_sample_dim_for_resolution(const dom_domain_volume* volume, u32 resolution)
{
    if (!volume) {
        return 0u;
    }
    switch (resolution) {
        case DOM_DOMAIN_RES_FULL: return volume->policy.sample_dim_full;
        case DOM_DOMAIN_RES_MEDIUM: return volume->policy.sample_dim_medium;
        case DOM_DOMAIN_RES_COARSE: return volume->policy.sample_dim_coarse;
        default: break;
    }
    return 0u;
}

static i32 dom_domain_floor_div_q16_16(i64 numer, q16_16 denom)
{
    i64 d = (i64)denom;
    i64 q;
    if (d == 0) {
        return 0;
    }
    if (numer >= 0) {
        return (i32)(numer / d);
    }
    q = (-numer) / d;
    if ((-numer) % d) {
        q += 1;
    }
    return (i32)(-q);
}

static q16_16 dom_domain_mul_i32_q16_16(i32 a, q16_16 b)
{
    i64 v = (i64)a * (i64)b;
    if (v > 2147483647LL) {
        return (q16_16)2147483647;
    }
    if (v < -2147483647LL - 1LL) {
        return (q16_16)(-2147483647LL - 1LL);
    }
    return (q16_16)v;
}

static void dom_domain_make_tile_bounds(const dom_domain_aabb* bounds,
                                        q16_16 tile_size,
                                        i32 tx,
                                        i32 ty,
                                        i32 tz,
                                        dom_domain_aabb* out_bounds)
{
    dom_domain_point minp;
    dom_domain_point maxp;
    minp.x = (q16_16)(bounds->min.x + dom_domain_mul_i32_q16_16(tx, tile_size));
    minp.y = (q16_16)(bounds->min.y + dom_domain_mul_i32_q16_16(ty, tile_size));
    minp.z = (q16_16)(bounds->min.z + dom_domain_mul_i32_q16_16(tz, tile_size));

    maxp.x = (q16_16)(minp.x + tile_size);
    maxp.y = (q16_16)(minp.y + tile_size);
    maxp.z = (q16_16)(minp.z + tile_size);

    if (maxp.x > bounds->max.x) {
        maxp.x = bounds->max.x;
    }
    if (maxp.y > bounds->max.y) {
        maxp.y = bounds->max.y;
    }
    if (maxp.z > bounds->max.z) {
        maxp.z = bounds->max.z;
    }

    if (minp.x < bounds->min.x) {
        minp.x = bounds->min.x;
    }
    if (minp.y < bounds->min.y) {
        minp.y = bounds->min.y;
    }
    if (minp.z < bounds->min.z) {
        minp.z = bounds->min.z;
    }

    out_bounds->min = minp;
    out_bounds->max = maxp;
}

static int dom_domain_build_tile_desc(const dom_domain_volume* volume,
                                      const dom_domain_point* point,
                                      u32 resolution,
                                      dom_domain_tile_desc* out_desc)
{
    i32 tx;
    i32 ty;
    i32 tz;
    q16_16 tile_size;
    u32 sample_dim;
    if (!volume || !volume->source || !out_desc || !point) {
        return -1;
    }
    tile_size = volume->policy.tile_size;
    if (tile_size <= 0) {
        return -1;
    }
    sample_dim = dom_domain_sample_dim_for_resolution(volume, resolution);
    if (sample_dim == 0u) {
        return -1;
    }

    tx = dom_domain_floor_div_q16_16((i64)point->x - (i64)volume->source->bounds.min.x, tile_size);
    ty = dom_domain_floor_div_q16_16((i64)point->y - (i64)volume->source->bounds.min.y, tile_size);
    tz = dom_domain_floor_div_q16_16((i64)point->z - (i64)volume->source->bounds.min.z, tile_size);

    dom_domain_tile_desc_init(out_desc);
    out_desc->resolution = resolution;
    out_desc->sample_dim = sample_dim;
    out_desc->tile_id = dom_domain_tile_id_from_coord(tx, ty, tz, resolution);
    out_desc->authoring_version = volume->authoring_version;
    dom_domain_make_tile_bounds(&volume->source->bounds, tile_size, tx, ty, tz, &out_desc->bounds);
    return 0;
}

static const dom_domain_tile* dom_domain_local_tile_get(dom_domain_volume* volume,
                                                       const dom_domain_tile_desc* desc,
                                                       d_bool allow_build)
{
    u32 idx;
    dom_domain_tile* tile;
    if (!volume || !desc || !volume->source) {
        return (const dom_domain_tile *)0;
    }
    if (desc->resolution == DOM_DOMAIN_RES_FULL) {
        idx = 0u;
    } else if (desc->resolution == DOM_DOMAIN_RES_MEDIUM) {
        idx = 1u;
    } else {
        idx = 2u;
    }
    if (idx >= DOM_DOMAIN_LOCAL_TILE_SLOTS) {
        return (const dom_domain_tile *)0;
    }

    if (volume->local_tile_valid[idx] &&
        volume->local_tile_ids[idx] == desc->tile_id &&
        volume->local_tile_versions[idx] == desc->authoring_version &&
        volume->local_tiles[idx].sample_dim == desc->sample_dim) {
        return &volume->local_tiles[idx];
    }

    if (!allow_build) {
        return (const dom_domain_tile *)0;
    }

    tile = &volume->local_tiles[idx];
    dom_domain_tile_free(tile);
    dom_domain_tile_init(tile);
    if (dom_domain_tile_build(tile, desc, volume->source) != 0) {
        return (const dom_domain_tile *)0;
    }
    volume->local_tile_valid[idx] = D_TRUE;
    volume->local_tile_ids[idx] = desc->tile_id;
    volume->local_tile_versions[idx] = desc->authoring_version;
    return tile;
}

static d_bool dom_domain_tile_cached(dom_domain_volume* volume, const dom_domain_tile_desc* desc)
{
    if (!volume || !desc) {
        return D_FALSE;
    }
    if (volume->cache) {
        return dom_domain_cache_peek(volume->cache, volume->domain_id, desc->tile_id,
                                     desc->resolution, desc->authoring_version) != (const dom_domain_tile *)0;
    }
    return dom_domain_local_tile_get(volume, desc, D_FALSE) != (const dom_domain_tile *)0;
}

static const dom_domain_tile* dom_domain_tile_get(dom_domain_volume* volume,
                                                  const dom_domain_tile_desc* desc,
                                                  d_bool allow_build)
{
    if (!volume || !desc) {
        return (const dom_domain_tile *)0;
    }
    if (volume->cache) {
        const dom_domain_tile* cached = dom_domain_cache_get(volume->cache, volume->domain_id,
                                                             desc->tile_id, desc->resolution,
                                                             desc->authoring_version);
        if (cached) {
            return cached;
        }
        if (!allow_build) {
            return (const dom_domain_tile *)0;
        }
        if (volume->source) {
            dom_domain_tile temp;
            dom_domain_tile_init(&temp);
            if (dom_domain_tile_build(&temp, desc, volume->source) != 0) {
                dom_domain_tile_free(&temp);
                return (const dom_domain_tile *)0;
            }
            cached = dom_domain_cache_put(volume->cache, volume->domain_id, &temp);
            if (!cached) {
                dom_domain_tile_free(&temp);
                return (const dom_domain_tile *)0;
            }
            return cached;
        }
        return (const dom_domain_tile *)0;
    }
    return dom_domain_local_tile_get(volume, desc, allow_build);
}

static q16_16 dom_domain_l1_distance(const dom_domain_point* a, const dom_domain_point* b)
{
    q16_16 dx;
    q16_16 dy;
    q16_16 dz;
    i64 sum;
    dx = (q16_16)(a->x - b->x);
    dy = (q16_16)(a->y - b->y);
    dz = (q16_16)(a->z - b->z);
    if (dx < 0) dx = (q16_16)-dx;
    if (dy < 0) dy = (q16_16)-dy;
    if (dz < 0) dz = (q16_16)-dz;
    sum = (i64)dx + (i64)dy + (i64)dz;
    if (sum > 2147483647LL) {
        return (q16_16)2147483647;
    }
    return (q16_16)sum;
}

typedef struct dom_domain_eval_result {
    dom_domain_point sample_point;
    q16_16 distance;
    dom_domain_query_meta meta;
} dom_domain_eval_result;

static dom_domain_eval_result dom_domain_eval_distance(const dom_domain_volume* volume,
                                                       const dom_domain_point* point,
                                                       dom_domain_budget* budget)
{
    dom_domain_eval_result result;
    dom_domain_tile_desc desc;
    const dom_domain_tile* tile;
    q16_16 distance;
    u32 cost;
    memset(&result, 0, sizeof(result));

    if (!volume || !point) {
        dom_domain_query_meta_refused(&result.meta, DOM_DOMAIN_REFUSE_INTERNAL, budget);
        return result;
    }
    if (!dom_domain_volume_is_active(volume)) {
        dom_domain_query_meta_refused(&result.meta, DOM_DOMAIN_REFUSE_DOMAIN_INACTIVE, budget);
        return result;
    }
    if (!volume->source || !volume->source->eval) {
        dom_domain_query_meta_refused(&result.meta, DOM_DOMAIN_REFUSE_NO_SOURCE, budget);
        return result;
    }

    if (!dom_domain_aabb_contains(&volume->source->bounds, point)) {
        distance = dom_domain_aabb_distance_l1(&volume->source->bounds, point);
        result.distance = distance;
        result.sample_point = *point;
        dom_domain_query_meta_ok(&result.meta, DOM_DOMAIN_RES_COARSE,
                                 DOM_DOMAIN_CONFIDENCE_LOWER_BOUND, 0u, budget);
        return result;
    }

    if (dom_domain_resolution_allowed(volume->policy.max_resolution, DOM_DOMAIN_RES_FULL)) {
        cost = volume->policy.cost_full;
        if (dom_domain_budget_consume(budget, cost)) {
            result.sample_point = *point;
            result.distance = volume->source->eval(volume->source->ctx, point);
            dom_domain_query_meta_ok(&result.meta, DOM_DOMAIN_RES_FULL,
                                     DOM_DOMAIN_CONFIDENCE_EXACT, cost, budget);
            return result;
        }
    }

    if (dom_domain_resolution_allowed(volume->policy.max_resolution, DOM_DOMAIN_RES_MEDIUM)) {
        cost = volume->policy.cost_medium;
        if (dom_domain_build_tile_desc(volume, point, DOM_DOMAIN_RES_MEDIUM, &desc) == 0) {
            if (!dom_domain_tile_cached((dom_domain_volume *)volume, &desc)) {
                cost += volume->policy.tile_build_cost_medium;
            }
            if (dom_domain_budget_consume(budget, cost)) {
                tile = dom_domain_tile_get((dom_domain_volume *)volume, &desc, D_TRUE);
                if (tile) {
                    dom_domain_point sample_point;
                    q16_16 sample = dom_domain_tile_sample_nearest(tile, point, &sample_point);
                    q16_16 l1 = dom_domain_l1_distance(point, &sample_point);
                    result.sample_point = sample_point;
                    result.distance = (q16_16)(sample - l1);
                    dom_domain_query_meta_ok(&result.meta, DOM_DOMAIN_RES_MEDIUM,
                                             DOM_DOMAIN_CONFIDENCE_LOWER_BOUND, cost, budget);
                    return result;
                }
                dom_domain_query_meta_refused(&result.meta, DOM_DOMAIN_REFUSE_INTERNAL, budget);
                return result;
            }
        }
    }

    if (dom_domain_resolution_allowed(volume->policy.max_resolution, DOM_DOMAIN_RES_COARSE)) {
        cost = volume->policy.cost_coarse;
        if (dom_domain_build_tile_desc(volume, point, DOM_DOMAIN_RES_COARSE, &desc) == 0) {
            if (!dom_domain_tile_cached((dom_domain_volume *)volume, &desc)) {
                cost += volume->policy.tile_build_cost_coarse;
            }
            if (dom_domain_budget_consume(budget, cost)) {
                tile = dom_domain_tile_get((dom_domain_volume *)volume, &desc, D_TRUE);
                if (tile) {
                    dom_domain_point sample_point;
                    q16_16 sample = dom_domain_tile_sample_nearest(tile, point, &sample_point);
                    q16_16 l1 = dom_domain_l1_distance(point, &sample_point);
                    result.sample_point = sample_point;
                    result.distance = (q16_16)(sample - l1);
                    dom_domain_query_meta_ok(&result.meta, DOM_DOMAIN_RES_COARSE,
                                             DOM_DOMAIN_CONFIDENCE_LOWER_BOUND, cost, budget);
                    return result;
                }
                dom_domain_query_meta_refused(&result.meta, DOM_DOMAIN_REFUSE_INTERNAL, budget);
                return result;
            }
        }
    }

    if (dom_domain_resolution_allowed(volume->policy.max_resolution, DOM_DOMAIN_RES_ANALYTIC)) {
        if (!volume->source->has_analytic || !volume->source->analytic_eval) {
            dom_domain_query_meta_refused(&result.meta, DOM_DOMAIN_REFUSE_NO_ANALYTIC, budget);
            return result;
        }
        cost = volume->policy.cost_analytic;
        if (dom_domain_budget_consume(budget, cost)) {
            result.sample_point = *point;
            result.distance = volume->source->analytic_eval(volume->source->ctx, point);
            dom_domain_query_meta_ok(&result.meta, DOM_DOMAIN_RES_ANALYTIC,
                                     DOM_DOMAIN_CONFIDENCE_EXACT, cost, budget);
            return result;
        }
    }

    dom_domain_query_meta_refused(&result.meta, DOM_DOMAIN_REFUSE_BUDGET, budget);
    return result;
}

d_bool dom_domain_contains(const dom_domain_volume* volume,
                           const dom_domain_point* point,
                           dom_domain_budget* budget,
                           dom_domain_query_meta* out_meta)
{
    dom_domain_eval_result eval = dom_domain_eval_distance(volume, point, budget);
    if (out_meta) {
        *out_meta = eval.meta;
    }
    if (eval.meta.status != DOM_DOMAIN_QUERY_OK) {
        return D_FALSE;
    }
    if (eval.meta.confidence != DOM_DOMAIN_CONFIDENCE_EXACT) {
        return D_FALSE;
    }
    return (eval.distance <= 0) ? D_TRUE : D_FALSE;
}

dom_domain_distance_result dom_domain_distance(const dom_domain_volume* volume,
                                               const dom_domain_point* point,
                                               dom_domain_budget* budget)
{
    dom_domain_eval_result eval = dom_domain_eval_distance(volume, point, budget);
    dom_domain_distance_result out;
    out.distance = eval.distance;
    out.meta = eval.meta;
    return out;
}

dom_domain_closest_point_result dom_domain_closest_point(const dom_domain_volume* volume,
                                                         const dom_domain_point* point,
                                                         dom_domain_budget* budget)
{
    dom_domain_eval_result eval = dom_domain_eval_distance(volume, point, budget);
    dom_domain_closest_point_result out;
    out.point = eval.sample_point;
    out.distance = eval.distance;
    out.meta = eval.meta;
    return out;
}

static dom_domain_point dom_domain_ray_point(const dom_domain_ray* ray, q16_16 t)
{
    dom_domain_point p;
    p.x = d_q16_16_add(ray->origin.x, d_q16_16_mul(ray->direction.x, t));
    p.y = d_q16_16_add(ray->origin.y, d_q16_16_mul(ray->direction.y, t));
    p.z = d_q16_16_add(ray->origin.z, d_q16_16_mul(ray->direction.z, t));
    return p;
}

dom_domain_ray_hit_result dom_domain_ray_intersect(const dom_domain_volume* volume,
                                                   const dom_domain_ray* ray,
                                                   dom_domain_budget* budget)
{
    dom_domain_ray_hit_result out;
    u32 steps;
    q16_16 t;
    q16_16 max_distance;
    q16_16 step;
    dom_domain_point p;
    dom_domain_eval_result eval;

    memset(&out, 0, sizeof(out));
    if (!volume || !ray) {
        dom_domain_query_meta_refused(&out.meta, DOM_DOMAIN_REFUSE_INTERNAL, budget);
        return out;
    }

    max_distance = ray->max_distance;
    if (max_distance <= 0) {
        max_distance = d_q16_16_from_int(1);
    }

    step = volume->policy.ray_step;
    if (step <= 0) {
        step = d_q16_16_from_int(1);
    }

    steps = volume->policy.max_ray_steps;
    if (steps == 0u) {
        steps = 1u;
    }

    t = 0;
    for (steps = volume->policy.max_ray_steps; steps > 0u; --steps) {
        if (t > max_distance) {
            break;
        }
        p = dom_domain_ray_point(ray, t);
        eval = dom_domain_eval_distance(volume, &p, budget);
        out.meta = eval.meta;
        if (eval.meta.status != DOM_DOMAIN_QUERY_OK) {
            out.hit = D_FALSE;
            return out;
        }
        if (eval.meta.confidence == DOM_DOMAIN_CONFIDENCE_EXACT && eval.distance <= 0) {
            out.hit = D_TRUE;
            out.point = p;
            out.distance = t;
            return out;
        }
        t = d_q16_16_add(t, step);
    }

    out.hit = D_FALSE;
    return out;
}
