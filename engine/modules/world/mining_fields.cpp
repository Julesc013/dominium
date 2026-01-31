/*
FILE: source/domino/world/mining_fields.cpp
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / world/mining_fields
RESPONSIBILITY: Implements deterministic mining cuts, extraction, and support checks.
ALLOWED DEPENDENCIES: `include/domino/**` and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: Engine private headers outside world.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: Fixed-point only; deterministic ordering and math.
*/
#include "domino/world/mining_fields.h"

#include "domino/core/fixed_math.h"
#include "domino/core/rng_model.h"

#include <string.h>
#include <stdio.h>

static q16_16 dom_mining_abs_q16_16(q16_16 v)
{
    return (v < 0) ? (q16_16)-v : v;
}

static q16_16 dom_mining_clamp_q16_16(q16_16 v, q16_16 lo, q16_16 hi)
{
    if (v < lo) {
        return lo;
    }
    if (v > hi) {
        return hi;
    }
    return v;
}

static q16_16 dom_mining_min_q16_16(q16_16 a, q16_16 b)
{
    return (a < b) ? a : b;
}

static q16_16 dom_mining_max_q16_16(q16_16 a, q16_16 b)
{
    return (a > b) ? a : b;
}

static void dom_mining_query_meta_refused(dom_domain_query_meta* meta,
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

static void dom_mining_query_meta_ok(dom_domain_query_meta* meta,
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

static d_bool dom_mining_domain_is_active(const dom_mining_domain* domain)
{
    if (!domain) {
        return D_FALSE;
    }
    if (domain->existence_state == DOM_DOMAIN_EXISTENCE_NONEXISTENT ||
        domain->existence_state == DOM_DOMAIN_EXISTENCE_DECLARED) {
        return D_FALSE;
    }
    return D_TRUE;
}

static q16_16 dom_mining_volume_metric(q16_16 radius)
{
    q16_16 r = dom_mining_abs_q16_16(radius);
    return d_q16_16_mul(r, r);
}

static q16_16 dom_mining_overlay_sdf(const dom_mining_overlay* overlay,
                                     const dom_domain_point* point)
{
    q16_16 dx;
    q16_16 dy;
    q16_16 dz;
    q16_16 dist;
    if (!overlay || !point) {
        return 0;
    }
    dx = d_q16_16_sub(point->x, overlay->center.x);
    dy = d_q16_16_sub(point->y, overlay->center.y);
    dz = d_q16_16_sub(point->z, overlay->center.z);
    dist = d_fixed_sqrt_q16_16(d_q16_16_add(d_q16_16_add(d_q16_16_mul(dx, dx),
                                                        d_q16_16_mul(dy, dy)),
                                           d_q16_16_mul(dz, dz)));
    return (q16_16)(dist - overlay->radius);
}

static q16_16 dom_mining_apply_overlays(const dom_mining_domain* domain,
                                        const dom_domain_point* point,
                                        q16_16 phi)
{
    if (!domain || !point) {
        return phi;
    }
    for (u32 i = 0u; i < domain->overlay_count && i < DOM_MINING_MAX_OVERLAYS; ++i) {
        const dom_mining_overlay* overlay = &domain->overlays[i];
        q16_16 overlay_phi = dom_mining_overlay_sdf(overlay, point);
        if (overlay->overlay_kind == DOM_MINING_OVERLAY_CUT) {
            phi = dom_mining_max_q16_16(phi, (q16_16)-overlay_phi);
        } else if (overlay->overlay_kind == DOM_MINING_OVERLAY_FILL) {
            phi = dom_mining_min_q16_16(phi, overlay_phi);
        }
    }
    return phi;
}

static d_bool dom_mining_point_in_sphere(const dom_domain_point* center,
                                         q16_16 radius,
                                         const dom_domain_point* point)
{
    q16_16 dx;
    q16_16 dy;
    q16_16 dz;
    q16_16 dist2;
    q16_16 r2;
    if (!center || !point) {
        return D_FALSE;
    }
    dx = d_q16_16_sub(point->x, center->x);
    dy = d_q16_16_sub(point->y, center->y);
    dz = d_q16_16_sub(point->z, center->z);
    dist2 = d_q16_16_add(d_q16_16_add(d_q16_16_mul(dx, dx), d_q16_16_mul(dy, dy)),
                         d_q16_16_mul(dz, dz));
    r2 = d_q16_16_mul(dom_mining_abs_q16_16(radius), dom_mining_abs_q16_16(radius));
    return dist2 <= r2;
}

static q16_16 dom_mining_apply_depletions(const dom_mining_domain* domain,
                                          u32 resource_id,
                                          const dom_domain_point* point,
                                          q16_16 density)
{
    if (!domain || !point) {
        return density;
    }
    for (u32 i = 0u; i < domain->depletion_count && i < DOM_MINING_MAX_DEPLETIONS; ++i) {
        const dom_mining_depletion* dep = &domain->depletions[i];
        if (dep->resource_id != resource_id) {
            continue;
        }
        if (!dom_mining_point_in_sphere(&dep->center, dep->radius, point)) {
            continue;
        }
        density = d_q16_16_sub(density, dep->depletion);
        if (density < 0) {
            density = 0;
        }
    }
    return density;
}

static q16_16 dom_mining_support_capacity(const dom_terrain_sample* terrain,
                                          const dom_geology_sample* geology)
{
    if (!terrain || !geology) {
        return DOM_MINING_UNKNOWN_Q16;
    }
    if (terrain->flags & (DOM_TERRAIN_SAMPLE_FIELDS_UNKNOWN | DOM_TERRAIN_SAMPLE_PHI_UNKNOWN)) {
        return DOM_MINING_UNKNOWN_Q16;
    }
    if (geology->flags & (DOM_GEOLOGY_SAMPLE_FIELDS_UNKNOWN | DOM_GEOLOGY_SAMPLE_STRATA_UNKNOWN)) {
        return DOM_MINING_UNKNOWN_Q16;
    }
    if (terrain->phi > 0) {
        return 0;
    }
    {
        q16_16 hardness = dom_mining_clamp_q16_16(geology->hardness, 0, d_q16_16_from_int(1));
        q16_16 fracture = dom_mining_clamp_q16_16(geology->fracture_risk, 0, d_q16_16_from_int(1));
        q16_16 slope_factor = dom_mining_clamp_q16_16(d_q16_16_sub(d_q16_16_from_int(1), terrain->slope), 0,
                                                      d_q16_16_from_int(1));
        q16_16 support = d_q16_16_mul(hardness, d_q16_16_sub(d_q16_16_from_int(1), fracture));
        support = d_q16_16_mul(support, slope_factor);
        return support;
    }
}

static q16_16 dom_mining_stress_from_radius(const dom_mining_surface_desc* surface,
                                            q16_16 radius)
{
    q16_16 scale;
    q16_16 stress;
    if (!surface) {
        return 0;
    }
    scale = surface->support_radius_scale;
    if (scale <= 0) {
        scale = d_q16_16_from_int(1);
    }
    stress = d_fixed_div_q16_16(dom_mining_abs_q16_16(radius), scale);
    return dom_mining_clamp_q16_16(stress, 0, d_q16_16_from_int(1));
}

static u32 dom_mining_cost_for_radius(q16_16 radius, u32 base, u32 per_unit)
{
    i32 units = d_q16_16_to_int(dom_mining_abs_q16_16(radius));
    if (units < 0) {
        units = -units;
    }
    return base + ((u32)units * per_unit);
}

static u32 dom_mining_process_id(const char* name)
{
    return d_rng_hash_str32(name ? name : "process.mine.unknown");
}

static u32 dom_mining_overlay_id(const dom_mining_domain* domain,
                                 u32 process_id,
                                 u64 tick,
                                 u32 offset)
{
    d_rng_state rng;
    const char* stream = "noise.stream.world.mining.overlay";
    D_DET_GUARD_RNG_STREAM_NAME(stream);
    if (!domain) {
        return 0u;
    }
    d_rng_state_from_context(&rng,
                             domain->surface.world_seed,
                             domain->surface.domain_id,
                             (u64)process_id,
                             tick,
                             stream,
                             D_RNG_MIX_DOMAIN | D_RNG_MIX_PROCESS | D_RNG_MIX_TICK | D_RNG_MIX_STREAM);
    for (u32 i = 0u; i <= offset; ++i) {
        (void)d_rng_next_u32(&rng);
    }
    return rng.state;
}

static u32 dom_mining_chunk_id(const dom_mining_domain* domain,
                               u32 process_id,
                               u64 tick,
                               u32 offset)
{
    d_rng_state rng;
    const char* stream = "noise.stream.world.mining.chunk";
    D_DET_GUARD_RNG_STREAM_NAME(stream);
    if (!domain) {
        return 0u;
    }
    d_rng_state_from_context(&rng,
                             domain->surface.world_seed,
                             domain->surface.domain_id,
                             (u64)process_id,
                             tick,
                             stream,
                             D_RNG_MIX_DOMAIN | D_RNG_MIX_PROCESS | D_RNG_MIX_TICK | D_RNG_MIX_STREAM);
    for (u32 i = 0u; i <= offset; ++i) {
        (void)d_rng_next_u32(&rng);
    }
    return rng.state;
}

void dom_mining_surface_desc_init(dom_mining_surface_desc* desc)
{
    if (!desc) {
        return;
    }
    memset(desc, 0, sizeof(*desc));
    desc->domain_id = 1u;
    desc->world_seed = 1u;
    desc->meters_per_unit = d_q16_16_from_int(1);
    desc->shape.kind = DOM_TERRAIN_SHAPE_SPHERE;
    desc->shape.radius_equatorial = d_q16_16_from_int(512);
    desc->shape.radius_polar = d_q16_16_from_int(512);
    desc->shape.slab_half_extent = d_q16_16_from_int(512);
    desc->shape.slab_half_thickness = d_q16_16_from_int(16);

    dom_terrain_surface_desc_init(&desc->terrain_desc);
    dom_geology_surface_desc_init(&desc->geology_desc);

    desc->terrain_desc.domain_id = desc->domain_id;
    desc->terrain_desc.world_seed = desc->world_seed;
    desc->terrain_desc.meters_per_unit = desc->meters_per_unit;
    desc->terrain_desc.shape = desc->shape;

    desc->geology_desc.domain_id = desc->domain_id;
    desc->geology_desc.world_seed = desc->world_seed;
    desc->geology_desc.meters_per_unit = desc->meters_per_unit;
    desc->geology_desc.shape = desc->shape;

    desc->cut_radius_max = d_q16_16_from_int(8);
    desc->extract_radius_max = d_q16_16_from_int(8);
    desc->support_radius_scale = d_q16_16_from_int(8);
    desc->collapse_fill_scale = d_q16_16_from_int(1);
    desc->cut_cost_base = 20u;
    desc->cut_cost_per_unit = 2u;
    desc->extract_cost_base = 30u;
    desc->extract_cost_per_unit = 3u;
    desc->support_cost_base = 10u;
    desc->overlay_capacity = 128u;
    desc->depletion_capacity = 128u;
    desc->chunk_capacity = 128u;
    desc->cache_capacity = 128u;
    desc->law_allow_mining = 1u;
    desc->metalaw_allow_mining = 1u;
    desc->tailings_material_id = d_rng_hash_str32("material.tailings");
}

void dom_mining_domain_init(dom_mining_domain* domain,
                            const dom_mining_surface_desc* desc)
{
    dom_mining_surface_desc normalized;
    dom_terrain_surface_desc terrain_desc;
    dom_geology_surface_desc geology_desc;
    u32 cache_capacity;
    if (!domain || !desc) {
        return;
    }
    normalized = *desc;
    normalized.domain_id = desc->domain_id;
    normalized.world_seed = desc->world_seed;
    normalized.meters_per_unit = desc->meters_per_unit;
    normalized.shape = desc->shape;

    terrain_desc = desc->terrain_desc;
    terrain_desc.domain_id = desc->domain_id;
    terrain_desc.world_seed = desc->world_seed;
    terrain_desc.meters_per_unit = desc->meters_per_unit;
    terrain_desc.shape = desc->shape;

    geology_desc = desc->geology_desc;
    geology_desc.domain_id = desc->domain_id;
    geology_desc.world_seed = desc->world_seed;
    geology_desc.meters_per_unit = desc->meters_per_unit;
    geology_desc.shape = desc->shape;

    memset(domain, 0, sizeof(*domain));
    domain->surface = normalized;
    cache_capacity = desc->cache_capacity;
    dom_terrain_domain_init(&domain->terrain_domain, &terrain_desc, cache_capacity);
    dom_geology_domain_init(&domain->geology_domain, &geology_desc, cache_capacity);
    dom_domain_policy_init(&domain->policy);
    domain->existence_state = DOM_DOMAIN_EXISTENCE_REALIZED;
    domain->archival_state = DOM_DOMAIN_ARCHIVAL_LIVE;
    domain->authoring_version = 1u;
    domain->overlay_count = 0u;
    domain->depletion_count = 0u;
    domain->chunk_count = 0u;
}

void dom_mining_domain_free(dom_mining_domain* domain)
{
    if (!domain) {
        return;
    }
    dom_terrain_domain_free(&domain->terrain_domain);
    dom_geology_domain_free(&domain->geology_domain);
    domain->overlay_count = 0u;
    domain->depletion_count = 0u;
    domain->chunk_count = 0u;
}

void dom_mining_domain_set_state(dom_mining_domain* domain,
                                 u32 existence_state,
                                 u32 archival_state)
{
    if (!domain) {
        return;
    }
    if (domain->existence_state != existence_state || domain->archival_state != archival_state) {
        domain->existence_state = existence_state;
        domain->archival_state = archival_state;
        dom_terrain_domain_set_state(&domain->terrain_domain, existence_state, archival_state);
        dom_geology_domain_set_state(&domain->geology_domain, existence_state, archival_state);
    }
}

void dom_mining_domain_set_policy(dom_mining_domain* domain,
                                  const dom_domain_policy* policy)
{
    if (!domain || !policy) {
        return;
    }
    domain->policy = *policy;
    dom_terrain_domain_set_policy(&domain->terrain_domain, policy);
    dom_geology_domain_set_policy(&domain->geology_domain, policy);
}

int dom_mining_sample_query(const dom_mining_domain* domain,
                            const dom_domain_point* point,
                            dom_domain_budget* budget,
                            dom_mining_sample* out_sample)
{
    dom_terrain_sample terrain;
    dom_geology_sample geology;
    const dom_domain_sdf_source* source;
    u32 budget_before = 0u;
    u32 cost_units = 0u;
    u32 confidence = DOM_DOMAIN_CONFIDENCE_EXACT;
    if (!domain || !point || !out_sample) {
        return -1;
    }
    memset(out_sample, 0, sizeof(*out_sample));
    out_sample->phi = DOM_MINING_UNKNOWN_Q16;
    out_sample->support_capacity = DOM_MINING_UNKNOWN_Q16;
    out_sample->stress = 0;
    out_sample->stress_ratio = 0;
    out_sample->resource_count = domain->geology_domain.surface.resource_count;
    if (out_sample->resource_count > DOM_MINING_MAX_RESOURCES) {
        out_sample->resource_count = DOM_MINING_MAX_RESOURCES;
    }
    for (u32 i = 0u; i < out_sample->resource_count; ++i) {
        out_sample->resource_density[i] = DOM_MINING_UNKNOWN_Q16;
    }
    if (budget) {
        budget_before = budget->used_units;
    }
    if (!dom_mining_domain_is_active(domain)) {
        dom_mining_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_DOMAIN_INACTIVE, budget);
        out_sample->flags |= DOM_MINING_SAMPLE_FIELDS_UNKNOWN;
        return 0;
    }
    source = dom_terrain_surface_sdf(&domain->terrain_domain.surface);
    if (!source || !source->eval) {
        dom_mining_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_NO_SOURCE, budget);
        out_sample->flags |= DOM_MINING_SAMPLE_FIELDS_UNKNOWN;
        return 0;
    }
    if (!dom_domain_aabb_contains(&source->bounds, point)) {
        dom_mining_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_COARSE,
                                 DOM_DOMAIN_CONFIDENCE_LOWER_BOUND, 0u, budget);
        out_sample->flags |= DOM_MINING_SAMPLE_FIELDS_UNKNOWN;
        return 0;
    }
    if (dom_terrain_sample_query(&domain->terrain_domain, point, budget, &terrain) != 0) {
        dom_mining_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_INTERNAL, budget);
        out_sample->flags |= DOM_MINING_SAMPLE_FIELDS_UNKNOWN;
        return 0;
    }
    if (terrain.meta.status != DOM_DOMAIN_QUERY_OK) {
        dom_mining_query_meta_refused(&out_sample->meta, terrain.meta.refusal_reason, budget);
        out_sample->flags |= DOM_MINING_SAMPLE_FIELDS_UNKNOWN;
        return 0;
    }
    if (dom_geology_sample_query(&domain->geology_domain, point, budget, &geology) != 0) {
        dom_mining_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_INTERNAL, budget);
        out_sample->flags |= DOM_MINING_SAMPLE_FIELDS_UNKNOWN;
        return 0;
    }
    if (geology.meta.status != DOM_DOMAIN_QUERY_OK) {
        dom_mining_query_meta_refused(&out_sample->meta, geology.meta.refusal_reason, budget);
        out_sample->flags |= DOM_MINING_SAMPLE_FIELDS_UNKNOWN;
        return 0;
    }
    if (terrain.flags & (DOM_TERRAIN_SAMPLE_FIELDS_UNKNOWN | DOM_TERRAIN_SAMPLE_PHI_UNKNOWN)) {
        out_sample->flags |= DOM_MINING_SAMPLE_FIELDS_UNKNOWN;
        confidence = DOM_DOMAIN_CONFIDENCE_UNKNOWN;
    }
    if (geology.flags & (DOM_GEOLOGY_SAMPLE_FIELDS_UNKNOWN | DOM_GEOLOGY_SAMPLE_STRATA_UNKNOWN)) {
        out_sample->flags |= DOM_MINING_SAMPLE_FIELDS_UNKNOWN;
        confidence = DOM_DOMAIN_CONFIDENCE_UNKNOWN;
    }

    if (!(out_sample->flags & DOM_MINING_SAMPLE_FIELDS_UNKNOWN)) {
        out_sample->phi = dom_mining_apply_overlays(domain, point, terrain.phi);
        out_sample->material_primary = terrain.material_primary;
        out_sample->support_capacity = dom_mining_support_capacity(&terrain, &geology);
        out_sample->stress = 0;
        out_sample->stress_ratio = 0;
        for (u32 i = 0u; i < out_sample->resource_count; ++i) {
            q16_16 density = geology.resource_density[i];
            density = dom_mining_apply_depletions(domain, domain->geology_domain.surface.resources[i].resource_id,
                                                  point, density);
            out_sample->resource_density[i] = density;
        }
    }
    if (budget) {
        cost_units = budget->used_units - budget_before;
    }
    dom_mining_query_meta_ok(&out_sample->meta,
                             terrain.meta.resolution,
                             confidence,
                             cost_units,
                             budget);
    return 0;
}

static void dom_mining_cut_result_init(dom_mining_cut_result* result)
{
    if (!result) {
        return;
    }
    memset(result, 0, sizeof(*result));
    result->ok = 0u;
    result->refusal_reason = DOM_DOMAIN_REFUSE_NONE;
    result->flags = 0u;
    result->overlay_id = 0u;
    result->cut_radius = 0;
    result->cut_volume = 0;
    result->overlay_count = 0u;
}

int dom_mining_cut(dom_mining_domain* domain,
                   const dom_domain_point* center,
                   q16_16 radius,
                   u64 tick,
                   dom_domain_budget* budget,
                   dom_mining_cut_result* out_result)
{
    dom_mining_overlay* overlay;
    u32 process_id;
    if (out_result) {
        dom_mining_cut_result_init(out_result);
    }
    if (!domain || !center) {
        if (out_result) {
            out_result->refusal_reason = DOM_DOMAIN_REFUSE_INTERNAL;
        }
        return -1;
    }
    if (!dom_mining_domain_is_active(domain)) {
        if (out_result) {
            out_result->refusal_reason = DOM_DOMAIN_REFUSE_DOMAIN_INACTIVE;
        }
        return -2;
    }
    if (!domain->surface.law_allow_mining) {
        if (out_result) {
            out_result->flags |= DOM_MINING_RESULT_LAW_BLOCK;
            out_result->refusal_reason = DOM_DOMAIN_REFUSE_POLICY;
        }
        return -3;
    }
    if (!domain->surface.metalaw_allow_mining) {
        if (out_result) {
            out_result->flags |= DOM_MINING_RESULT_METALAW_BLOCK;
            out_result->refusal_reason = DOM_DOMAIN_REFUSE_POLICY;
        }
        return -4;
    }
    radius = dom_mining_abs_q16_16(radius);
    if (radius <= 0 || radius > domain->surface.cut_radius_max) {
        if (out_result) {
            out_result->refusal_reason = DOM_DOMAIN_REFUSE_POLICY;
        }
        return -5;
    }
    if (domain->overlay_count >= domain->surface.overlay_capacity ||
        domain->overlay_count >= DOM_MINING_MAX_OVERLAYS) {
        if (out_result) {
            out_result->refusal_reason = DOM_DOMAIN_REFUSE_INTERNAL;
        }
        return -6;
    }
    {
        u32 cost = dom_mining_cost_for_radius(radius, domain->surface.cut_cost_base,
                                              domain->surface.cut_cost_per_unit);
        if (!dom_domain_budget_consume(budget, cost)) {
            if (out_result) {
                out_result->refusal_reason = DOM_DOMAIN_REFUSE_BUDGET;
            }
            return -7;
        }
    }

    process_id = dom_mining_process_id("process.mine.cut");
    overlay = &domain->overlays[domain->overlay_count];
    memset(overlay, 0, sizeof(*overlay));
    overlay->overlay_kind = DOM_MINING_OVERLAY_CUT;
    overlay->center = *center;
    overlay->radius = radius;
    overlay->tick = tick;
    overlay->process_id = process_id;
    overlay->event_id = d_rng_hash_str32("event.mine.cut");
    overlay->flags = DOM_MINING_OVERLAY_TOOL;
    overlay->overlay_id = dom_mining_overlay_id(domain, process_id, tick, domain->overlay_count);
    domain->overlay_count += 1u;

    if (out_result) {
        out_result->ok = 1u;
        out_result->overlay_id = overlay->overlay_id;
        out_result->cut_radius = radius;
        out_result->cut_volume = dom_mining_volume_metric(radius);
        out_result->overlay_count = domain->overlay_count;
    }
    return 0;
}

static void dom_mining_extract_result_init(dom_mining_extract_result* result)
{
    if (!result) {
        return;
    }
    memset(result, 0, sizeof(*result));
    result->ok = 0u;
    result->refusal_reason = DOM_DOMAIN_REFUSE_NONE;
    result->flags = 0u;
    result->extract_radius = 0;
    result->extract_volume = 0;
    result->extracted_mass = 0;
    result->tailings_mass = 0;
    result->resource_chunks = 0u;
    result->tailings_chunks = 0u;
    result->chunk_count = 0u;
}

int dom_mining_extract(dom_mining_domain* domain,
                       const dom_domain_point* center,
                       q16_16 radius,
                       u64 tick,
                       dom_domain_budget* budget,
                       dom_mining_extract_result* out_result)
{
    dom_geology_sample geology;
    dom_terrain_sample terrain;
    q16_16 volume_metric;
    q16_16 density_sum = 0;
    u32 process_id;
    if (out_result) {
        dom_mining_extract_result_init(out_result);
    }
    if (!domain || !center) {
        if (out_result) {
            out_result->refusal_reason = DOM_DOMAIN_REFUSE_INTERNAL;
        }
        return -1;
    }
    if (!dom_mining_domain_is_active(domain)) {
        if (out_result) {
            out_result->refusal_reason = DOM_DOMAIN_REFUSE_DOMAIN_INACTIVE;
        }
        return -2;
    }
    if (!domain->surface.law_allow_mining) {
        if (out_result) {
            out_result->flags |= DOM_MINING_RESULT_LAW_BLOCK;
            out_result->refusal_reason = DOM_DOMAIN_REFUSE_POLICY;
        }
        return -3;
    }
    if (!domain->surface.metalaw_allow_mining) {
        if (out_result) {
            out_result->flags |= DOM_MINING_RESULT_METALAW_BLOCK;
            out_result->refusal_reason = DOM_DOMAIN_REFUSE_POLICY;
        }
        return -4;
    }
    radius = dom_mining_abs_q16_16(radius);
    if (radius <= 0 || radius > domain->surface.extract_radius_max) {
        if (out_result) {
            out_result->refusal_reason = DOM_DOMAIN_REFUSE_POLICY;
        }
        return -5;
    }
    if (domain->chunk_count >= domain->surface.chunk_capacity ||
        domain->chunk_count >= DOM_MINING_MAX_CHUNKS) {
        if (out_result) {
            out_result->refusal_reason = DOM_DOMAIN_REFUSE_INTERNAL;
        }
        return -6;
    }
    if (dom_terrain_sample_query(&domain->terrain_domain, center, budget, &terrain) != 0) {
        if (out_result) {
            out_result->refusal_reason = DOM_DOMAIN_REFUSE_INTERNAL;
        }
        return -7;
    }
    if (terrain.flags & (DOM_TERRAIN_SAMPLE_FIELDS_UNKNOWN | DOM_TERRAIN_SAMPLE_PHI_UNKNOWN)) {
        if (out_result) {
            out_result->refusal_reason = DOM_DOMAIN_REFUSE_NO_ANALYTIC;
        }
        return -8;
    }
    if (terrain.phi > 0) {
        if (out_result) {
            out_result->refusal_reason = DOM_DOMAIN_REFUSE_POLICY;
        }
        return -9;
    }
    if (dom_geology_sample_query(&domain->geology_domain, center, budget, &geology) != 0) {
        if (out_result) {
            out_result->refusal_reason = DOM_DOMAIN_REFUSE_INTERNAL;
        }
        return -10;
    }
    if (geology.flags & (DOM_GEOLOGY_SAMPLE_FIELDS_UNKNOWN | DOM_GEOLOGY_SAMPLE_STRATA_UNKNOWN)) {
        if (out_result) {
            out_result->refusal_reason = DOM_DOMAIN_REFUSE_NO_ANALYTIC;
        }
        return -11;
    }
    {
        u32 cost = dom_mining_cost_for_radius(radius, domain->surface.extract_cost_base,
                                              domain->surface.extract_cost_per_unit);
        if (!dom_domain_budget_consume(budget, cost)) {
            if (out_result) {
                out_result->refusal_reason = DOM_DOMAIN_REFUSE_BUDGET;
            }
            return -12;
        }
    }

    process_id = dom_mining_process_id("process.mine.extract");
    volume_metric = dom_mining_volume_metric(radius);

    for (u32 i = 0u; i < geology.resource_count && i < DOM_MINING_MAX_RESOURCES; ++i) {
        q16_16 density = geology.resource_density[i];
        u32 resource_id = domain->geology_domain.surface.resources[i].resource_id;
        density = dom_mining_apply_depletions(domain, resource_id, center, density);
        if (density <= 0) {
            continue;
        }
        density_sum = d_q16_16_add(density_sum, density);
        if (domain->chunk_count >= domain->surface.chunk_capacity ||
            domain->chunk_count >= DOM_MINING_MAX_CHUNKS) {
            break;
        }
        {
            dom_material_chunk* chunk = &domain->chunks[domain->chunk_count++];
            memset(chunk, 0, sizeof(*chunk));
            chunk->chunk_id = dom_mining_chunk_id(domain, process_id, tick, domain->chunk_count);
            chunk->material_id = resource_id;
            chunk->location = *center;
            chunk->volume = volume_metric;
            chunk->mass = d_q16_16_mul(volume_metric, density);
            chunk->purity = density;
            chunk->flags = 0u;
            chunk->process_id = process_id;
            chunk->tick = tick;
            if (out_result) {
                out_result->resource_chunks += 1u;
                out_result->extracted_mass = d_q16_16_add(out_result->extracted_mass, chunk->mass);
            }
        }
        if (domain->depletion_count < domain->surface.depletion_capacity &&
            domain->depletion_count < DOM_MINING_MAX_DEPLETIONS) {
            dom_mining_depletion* dep = &domain->depletions[domain->depletion_count++];
            memset(dep, 0, sizeof(*dep));
            dep->resource_id = resource_id;
            dep->center = *center;
            dep->radius = radius;
            dep->depletion = density;
            dep->tick = tick;
        }
    }

    {
        q16_16 tailings_density = d_q16_16_sub(d_q16_16_from_int(1), density_sum);
        tailings_density = dom_mining_clamp_q16_16(tailings_density, 0, d_q16_16_from_int(1));
        if (tailings_density > 0 &&
            domain->chunk_count < domain->surface.chunk_capacity &&
            domain->chunk_count < DOM_MINING_MAX_CHUNKS) {
            dom_material_chunk* chunk = &domain->chunks[domain->chunk_count++];
            memset(chunk, 0, sizeof(*chunk));
            chunk->chunk_id = dom_mining_chunk_id(domain, process_id, tick, domain->chunk_count);
            chunk->material_id = domain->surface.tailings_material_id;
            chunk->location = *center;
            chunk->volume = volume_metric;
            chunk->mass = d_q16_16_mul(volume_metric, tailings_density);
            chunk->purity = 0;
            chunk->flags = DOM_MINING_CHUNK_WASTE;
            chunk->process_id = process_id;
            chunk->tick = tick;
            if (out_result) {
                out_result->tailings_chunks += 1u;
                out_result->tailings_mass = d_q16_16_add(out_result->tailings_mass, chunk->mass);
            }
        }
        if (density_sum <= 0 && out_result) {
            out_result->flags |= DOM_MINING_RESULT_DEPLETED;
        }
    }

    if (out_result) {
        out_result->ok = 1u;
        out_result->extract_radius = radius;
        out_result->extract_volume = volume_metric;
        out_result->chunk_count = domain->chunk_count;
    }
    return 0;
}

static void dom_mining_support_result_init(dom_mining_support_result* result)
{
    if (!result) {
        return;
    }
    memset(result, 0, sizeof(*result));
    result->ok = 0u;
    result->refusal_reason = DOM_DOMAIN_REFUSE_NONE;
    result->flags = 0u;
    result->support_capacity = DOM_MINING_UNKNOWN_Q16;
    result->stress = 0;
    result->stress_ratio = 0;
    result->collapse_risk = 0u;
    result->collapse_radius = 0;
}

int dom_mining_support_check(dom_mining_domain* domain,
                             const dom_domain_point* center,
                             q16_16 radius,
                             u64 tick,
                             dom_mining_support_result* out_result)
{
    dom_terrain_sample terrain;
    dom_geology_sample geology;
    q16_16 support;
    q16_16 stress;
    (void)tick;
    if (out_result) {
        dom_mining_support_result_init(out_result);
    }
    if (!domain || !center) {
        if (out_result) {
            out_result->refusal_reason = DOM_DOMAIN_REFUSE_INTERNAL;
        }
        return -1;
    }
    if (!dom_mining_domain_is_active(domain)) {
        if (out_result) {
            out_result->refusal_reason = DOM_DOMAIN_REFUSE_DOMAIN_INACTIVE;
        }
        return -2;
    }
    if (!domain->surface.law_allow_mining) {
        if (out_result) {
            out_result->flags |= DOM_MINING_RESULT_LAW_BLOCK;
            out_result->refusal_reason = DOM_DOMAIN_REFUSE_POLICY;
        }
        return -3;
    }
    if (!domain->surface.metalaw_allow_mining) {
        if (out_result) {
            out_result->flags |= DOM_MINING_RESULT_METALAW_BLOCK;
            out_result->refusal_reason = DOM_DOMAIN_REFUSE_POLICY;
        }
        return -4;
    }
    radius = dom_mining_abs_q16_16(radius);
    if (radius <= 0) {
        if (out_result) {
            out_result->refusal_reason = DOM_DOMAIN_REFUSE_POLICY;
        }
        return -5;
    }
    if (dom_terrain_sample_query(&domain->terrain_domain, center, (dom_domain_budget*)0, &terrain) != 0 ||
        dom_geology_sample_query(&domain->geology_domain, center, (dom_domain_budget*)0, &geology) != 0) {
        if (out_result) {
            out_result->refusal_reason = DOM_DOMAIN_REFUSE_INTERNAL;
        }
        return -6;
    }
    support = dom_mining_support_capacity(&terrain, &geology);
    stress = dom_mining_stress_from_radius(&domain->surface, radius);
    if (support == DOM_MINING_UNKNOWN_Q16) {
        if (out_result) {
            out_result->refusal_reason = DOM_DOMAIN_REFUSE_NO_ANALYTIC;
        }
        return -7;
    }
    if (out_result) {
        out_result->support_capacity = support;
        out_result->stress = stress;
        if (support > 0) {
            out_result->stress_ratio = d_fixed_div_q16_16(stress, support);
        } else if (stress > 0) {
            out_result->stress_ratio = (q16_16)0x7fffffff;
        }
        if (stress > support) {
            out_result->collapse_risk = 1u;
            out_result->flags |= DOM_MINING_RESULT_COLLAPSE_RISK;
            out_result->collapse_radius = d_q16_16_mul(radius, domain->surface.collapse_fill_scale);
        }
        out_result->ok = 1u;
    }
    return 0;
}

u32 dom_mining_overlay_count(const dom_mining_domain* domain)
{
    return domain ? domain->overlay_count : 0u;
}

const dom_mining_overlay* dom_mining_overlay_at(const dom_mining_domain* domain, u32 index)
{
    if (!domain || index >= domain->overlay_count) {
        return (const dom_mining_overlay*)0;
    }
    return &domain->overlays[index];
}

u32 dom_mining_chunk_count(const dom_mining_domain* domain)
{
    return domain ? domain->chunk_count : 0u;
}

const dom_material_chunk* dom_mining_chunk_at(const dom_mining_domain* domain, u32 index)
{
    if (!domain || index >= domain->chunk_count) {
        return (const dom_material_chunk*)0;
    }
    return &domain->chunks[index];
}
