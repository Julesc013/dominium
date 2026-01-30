/*
FILE: source/domino/world/climate_fields.cpp
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / world/climate_fields
RESPONSIBILITY: Implements deterministic climate envelope sampling and biome classification.
ALLOWED DEPENDENCIES: `include/domino/**` and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: Engine private headers outside world.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: Fixed-point only; deterministic ordering and math.
*/
#include "domino/world/climate_fields.h"

#include "domino/core/fixed_math.h"
#include "domino/core/rng_model.h"

#include <stdlib.h>
#include <string.h>

typedef struct dom_climate_latlon {
    q16_16 latitude;
    q16_16 longitude;
    q16_16 altitude;
    u32 valid;
} dom_climate_latlon;

static q16_16 dom_climate_abs_q16_16(q16_16 v)
{
    return (v < 0) ? (q16_16)-v : v;
}

static q16_16 dom_climate_clamp_q16_16(q16_16 v, q16_16 lo, q16_16 hi)
{
    if (v < lo) {
        return lo;
    }
    if (v > hi) {
        return hi;
    }
    return v;
}

static i32 dom_climate_floor_div_q16(q16_16 value, q16_16 denom)
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

static u32 dom_climate_hash_u32(u64 seed, i32 x, i32 y, i32 z)
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

static q16_16 dom_climate_noise_sample(u64 seed,
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
    gx = dom_climate_floor_div_q16(point->x, cell_size);
    gy = dom_climate_floor_div_q16(point->y, cell_size);
    gz = dom_climate_floor_div_q16(point->z, cell_size);
    h = dom_climate_hash_u32(seed, gx, gy, gz);
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

static q16_16 dom_climate_noise_ratio(u64 seed,
                                      const dom_domain_point* point,
                                      q16_16 cell_size)
{
    q16_16 sample = dom_climate_noise_sample(seed, point, cell_size, d_q16_16_from_int(1));
    return d_fixed_div_q16_16(d_q16_16_add(sample, d_q16_16_from_int(1)), d_q16_16_from_int(2));
}

static void dom_climate_cache_init(dom_climate_cache* cache)
{
    if (!cache) {
        return;
    }
    memset(cache, 0, sizeof(*cache));
}

static void dom_climate_tile_init(dom_climate_tile* tile)
{
    if (!tile) {
        return;
    }
    memset(tile, 0, sizeof(*tile));
}

static void dom_climate_tile_free(dom_climate_tile* tile)
{
    if (!tile) {
        return;
    }
    if (tile->data) {
        free(tile->data);
        tile->data = (q16_16*)0;
    }
    if (tile->wind_prevailing) {
        free(tile->wind_prevailing);
        tile->wind_prevailing = (u32*)0;
    }
    tile->temperature_mean = (q16_16*)0;
    tile->temperature_range = (q16_16*)0;
    tile->precipitation_mean = (q16_16*)0;
    tile->precipitation_range = (q16_16*)0;
    tile->seasonality = (q16_16*)0;
    tile->sample_count = 0u;
    tile->sample_dim = 0u;
    tile->tile_id = 0u;
    tile->resolution = DOM_DOMAIN_RES_REFUSED;
    memset(&tile->bounds, 0, sizeof(tile->bounds));
    tile->authoring_version = 0u;
}

static void dom_climate_cache_free(dom_climate_cache* cache)
{
    u32 i;
    if (!cache) {
        return;
    }
    if (cache->entries) {
        for (i = 0u; i < cache->capacity; ++i) {
            dom_climate_tile_free(&cache->entries[i].tile);
        }
        free(cache->entries);
        cache->entries = (dom_climate_cache_entry*)0;
    }
    cache->capacity = 0u;
    cache->count = 0u;
    cache->use_counter = 0u;
    cache->next_insert_order = 0u;
}

static int dom_climate_cache_reserve(dom_climate_cache* cache, u32 capacity)
{
    dom_climate_cache_entry* new_entries;
    u32 old_cap;
    u32 i;
    if (!cache) {
        return -1;
    }
    if (capacity <= cache->capacity) {
        return 0;
    }
    new_entries = (dom_climate_cache_entry*)realloc(cache->entries,
                                                   capacity * sizeof(dom_climate_cache_entry));
    if (!new_entries) {
        return -1;
    }
    old_cap = cache->capacity;
    cache->entries = new_entries;
    cache->capacity = capacity;
    for (i = old_cap; i < cache->capacity; ++i) {
        memset(&cache->entries[i], 0, sizeof(dom_climate_cache_entry));
        dom_climate_tile_init(&cache->entries[i].tile);
        cache->entries[i].valid = D_FALSE;
    }
    return 0;
}

static dom_climate_cache_entry* dom_climate_cache_find_entry(dom_climate_cache* cache,
                                                             dom_domain_id domain_id,
                                                             u64 tile_id,
                                                             u32 resolution,
                                                             u32 authoring_version)
{
    u32 i;
    if (!cache || !cache->entries) {
        return (dom_climate_cache_entry*)0;
    }
    for (i = 0u; i < cache->capacity; ++i) {
        dom_climate_cache_entry* entry = &cache->entries[i];
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
    return (dom_climate_cache_entry*)0;
}

static const dom_climate_tile* dom_climate_cache_peek(const dom_climate_cache* cache,
                                                      dom_domain_id domain_id,
                                                      u64 tile_id,
                                                      u32 resolution,
                                                      u32 authoring_version)
{
    u32 i;
    if (!cache || !cache->entries) {
        return (const dom_climate_tile*)0;
    }
    for (i = 0u; i < cache->capacity; ++i) {
        const dom_climate_cache_entry* entry = &cache->entries[i];
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
    return (const dom_climate_tile*)0;
}

static const dom_climate_tile* dom_climate_cache_get(dom_climate_cache* cache,
                                                     dom_domain_id domain_id,
                                                     u64 tile_id,
                                                     u32 resolution,
                                                     u32 authoring_version)
{
    dom_climate_cache_entry* entry;
    if (!cache) {
        return (const dom_climate_tile*)0;
    }
    entry = dom_climate_cache_find_entry(cache, domain_id, tile_id, resolution, authoring_version);
    if (!entry) {
        return (const dom_climate_tile*)0;
    }
    cache->use_counter += 1u;
    entry->last_used = cache->use_counter;
    return &entry->tile;
}

static dom_climate_cache_entry* dom_climate_cache_select_slot(dom_climate_cache* cache)
{
    u32 i;
    dom_climate_cache_entry* best = (dom_climate_cache_entry*)0;
    if (!cache || !cache->entries || cache->capacity == 0u) {
        return (dom_climate_cache_entry*)0;
    }
    for (i = 0u; i < cache->capacity; ++i) {
        dom_climate_cache_entry* entry = &cache->entries[i];
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

static dom_climate_tile* dom_climate_cache_put(dom_climate_cache* cache,
                                               dom_domain_id domain_id,
                                               dom_climate_tile* tile)
{
    dom_climate_cache_entry* entry;
    if (!cache || !tile) {
        return (dom_climate_tile*)0;
    }
    if (!cache->entries || cache->capacity == 0u) {
        return (dom_climate_tile*)0;
    }

    entry = dom_climate_cache_find_entry(cache, domain_id, tile->tile_id,
                                         tile->resolution, tile->authoring_version);
    if (!entry) {
        entry = dom_climate_cache_select_slot(cache);
    }
    if (!entry) {
        return (dom_climate_tile*)0;
    }
    if (entry->valid) {
        dom_climate_tile_free(&entry->tile);
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

    dom_climate_tile_init(tile);
    return &entry->tile;
}

static void dom_climate_cache_invalidate_domain(dom_climate_cache* cache, dom_domain_id domain_id)
{
    u32 i;
    if (!cache || !cache->entries) {
        return;
    }
    for (i = 0u; i < cache->capacity; ++i) {
        dom_climate_cache_entry* entry = &cache->entries[i];
        if (entry->valid && entry->domain_id == domain_id) {
            dom_climate_tile_free(&entry->tile);
            entry->valid = D_FALSE;
            if (cache->count > 0u) {
                cache->count -= 1u;
            }
        }
    }
}

static q16_16 dom_climate_step_from_extent(q16_16 extent, u32 sample_dim)
{
    if (sample_dim <= 1u) {
        return 0;
    }
    return (q16_16)((i64)extent / (i64)(sample_dim - 1u));
}

static u32 dom_climate_sample_index_from_coord(q16_16 coord,
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

static void dom_climate_query_meta_refused(dom_domain_query_meta* meta,
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

static void dom_climate_query_meta_ok(dom_domain_query_meta* meta,
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

static d_bool dom_climate_resolution_allowed(u32 max_resolution, u32 resolution)
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

static d_bool dom_climate_domain_is_active(const dom_climate_domain* domain)
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

static u64 dom_climate_noise_seed(const dom_climate_surface_desc* desc, const char* stream)
{
    u64 base_seed;
    if (!desc || !stream) {
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

static q16_16 dom_climate_lerp(q16_16 a, q16_16 b, q16_16 t)
{
    return d_q16_16_add(a, d_q16_16_mul(d_q16_16_sub(b, a), t));
}

static dom_climate_latlon dom_climate_point_latlon(const dom_climate_surface* surface,
                                                   const dom_domain_point* point)
{
    dom_climate_latlon out;
    memset(&out, 0, sizeof(out));
    if (!surface || !point) {
        return out;
    }
    if (surface->shape.kind == DOM_TERRAIN_SHAPE_SLAB) {
        q16_16 extent = surface->shape.slab_half_extent;
        q16_16 span;
        q16_16 lat_max = d_q16_16_from_double(0.25);
        q16_16 lon_max = d_q16_16_from_double(0.5);
        if (extent <= 0) {
            extent = d_q16_16_from_int(512);
        }
        span = d_q16_16_mul(extent, d_q16_16_from_int(2));
        if (span <= 0) {
            span = d_q16_16_from_int(1);
        }
        out.latitude = dom_climate_clamp_q16_16(d_fixed_div_q16_16(point->y, span),
                                                (q16_16)-lat_max, lat_max);
        out.longitude = dom_climate_clamp_q16_16(d_fixed_div_q16_16(point->x, span),
                                                 (q16_16)-lon_max, lon_max);
        out.altitude = dom_climate_abs_q16_16(point->z);
        out.valid = 1u;
        return out;
    }
    {
        dom_terrain_latlon terrain_latlon = dom_terrain_local_to_latlon(&surface->shape, point);
        out.latitude = terrain_latlon.latitude;
        out.longitude = terrain_latlon.longitude;
        out.altitude = terrain_latlon.altitude;
        out.valid = terrain_latlon.valid;
    }
    return out;
}

static q16_16 dom_climate_lat_ratio(const dom_climate_latlon* latlon)
{
    q16_16 lat_max = d_q16_16_from_double(0.25);
    q16_16 lat_abs;
    q16_16 ratio;
    if (!latlon) {
        return 0;
    }
    lat_abs = dom_climate_abs_q16_16(latlon->latitude);
    ratio = d_fixed_div_q16_16(lat_abs, lat_max);
    return dom_climate_clamp_q16_16(ratio, 0, d_q16_16_from_int(1));
}

static q16_16 dom_climate_altitude_ratio(const dom_climate_surface* surface,
                                         const dom_climate_latlon* latlon)
{
    q16_16 alt;
    q16_16 denom;
    q16_16 ratio;
    if (!surface || !latlon) {
        return 0;
    }
    alt = latlon->altitude;
    if (alt < 0) {
        alt = 0;
    }
    if (surface->shape.kind == DOM_TERRAIN_SHAPE_SLAB) {
        denom = surface->shape.slab_half_thickness;
    } else {
        denom = surface->shape.radius_equatorial;
        if (surface->shape.radius_polar > denom) {
            denom = surface->shape.radius_polar;
        }
    }
    if (denom <= 0) {
        denom = d_q16_16_from_int(1);
    }
    ratio = d_fixed_div_q16_16(alt, denom);
    return dom_climate_clamp_q16_16(ratio, 0, d_q16_16_from_int(1));
}

static u32 dom_climate_wind_dir_from_sector(u32 sector)
{
    static const u32 dirs[8] = {
        DOM_CLIMATE_WIND_EAST,
        DOM_CLIMATE_WIND_NORTHEAST,
        DOM_CLIMATE_WIND_NORTH,
        DOM_CLIMATE_WIND_NORTHWEST,
        DOM_CLIMATE_WIND_WEST,
        DOM_CLIMATE_WIND_SOUTHWEST,
        DOM_CLIMATE_WIND_SOUTH,
        DOM_CLIMATE_WIND_SOUTHEAST
    };
    return dirs[sector & 7u];
}

static u32 dom_climate_wind_prevailing(const dom_climate_surface* surface,
                                       const dom_domain_point* point,
                                       const dom_climate_latlon* latlon,
                                       q16_16 lat_ratio)
{
    u32 band_count = 8u;
    u32 sector;
    q16_16 noise_ratio;
    if (!surface || !point) {
        return DOM_CLIMATE_WIND_UNKNOWN;
    }
    if (surface->wind_band_count > 0u) {
        band_count = surface->wind_band_count;
    }
    noise_ratio = dom_climate_noise_ratio(surface->noise_seed_wind, point, surface->noise.cell_size);
    sector = (u32)(((u64)noise_ratio * (u64)band_count) >> 16);
    if (band_count == 0u) {
        sector = 0u;
    } else if (sector >= band_count) {
        sector = band_count - 1u;
    }
    if (band_count != 0u) {
        sector = (u32)((sector * 8u) / band_count);
    }
    if (lat_ratio > d_q16_16_from_double(0.5)) {
        sector = (sector + 2u) & 7u;
    }
    if (latlon && latlon->latitude < 0) {
        sector = (sector + 4u) & 7u;
    }
    return dom_climate_wind_dir_from_sector(sector);
}

static void dom_climate_sample_init(dom_climate_sample* sample)
{
    if (!sample) {
        return;
    }
    memset(sample, 0, sizeof(*sample));
    sample->temperature_mean = DOM_CLIMATE_UNKNOWN_Q16;
    sample->temperature_range = DOM_CLIMATE_UNKNOWN_Q16;
    sample->precipitation_mean = DOM_CLIMATE_UNKNOWN_Q16;
    sample->precipitation_range = DOM_CLIMATE_UNKNOWN_Q16;
    sample->seasonality = DOM_CLIMATE_UNKNOWN_Q16;
    sample->wind_prevailing = DOM_CLIMATE_WIND_UNKNOWN;
}

static void dom_climate_eval_fields(const dom_climate_domain* domain,
                                    const dom_domain_point* point,
                                    dom_climate_sample* out_sample)
{
    const dom_climate_surface* surface;
    dom_climate_latlon latlon;
    q16_16 lat_ratio;
    q16_16 alt_ratio;
    q16_16 temp_mean;
    q16_16 temp_range;
    q16_16 precip_mean;
    q16_16 precip_range;
    q16_16 seasonality;
    q16_16 noise_temp;
    q16_16 noise_precip;
    q16_16 noise_season;
    if (!domain || !point || !out_sample) {
        return;
    }
    surface = &domain->surface;
    dom_climate_sample_init(out_sample);

    latlon = dom_climate_point_latlon(surface, point);
    if (!latlon.valid && surface->shape.kind != DOM_TERRAIN_SHAPE_SLAB) {
        out_sample->flags |= DOM_CLIMATE_SAMPLE_FIELDS_UNKNOWN | DOM_CLIMATE_SAMPLE_WIND_UNKNOWN;
        return;
    }
    lat_ratio = dom_climate_lat_ratio(&latlon);
    alt_ratio = dom_climate_altitude_ratio(surface, &latlon);

    temp_mean = dom_climate_lerp(surface->temp_equator, surface->temp_pole, lat_ratio);
    temp_mean = d_q16_16_sub(temp_mean, d_q16_16_mul(surface->temp_altitude_scale, alt_ratio));
    noise_temp = dom_climate_noise_sample(surface->noise_seed_temp, point,
                                          surface->noise.cell_size, surface->noise.amplitude);
    temp_mean = d_q16_16_add(temp_mean, d_q16_16_mul(noise_temp, surface->noise_temp_scale));
    temp_mean = dom_climate_clamp_q16_16(temp_mean, 0, d_q16_16_from_int(1));

    temp_range = d_q16_16_add(surface->temp_range_base,
                              d_q16_16_mul(surface->temp_range_lat_scale, lat_ratio));
    temp_range = dom_climate_clamp_q16_16(temp_range, 0, d_q16_16_from_int(1));

    precip_mean = dom_climate_lerp(surface->precip_equator, surface->precip_pole, lat_ratio);
    precip_mean = d_q16_16_sub(precip_mean, d_q16_16_mul(surface->precip_altitude_scale, alt_ratio));
    noise_precip = dom_climate_noise_sample(surface->noise_seed_precip, point,
                                            surface->noise.cell_size, surface->noise.amplitude);
    precip_mean = d_q16_16_add(precip_mean, d_q16_16_mul(noise_precip, surface->noise_precip_scale));
    precip_mean = dom_climate_clamp_q16_16(precip_mean, 0, d_q16_16_from_int(1));

    precip_range = d_q16_16_add(surface->precip_range_base,
                                d_q16_16_mul(surface->precip_range_lat_scale, lat_ratio));
    precip_range = dom_climate_clamp_q16_16(precip_range, 0, d_q16_16_from_int(1));

    seasonality = d_q16_16_add(surface->seasonality_base,
                               d_q16_16_mul(surface->seasonality_lat_scale, lat_ratio));
    noise_season = dom_climate_noise_sample(surface->noise_seed_season, point,
                                            surface->noise.cell_size, surface->noise.amplitude);
    seasonality = d_q16_16_add(seasonality, d_q16_16_mul(noise_season, surface->noise_season_scale));
    seasonality = dom_climate_clamp_q16_16(seasonality, 0, d_q16_16_from_int(1));

    if (surface->anchor.mask & DOM_CLIMATE_ANCHOR_TEMPERATURE_MEAN) {
        temp_mean = surface->anchor.temperature_mean;
    }
    if (surface->anchor.mask & DOM_CLIMATE_ANCHOR_TEMPERATURE_RANGE) {
        temp_range = surface->anchor.temperature_range;
    }
    if (surface->anchor.mask & DOM_CLIMATE_ANCHOR_PRECIP_MEAN) {
        precip_mean = surface->anchor.precipitation_mean;
    }
    if (surface->anchor.mask & DOM_CLIMATE_ANCHOR_PRECIP_RANGE) {
        precip_range = surface->anchor.precipitation_range;
    }
    if (surface->anchor.mask & DOM_CLIMATE_ANCHOR_SEASONALITY) {
        seasonality = surface->anchor.seasonality;
    }

    out_sample->temperature_mean = dom_climate_clamp_q16_16(temp_mean, 0, d_q16_16_from_int(1));
    out_sample->temperature_range = dom_climate_clamp_q16_16(temp_range, 0, d_q16_16_from_int(1));
    out_sample->precipitation_mean = dom_climate_clamp_q16_16(precip_mean, 0, d_q16_16_from_int(1));
    out_sample->precipitation_range = dom_climate_clamp_q16_16(precip_range, 0, d_q16_16_from_int(1));
    out_sample->seasonality = dom_climate_clamp_q16_16(seasonality, 0, d_q16_16_from_int(1));

    if (surface->anchor.mask & DOM_CLIMATE_ANCHOR_WIND_PREVAILING) {
        out_sample->wind_prevailing = surface->anchor.wind_prevailing;
    } else {
        out_sample->wind_prevailing = dom_climate_wind_prevailing(surface, point, &latlon, lat_ratio);
    }
    if (out_sample->wind_prevailing == DOM_CLIMATE_WIND_UNKNOWN) {
        out_sample->flags |= DOM_CLIMATE_SAMPLE_WIND_UNKNOWN;
    }
}

static q16_16 dom_climate_tile_sample_scalar(const dom_climate_tile* tile,
                                             const dom_domain_point* point,
                                             const q16_16* values)
{
    q16_16 px;
    q16_16 py;
    q16_16 pz;
    q16_16 step_x;
    q16_16 step_y;
    q16_16 step_z;
    u32 ix;
    u32 iy;
    u32 iz;
    u32 idx;
    if (!tile || !point || !values || tile->sample_dim == 0u) {
        return DOM_CLIMATE_UNKNOWN_Q16;
    }
    px = dom_climate_clamp_q16_16(point->x, tile->bounds.min.x, tile->bounds.max.x);
    py = dom_climate_clamp_q16_16(point->y, tile->bounds.min.y, tile->bounds.max.y);
    pz = dom_climate_clamp_q16_16(point->z, tile->bounds.min.z, tile->bounds.max.z);

    step_x = dom_climate_step_from_extent((q16_16)(tile->bounds.max.x - tile->bounds.min.x), tile->sample_dim);
    step_y = dom_climate_step_from_extent((q16_16)(tile->bounds.max.y - tile->bounds.min.y), tile->sample_dim);
    step_z = dom_climate_step_from_extent((q16_16)(tile->bounds.max.z - tile->bounds.min.z), tile->sample_dim);

    ix = dom_climate_sample_index_from_coord(px, tile->bounds.min.x, tile->bounds.max.x, step_x, tile->sample_dim);
    iy = dom_climate_sample_index_from_coord(py, tile->bounds.min.y, tile->bounds.max.y, step_y, tile->sample_dim);
    iz = dom_climate_sample_index_from_coord(pz, tile->bounds.min.z, tile->bounds.max.z, step_z, tile->sample_dim);
    idx = ix + tile->sample_dim * (iy + tile->sample_dim * iz);
    if (idx >= tile->sample_count) {
        return DOM_CLIMATE_UNKNOWN_Q16;
    }
    return values[idx];
}

static u32 dom_climate_tile_sample_wind(const dom_climate_tile* tile,
                                        const dom_domain_point* point)
{
    q16_16 px;
    q16_16 py;
    q16_16 pz;
    q16_16 step_x;
    q16_16 step_y;
    q16_16 step_z;
    u32 ix;
    u32 iy;
    u32 iz;
    u32 idx;
    if (!tile || !point || !tile->wind_prevailing || tile->sample_dim == 0u) {
        return DOM_CLIMATE_WIND_UNKNOWN;
    }
    px = dom_climate_clamp_q16_16(point->x, tile->bounds.min.x, tile->bounds.max.x);
    py = dom_climate_clamp_q16_16(point->y, tile->bounds.min.y, tile->bounds.max.y);
    pz = dom_climate_clamp_q16_16(point->z, tile->bounds.min.z, tile->bounds.max.z);

    step_x = dom_climate_step_from_extent((q16_16)(tile->bounds.max.x - tile->bounds.min.x), tile->sample_dim);
    step_y = dom_climate_step_from_extent((q16_16)(tile->bounds.max.y - tile->bounds.min.y), tile->sample_dim);
    step_z = dom_climate_step_from_extent((q16_16)(tile->bounds.max.z - tile->bounds.min.z), tile->sample_dim);

    ix = dom_climate_sample_index_from_coord(px, tile->bounds.min.x, tile->bounds.max.x, step_x, tile->sample_dim);
    iy = dom_climate_sample_index_from_coord(py, tile->bounds.min.y, tile->bounds.max.y, step_y, tile->sample_dim);
    iz = dom_climate_sample_index_from_coord(pz, tile->bounds.min.z, tile->bounds.max.z, step_z, tile->sample_dim);
    idx = ix + tile->sample_dim * (iy + tile->sample_dim * iz);
    if (idx >= tile->sample_count) {
        return DOM_CLIMATE_WIND_UNKNOWN;
    }
    return tile->wind_prevailing[idx];
}

static int dom_climate_tile_build(dom_climate_tile* tile,
                                  const dom_domain_tile_desc* desc,
                                  const dom_climate_domain* domain)
{
    u32 dim;
    u32 sample_count;
    size_t q16_count;
    q16_16* data;
    u32* winds;
    q16_16 step_x;
    q16_16 step_y;
    q16_16 step_z;
    if (!tile || !desc || !domain) {
        return -1;
    }
    dim = desc->sample_dim;
    if (dim == 0u) {
        return -1;
    }
    sample_count = dim * dim * dim;
    q16_count = (size_t)sample_count * 5u;
    data = (q16_16*)malloc(q16_count * sizeof(q16_16));
    winds = (u32*)malloc((size_t)sample_count * sizeof(u32));
    if (!data || !winds) {
        if (data) free(data);
        if (winds) free(winds);
        return -1;
    }

    dom_climate_tile_free(tile);
    dom_climate_tile_init(tile);
    tile->tile_id = desc->tile_id;
    tile->resolution = desc->resolution;
    tile->sample_dim = dim;
    tile->bounds = desc->bounds;
    tile->authoring_version = desc->authoring_version;
    tile->sample_count = sample_count;
    tile->data = data;
    tile->wind_prevailing = winds;
    tile->temperature_mean = data;
    tile->temperature_range = data + sample_count;
    tile->precipitation_mean = data + sample_count * 2u;
    tile->precipitation_range = data + sample_count * 3u;
    tile->seasonality = data + sample_count * 4u;

    step_x = dom_climate_step_from_extent((q16_16)(tile->bounds.max.x - tile->bounds.min.x), dim);
    step_y = dom_climate_step_from_extent((q16_16)(tile->bounds.max.y - tile->bounds.min.y), dim);
    step_z = dom_climate_step_from_extent((q16_16)(tile->bounds.max.z - tile->bounds.min.z), dim);

    for (u32 z = 0u; z < dim; ++z) {
        for (u32 y = 0u; y < dim; ++y) {
            for (u32 x = 0u; x < dim; ++x) {
                u32 idx = x + dim * (y + dim * z);
                dom_domain_point p;
                dom_climate_sample sample;
                p.x = (q16_16)(tile->bounds.min.x + (q16_16)((i64)step_x * (i64)x));
                p.y = (q16_16)(tile->bounds.min.y + (q16_16)((i64)step_y * (i64)y));
                p.z = (q16_16)(tile->bounds.min.z + (q16_16)((i64)step_z * (i64)z));
                dom_climate_eval_fields(domain, &p, &sample);
                tile->temperature_mean[idx] = sample.temperature_mean;
                tile->temperature_range[idx] = sample.temperature_range;
                tile->precipitation_mean[idx] = sample.precipitation_mean;
                tile->precipitation_range[idx] = sample.precipitation_range;
                tile->seasonality[idx] = sample.seasonality;
                tile->wind_prevailing[idx] = sample.wind_prevailing;
            }
        }
    }

    return 0;
}

static void dom_climate_sample_from_tile(const dom_climate_tile* tile,
                                         const dom_domain_point* point,
                                         dom_climate_sample* out_sample)
{
    if (!tile || !point || !out_sample) {
        return;
    }
    dom_climate_sample_init(out_sample);
    out_sample->temperature_mean = dom_climate_tile_sample_scalar(tile, point, tile->temperature_mean);
    out_sample->temperature_range = dom_climate_tile_sample_scalar(tile, point, tile->temperature_range);
    out_sample->precipitation_mean = dom_climate_tile_sample_scalar(tile, point, tile->precipitation_mean);
    out_sample->precipitation_range = dom_climate_tile_sample_scalar(tile, point, tile->precipitation_range);
    out_sample->seasonality = dom_climate_tile_sample_scalar(tile, point, tile->seasonality);
    out_sample->wind_prevailing = dom_climate_tile_sample_wind(tile, point);
    if (out_sample->wind_prevailing == DOM_CLIMATE_WIND_UNKNOWN) {
        out_sample->flags |= DOM_CLIMATE_SAMPLE_WIND_UNKNOWN;
    }
}

static int dom_climate_build_tile_desc(const dom_climate_domain* domain,
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
    tx = dom_climate_floor_div_q16((q16_16)(point->x - source->bounds.min.x), tile_size);
    ty = dom_climate_floor_div_q16((q16_16)(point->y - source->bounds.min.y), tile_size);
    tz = dom_climate_floor_div_q16((q16_16)(point->z - source->bounds.min.z), tile_size);
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

static const dom_climate_tile* dom_climate_tile_get(dom_climate_domain* domain,
                                                    const dom_domain_tile_desc* desc,
                                                    d_bool allow_build)
{
    if (!domain || !desc) {
        return (const dom_climate_tile*)0;
    }
    if (domain->cache.entries) {
        const dom_climate_tile* cached = dom_climate_cache_get(&domain->cache,
                                                               domain->surface.domain_id,
                                                               desc->tile_id,
                                                               desc->resolution,
                                                               desc->authoring_version);
        if (cached) {
            return cached;
        }
        if (!allow_build) {
            return (const dom_climate_tile*)0;
        }
        {
            dom_climate_tile temp;
            dom_climate_tile_init(&temp);
            if (dom_climate_tile_build(&temp, desc, domain) != 0) {
                dom_climate_tile_free(&temp);
                return (const dom_climate_tile*)0;
            }
            cached = dom_climate_cache_put(&domain->cache, domain->surface.domain_id, &temp);
            if (!cached) {
                dom_climate_tile_free(&temp);
                return (const dom_climate_tile*)0;
            }
            return cached;
        }
    }
    return (const dom_climate_tile*)0;
}

static d_bool dom_climate_tile_cached(const dom_climate_domain* domain, const dom_domain_tile_desc* desc)
{
    if (!domain || !desc) {
        return D_FALSE;
    }
    return dom_climate_cache_peek(&domain->cache,
                                  domain->surface.domain_id,
                                  desc->tile_id,
                                  desc->resolution,
                                  desc->authoring_version) != (const dom_climate_tile*)0;
}

void dom_climate_surface_desc_init(dom_climate_surface_desc* desc)
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
    desc->noise.cell_size = d_q16_16_from_int(32);
    desc->noise.amplitude = d_q16_16_from_double(0.05);
    desc->temp_equator = d_q16_16_from_double(0.7);
    desc->temp_pole = d_q16_16_from_double(0.2);
    desc->temp_altitude_scale = d_q16_16_from_double(0.2);
    desc->temp_range_base = d_q16_16_from_double(0.1);
    desc->temp_range_lat_scale = d_q16_16_from_double(0.2);
    desc->precip_equator = d_q16_16_from_double(0.7);
    desc->precip_pole = d_q16_16_from_double(0.1);
    desc->precip_altitude_scale = d_q16_16_from_double(0.2);
    desc->precip_range_base = d_q16_16_from_double(0.1);
    desc->precip_range_lat_scale = d_q16_16_from_double(0.2);
    desc->seasonality_base = d_q16_16_from_double(0.2);
    desc->seasonality_lat_scale = d_q16_16_from_double(0.5);
    desc->noise_temp_scale = d_q16_16_from_double(0.4);
    desc->noise_precip_scale = d_q16_16_from_double(0.4);
    desc->noise_season_scale = d_q16_16_from_double(0.3);
    desc->wind_band_count = 8u;
}

void dom_climate_surface_init(dom_climate_surface* surface, const dom_climate_surface_desc* desc)
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
    surface->temp_equator = desc->temp_equator;
    surface->temp_pole = desc->temp_pole;
    surface->temp_altitude_scale = desc->temp_altitude_scale;
    surface->temp_range_base = desc->temp_range_base;
    surface->temp_range_lat_scale = desc->temp_range_lat_scale;
    surface->precip_equator = desc->precip_equator;
    surface->precip_pole = desc->precip_pole;
    surface->precip_altitude_scale = desc->precip_altitude_scale;
    surface->precip_range_base = desc->precip_range_base;
    surface->precip_range_lat_scale = desc->precip_range_lat_scale;
    surface->seasonality_base = desc->seasonality_base;
    surface->seasonality_lat_scale = desc->seasonality_lat_scale;
    surface->noise_temp_scale = desc->noise_temp_scale;
    surface->noise_precip_scale = desc->noise_precip_scale;
    surface->noise_season_scale = desc->noise_season_scale;
    surface->wind_band_count = desc->wind_band_count;
    surface->anchor = desc->anchor;
    surface->noise_seed_temp = dom_climate_noise_seed(desc, "noise.stream.climate.temp.base");
    surface->noise_seed_precip = dom_climate_noise_seed(desc, "noise.stream.climate.precip.base");
    surface->noise_seed_season = dom_climate_noise_seed(desc, "noise.stream.climate.season.base");
    surface->noise_seed_wind = dom_climate_noise_seed(desc, "noise.stream.climate.wind.base");

    dom_terrain_surface_desc_init(&terrain_desc);
    terrain_desc.domain_id = desc->domain_id;
    terrain_desc.world_seed = desc->world_seed;
    terrain_desc.meters_per_unit = desc->meters_per_unit;
    terrain_desc.shape = desc->shape;
    terrain_desc.noise.amplitude = 0;
    terrain_desc.noise.cell_size = d_q16_16_from_int(1);
    dom_terrain_surface_init(&surface->terrain_surface, &terrain_desc);
}

void dom_climate_domain_init(dom_climate_domain* domain,
                             const dom_climate_surface_desc* desc,
                             u32 cache_capacity)
{
    if (!domain || !desc) {
        return;
    }
    memset(domain, 0, sizeof(*domain));
    dom_climate_surface_init(&domain->surface, desc);
    dom_domain_policy_init(&domain->policy);
    domain->existence_state = DOM_DOMAIN_EXISTENCE_REALIZED;
    domain->archival_state = DOM_DOMAIN_ARCHIVAL_LIVE;
    domain->authoring_version = 1u;
    dom_climate_cache_init(&domain->cache);
    if (cache_capacity > 0u) {
        dom_climate_cache_reserve(&domain->cache, cache_capacity);
    }
    domain->capsule_count = 0u;
}

void dom_climate_domain_free(dom_climate_domain* domain)
{
    if (!domain) {
        return;
    }
    dom_climate_cache_free(&domain->cache);
    domain->capsule_count = 0u;
}

void dom_climate_domain_set_state(dom_climate_domain* domain,
                                  u32 existence_state,
                                  u32 archival_state)
{
    if (!domain) {
        return;
    }
    if (domain->existence_state != existence_state || domain->archival_state != archival_state) {
        domain->existence_state = existence_state;
        domain->archival_state = archival_state;
        dom_climate_cache_invalidate_domain(&domain->cache, domain->surface.domain_id);
    }
}

void dom_climate_domain_set_policy(dom_climate_domain* domain,
                                   const dom_domain_policy* policy)
{
    if (!domain || !policy) {
        return;
    }
    domain->policy = *policy;
    dom_climate_cache_invalidate_domain(&domain->cache, domain->surface.domain_id);
}

int dom_climate_sample_query(const dom_climate_domain* domain,
                             const dom_domain_point* point,
                             dom_domain_budget* budget,
                             dom_climate_sample* out_sample)
{
    dom_domain_tile_desc desc;
    const dom_domain_sdf_source* source;
    u32 cost;
    d_bool collapsed = D_FALSE;
    if (!domain || !point || !out_sample) {
        return -1;
    }
    dom_climate_sample_init(out_sample);

    if (!dom_climate_domain_is_active(domain)) {
        dom_climate_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_DOMAIN_INACTIVE, budget);
        out_sample->flags |= DOM_CLIMATE_SAMPLE_FIELDS_UNKNOWN | DOM_CLIMATE_SAMPLE_WIND_UNKNOWN;
        return 0;
    }

    source = dom_terrain_surface_sdf(&domain->surface.terrain_surface);
    if (!source || !source->eval) {
        dom_climate_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_NO_SOURCE, budget);
        out_sample->flags |= DOM_CLIMATE_SAMPLE_FIELDS_UNKNOWN | DOM_CLIMATE_SAMPLE_WIND_UNKNOWN;
        return 0;
    }

    if (!dom_domain_aabb_contains(&source->bounds, point)) {
        dom_climate_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_COARSE,
                                  DOM_DOMAIN_CONFIDENCE_LOWER_BOUND, 0u, budget);
        out_sample->flags |= DOM_CLIMATE_SAMPLE_FIELDS_UNKNOWN | DOM_CLIMATE_SAMPLE_WIND_UNKNOWN;
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
        dom_climate_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                                  DOM_DOMAIN_CONFIDENCE_UNKNOWN, 0u, budget);
        out_sample->flags |= DOM_CLIMATE_SAMPLE_FIELDS_UNKNOWN |
                             DOM_CLIMATE_SAMPLE_WIND_UNKNOWN |
                             DOM_CLIMATE_SAMPLE_COLLAPSED;
        return 0;
    }

    if (dom_climate_resolution_allowed(domain->policy.max_resolution, DOM_DOMAIN_RES_FULL)) {
        cost = domain->policy.cost_full;
        if (dom_domain_budget_consume(budget, cost)) {
            dom_climate_eval_fields(domain, point, out_sample);
            dom_climate_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_FULL,
                                      DOM_DOMAIN_CONFIDENCE_EXACT, cost, budget);
            return 0;
        }
    }

    if (dom_climate_resolution_allowed(domain->policy.max_resolution, DOM_DOMAIN_RES_MEDIUM)) {
        cost = domain->policy.cost_medium;
        if (dom_climate_build_tile_desc(domain, point, DOM_DOMAIN_RES_MEDIUM, &desc) == 0) {
            if (!dom_climate_tile_cached(domain, &desc)) {
                cost += domain->policy.tile_build_cost_medium;
            }
            if (dom_domain_budget_consume(budget, cost)) {
                const dom_climate_tile* tile = dom_climate_tile_get((dom_climate_domain*)domain, &desc, D_TRUE);
                if (!tile) {
                    dom_climate_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_INTERNAL, budget);
                    out_sample->flags |= DOM_CLIMATE_SAMPLE_FIELDS_UNKNOWN | DOM_CLIMATE_SAMPLE_WIND_UNKNOWN;
                    return 0;
                }
                dom_climate_sample_from_tile(tile, point, out_sample);
                dom_climate_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_MEDIUM,
                                          DOM_DOMAIN_CONFIDENCE_LOWER_BOUND, cost, budget);
                return 0;
            }
        }
    }

    if (dom_climate_resolution_allowed(domain->policy.max_resolution, DOM_DOMAIN_RES_COARSE)) {
        cost = domain->policy.cost_coarse;
        if (dom_climate_build_tile_desc(domain, point, DOM_DOMAIN_RES_COARSE, &desc) == 0) {
            if (!dom_climate_tile_cached(domain, &desc)) {
                cost += domain->policy.tile_build_cost_coarse;
            }
            if (dom_domain_budget_consume(budget, cost)) {
                const dom_climate_tile* tile = dom_climate_tile_get((dom_climate_domain*)domain, &desc, D_TRUE);
                if (!tile) {
                    dom_climate_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_INTERNAL, budget);
                    out_sample->flags |= DOM_CLIMATE_SAMPLE_FIELDS_UNKNOWN | DOM_CLIMATE_SAMPLE_WIND_UNKNOWN;
                    return 0;
                }
                dom_climate_sample_from_tile(tile, point, out_sample);
                dom_climate_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_COARSE,
                                          DOM_DOMAIN_CONFIDENCE_LOWER_BOUND, cost, budget);
                return 0;
            }
        }
    }

    if (dom_climate_resolution_allowed(domain->policy.max_resolution, DOM_DOMAIN_RES_ANALYTIC)) {
        cost = domain->policy.cost_analytic;
        if (dom_domain_budget_consume(budget, cost)) {
            dom_climate_eval_fields(domain, point, out_sample);
            dom_climate_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                                      DOM_DOMAIN_CONFIDENCE_EXACT, cost, budget);
            return 0;
        }
    }

    dom_climate_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_BUDGET, budget);
    out_sample->flags |= DOM_CLIMATE_SAMPLE_FIELDS_UNKNOWN | DOM_CLIMATE_SAMPLE_WIND_UNKNOWN;
    return 0;
}

static q16_16 dom_climate_hist_bin_ratio(u32 count, u32 total)
{
    if (total == 0u) {
        return 0;
    }
    return (q16_16)(((u64)count << 16) / total);
}

static u32 dom_climate_hist_bin(q16_16 value)
{
    q16_16 clamped = dom_climate_clamp_q16_16(value, 0, d_q16_16_from_int(1));
    u32 scaled = (u32)(((i64)clamped * (DOM_CLIMATE_HIST_BINS - 1u)) >> 16);
    if (scaled >= DOM_CLIMATE_HIST_BINS) {
        scaled = DOM_CLIMATE_HIST_BINS - 1u;
    }
    return scaled;
}

static int dom_climate_capsule_store(dom_climate_domain* domain,
                                     const dom_domain_tile_desc* desc)
{
    dom_climate_macro_capsule capsule;
    dom_climate_tile tile;
    u32 temp_bins[DOM_CLIMATE_HIST_BINS];
    u32 precip_bins[DOM_CLIMATE_HIST_BINS];
    u32 season_bins[DOM_CLIMATE_HIST_BINS];
    q16_16 temp_sum;
    q16_16 precip_sum;
    u32 sample_count;
    if (!domain || !desc) {
        return -1;
    }
    if (domain->capsule_count >= DOM_CLIMATE_MAX_CAPSULES) {
        return -2;
    }

    memset(temp_bins, 0, sizeof(temp_bins));
    memset(precip_bins, 0, sizeof(precip_bins));
    memset(season_bins, 0, sizeof(season_bins));
    temp_sum = 0;
    precip_sum = 0;

    dom_climate_tile_init(&tile);
    if (dom_climate_tile_build(&tile, desc, domain) != 0) {
        dom_climate_tile_free(&tile);
        return -1;
    }

    sample_count = tile.sample_count;
    for (u32 i = 0u; i < sample_count; ++i) {
        q16_16 t = tile.temperature_mean[i];
        q16_16 p = tile.precipitation_mean[i];
        q16_16 s = tile.seasonality[i];
        temp_bins[dom_climate_hist_bin(t)] += 1u;
        precip_bins[dom_climate_hist_bin(p)] += 1u;
        season_bins[dom_climate_hist_bin(s)] += 1u;
        temp_sum = d_q16_16_add(temp_sum, t);
        precip_sum = d_q16_16_add(precip_sum, p);
    }

    memset(&capsule, 0, sizeof(capsule));
    capsule.capsule_id = desc->tile_id;
    capsule.tile_id = desc->tile_id;
    capsule.bounds = desc->bounds;
    capsule.sample_count = sample_count;
    capsule.temperature_mean_avg = (sample_count > 0u) ? (q16_16)(temp_sum / (i64)sample_count) : 0;
    capsule.precipitation_mean_avg = (sample_count > 0u) ? (q16_16)(precip_sum / (i64)sample_count) : 0;
    for (u32 b = 0u; b < DOM_CLIMATE_HIST_BINS; ++b) {
        capsule.temperature_hist[b] = dom_climate_hist_bin_ratio(temp_bins[b], sample_count);
        capsule.precipitation_hist[b] = dom_climate_hist_bin_ratio(precip_bins[b], sample_count);
        capsule.seasonality_hist[b] = dom_climate_hist_bin_ratio(season_bins[b], sample_count);
    }

    dom_climate_tile_free(&tile);
    domain->capsules[domain->capsule_count++] = capsule;
    return 0;
}

int dom_climate_domain_collapse_tile(dom_climate_domain* domain,
                                     const dom_domain_tile_desc* desc)
{
    u32 i;
    if (!domain || !desc) {
        return -1;
    }
    if (domain->cache.entries) {
        for (i = 0u; i < domain->cache.capacity; ++i) {
            dom_climate_cache_entry* entry = &domain->cache.entries[i];
            if (!entry->valid) {
                continue;
            }
            if (entry->domain_id == domain->surface.domain_id &&
                entry->tile_id == desc->tile_id) {
                dom_climate_tile_free(&entry->tile);
                entry->valid = D_FALSE;
                if (domain->cache.count > 0u) {
                    domain->cache.count -= 1u;
                }
            }
        }
    }
    return dom_climate_capsule_store(domain, desc);
}

int dom_climate_domain_expand_tile(dom_climate_domain* domain, u64 tile_id)
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

u32 dom_climate_domain_capsule_count(const dom_climate_domain* domain)
{
    return domain ? domain->capsule_count : 0u;
}

const dom_climate_macro_capsule* dom_climate_domain_capsule_at(const dom_climate_domain* domain,
                                                               u32 index)
{
    if (!domain || index >= domain->capsule_count) {
        return (const dom_climate_macro_capsule*)0;
    }
    return &domain->capsules[index];
}

static d_bool dom_climate_biome_rule_value_match(q16_16 value,
                                                 q16_16 minv,
                                                 q16_16 maxv,
                                                 d_bool known,
                                                 u32* io_total,
                                                 u32* io_known)
{
    if (!io_total || !io_known) {
        return D_FALSE;
    }
    *io_total += 1u;
    if (!known) {
        return D_TRUE;
    }
    *io_known += 1u;
    if (value < minv || value > maxv) {
        return D_FALSE;
    }
    return D_TRUE;
}

int dom_climate_biome_resolve(const dom_climate_biome_catalog* catalog,
                              const dom_climate_biome_inputs* inputs,
                              dom_climate_biome_result* out_result)
{
    u32 best_rule = 0u;
    q16_16 best_confidence = 0;
    u32 best_known = 0u;
    d_bool best_found = D_FALSE;
    if (!out_result) {
        return -1;
    }
    memset(out_result, 0, sizeof(*out_result));
    out_result->biome_id = 0u;
    out_result->confidence = 0;
    out_result->flags = DOM_CLIMATE_BIOME_RESULT_UNKNOWN;
    if (!catalog || catalog->biome_count == 0u || !inputs) {
        return 0;
    }

    d_bool climate_known = inputs->climate &&
                           ((inputs->climate->flags & DOM_CLIMATE_SAMPLE_FIELDS_UNKNOWN) == 0u);
    d_bool terrain_known = inputs->terrain &&
                           ((inputs->terrain->flags & DOM_TERRAIN_SAMPLE_FIELDS_UNKNOWN) == 0u);
    d_bool geology_known = inputs->geology &&
                           ((inputs->geology->flags & DOM_GEOLOGY_SAMPLE_FIELDS_UNKNOWN) == 0u);
    d_bool moisture_known = (inputs->flags & DOM_CLIMATE_BIOME_INPUT_MOISTURE_UNKNOWN) == 0u;
    d_bool elevation_known = (inputs->flags & DOM_CLIMATE_BIOME_INPUT_ELEVATION_UNKNOWN) == 0u;
    (void)terrain_known;

    for (u32 i = 0u; i < catalog->biome_count && i < DOM_CLIMATE_MAX_BIOMES; ++i) {
        const dom_climate_biome_rule* rule = &catalog->rules[i];
        u32 total = 0u;
        u32 known = 0u;
        d_bool ok = D_TRUE;

        if (rule->mask & DOM_CLIMATE_BIOME_RULE_TEMP) {
            q16_16 value = climate_known ? inputs->climate->temperature_mean : DOM_CLIMATE_UNKNOWN_Q16;
            ok = dom_climate_biome_rule_value_match(value, rule->temp_min, rule->temp_max,
                                                    climate_known, &total, &known);
        }
        if (ok && (rule->mask & DOM_CLIMATE_BIOME_RULE_PRECIP)) {
            q16_16 value = climate_known ? inputs->climate->precipitation_mean : DOM_CLIMATE_UNKNOWN_Q16;
            ok = dom_climate_biome_rule_value_match(value, rule->precip_min, rule->precip_max,
                                                    climate_known, &total, &known);
        }
        if (ok && (rule->mask & DOM_CLIMATE_BIOME_RULE_SEASON)) {
            q16_16 value = climate_known ? inputs->climate->seasonality : DOM_CLIMATE_UNKNOWN_Q16;
            ok = dom_climate_biome_rule_value_match(value, rule->season_min, rule->season_max,
                                                    climate_known, &total, &known);
        }
        if (ok && (rule->mask & DOM_CLIMATE_BIOME_RULE_ELEVATION)) {
            q16_16 value = elevation_known ? inputs->elevation : DOM_CLIMATE_UNKNOWN_Q16;
            ok = dom_climate_biome_rule_value_match(value, rule->elevation_min, rule->elevation_max,
                                                    elevation_known, &total, &known);
        }
        if (ok && (rule->mask & DOM_CLIMATE_BIOME_RULE_MOISTURE)) {
            q16_16 value = moisture_known ? inputs->moisture_proxy : DOM_CLIMATE_UNKNOWN_Q16;
            ok = dom_climate_biome_rule_value_match(value, rule->moisture_min, rule->moisture_max,
                                                    moisture_known, &total, &known);
        }
        if (ok && (rule->mask & DOM_CLIMATE_BIOME_RULE_HARDNESS)) {
            q16_16 value = geology_known ? inputs->geology->hardness : DOM_CLIMATE_UNKNOWN_Q16;
            ok = dom_climate_biome_rule_value_match(value, rule->hardness_min, rule->hardness_max,
                                                    geology_known, &total, &known);
        }
        if (ok && (rule->mask & DOM_CLIMATE_BIOME_RULE_STRATA)) {
            total += 1u;
            if (!geology_known) {
                /* unknown strata, keep candidate with reduced confidence */
            } else if (inputs->geology->strata_layer_id != rule->required_strata_id) {
                ok = D_FALSE;
            } else {
                known += 1u;
            }
        }
        if (!ok) {
            continue;
        }
        {
            q16_16 confidence = 0;
            if (total > 0u) {
                confidence = (q16_16)(((u64)known << 16) / total);
            }
            if (!best_found ||
                confidence > best_confidence ||
                (confidence == best_confidence && known > best_known) ||
                (confidence == best_confidence && known == best_known && rule->biome_id < best_rule)) {
                best_found = D_TRUE;
                best_rule = rule->biome_id;
                best_confidence = confidence;
                best_known = known;
            }
        }
    }

    if (!best_found || best_known == 0u) {
        out_result->biome_id = 0u;
        out_result->confidence = 0;
        out_result->flags = DOM_CLIMATE_BIOME_RESULT_UNKNOWN;
        return 0;
    }

    out_result->biome_id = best_rule;
    out_result->confidence = best_confidence;
    out_result->flags = 0u;
    return 0;
}
