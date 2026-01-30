/*
FILE: source/domino/world/geology_fields.cpp
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / world/geology_fields
RESPONSIBILITY: Implements deterministic geology and resource field sampling.
ALLOWED DEPENDENCIES: `include/domino/**` and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: Engine private headers outside world.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: Fixed-point only; deterministic ordering and math.
*/
#include "domino/world/geology_fields.h"

#include "domino/core/fixed_math.h"
#include "domino/core/rng_model.h"

#include <stdlib.h>
#include <string.h>

static q16_16 dom_geology_abs_q16_16(q16_16 v)
{
    return (v < 0) ? (q16_16)-v : v;
}

static q16_16 dom_geology_clamp_q16_16(q16_16 v, q16_16 lo, q16_16 hi)
{
    if (v < lo) {
        return lo;
    }
    if (v > hi) {
        return hi;
    }
    return v;
}

static i32 dom_geology_floor_div_q16(q16_16 value, q16_16 denom)
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

static u32 dom_geology_hash_u32(u64 seed, i32 x, i32 y, i32 z)
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

static q16_16 dom_geology_noise_sample(u64 seed,
                                       const dom_domain_point* point,
                                       q16_16 cell_size,
                                       q16_16 amplitude)
{
    i32 gx;
    i32 gy;
    i32 gz;
    u32 h;
    i32 sample;
    i64 scaled;
    if (!point || amplitude == 0) {
        return 0;
    }
    if (cell_size <= 0) {
        cell_size = d_q16_16_from_int(1);
    }
    gx = dom_geology_floor_div_q16(point->x, cell_size);
    gy = dom_geology_floor_div_q16(point->y, cell_size);
    gz = dom_geology_floor_div_q16(point->z, cell_size);
    h = dom_geology_hash_u32(seed, gx, gy, gz);
    sample = (i32)(h & 0xFFFFu);
    sample -= 32768;
    scaled = (i64)sample * (i64)amplitude;
    scaled /= 32768;
    if (scaled > 2147483647LL) {
        scaled = 2147483647LL;
    } else if (scaled < -2147483647LL - 1LL) {
        scaled = -2147483647LL - 1LL;
    }
    return (q16_16)scaled;
}

static q16_16 dom_geology_noise_ratio(u64 seed,
                                      const dom_domain_point* point,
                                      q16_16 cell_size)
{
    q16_16 sample = dom_geology_noise_sample(seed, point, cell_size, d_q16_16_from_int(1));
    return d_fixed_div_q16_16(d_q16_16_add(sample, d_q16_16_from_int(1)), d_q16_16_from_int(2));
}

static void dom_geology_cache_init(dom_geology_cache* cache)
{
    if (!cache) {
        return;
    }
    memset(cache, 0, sizeof(*cache));
}

static void dom_geology_tile_init(dom_geology_tile* tile)
{
    if (!tile) {
        return;
    }
    memset(tile, 0, sizeof(*tile));
}

static void dom_geology_tile_free(dom_geology_tile* tile)
{
    if (!tile) {
        return;
    }
    if (tile->data) {
        free(tile->data);
        tile->data = (q16_16 *)0;
    }
    if (tile->strata_ids) {
        free(tile->strata_ids);
        tile->strata_ids = (u32 *)0;
    }
    tile->hardness = (q16_16 *)0;
    tile->fracture_risk = (q16_16 *)0;
    tile->resource_density = (q16_16 *)0;
    tile->sample_count = 0u;
    tile->sample_dim = 0u;
    tile->tile_id = 0u;
    tile->resolution = DOM_DOMAIN_RES_REFUSED;
    memset(&tile->bounds, 0, sizeof(tile->bounds));
    tile->authoring_version = 0u;
}

static void dom_geology_cache_free(dom_geology_cache* cache)
{
    u32 i;
    if (!cache) {
        return;
    }
    if (cache->entries) {
        for (i = 0u; i < cache->capacity; ++i) {
            dom_geology_tile_free(&cache->entries[i].tile);
        }
        free(cache->entries);
        cache->entries = (dom_geology_cache_entry *)0;
    }
    cache->capacity = 0u;
    cache->count = 0u;
    cache->use_counter = 0u;
    cache->next_insert_order = 0u;
}

static int dom_geology_cache_reserve(dom_geology_cache* cache, u32 capacity)
{
    dom_geology_cache_entry* new_entries;
    u32 old_cap;
    u32 i;
    if (!cache) {
        return -1;
    }
    if (capacity <= cache->capacity) {
        return 0;
    }
    new_entries = (dom_geology_cache_entry *)realloc(cache->entries,
                                                     capacity * sizeof(dom_geology_cache_entry));
    if (!new_entries) {
        return -1;
    }
    old_cap = cache->capacity;
    cache->entries = new_entries;
    cache->capacity = capacity;
    for (i = old_cap; i < cache->capacity; ++i) {
        memset(&cache->entries[i], 0, sizeof(dom_geology_cache_entry));
        dom_geology_tile_init(&cache->entries[i].tile);
        cache->entries[i].valid = D_FALSE;
    }
    return 0;
}

static dom_geology_cache_entry* dom_geology_cache_find_entry(dom_geology_cache* cache,
                                                             dom_domain_id domain_id,
                                                             u64 tile_id,
                                                             u32 resolution,
                                                             u32 authoring_version)
{
    u32 i;
    if (!cache || !cache->entries) {
        return (dom_geology_cache_entry *)0;
    }
    for (i = 0u; i < cache->capacity; ++i) {
        dom_geology_cache_entry* entry = &cache->entries[i];
        if (!entry->valid) {
            continue;
        }
        if (entry->domain_id == domain_id &&
            entry->tile_id == tile_id &&
            entry->resolution == resolution &&
            entry->authoring_version == authoring_version) {
            return entry;
        }
    }
    return (dom_geology_cache_entry *)0;
}

static const dom_geology_tile* dom_geology_cache_peek(const dom_geology_cache* cache,
                                                      dom_domain_id domain_id,
                                                      u64 tile_id,
                                                      u32 resolution,
                                                      u32 authoring_version)
{
    u32 i;
    if (!cache || !cache->entries) {
        return (const dom_geology_tile *)0;
    }
    for (i = 0u; i < cache->capacity; ++i) {
        const dom_geology_cache_entry* entry = &cache->entries[i];
        if (!entry->valid) {
            continue;
        }
        if (entry->domain_id == domain_id &&
            entry->tile_id == tile_id &&
            entry->resolution == resolution &&
            entry->authoring_version == authoring_version) {
            return &entry->tile;
        }
    }
    return (const dom_geology_tile *)0;
}

static const dom_geology_tile* dom_geology_cache_get(dom_geology_cache* cache,
                                                     dom_domain_id domain_id,
                                                     u64 tile_id,
                                                     u32 resolution,
                                                     u32 authoring_version)
{
    dom_geology_cache_entry* entry;
    if (!cache) {
        return (const dom_geology_tile *)0;
    }
    entry = dom_geology_cache_find_entry(cache, domain_id, tile_id, resolution, authoring_version);
    if (!entry) {
        return (const dom_geology_tile *)0;
    }
    cache->use_counter += 1u;
    entry->last_used = cache->use_counter;
    return &entry->tile;
}

static dom_geology_cache_entry* dom_geology_cache_select_slot(dom_geology_cache* cache)
{
    u32 i;
    dom_geology_cache_entry* best = (dom_geology_cache_entry *)0;
    if (!cache || !cache->entries || cache->capacity == 0u) {
        return (dom_geology_cache_entry *)0;
    }
    for (i = 0u; i < cache->capacity; ++i) {
        dom_geology_cache_entry* entry = &cache->entries[i];
        if (!entry->valid) {
            return entry;
        }
        if (!best) {
            best = entry;
            continue;
        }
        if (entry->last_used < best->last_used) {
            best = entry;
        } else if (entry->last_used == best->last_used &&
                   entry->insert_order < best->insert_order) {
            best = entry;
        }
    }
    return best;
}

static dom_geology_tile* dom_geology_cache_put(dom_geology_cache* cache,
                                               dom_domain_id domain_id,
                                               dom_geology_tile* tile)
{
    dom_geology_cache_entry* entry;
    if (!cache || !tile) {
        return (dom_geology_tile *)0;
    }
    if (!cache->entries || cache->capacity == 0u) {
        return (dom_geology_tile *)0;
    }

    entry = dom_geology_cache_find_entry(cache, domain_id, tile->tile_id,
                                         tile->resolution, tile->authoring_version);
    if (!entry) {
        entry = dom_geology_cache_select_slot(cache);
    }
    if (!entry) {
        return (dom_geology_tile *)0;
    }
    if (entry->valid) {
        dom_geology_tile_free(&entry->tile);
    } else {
        cache->count += 1u;
        entry->insert_order = cache->next_insert_order++;
    }

    entry->domain_id = domain_id;
    entry->tile_id = tile->tile_id;
    entry->resolution = tile->resolution;
    entry->authoring_version = tile->authoring_version;
    entry->tile = *tile;
    entry->valid = D_TRUE;

    cache->use_counter += 1u;
    entry->last_used = cache->use_counter;

    dom_geology_tile_init(tile);
    return &entry->tile;
}

static void dom_geology_cache_invalidate_domain(dom_geology_cache* cache, dom_domain_id domain_id)
{
    u32 i;
    if (!cache || !cache->entries) {
        return;
    }
    for (i = 0u; i < cache->capacity; ++i) {
        dom_geology_cache_entry* entry = &cache->entries[i];
        if (entry->valid && entry->domain_id == domain_id) {
            dom_geology_tile_free(&entry->tile);
            entry->valid = D_FALSE;
            if (cache->count > 0u) {
                cache->count -= 1u;
            }
        }
    }
}

static q16_16 dom_geology_step_from_extent(q16_16 extent, u32 sample_dim)
{
    if (sample_dim <= 1u) {
        return 0;
    }
    return (q16_16)((i64)extent / (i64)(sample_dim - 1u));
}

static u32 dom_geology_sample_index_from_coord(q16_16 coord,
                                               q16_16 minv,
                                               q16_16 maxv,
                                               q16_16 step,
                                               u32 dim)
{
    i64 rel;
    i64 idx;
    i64 rem;
    if (dim <= 1u || step <= 0) {
        return 0u;
    }
    if (coord <= minv) {
        return 0u;
    }
    if (coord >= maxv) {
        return dim - 1u;
    }
    rel = (i64)coord - (i64)minv;
    idx = rel / (i64)step;
    rem = rel - (idx * (i64)step);
    if ((rem * 2) >= (i64)step && (u32)(idx + 1) < dim) {
        idx += 1;
    }
    if (idx < 0) {
        return 0u;
    }
    if ((u32)idx >= dim) {
        return dim - 1u;
    }
    return (u32)idx;
}

static void dom_geology_query_meta_refused(dom_domain_query_meta* meta,
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

static void dom_geology_query_meta_ok(dom_domain_query_meta* meta,
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

static d_bool dom_geology_resolution_allowed(u32 max_resolution, u32 resolution)
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

static d_bool dom_geology_domain_is_active(const dom_geology_domain* domain)
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

static u64 dom_geology_resource_seed(const dom_geology_surface_desc* desc, u32 resource_id)
{
    const char* stream = "noise.stream.geology.resource.base";
    u64 base_seed;
    if (!desc) {
        return 0u;
    }
    D_DET_GUARD_RNG_STREAM_NAME(stream);
    base_seed = desc->world_seed ^ (u64)resource_id;
    return (u64)d_rng_seed_from_context(base_seed,
                                        desc->domain_id,
                                        0u,
                                        0u,
                                        stream,
                                        D_RNG_MIX_DOMAIN | D_RNG_MIX_STREAM);
}

static u64 dom_geology_surface_seed(const dom_geology_surface_desc* desc)
{
    const char* stream = "noise.stream.geology.surface.base";
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

static void dom_geology_layer_select(const dom_geology_surface* surface,
                                     q16_16 depth,
                                     u32* out_index,
                                     const dom_geology_layer_desc** out_layer)
{
    q16_16 remaining = depth;
    u32 i;
    if (out_index) {
        *out_index = 0u;
    }
    if (out_layer) {
        *out_layer = (const dom_geology_layer_desc*)0;
    }
    if (!surface || surface->layer_count == 0u) {
        return;
    }
    for (i = 0u; i < surface->layer_count; ++i) {
        const dom_geology_layer_desc* layer = &surface->layers[i];
        q16_16 thickness = layer->thickness;
        if (thickness <= 0) {
            if (out_index) *out_index = i;
            if (out_layer) *out_layer = layer;
            return;
        }
        if (remaining <= thickness) {
            if (out_index) *out_index = i;
            if (out_layer) *out_layer = layer;
            return;
        }
        remaining = d_q16_16_sub(remaining, thickness);
    }
    if (out_index) {
        *out_index = surface->layer_count - 1u;
    }
    if (out_layer) {
        *out_layer = &surface->layers[surface->layer_count - 1u];
    }
}

static q16_16 dom_geology_resource_density(const dom_geology_resource_desc* res,
                                           const dom_domain_point* point)
{
    q16_16 density;
    q16_16 noise;
    q16_16 pocket_ratio;
    q16_16 pocket_cell;
    if (!res || !point) {
        return 0;
    }
    density = res->base_density;
    noise = dom_geology_noise_sample(res->seed, point, res->noise_cell_size, res->noise_amplitude);
    density = d_q16_16_add(density, noise);
    if (res->pocket_boost > 0) {
        pocket_cell = res->pocket_cell_size;
        if (pocket_cell <= 0) {
            pocket_cell = d_q16_16_mul(res->noise_cell_size, d_q16_16_from_int(4));
        }
        pocket_ratio = dom_geology_noise_ratio(res->seed ^ 0x9e3779b9u, point, pocket_cell);
        if (pocket_ratio >= res->pocket_threshold) {
            density = d_q16_16_add(density, res->pocket_boost);
        }
    }
    return dom_geology_clamp_q16_16(density, 0, d_q16_16_from_int(1));
}

static q16_16 dom_geology_surface_phi(const dom_geology_surface* surface,
                                      const dom_domain_point* point)
{
    const dom_domain_sdf_source* sdf;
    if (!surface || !point) {
        return 0;
    }
    sdf = dom_terrain_surface_sdf(&surface->terrain_surface);
    if (!sdf || !sdf->eval) {
        return 0;
    }
    return sdf->eval(sdf->ctx, point);
}

static void dom_geology_sample_init(dom_geology_sample* sample, u32 resource_count)
{
    if (!sample) {
        return;
    }
    memset(sample, 0, sizeof(*sample));
    sample->strata_layer_id = 0u;
    sample->strata_index = 0u;
    sample->hardness = DOM_GEOLOGY_UNKNOWN_Q16;
    sample->fracture_risk = DOM_GEOLOGY_UNKNOWN_Q16;
    sample->resource_count = resource_count;
    for (u32 i = 0u; i < resource_count && i < DOM_GEOLOGY_MAX_RESOURCES; ++i) {
        sample->resource_density[i] = DOM_GEOLOGY_UNKNOWN_Q16;
    }
}

static void dom_geology_eval_fields(const dom_geology_domain* domain,
                                    const dom_domain_point* point,
                                    dom_geology_sample* out_sample)
{
    const dom_geology_surface* surface;
    q16_16 phi;
    q16_16 depth;
    u32 layer_index = 0u;
    const dom_geology_layer_desc* layer = (const dom_geology_layer_desc*)0;
    u32 resource_count;
    u32 i;
    if (!domain || !point || !out_sample) {
        return;
    }
    surface = &domain->surface;
    resource_count = surface->resource_count;
    dom_geology_sample_init(out_sample, resource_count);
    phi = dom_geology_surface_phi(surface, point);
    if (phi > 0) {
        out_sample->flags |= DOM_GEOLOGY_SAMPLE_STRATA_UNKNOWN |
                             DOM_GEOLOGY_SAMPLE_FIELDS_UNKNOWN |
                             DOM_GEOLOGY_SAMPLE_RESOURCES_UNKNOWN;
        return;
    }
    depth = dom_geology_abs_q16_16(phi);
    dom_geology_layer_select(surface, depth, &layer_index, &layer);
    if (!layer) {
        out_sample->flags |= DOM_GEOLOGY_SAMPLE_STRATA_UNKNOWN |
                             DOM_GEOLOGY_SAMPLE_FIELDS_UNKNOWN;
        out_sample->hardness = surface->default_hardness;
        out_sample->fracture_risk = surface->default_fracture_risk;
    } else {
        out_sample->strata_layer_id = layer->layer_id;
        out_sample->strata_index = layer_index;
        out_sample->hardness = layer->hardness;
        if (layer->has_fracture) {
            out_sample->fracture_risk = layer->fracture_risk;
        } else {
            out_sample->fracture_risk = DOM_GEOLOGY_UNKNOWN_Q16;
            out_sample->flags |= DOM_GEOLOGY_SAMPLE_FIELDS_UNKNOWN;
        }
    }
    for (i = 0u; i < resource_count; ++i) {
        out_sample->resource_density[i] = dom_geology_resource_density(&surface->resources[i], point);
    }
}

static q16_16 dom_geology_tile_sample_scalar(const dom_geology_tile* tile,
                                             const dom_domain_point* point,
                                             q16_16* array)
{
    u32 ix;
    u32 iy;
    u32 iz;
    q16_16 step_x;
    q16_16 step_y;
    q16_16 step_z;
    q16_16 px;
    q16_16 py;
    q16_16 pz;
    if (!tile || !array || tile->sample_dim == 0u) {
        return 0;
    }
    px = dom_geology_clamp_q16_16(point->x, tile->bounds.min.x, tile->bounds.max.x);
    py = dom_geology_clamp_q16_16(point->y, tile->bounds.min.y, tile->bounds.max.y);
    pz = dom_geology_clamp_q16_16(point->z, tile->bounds.min.z, tile->bounds.max.z);

    step_x = dom_geology_step_from_extent((q16_16)(tile->bounds.max.x - tile->bounds.min.x), tile->sample_dim);
    step_y = dom_geology_step_from_extent((q16_16)(tile->bounds.max.y - tile->bounds.min.y), tile->sample_dim);
    step_z = dom_geology_step_from_extent((q16_16)(tile->bounds.max.z - tile->bounds.min.z), tile->sample_dim);

    ix = dom_geology_sample_index_from_coord(px, tile->bounds.min.x, tile->bounds.max.x, step_x, tile->sample_dim);
    iy = dom_geology_sample_index_from_coord(py, tile->bounds.min.y, tile->bounds.max.y, step_y, tile->sample_dim);
    iz = dom_geology_sample_index_from_coord(pz, tile->bounds.min.z, tile->bounds.max.z, step_z, tile->sample_dim);

    return array[(iz * tile->sample_dim * tile->sample_dim) + (iy * tile->sample_dim) + ix];
}

static u32 dom_geology_tile_sample_strata(const dom_geology_tile* tile,
                                          const dom_domain_point* point)
{
    u32 ix;
    u32 iy;
    u32 iz;
    q16_16 step_x;
    q16_16 step_y;
    q16_16 step_z;
    q16_16 px;
    q16_16 py;
    q16_16 pz;
    if (!tile || !tile->strata_ids || tile->sample_dim == 0u) {
        return 0u;
    }
    px = dom_geology_clamp_q16_16(point->x, tile->bounds.min.x, tile->bounds.max.x);
    py = dom_geology_clamp_q16_16(point->y, tile->bounds.min.y, tile->bounds.max.y);
    pz = dom_geology_clamp_q16_16(point->z, tile->bounds.min.z, tile->bounds.max.z);

    step_x = dom_geology_step_from_extent((q16_16)(tile->bounds.max.x - tile->bounds.min.x), tile->sample_dim);
    step_y = dom_geology_step_from_extent((q16_16)(tile->bounds.max.y - tile->bounds.min.y), tile->sample_dim);
    step_z = dom_geology_step_from_extent((q16_16)(tile->bounds.max.z - tile->bounds.min.z), tile->sample_dim);

    ix = dom_geology_sample_index_from_coord(px, tile->bounds.min.x, tile->bounds.max.x, step_x, tile->sample_dim);
    iy = dom_geology_sample_index_from_coord(py, tile->bounds.min.y, tile->bounds.max.y, step_y, tile->sample_dim);
    iz = dom_geology_sample_index_from_coord(pz, tile->bounds.min.z, tile->bounds.max.z, step_z, tile->sample_dim);

    return tile->strata_ids[(iz * tile->sample_dim * tile->sample_dim) + (iy * tile->sample_dim) + ix];
}

static int dom_geology_tile_build(dom_geology_tile* tile,
                                  const dom_domain_tile_desc* desc,
                                  const dom_geology_domain* domain)
{
    u32 i;
    u32 j;
    u32 k;
    u32 dim;
    q16_16 step_x;
    q16_16 step_y;
    q16_16 step_z;
    u32 sample_count;
    u32 resource_count;
    size_t data_count;
    if (!tile || !desc || !domain) {
        return -1;
    }

    dim = desc->sample_dim;
    if (dim == 0u) {
        return -1;
    }

    dom_geology_tile_free(tile);
    dom_geology_tile_init(tile);

    tile->tile_id = desc->tile_id;
    tile->resolution = desc->resolution;
    tile->sample_dim = dim;
    tile->bounds = desc->bounds;
    tile->authoring_version = desc->authoring_version;

    sample_count = dim * dim * dim;
    tile->sample_count = sample_count;
    resource_count = domain->surface.resource_count;
    tile->resource_count = resource_count;

    data_count = (size_t)(2u + resource_count) * (size_t)sample_count;
    tile->data = (q16_16 *)malloc(sizeof(q16_16) * data_count);
    tile->strata_ids = (u32 *)malloc(sizeof(u32) * sample_count);
    if (!tile->data || !tile->strata_ids) {
        dom_geology_tile_free(tile);
        return -1;
    }

    tile->hardness = tile->data;
    tile->fracture_risk = tile->data + sample_count;
    tile->resource_density = tile->data + (2u * sample_count);

    step_x = dom_geology_step_from_extent((q16_16)(tile->bounds.max.x - tile->bounds.min.x), dim);
    step_y = dom_geology_step_from_extent((q16_16)(tile->bounds.max.y - tile->bounds.min.y), dim);
    step_z = dom_geology_step_from_extent((q16_16)(tile->bounds.max.z - tile->bounds.min.z), dim);

    for (k = 0u; k < dim; ++k) {
        q16_16 pz = (k == dim - 1u)
            ? tile->bounds.max.z
            : (q16_16)(tile->bounds.min.z + (q16_16)((i64)step_z * (i64)k));
        for (j = 0u; j < dim; ++j) {
            q16_16 py = (j == dim - 1u)
                ? tile->bounds.max.y
                : (q16_16)(tile->bounds.min.y + (q16_16)((i64)step_y * (i64)j));
            for (i = 0u; i < dim; ++i) {
                q16_16 px = (i == dim - 1u)
                    ? tile->bounds.max.x
                    : (q16_16)(tile->bounds.min.x + (q16_16)((i64)step_x * (i64)i));
                dom_domain_point p;
                dom_geology_sample sample;
                u32 idx = (k * dim * dim) + (j * dim) + i;
                p.x = px;
                p.y = py;
                p.z = pz;
                dom_geology_eval_fields(domain, &p, &sample);
                tile->strata_ids[idx] = sample.strata_layer_id;
                tile->hardness[idx] = sample.hardness;
                tile->fracture_risk[idx] = sample.fracture_risk;
                for (u32 r = 0u; r < resource_count; ++r) {
                    tile->resource_density[r * sample_count + idx] = sample.resource_density[r];
                }
            }
        }
    }

    return 0;
}

static void dom_geology_sample_from_tile(const dom_geology_tile* tile,
                                         const dom_domain_point* point,
                                         dom_geology_sample* out_sample)
{
    u32 resource_count;
    if (!tile || !point || !out_sample) {
        return;
    }
    resource_count = tile->resource_count;
    dom_geology_sample_init(out_sample, resource_count);
    out_sample->strata_layer_id = dom_geology_tile_sample_strata(tile, point);
    out_sample->hardness = dom_geology_tile_sample_scalar(tile, point, tile->hardness);
    out_sample->fracture_risk = dom_geology_tile_sample_scalar(tile, point, tile->fracture_risk);
    for (u32 r = 0u; r < resource_count; ++r) {
        out_sample->resource_density[r] = dom_geology_tile_sample_scalar(tile, point,
                                                                         tile->resource_density + (r * tile->sample_count));
    }
}

static q16_16 dom_geology_hist_bin_ratio(u32 count, u32 total)
{
    if (total == 0u) {
        return 0;
    }
    return (q16_16)((((i64)count) << 16) / (i64)total);
}

static u32 dom_geology_hist_bin(q16_16 value)
{
    q16_16 clamped = dom_geology_clamp_q16_16(value, 0, d_q16_16_from_int(1));
    u32 scaled = (u32)(((i64)clamped * (DOM_GEOLOGY_HIST_BINS - 1u)) >> 16);
    if (scaled >= DOM_GEOLOGY_HIST_BINS) {
        scaled = DOM_GEOLOGY_HIST_BINS - 1u;
    }
    return scaled;
}

static int dom_geology_build_tile_desc(const dom_geology_domain* domain,
                                       const dom_domain_point* point,
                                       u32 resolution,
                                       dom_domain_tile_desc* out_desc)
{
    const dom_domain_sdf_source* source;
    q16_16 tile_size;
    i32 tx;
    i32 ty;
    i32 tz;
    u32 sample_dim;
    if (!domain || !point || !out_desc) {
        return -1;
    }
    source = dom_terrain_surface_sdf(&domain->surface.terrain_surface);
    if (!source) {
        return -1;
    }
    tile_size = domain->policy.tile_size;
    if (tile_size <= 0) {
        return -1;
    }
    if (resolution == DOM_DOMAIN_RES_FULL) {
        sample_dim = domain->policy.sample_dim_full;
    } else if (resolution == DOM_DOMAIN_RES_MEDIUM) {
        sample_dim = domain->policy.sample_dim_medium;
    } else {
        sample_dim = domain->policy.sample_dim_coarse;
    }
    if (sample_dim == 0u) {
        return -1;
    }
    tx = dom_geology_floor_div_q16((q16_16)(point->x - source->bounds.min.x), tile_size);
    ty = dom_geology_floor_div_q16((q16_16)(point->y - source->bounds.min.y), tile_size);
    tz = dom_geology_floor_div_q16((q16_16)(point->z - source->bounds.min.z), tile_size);
    dom_domain_tile_desc_init(out_desc);
    out_desc->resolution = resolution;
    out_desc->sample_dim = sample_dim;
    out_desc->tile_id = dom_domain_tile_id_from_coord(tx, ty, tz, resolution);
    out_desc->authoring_version = domain->authoring_version;

    {
        dom_domain_point minp;
        dom_domain_point maxp;
        minp.x = (q16_16)(source->bounds.min.x + (q16_16)((i64)tx * (i64)tile_size));
        minp.y = (q16_16)(source->bounds.min.y + (q16_16)((i64)ty * (i64)tile_size));
        minp.z = (q16_16)(source->bounds.min.z + (q16_16)((i64)tz * (i64)tile_size));

        maxp.x = (q16_16)(minp.x + tile_size);
        maxp.y = (q16_16)(minp.y + tile_size);
        maxp.z = (q16_16)(minp.z + tile_size);

        if (maxp.x > source->bounds.max.x) maxp.x = source->bounds.max.x;
        if (maxp.y > source->bounds.max.y) maxp.y = source->bounds.max.y;
        if (maxp.z > source->bounds.max.z) maxp.z = source->bounds.max.z;

        if (minp.x < source->bounds.min.x) minp.x = source->bounds.min.x;
        if (minp.y < source->bounds.min.y) minp.y = source->bounds.min.y;
        if (minp.z < source->bounds.min.z) minp.z = source->bounds.min.z;

        out_desc->bounds.min = minp;
        out_desc->bounds.max = maxp;
    }
    return 0;
}

static const dom_geology_tile* dom_geology_tile_get(dom_geology_domain* domain,
                                                    const dom_domain_tile_desc* desc,
                                                    d_bool allow_build)
{
    if (!domain || !desc) {
        return (const dom_geology_tile *)0;
    }
    if (domain->cache.entries) {
        const dom_geology_tile* cached = dom_geology_cache_get(&domain->cache,
                                                               domain->surface.domain_id,
                                                               desc->tile_id,
                                                               desc->resolution,
                                                               desc->authoring_version);
        if (cached) {
            return cached;
        }
        if (!allow_build) {
            return (const dom_geology_tile *)0;
        }
        {
            dom_geology_tile temp;
            dom_geology_tile_init(&temp);
            if (dom_geology_tile_build(&temp, desc, domain) != 0) {
                dom_geology_tile_free(&temp);
                return (const dom_geology_tile *)0;
            }
            cached = dom_geology_cache_put(&domain->cache, domain->surface.domain_id, &temp);
            if (!cached) {
                dom_geology_tile_free(&temp);
                return (const dom_geology_tile *)0;
            }
            return cached;
        }
    }
    return (const dom_geology_tile *)0;
}

static d_bool dom_geology_tile_cached(const dom_geology_domain* domain, const dom_domain_tile_desc* desc)
{
    if (!domain || !desc) {
        return D_FALSE;
    }
    return dom_geology_cache_peek(&domain->cache,
                                  domain->surface.domain_id,
                                  desc->tile_id,
                                  desc->resolution,
                                  desc->authoring_version) != (const dom_geology_tile *)0;
}

void dom_geology_surface_desc_init(dom_geology_surface_desc* desc)
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
    desc->noise.cell_size = d_q16_16_from_int(16);
    desc->noise.amplitude = 0;
    desc->layer_count = 1u;
    desc->layers[0].layer_id = 1u;
    desc->layers[0].thickness = d_q16_16_from_int(1024);
    desc->layers[0].hardness = d_q16_16_from_int(1);
    desc->layers[0].fracture_risk = 0;
    desc->layers[0].has_fracture = 0u;
    desc->resource_count = 0u;
    desc->default_hardness = d_q16_16_from_int(1);
    desc->default_fracture_risk = 0;
}

void dom_geology_surface_init(dom_geology_surface* surface, const dom_geology_surface_desc* desc)
{
    dom_terrain_surface_desc terrain_desc;
    if (!surface || !desc) {
        return;
    }
    memset(surface, 0, sizeof(*surface));
    surface->domain_id = desc->domain_id;
    surface->world_seed = desc->world_seed;
    surface->meters_per_unit = desc->meters_per_unit;
    surface->shape = desc->shape;
    surface->noise = desc->noise;
    surface->noise.seed = dom_geology_surface_seed(desc);
    surface->layer_count = desc->layer_count;
    if (surface->layer_count > DOM_GEOLOGY_MAX_LAYERS) {
        surface->layer_count = DOM_GEOLOGY_MAX_LAYERS;
    }
    for (u32 i = 0u; i < surface->layer_count; ++i) {
        surface->layers[i] = desc->layers[i];
    }
    surface->resource_count = desc->resource_count;
    if (surface->resource_count > DOM_GEOLOGY_MAX_RESOURCES) {
        surface->resource_count = DOM_GEOLOGY_MAX_RESOURCES;
    }
    for (u32 i = 0u; i < surface->resource_count; ++i) {
        surface->resources[i] = desc->resources[i];
        surface->resources[i].seed = dom_geology_resource_seed(desc, surface->resources[i].resource_id);
    }
    surface->default_hardness = desc->default_hardness;
    surface->default_fracture_risk = desc->default_fracture_risk;

    dom_terrain_surface_desc_init(&terrain_desc);
    terrain_desc.domain_id = desc->domain_id;
    terrain_desc.world_seed = desc->world_seed;
    terrain_desc.meters_per_unit = desc->meters_per_unit;
    terrain_desc.shape = desc->shape;
    terrain_desc.noise = desc->noise;
    dom_terrain_surface_init(&surface->terrain_surface, &terrain_desc);
}

void dom_geology_domain_init(dom_geology_domain* domain,
                             const dom_geology_surface_desc* desc,
                             u32 cache_capacity)
{
    if (!domain || !desc) {
        return;
    }
    memset(domain, 0, sizeof(*domain));
    dom_geology_surface_init(&domain->surface, desc);
    dom_domain_policy_init(&domain->policy);
    domain->existence_state = DOM_DOMAIN_EXISTENCE_REALIZED;
    domain->archival_state = DOM_DOMAIN_ARCHIVAL_LIVE;
    domain->authoring_version = 1u;
    dom_geology_cache_init(&domain->cache);
    if (cache_capacity > 0u) {
        dom_geology_cache_reserve(&domain->cache, cache_capacity);
    }
    domain->capsule_count = 0u;
}

void dom_geology_domain_free(dom_geology_domain* domain)
{
    if (!domain) {
        return;
    }
    dom_geology_cache_free(&domain->cache);
    domain->capsule_count = 0u;
}

void dom_geology_domain_set_state(dom_geology_domain* domain,
                                  u32 existence_state,
                                  u32 archival_state)
{
    if (!domain) {
        return;
    }
    if (domain->existence_state != existence_state || domain->archival_state != archival_state) {
        domain->existence_state = existence_state;
        domain->archival_state = archival_state;
        dom_geology_cache_invalidate_domain(&domain->cache, domain->surface.domain_id);
    }
}

void dom_geology_domain_set_policy(dom_geology_domain* domain,
                                   const dom_domain_policy* policy)
{
    if (!domain || !policy) {
        return;
    }
    domain->policy = *policy;
    dom_geology_cache_invalidate_domain(&domain->cache, domain->surface.domain_id);
}

int dom_geology_sample_query(const dom_geology_domain* domain,
                             const dom_domain_point* point,
                             dom_domain_budget* budget,
                             dom_geology_sample* out_sample)
{
    dom_domain_tile_desc desc;
    const dom_domain_sdf_source* source;
    u32 cost;
    d_bool collapsed = D_FALSE;
    u32 resource_count;
    if (!domain || !point || !out_sample) {
        return -1;
    }
    resource_count = domain->surface.resource_count;
    dom_geology_sample_init(out_sample, resource_count);

    if (!dom_geology_domain_is_active(domain)) {
        dom_geology_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_DOMAIN_INACTIVE, budget);
        out_sample->flags |= DOM_GEOLOGY_SAMPLE_STRATA_UNKNOWN |
                             DOM_GEOLOGY_SAMPLE_FIELDS_UNKNOWN |
                             DOM_GEOLOGY_SAMPLE_RESOURCES_UNKNOWN;
        return 0;
    }

    source = dom_terrain_surface_sdf(&domain->surface.terrain_surface);
    if (!source || !source->eval) {
        dom_geology_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_NO_SOURCE, budget);
        out_sample->flags |= DOM_GEOLOGY_SAMPLE_STRATA_UNKNOWN |
                             DOM_GEOLOGY_SAMPLE_FIELDS_UNKNOWN |
                             DOM_GEOLOGY_SAMPLE_RESOURCES_UNKNOWN;
        return 0;
    }

    if (!dom_domain_aabb_contains(&source->bounds, point)) {
        dom_geology_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_COARSE,
                                  DOM_DOMAIN_CONFIDENCE_LOWER_BOUND, 0u, budget);
        out_sample->flags |= DOM_GEOLOGY_SAMPLE_STRATA_UNKNOWN |
                             DOM_GEOLOGY_SAMPLE_FIELDS_UNKNOWN |
                             DOM_GEOLOGY_SAMPLE_RESOURCES_UNKNOWN;
        return 0;
    }

    if (domain->capsule_count > 0u) {
        for (u32 i = 0u; i < domain->capsule_count; ++i) {
            if (dom_domain_aabb_contains(&domain->capsules[i].bounds, point)) {
                collapsed = D_TRUE;
                break;
            }
        }
    }
    if (collapsed) {
        dom_geology_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                                  DOM_DOMAIN_CONFIDENCE_UNKNOWN, 0u, budget);
        out_sample->flags |= DOM_GEOLOGY_SAMPLE_STRATA_UNKNOWN |
                             DOM_GEOLOGY_SAMPLE_FIELDS_UNKNOWN |
                             DOM_GEOLOGY_SAMPLE_RESOURCES_UNKNOWN |
                             DOM_GEOLOGY_SAMPLE_COLLAPSED;
        return 0;
    }

    if (dom_geology_resolution_allowed(domain->policy.max_resolution, DOM_DOMAIN_RES_FULL)) {
        cost = domain->policy.cost_full;
        if (dom_domain_budget_consume(budget, cost)) {
            dom_geology_eval_fields(domain, point, out_sample);
            dom_geology_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_FULL,
                                      DOM_DOMAIN_CONFIDENCE_EXACT, cost, budget);
            return 0;
        }
    }

    if (dom_geology_resolution_allowed(domain->policy.max_resolution, DOM_DOMAIN_RES_MEDIUM)) {
        cost = domain->policy.cost_medium;
        if (dom_geology_build_tile_desc(domain, point, DOM_DOMAIN_RES_MEDIUM, &desc) == 0) {
            if (!dom_geology_tile_cached(domain, &desc)) {
                cost += domain->policy.tile_build_cost_medium;
            }
            if (dom_domain_budget_consume(budget, cost)) {
                const dom_geology_tile* tile = dom_geology_tile_get((dom_geology_domain*)domain, &desc, D_TRUE);
                if (!tile) {
                    dom_geology_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_INTERNAL, budget);
                    out_sample->flags |= DOM_GEOLOGY_SAMPLE_STRATA_UNKNOWN |
                                         DOM_GEOLOGY_SAMPLE_FIELDS_UNKNOWN |
                                         DOM_GEOLOGY_SAMPLE_RESOURCES_UNKNOWN;
                    return 0;
                }
                dom_geology_sample_from_tile(tile, point, out_sample);
                dom_geology_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_MEDIUM,
                                          DOM_DOMAIN_CONFIDENCE_LOWER_BOUND, cost, budget);
                return 0;
            }
        }
    }

    if (dom_geology_resolution_allowed(domain->policy.max_resolution, DOM_DOMAIN_RES_COARSE)) {
        cost = domain->policy.cost_coarse;
        if (dom_geology_build_tile_desc(domain, point, DOM_DOMAIN_RES_COARSE, &desc) == 0) {
            if (!dom_geology_tile_cached(domain, &desc)) {
                cost += domain->policy.tile_build_cost_coarse;
            }
            if (dom_domain_budget_consume(budget, cost)) {
                const dom_geology_tile* tile = dom_geology_tile_get((dom_geology_domain*)domain, &desc, D_TRUE);
                if (!tile) {
                    dom_geology_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_INTERNAL, budget);
                    out_sample->flags |= DOM_GEOLOGY_SAMPLE_STRATA_UNKNOWN |
                                         DOM_GEOLOGY_SAMPLE_FIELDS_UNKNOWN |
                                         DOM_GEOLOGY_SAMPLE_RESOURCES_UNKNOWN;
                    return 0;
                }
                dom_geology_sample_from_tile(tile, point, out_sample);
                dom_geology_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_COARSE,
                                          DOM_DOMAIN_CONFIDENCE_LOWER_BOUND, cost, budget);
                return 0;
            }
        }
    }

    if (dom_geology_resolution_allowed(domain->policy.max_resolution, DOM_DOMAIN_RES_ANALYTIC)) {
        cost = domain->policy.cost_analytic;
        if (dom_domain_budget_consume(budget, cost)) {
            dom_geology_eval_fields(domain, point, out_sample);
            dom_geology_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                                      DOM_DOMAIN_CONFIDENCE_EXACT, cost, budget);
            return 0;
        }
    }

    dom_geology_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_BUDGET, budget);
    out_sample->flags |= DOM_GEOLOGY_SAMPLE_STRATA_UNKNOWN |
                         DOM_GEOLOGY_SAMPLE_FIELDS_UNKNOWN |
                         DOM_GEOLOGY_SAMPLE_RESOURCES_UNKNOWN;
    return 0;
}

static int dom_geology_capsule_store(dom_geology_domain* domain,
                                     const dom_domain_tile_desc* desc)
{
    dom_geology_macro_capsule capsule;
    dom_geology_tile tile;
    u32 layer_counts[DOM_GEOLOGY_MAX_LAYERS];
    u32 hardness_bins[DOM_GEOLOGY_HIST_BINS];
    u32 resource_bins[DOM_GEOLOGY_MAX_RESOURCES][DOM_GEOLOGY_HIST_BINS];
    q16_16 resource_sum[DOM_GEOLOGY_MAX_RESOURCES];
    u32 sample_count;
    u32 resource_count;
    if (!domain || !desc) {
        return -1;
    }
    if (domain->capsule_count >= DOM_GEOLOGY_MAX_CAPSULES) {
        return -2;
    }

    memset(layer_counts, 0, sizeof(layer_counts));
    memset(hardness_bins, 0, sizeof(hardness_bins));
    memset(resource_bins, 0, sizeof(resource_bins));
    memset(resource_sum, 0, sizeof(resource_sum));

    dom_geology_tile_init(&tile);
    if (dom_geology_tile_build(&tile, desc, domain) != 0) {
        dom_geology_tile_free(&tile);
        return -1;
    }

    sample_count = tile.sample_count;
    resource_count = domain->surface.resource_count;
    for (u32 i = 0u; i < sample_count; ++i) {
        u32 layer_index = 0u;
        for (u32 l = 0u; l < domain->surface.layer_count; ++l) {
            if (domain->surface.layers[l].layer_id == tile.strata_ids[i]) {
                layer_index = l;
                break;
            }
        }
        if (layer_index < DOM_GEOLOGY_MAX_LAYERS) {
            layer_counts[layer_index] += 1u;
        }
        hardness_bins[dom_geology_hist_bin(tile.hardness[i])] += 1u;
        for (u32 r = 0u; r < resource_count; ++r) {
            q16_16 value = tile.resource_density[r * sample_count + i];
            resource_bins[r][dom_geology_hist_bin(value)] += 1u;
            resource_sum[r] = d_q16_16_add(resource_sum[r], value);
        }
    }

    memset(&capsule, 0, sizeof(capsule));
    capsule.capsule_id = desc->tile_id;
    capsule.tile_id = desc->tile_id;
    capsule.bounds = desc->bounds;
    capsule.sample_count = sample_count;
    capsule.layer_count = domain->surface.layer_count;
    for (u32 l = 0u; l < capsule.layer_count; ++l) {
        capsule.layer_ids[l] = domain->surface.layers[l].layer_id;
        capsule.layer_sample_counts[l] = layer_counts[l];
    }
    for (u32 b = 0u; b < DOM_GEOLOGY_HIST_BINS; ++b) {
        capsule.hardness_hist[b] = dom_geology_hist_bin_ratio(hardness_bins[b], sample_count);
    }
    for (u32 r = 0u; r < resource_count; ++r) {
        for (u32 b = 0u; b < DOM_GEOLOGY_HIST_BINS; ++b) {
            capsule.resource_hist[r][b] = dom_geology_hist_bin_ratio(resource_bins[r][b], sample_count);
        }
        capsule.resource_total[r] = dom_geology_hist_bin_ratio((u32)(resource_sum[r] >> 16), sample_count);
    }

    dom_geology_tile_free(&tile);
    domain->capsules[domain->capsule_count++] = capsule;
    return 0;
}

int dom_geology_domain_collapse_tile(dom_geology_domain* domain,
                                     const dom_domain_tile_desc* desc)
{
    u32 i;
    if (!domain || !desc) {
        return -1;
    }
    if (domain->cache.entries) {
        for (i = 0u; i < domain->cache.capacity; ++i) {
            dom_geology_cache_entry* entry = &domain->cache.entries[i];
            if (!entry->valid) {
                continue;
            }
            if (entry->domain_id == domain->surface.domain_id &&
                entry->tile_id == desc->tile_id) {
                dom_geology_tile_free(&entry->tile);
                entry->valid = D_FALSE;
                if (domain->cache.count > 0u) {
                    domain->cache.count -= 1u;
                }
            }
        }
    }
    return dom_geology_capsule_store(domain, desc);
}

int dom_geology_domain_expand_tile(dom_geology_domain* domain, u64 tile_id)
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

u32 dom_geology_domain_capsule_count(const dom_geology_domain* domain)
{
    return domain ? domain->capsule_count : 0u;
}

const dom_geology_macro_capsule* dom_geology_domain_capsule_at(const dom_geology_domain* domain,
                                                               u32 index)
{
    if (!domain || index >= domain->capsule_count) {
        return (const dom_geology_macro_capsule*)0;
    }
    return &domain->capsules[index];
}
