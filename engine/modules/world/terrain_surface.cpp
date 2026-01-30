/*
FILE: source/domino/world/terrain_surface.cpp
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / world/terrain_surface
RESPONSIBILITY: Implements deterministic terrain surface sampling and helpers.
ALLOWED DEPENDENCIES: `include/domino/**` and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: Engine private headers outside world.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: Fixed-point only; deterministic ordering and math.
*/
#include "domino/world/terrain_surface.h"

#include "domino/core/dom_deterministic_math.h"
#include "domino/core/fixed_math.h"
#include "domino/core/rng_model.h"

#include <string.h>

static q16_16 dom_terrain_abs_q16_16(q16_16 v)
{
    return (v < 0) ? (q16_16)-v : v;
}

static q16_16 dom_terrain_clamp_q16_16(q16_16 v, q16_16 lo, q16_16 hi)
{
    if (v < lo) {
        return lo;
    }
    if (v > hi) {
        return hi;
    }
    return v;
}

static u64 dom_terrain_noise_seed(const dom_terrain_surface_desc* desc)
{
    const char* stream = "noise.stream.terrain.surface.base";
    u64 base_seed;
    if (!desc) {
        return 0u;
    }
    D_DET_GUARD_RNG_STREAM_NAME(stream);
    base_seed = desc->world_seed ^ desc->noise.seed;
    return (u64)d_rng_seed_from_context(base_seed,
                                        desc->domain_id,
                                        0u,
                                        0u,
                                        stream,
                                        D_RNG_MIX_DOMAIN | D_RNG_MIX_STREAM);
}

static u32 dom_terrain_hash_u32(u64 seed, i32 x, i32 y, i32 z)
{
    u32 h = (u32)(seed ^ (seed >> 32));
    h ^= (u32)x * 0x9e3779b9u;
    h ^= (u32)y * 0x85ebca6bu;
    h ^= (u32)z * 0xc2b2ae35u;
    h ^= h >> 16;
    h *= 0x7feb352du;
    h ^= h >> 15;
    h *= 0x846ca68bu;
    h ^= h >> 16;
    return h;
}

static i32 dom_terrain_floor_div_q16(q16_16 value, q16_16 denom)
{
    i64 v = (i64)value;
    i64 d = (i64)denom;
    i64 q;
    if (d == 0) {
        return 0;
    }
    if (v >= 0) {
        return (i32)(v / d);
    }
    q = (-v) / d;
    if ((-v) % d) {
        q += 1;
    }
    return (i32)(-q);
}

static q16_16 dom_terrain_noise_sample(const dom_terrain_surface* surface,
                                       const dom_domain_point* point)
{
    i32 gx;
    i32 gy;
    i32 gz;
    u32 h;
    i32 sample;
    i64 scaled;
    q16_16 cell_size;
    if (!surface || !point) {
        return 0;
    }
    if (surface->noise.amplitude == 0) {
        return 0;
    }
    cell_size = surface->noise.cell_size;
    if (cell_size <= 0) {
        cell_size = d_q16_16_from_int(1);
    }
    gx = dom_terrain_floor_div_q16(point->x, cell_size);
    gy = dom_terrain_floor_div_q16(point->y, cell_size);
    gz = dom_terrain_floor_div_q16(point->z, cell_size);
    h = dom_terrain_hash_u32(surface->noise.seed, gx, gy, gz);
    sample = (i32)(h & 0xFFFFu);
    sample -= 32768;
    scaled = (i64)sample * (i64)surface->noise.amplitude;
    scaled /= 32768;
    if (scaled > 2147483647LL) {
        scaled = 2147483647LL;
    } else if (scaled < -2147483647LL - 1LL) {
        scaled = -2147483647LL - 1LL;
    }
    return (q16_16)scaled;
}

static q16_16 dom_terrain_sdf_sphere(const dom_terrain_surface* surface,
                                     const dom_domain_point* point)
{
    q16_16 xx = d_q16_16_mul(point->x, point->x);
    q16_16 yy = d_q16_16_mul(point->y, point->y);
    q16_16 zz = d_q16_16_mul(point->z, point->z);
    q16_16 sum = d_q16_16_add(d_q16_16_add(xx, yy), zz);
    q16_16 radius = surface->shape.radius_equatorial;
    q16_16 dist = d_fixed_sqrt_q16_16(sum);
    return (q16_16)(dist - radius);
}

static q16_16 dom_terrain_sdf_oblate(const dom_terrain_surface* surface,
                                     const dom_domain_point* point)
{
    q16_16 a = surface->shape.radius_equatorial;
    q16_16 c = surface->shape.radius_polar;
    q16_16 nx;
    q16_16 ny;
    q16_16 nz;
    q16_16 sum;
    q16_16 scale;
    if (c == 0) {
        c = a;
    }
    if (a == 0) {
        return 0;
    }
    nx = d_fixed_div_q16_16(point->x, a);
    ny = d_fixed_div_q16_16(point->y, a);
    nz = d_fixed_div_q16_16(point->z, c);
    sum = d_q16_16_add(d_q16_16_add(d_q16_16_mul(nx, nx),
                                   d_q16_16_mul(ny, ny)),
                       d_q16_16_mul(nz, nz));
    scale = (a < c) ? a : c;
    return d_q16_16_mul(d_q16_16_sub(d_fixed_sqrt_q16_16(sum), d_q16_16_from_int(1)), scale);
}

static q16_16 dom_terrain_sdf_slab(const dom_terrain_surface* surface,
                                   const dom_domain_point* point)
{
    q16_16 half_thickness = surface->shape.slab_half_thickness;
    q16_16 dz = dom_terrain_abs_q16_16(point->z);
    return (q16_16)(dz - half_thickness);
}

static q16_16 dom_terrain_surface_eval(const void* ctx, const dom_domain_point* point)
{
    const dom_terrain_surface* surface = (const dom_terrain_surface*)ctx;
    q16_16 phi = 0;
    if (!surface || !point) {
        return 0;
    }
    switch (surface->shape.kind) {
        case DOM_TERRAIN_SHAPE_OBLATE:
            phi = dom_terrain_sdf_oblate(surface, point);
            break;
        case DOM_TERRAIN_SHAPE_SLAB:
            phi = dom_terrain_sdf_slab(surface, point);
            break;
        case DOM_TERRAIN_SHAPE_SPHERE:
        default:
            phi = dom_terrain_sdf_sphere(surface, point);
            break;
    }
    phi = d_q16_16_add(phi, dom_terrain_noise_sample(surface, point));
    return phi;
}

static q16_16 dom_terrain_surface_eval_analytic(const void* ctx, const dom_domain_point* point)
{
    const dom_terrain_surface* surface = (const dom_terrain_surface*)ctx;
    if (!surface || !point) {
        return 0;
    }
    switch (surface->shape.kind) {
        case DOM_TERRAIN_SHAPE_OBLATE:
            return dom_terrain_sdf_oblate(surface, point);
        case DOM_TERRAIN_SHAPE_SLAB:
            return dom_terrain_sdf_slab(surface, point);
        case DOM_TERRAIN_SHAPE_SPHERE:
        default:
            return dom_terrain_sdf_sphere(surface, point);
    }
}

static void dom_terrain_surface_bounds(dom_terrain_surface* surface)
{
    q16_16 extent = 0;
    q16_16 noise = surface->noise.amplitude;
    if (noise < 0) {
        noise = (q16_16)-noise;
    }
    if (surface->shape.kind == DOM_TERRAIN_SHAPE_SLAB) {
        extent = surface->shape.slab_half_extent;
        if (extent <= 0) {
            extent = d_q16_16_from_int(1024);
        }
        surface->sdf_source.bounds.min.x = (q16_16)(-extent);
        surface->sdf_source.bounds.max.x = extent;
        surface->sdf_source.bounds.min.y = (q16_16)(-extent);
        surface->sdf_source.bounds.max.y = extent;
        surface->sdf_source.bounds.min.z = (q16_16)(-surface->shape.slab_half_thickness - noise);
        surface->sdf_source.bounds.max.z = (q16_16)(surface->shape.slab_half_thickness + noise);
    } else {
        q16_16 radius = surface->shape.radius_equatorial;
        q16_16 pole = surface->shape.radius_polar;
        if (pole == 0) {
            pole = radius;
        }
        extent = (radius > pole) ? radius : pole;
        extent = (q16_16)(extent + noise);
        surface->sdf_source.bounds.min.x = (q16_16)(-extent);
        surface->sdf_source.bounds.max.x = extent;
        surface->sdf_source.bounds.min.y = (q16_16)(-extent);
        surface->sdf_source.bounds.max.y = extent;
        surface->sdf_source.bounds.min.z = (q16_16)(-extent);
        surface->sdf_source.bounds.max.z = extent;
    }
}

void dom_terrain_surface_desc_init(dom_terrain_surface_desc* desc)
{
    if (!desc) {
        return;
    }
    memset(desc, 0, sizeof(*desc));
    desc->shape.kind = DOM_TERRAIN_SHAPE_SPHERE;
    desc->meters_per_unit = d_q16_16_from_int(1);
    desc->shape.radius_equatorial = d_q16_16_from_int(512);
    desc->shape.radius_polar = d_q16_16_from_int(512);
    desc->shape.slab_half_extent = d_q16_16_from_int(512);
    desc->shape.slab_half_thickness = d_q16_16_from_int(16);
    desc->noise.cell_size = d_q16_16_from_int(16);
    desc->material_primary = 1u;
    desc->roughness_base = 0;
    desc->travel_cost_base = d_q16_16_from_int(1);
    desc->travel_cost_slope_scale = d_q16_16_from_int(1);
    desc->travel_cost_roughness_scale = d_q16_16_from_int(1);
    desc->walkable_max_slope = d_q16_16_from_int(1);
}

void dom_terrain_surface_init(dom_terrain_surface* surface, const dom_terrain_surface_desc* desc)
{
    if (!surface || !desc) {
        return;
    }
    memset(surface, 0, sizeof(*surface));
    surface->domain_id = desc->domain_id;
    surface->world_seed = desc->world_seed;
    surface->meters_per_unit = desc->meters_per_unit;
    surface->shape = desc->shape;
    surface->noise = desc->noise;
    surface->noise.seed = dom_terrain_noise_seed(desc);
    surface->material_primary = desc->material_primary;
    surface->roughness_base = desc->roughness_base;
    surface->travel_cost_base = desc->travel_cost_base;
    surface->travel_cost_slope_scale = desc->travel_cost_slope_scale;
    surface->travel_cost_roughness_scale = desc->travel_cost_roughness_scale;
    surface->walkable_max_slope = desc->walkable_max_slope;
    surface->sdf_source.eval = dom_terrain_surface_eval;
    surface->sdf_source.analytic_eval = dom_terrain_surface_eval_analytic;
    surface->sdf_source.ctx = surface;
    surface->sdf_source.has_analytic = 1u;
    dom_terrain_surface_bounds(surface);
}

const dom_domain_sdf_source* dom_terrain_surface_sdf(const dom_terrain_surface* surface)
{
    if (!surface) {
        return (const dom_domain_sdf_source*)0;
    }
    return &surface->sdf_source;
}

void dom_terrain_domain_init(dom_terrain_domain* domain,
                             const dom_terrain_surface_desc* desc,
                             u32 cache_capacity)
{
    if (!domain || !desc) {
        return;
    }
    memset(domain, 0, sizeof(*domain));
    dom_terrain_surface_init(&domain->surface, desc);
    dom_domain_volume_init(&domain->volume);
    domain->volume.domain_id = desc->domain_id;
    domain->volume.authoring_version = 1u;
    domain->volume.existence_state = DOM_DOMAIN_EXISTENCE_REALIZED;
    domain->volume.archival_state = DOM_DOMAIN_ARCHIVAL_LIVE;
    dom_domain_cache_init(&domain->cache);
    if (cache_capacity > 0u) {
        dom_domain_cache_reserve(&domain->cache, cache_capacity);
    }
    dom_domain_volume_set_cache(&domain->volume, &domain->cache);
    dom_domain_volume_set_source(&domain->volume, dom_terrain_surface_sdf(&domain->surface));
    domain->capsule_count = 0u;
}

void dom_terrain_domain_free(dom_terrain_domain* domain)
{
    if (!domain) {
        return;
    }
    dom_domain_volume_free(&domain->volume);
    dom_domain_cache_free(&domain->cache);
    domain->capsule_count = 0u;
}

void dom_terrain_domain_set_state(dom_terrain_domain* domain,
                                  u32 existence_state,
                                  u32 archival_state)
{
    if (!domain) {
        return;
    }
    dom_domain_volume_set_state(&domain->volume, existence_state, archival_state);
}

void dom_terrain_domain_set_policy(dom_terrain_domain* domain,
                                   const dom_domain_policy* policy)
{
    if (!domain || !policy) {
        return;
    }
    dom_domain_volume_set_policy(&domain->volume, policy);
}

int dom_terrain_gradient(const dom_terrain_surface* surface,
                         const dom_domain_point* point,
                         dom_domain_point* out_grad)
{
    dom_domain_point p1;
    dom_domain_point p2;
    q16_16 step;
    q16_16 denom;
    if (!surface || !point || !out_grad) {
        return -1;
    }
    step = d_q16_16_from_int(1);
    denom = d_q16_16_from_int(2);

    p1 = *point;
    p2 = *point;
    p1.x = d_q16_16_sub(p1.x, step);
    p2.x = d_q16_16_add(p2.x, step);
    out_grad->x = d_fixed_div_q16_16(
        d_q16_16_sub(dom_terrain_surface_eval(surface, &p2),
                     dom_terrain_surface_eval(surface, &p1)),
        d_q16_16_mul(step, denom));

    p1 = *point;
    p2 = *point;
    p1.y = d_q16_16_sub(p1.y, step);
    p2.y = d_q16_16_add(p2.y, step);
    out_grad->y = d_fixed_div_q16_16(
        d_q16_16_sub(dom_terrain_surface_eval(surface, &p2),
                     dom_terrain_surface_eval(surface, &p1)),
        d_q16_16_mul(step, denom));

    p1 = *point;
    p2 = *point;
    p1.z = d_q16_16_sub(p1.z, step);
    p2.z = d_q16_16_add(p2.z, step);
    out_grad->z = d_fixed_div_q16_16(
        d_q16_16_sub(dom_terrain_surface_eval(surface, &p2),
                     dom_terrain_surface_eval(surface, &p1)),
        d_q16_16_mul(step, denom));

    return 0;
}

static q16_16 dom_terrain_slope_from_normal(const dom_domain_point* n)
{
    q16_16 nx2 = d_q16_16_mul(n->x, n->x);
    q16_16 ny2 = d_q16_16_mul(n->y, n->y);
    q16_16 nz = dom_terrain_abs_q16_16(n->z);
    q16_16 horiz = d_fixed_sqrt_q16_16(d_q16_16_add(nx2, ny2));
    if (nz == 0) {
        return (q16_16)0x7fffffff;
    }
    return d_fixed_div_q16_16(horiz, nz);
}

static q16_16 dom_terrain_roughness_from_noise(const dom_terrain_surface* surface,
                                               const dom_domain_point* point)
{
    q16_16 noise = dom_terrain_abs_q16_16(dom_terrain_noise_sample(surface, point));
    q16_16 amp = dom_terrain_abs_q16_16(surface->noise.amplitude);
    q16_16 base = surface->roughness_base;
    if (amp == 0) {
        return base;
    }
    return dom_terrain_clamp_q16_16(d_q16_16_add(base, d_fixed_div_q16_16(noise, amp)),
                                    0, d_q16_16_from_int(1));
}

int dom_terrain_sample_query(const dom_terrain_domain* domain,
                             const dom_domain_point* point,
                             dom_domain_budget* budget,
                             dom_terrain_sample* out_sample)
{
    dom_domain_distance_result dist;
    dom_domain_point grad;
    dom_domain_point normal;
    q16_16 len;
    d_bool collapsed;
    if (!domain || !point || !out_sample) {
        return -1;
    }
    memset(out_sample, 0, sizeof(*out_sample));
    collapsed = D_FALSE;
    if (domain->capsule_count > 0u) {
        u32 i;
        for (i = 0u; i < domain->capsule_count; ++i) {
            if (dom_domain_aabb_contains(&domain->capsules[i].bounds, point)) {
                collapsed = D_TRUE;
                break;
            }
        }
    }
    if (collapsed) {
        dom_domain_volume temp = domain->volume;
        temp.policy.max_resolution = DOM_DOMAIN_RES_ANALYTIC;
        dist = dom_domain_distance(&temp, point, budget);
    } else {
        dist = dom_domain_distance(&domain->volume, point, budget);
    }
    out_sample->phi = dist.distance;
    out_sample->meta = dist.meta;

    if (dist.meta.status != DOM_DOMAIN_QUERY_OK ||
        dist.meta.confidence != DOM_DOMAIN_CONFIDENCE_EXACT) {
        out_sample->material_primary = 0u;
        out_sample->roughness = DOM_TERRAIN_UNKNOWN_Q16;
        out_sample->slope = DOM_TERRAIN_UNKNOWN_Q16;
        out_sample->travel_cost = DOM_TERRAIN_UNKNOWN_Q16;
        out_sample->flags |= DOM_TERRAIN_SAMPLE_PHI_UNKNOWN | DOM_TERRAIN_SAMPLE_FIELDS_UNKNOWN;
        return 0;
    }

    if (collapsed) {
        out_sample->material_primary = (dist.distance <= 0) ? domain->surface.material_primary : 0u;
        out_sample->roughness = DOM_TERRAIN_UNKNOWN_Q16;
        out_sample->slope = DOM_TERRAIN_UNKNOWN_Q16;
        out_sample->travel_cost = DOM_TERRAIN_UNKNOWN_Q16;
        out_sample->flags |= DOM_TERRAIN_SAMPLE_FIELDS_UNKNOWN;
        return 0;
    }

    if (dom_terrain_gradient(&domain->surface, point, &grad) != 0) {
        out_sample->flags |= DOM_TERRAIN_SAMPLE_FIELDS_UNKNOWN;
        out_sample->roughness = DOM_TERRAIN_UNKNOWN_Q16;
        out_sample->slope = DOM_TERRAIN_UNKNOWN_Q16;
        out_sample->travel_cost = DOM_TERRAIN_UNKNOWN_Q16;
        return 0;
    }

    len = d_fixed_sqrt_q16_16(d_q16_16_add(
        d_q16_16_add(d_q16_16_mul(grad.x, grad.x), d_q16_16_mul(grad.y, grad.y)),
        d_q16_16_mul(grad.z, grad.z)));
    if (len == 0) {
        normal.x = 0;
        normal.y = 0;
        normal.z = d_q16_16_from_int(1);
    } else {
        normal.x = d_fixed_div_q16_16(grad.x, len);
        normal.y = d_fixed_div_q16_16(grad.y, len);
        normal.z = d_fixed_div_q16_16(grad.z, len);
    }

    out_sample->roughness = dom_terrain_roughness_from_noise(&domain->surface, point);
    out_sample->slope = dom_terrain_slope_from_normal(&normal);
    out_sample->material_primary = (dist.distance <= 0) ? domain->surface.material_primary : 0u;
    out_sample->travel_cost = domain->surface.travel_cost_base;
    out_sample->travel_cost = d_q16_16_add(out_sample->travel_cost,
                                           d_q16_16_mul(out_sample->slope,
                                                        domain->surface.travel_cost_slope_scale));
    out_sample->travel_cost = d_q16_16_add(out_sample->travel_cost,
                                           d_q16_16_mul(out_sample->roughness,
                                                        domain->surface.travel_cost_roughness_scale));
    return 0;
}

d_bool dom_terrain_collision(const dom_terrain_domain* domain,
                             const dom_domain_point* point,
                             dom_domain_budget* budget,
                             dom_domain_query_meta* out_meta)
{
    dom_domain_query_meta meta;
    d_bool inside;
    d_bool collapsed;
    if (!domain || !point) {
        return D_FALSE;
    }
    collapsed = D_FALSE;
    if (domain->capsule_count > 0u) {
        u32 i;
        for (i = 0u; i < domain->capsule_count; ++i) {
            if (dom_domain_aabb_contains(&domain->capsules[i].bounds, point)) {
                collapsed = D_TRUE;
                break;
            }
        }
    }
    if (collapsed) {
        dom_domain_volume temp = domain->volume;
        temp.policy.max_resolution = DOM_DOMAIN_RES_ANALYTIC;
        inside = dom_domain_contains(&temp, point, budget, &meta);
    } else {
        inside = dom_domain_contains(&domain->volume, point, budget, &meta);
    }
    if (out_meta) {
        *out_meta = meta;
    }
    if (meta.status != DOM_DOMAIN_QUERY_OK || meta.confidence != DOM_DOMAIN_CONFIDENCE_EXACT) {
        return D_FALSE;
    }
    return inside;
}

d_bool dom_terrain_walkable(const dom_terrain_domain* domain,
                            const dom_domain_point* point,
                            dom_domain_budget* budget,
                            dom_domain_query_meta* out_meta)
{
    dom_terrain_sample sample;
    if (!domain || !point) {
        return D_FALSE;
    }
    if (dom_terrain_sample_query(domain, point, budget, &sample) != 0) {
        return D_FALSE;
    }
    if (out_meta) {
        *out_meta = sample.meta;
    }
    if (sample.flags & (DOM_TERRAIN_SAMPLE_PHI_UNKNOWN | DOM_TERRAIN_SAMPLE_FIELDS_UNKNOWN)) {
        return D_FALSE;
    }
    if (sample.phi > 0) {
        return D_FALSE;
    }
    if (sample.slope > domain->surface.walkable_max_slope) {
        return D_FALSE;
    }
    return D_TRUE;
}

void dom_terrain_chunk_coord_from_point(q16_16 tile_size,
                                        const dom_domain_point* point,
                                        dom_terrain_chunk_coord* out_coord)
{
    if (!out_coord) {
        return;
    }
    memset(out_coord, 0, sizeof(*out_coord));
    if (!point || tile_size <= 0) {
        return;
    }
    out_coord->tx = dom_terrain_floor_div_q16(point->x, tile_size);
    out_coord->ty = dom_terrain_floor_div_q16(point->y, tile_size);
    out_coord->tz = dom_terrain_floor_div_q16(point->z, tile_size);
    out_coord->origin.x = (q16_16)((i64)out_coord->tx * (i64)tile_size);
    out_coord->origin.y = (q16_16)((i64)out_coord->ty * (i64)tile_size);
    out_coord->origin.z = (q16_16)((i64)out_coord->tz * (i64)tile_size);
}

void dom_terrain_point_to_chunk_local(const dom_terrain_chunk_coord* coord,
                                      const dom_domain_point* point,
                                      dom_domain_point* out_local)
{
    if (!coord || !point || !out_local) {
        return;
    }
    out_local->x = d_q16_16_sub(point->x, coord->origin.x);
    out_local->y = d_q16_16_sub(point->y, coord->origin.y);
    out_local->z = d_q16_16_sub(point->z, coord->origin.z);
}

void dom_terrain_point_to_player_local(const dom_domain_point* point,
                                       const dom_domain_point* player_origin,
                                       dom_domain_point* out_local)
{
    if (!point || !player_origin || !out_local) {
        return;
    }
    out_local->x = d_q16_16_sub(point->x, player_origin->x);
    out_local->y = d_q16_16_sub(point->y, player_origin->y);
    out_local->z = d_q16_16_sub(point->z, player_origin->z);
}

void dom_terrain_global_to_local(const dom_terrain_surface* surface,
                                 const dom_terrain_global_point* global_point,
                                 dom_domain_point* out_local)
{
    q48_16 scale;
    if (!surface || !global_point || !out_local) {
        return;
    }
    scale = d_q48_16_from_q16_16(surface->meters_per_unit);
    if (scale == 0) {
        out_local->x = 0;
        out_local->y = 0;
        out_local->z = 0;
        return;
    }
    out_local->x = d_q16_16_from_q48_16(d_q48_16_div(global_point->x, scale));
    out_local->y = d_q16_16_from_q48_16(d_q48_16_div(global_point->y, scale));
    out_local->z = d_q16_16_from_q48_16(d_q48_16_div(global_point->z, scale));
}

void dom_terrain_local_to_global(const dom_terrain_surface* surface,
                                 const dom_domain_point* local_point,
                                 dom_terrain_global_point* out_global)
{
    q48_16 scale;
    if (!surface || !local_point || !out_global) {
        return;
    }
    scale = d_q48_16_from_q16_16(surface->meters_per_unit);
    out_global->x = d_q48_16_mul(d_q48_16_from_q16_16(local_point->x), scale);
    out_global->y = d_q48_16_mul(d_q48_16_from_q16_16(local_point->y), scale);
    out_global->z = d_q48_16_mul(d_q48_16_from_q16_16(local_point->z), scale);
}

static q16_16 dom_terrain_atan2_turn_q16(q16_16 y, q16_16 x)
{
    /* CORDIC vectoring mode, 16 iterations */
    static const q16_16 k_atan_turn[16] = {
        8192, 4836, 2555, 1297, 651, 326, 163, 82,
        41, 20, 10, 5, 3, 1, 1, 0
    };
    q16_16 angle = 0;
    i32 i;
    if (x == 0 && y == 0) {
        return 0;
    }
    if (x < 0) {
        x = (q16_16)-x;
        y = (q16_16)-y;
        angle = (q16_16)0x8000; /* half turn */
    }
    for (i = 0; i < 16; ++i) {
        q16_16 x_new;
        q16_16 y_new;
        if (y > 0) {
            x_new = (q16_16)(x + (y >> i));
            y_new = (q16_16)(y - (x >> i));
            angle = (q16_16)(angle + k_atan_turn[i]);
        } else {
            x_new = (q16_16)(x - (y >> i));
            y_new = (q16_16)(y + (x >> i));
            angle = (q16_16)(angle - k_atan_turn[i]);
        }
        x = x_new;
        y = y_new;
    }
    return dom_angle_normalize_q16(angle);
}

dom_domain_point dom_terrain_latlon_to_local(const dom_terrain_shape_desc* shape,
                                             q16_16 latitude_turns,
                                             q16_16 longitude_turns,
                                             q16_16 altitude)
{
    dom_domain_point out;
    q16_16 cos_lat;
    q16_16 sin_lat;
    q16_16 cos_lon;
    q16_16 sin_lon;
    q16_16 radius;
    q16_16 z_scale;
    memset(&out, 0, sizeof(out));
    if (!shape) {
        return out;
    }
    if (shape->kind == DOM_TERRAIN_SHAPE_SLAB) {
        out.x = 0;
        out.y = 0;
        out.z = altitude;
        return out;
    }
    radius = shape->radius_equatorial;
    z_scale = shape->radius_polar;
    if (z_scale == 0) {
        z_scale = radius;
    }
    cos_lat = dom_cos_q16(latitude_turns);
    sin_lat = dom_sin_q16(latitude_turns);
    cos_lon = dom_cos_q16(longitude_turns);
    sin_lon = dom_sin_q16(longitude_turns);
    out.x = d_q16_16_mul(d_q16_16_add(radius, altitude), d_q16_16_mul(cos_lat, cos_lon));
    out.y = d_q16_16_mul(d_q16_16_add(radius, altitude), d_q16_16_mul(cos_lat, sin_lon));
    out.z = d_q16_16_mul(d_q16_16_add(z_scale, altitude), sin_lat);
    return out;
}

dom_terrain_latlon dom_terrain_local_to_latlon(const dom_terrain_shape_desc* shape,
                                               const dom_domain_point* point)
{
    dom_terrain_latlon out;
    q16_16 r_xy;
    q16_16 radius;
    q16_16 z_scale;
    memset(&out, 0, sizeof(out));
    if (!shape || !point) {
        return out;
    }
    if (shape->kind == DOM_TERRAIN_SHAPE_SLAB) {
        out.valid = 0u;
        out.latitude = 0;
        out.longitude = 0;
        out.altitude = point->z;
        return out;
    }
    radius = shape->radius_equatorial;
    z_scale = shape->radius_polar;
    if (z_scale == 0) {
        z_scale = radius;
    }
    r_xy = d_fixed_sqrt_q16_16(d_q16_16_add(d_q16_16_mul(point->x, point->x),
                                            d_q16_16_mul(point->y, point->y)));
    out.longitude = dom_terrain_atan2_turn_q16(point->y, point->x);
    out.latitude = dom_terrain_atan2_turn_q16(point->z, r_xy);
    out.altitude = d_q16_16_sub(r_xy, radius);
    out.valid = 1u;
    (void)z_scale;
    return out;
}

static int dom_terrain_capsule_store(dom_terrain_domain* domain,
                                     const dom_domain_tile_desc* desc)
{
    dom_terrain_macro_capsule capsule;
    dom_domain_point corners[8];
    u32 i;
    q16_16 phi_min = 0;
    q16_16 phi_max = 0;
    q16_16 rough_min = 0;
    q16_16 rough_max = 0;
    if (!domain || !desc) {
        return -1;
    }
    if (domain->capsule_count >= DOM_TERRAIN_MAX_CAPSULES) {
        return -2;
    }
    corners[0] = desc->bounds.min;
    corners[1].x = desc->bounds.max.x; corners[1].y = desc->bounds.min.y; corners[1].z = desc->bounds.min.z;
    corners[2].x = desc->bounds.max.x; corners[2].y = desc->bounds.max.y; corners[2].z = desc->bounds.min.z;
    corners[3].x = desc->bounds.min.x; corners[3].y = desc->bounds.max.y; corners[3].z = desc->bounds.min.z;
    corners[4].x = desc->bounds.min.x; corners[4].y = desc->bounds.min.y; corners[4].z = desc->bounds.max.z;
    corners[5].x = desc->bounds.max.x; corners[5].y = desc->bounds.min.y; corners[5].z = desc->bounds.max.z;
    corners[6].x = desc->bounds.max.x; corners[6].y = desc->bounds.max.y; corners[6].z = desc->bounds.max.z;
    corners[7].x = desc->bounds.min.x; corners[7].y = desc->bounds.max.y; corners[7].z = desc->bounds.max.z;

    for (i = 0u; i < 8u; ++i) {
        q16_16 phi = dom_terrain_surface_eval_analytic(&domain->surface, &corners[i]);
        q16_16 rough = dom_terrain_roughness_from_noise(&domain->surface, &corners[i]);
        if (i == 0u || phi < phi_min) phi_min = phi;
        if (i == 0u || phi > phi_max) phi_max = phi;
        if (i == 0u || rough < rough_min) rough_min = rough;
        if (i == 0u || rough > rough_max) rough_max = rough;
    }

    memset(&capsule, 0, sizeof(capsule));
    capsule.tile_id = desc->tile_id;
    capsule.capsule_id = desc->tile_id;
    capsule.bounds = desc->bounds;
    capsule.phi_min = phi_min;
    capsule.phi_max = phi_max;
    capsule.roughness_min = rough_min;
    capsule.roughness_max = rough_max;
    capsule.material_primary = domain->surface.material_primary;

    domain->capsules[domain->capsule_count++] = capsule;
    return 0;
}

int dom_terrain_domain_collapse_tile(dom_terrain_domain* domain,
                                     const dom_domain_tile_desc* desc)
{
    u32 i;
    if (!domain || !desc) {
        return -1;
    }
    if (domain->cache.entries) {
        for (i = 0u; i < domain->cache.capacity; ++i) {
            dom_domain_cache_entry* entry = &domain->cache.entries[i];
            if (!entry->valid) {
                continue;
            }
            if (entry->domain_id == domain->surface.domain_id &&
                entry->tile_id == desc->tile_id) {
                dom_domain_tile_free(&entry->tile);
                entry->valid = D_FALSE;
                if (domain->cache.count > 0u) {
                    domain->cache.count -= 1u;
                }
            }
        }
    }
    return dom_terrain_capsule_store(domain, desc);
}

int dom_terrain_domain_expand_tile(dom_terrain_domain* domain, u64 tile_id)
{
    u32 i;
    if (!domain) {
        return -1;
    }
    for (i = 0u; i < domain->capsule_count; ++i) {
        if (domain->capsules[i].tile_id == tile_id) {
            domain->capsules[i] = domain->capsules[domain->capsule_count - 1u];
            domain->capsule_count -= 1u;
            return 0;
        }
    }
    return -2;
}

u32 dom_terrain_domain_capsule_count(const dom_terrain_domain* domain)
{
    return domain ? domain->capsule_count : 0u;
}

const dom_terrain_macro_capsule* dom_terrain_domain_capsule_at(const dom_terrain_domain* domain,
                                                               u32 index)
{
    if (!domain || index >= domain->capsule_count) {
        return (const dom_terrain_macro_capsule*)0;
    }
    return &domain->capsules[index];
}
