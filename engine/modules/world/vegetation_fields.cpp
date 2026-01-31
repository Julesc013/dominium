/*
FILE: source/domino/world/vegetation_fields.cpp
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / world/vegetation_fields
RESPONSIBILITY: Implements deterministic vegetation placement and event-driven growth sampling.
ALLOWED DEPENDENCIES: `include/domino/**` and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: Engine private headers outside world.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: Fixed-point only; deterministic ordering and math.
*/
#include "domino/world/vegetation_fields.h"

#include "domino/core/fixed_math.h"
#include "domino/core/rng_model.h"

#include <stdlib.h>
#include <string.h>
#include <stdio.h>

static q16_16 dom_veg_abs_q16_16(q16_16 v)
{
    return (v < 0) ? (q16_16)-v : v;
}

static q16_16 dom_veg_clamp_q16_16(q16_16 v, q16_16 lo, q16_16 hi)
{
    if (v < lo) {
        return lo;
    }
    if (v > hi) {
        return hi;
    }
    return v;
}

static i32 dom_veg_floor_div_q16(q16_16 value, q16_16 denom)
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

static u64 dom_veg_hash_u64(u64 h, u64 v)
{
    unsigned char bytes[8];
    bytes[0] = (unsigned char)((v >> 56) & 0xFFu);
    bytes[1] = (unsigned char)((v >> 48) & 0xFFu);
    bytes[2] = (unsigned char)((v >> 40) & 0xFFu);
    bytes[3] = (unsigned char)((v >> 32) & 0xFFu);
    bytes[4] = (unsigned char)((v >> 24) & 0xFFu);
    bytes[5] = (unsigned char)((v >> 16) & 0xFFu);
    bytes[6] = (unsigned char)((v >> 8) & 0xFFu);
    bytes[7] = (unsigned char)(v & 0xFFu);
    for (u32 i = 0u; i < 8u; ++i) {
        h ^= (u64)bytes[i];
        h *= 1099511628211ULL;
    }
    return h;
}

static u64 dom_veg_cell_key(i32 cx, i32 cy, i32 cz)
{
    u64 h = 14695981039346656037ULL;
    h = dom_veg_hash_u64(h, (u64)(u32)cx);
    h = dom_veg_hash_u64(h, (u64)(u32)cy);
    h = dom_veg_hash_u64(h, (u64)(u32)cz);
    return h;
}

static q16_16 dom_veg_ratio_from_u32(u32 value)
{
    return (q16_16)(value >> 16);
}

static u64 dom_veg_rng_u64(d_rng_state* rng)
{
    u64 hi = (u64)d_rng_next_u32(rng);
    u64 lo = (u64)d_rng_next_u32(rng);
    return (hi << 32) | lo;
}

static void dom_veg_stream_name(char* out_name, size_t cap,
                                dom_domain_id domain_id,
                                const char* purpose)
{
    if (!out_name || cap == 0u) {
        return;
    }
    if (!purpose || !purpose[0]) {
        purpose = "unknown";
    }
    sprintf(out_name, "noise.stream.%llu.vegetation.%s",
            (unsigned long long)domain_id,
            purpose);
    out_name[cap - 1u] = '\0';
}

static void dom_veg_rng_state_for_cell(d_rng_state* rng,
                                       const dom_vegetation_surface_desc* surface,
                                       const char* purpose,
                                       u64 cell_key,
                                       u32 species_id,
                                       u64 event_index)
{
    char stream[96];
    u64 tick_index;
    if (!rng || !surface) {
        return;
    }
    dom_veg_stream_name(stream, sizeof(stream), surface->domain_id, purpose);
    D_DET_GUARD_RNG_STREAM_NAME(stream);
    tick_index = dom_veg_hash_u64(cell_key, event_index);
    d_rng_state_from_context(rng,
                             surface->world_seed,
                             surface->domain_id,
                             (u64)species_id,
                             tick_index,
                             stream,
                             D_RNG_MIX_DOMAIN | D_RNG_MIX_PROCESS | D_RNG_MIX_TICK | D_RNG_MIX_STREAM);
}

static void dom_veg_cell_coord(q16_16 cell_size,
                               const dom_domain_point* point,
                               i32* out_cx,
                               i32* out_cy,
                               i32* out_cz)
{
    if (!point || !out_cx || !out_cy || !out_cz) {
        return;
    }
    if (cell_size <= 0) {
        cell_size = d_q16_16_from_int(1);
    }
    *out_cx = dom_veg_floor_div_q16(point->x, cell_size);
    *out_cy = dom_veg_floor_div_q16(point->y, cell_size);
    *out_cz = dom_veg_floor_div_q16(point->z, cell_size);
}

static dom_domain_point dom_veg_cell_center(q16_16 cell_size, i32 cx, i32 cy, i32 cz)
{
    dom_domain_point center;
    q16_16 half = d_fixed_div_q16_16(cell_size, d_q16_16_from_int(2));
    center.x = (q16_16)((i64)cx * (i64)cell_size);
    center.y = (q16_16)((i64)cy * (i64)cell_size);
    center.z = (q16_16)((i64)cz * (i64)cell_size);
    center.x = d_q16_16_add(center.x, half);
    center.y = d_q16_16_add(center.y, half);
    center.z = d_q16_16_add(center.z, half);
    return center;
}

static void dom_vegetation_cache_init(dom_vegetation_cache* cache)
{
    if (!cache) {
        return;
    }
    memset(cache, 0, sizeof(*cache));
}

static void dom_vegetation_tile_init(dom_vegetation_tile* tile)
{
    if (!tile) {
        return;
    }
    memset(tile, 0, sizeof(*tile));
}

static void dom_vegetation_tile_free(dom_vegetation_tile* tile)
{
    if (!tile) {
        return;
    }
    if (tile->data_q16) {
        free(tile->data_q16);
        tile->data_q16 = (q16_16*)0;
    }
    if (tile->data_u32) {
        free(tile->data_u32);
        tile->data_u32 = (u32*)0;
    }
    if (tile->age_ticks) {
        free(tile->age_ticks);
        tile->age_ticks = (u64*)0;
    }
    tile->coverage = (q16_16*)0;
    tile->suitability = (q16_16*)0;
    tile->size = (q16_16*)0;
    tile->health = (q16_16*)0;
    tile->biome_id = (u32*)0;
    tile->species_id = (u32*)0;
    tile->flags = (u32*)0;
    tile->sample_count = 0u;
    tile->sample_dim = 0u;
    tile->tile_id = 0u;
    tile->resolution = DOM_DOMAIN_RES_REFUSED;
    tile->window_start = 0u;
    tile->window_ticks = 0u;
    memset(&tile->bounds, 0, sizeof(tile->bounds));
    tile->authoring_version = 0u;
}

static void dom_vegetation_cache_free(dom_vegetation_cache* cache)
{
    if (!cache) {
        return;
    }
    if (cache->entries) {
        for (u32 i = 0u; i < cache->capacity; ++i) {
            dom_vegetation_tile_free(&cache->entries[i].tile);
        }
        free(cache->entries);
        cache->entries = (dom_vegetation_cache_entry*)0;
    }
    cache->capacity = 0u;
    cache->count = 0u;
    cache->use_counter = 0u;
    cache->next_insert_order = 0u;
}

static int dom_vegetation_cache_reserve(dom_vegetation_cache* cache, u32 capacity)
{
    dom_vegetation_cache_entry* new_entries;
    u32 old_cap;
    if (!cache) {
        return -1;
    }
    if (capacity <= cache->capacity) {
        return 0;
    }
    new_entries = (dom_vegetation_cache_entry*)realloc(cache->entries,
                                                       capacity * sizeof(dom_vegetation_cache_entry));
    if (!new_entries) {
        return -1;
    }
    old_cap = cache->capacity;
    cache->entries = new_entries;
    cache->capacity = capacity;
    for (u32 i = old_cap; i < cache->capacity; ++i) {
        memset(&cache->entries[i], 0, sizeof(dom_vegetation_cache_entry));
        dom_vegetation_tile_init(&cache->entries[i].tile);
        cache->entries[i].valid = D_FALSE;
    }
    return 0;
}

static dom_vegetation_cache_entry* dom_vegetation_cache_find_entry(dom_vegetation_cache* cache,
                                                                   dom_domain_id domain_id,
                                                                   u64 tile_id,
                                                                   u32 resolution,
                                                                   u32 authoring_version,
                                                                   u64 window_start,
                                                                   u64 window_ticks)
{
    if (!cache || !cache->entries) {
        return (dom_vegetation_cache_entry*)0;
    }
    for (u32 i = 0u; i < cache->capacity; ++i) {
        dom_vegetation_cache_entry* entry = &cache->entries[i];
        if (!entry->valid) {
            continue;
        }
        if (entry->domain_id == domain_id &&
            entry->tile_id == tile_id &&
            entry->resolution == resolution &&
            entry->authoring_version == authoring_version &&
            entry->window_start == window_start &&
            entry->window_ticks == window_ticks) {
            return entry;
        }
    }
    return (dom_vegetation_cache_entry*)0;
}

static const dom_vegetation_tile* dom_vegetation_cache_peek(const dom_vegetation_cache* cache,
                                                            dom_domain_id domain_id,
                                                            u64 tile_id,
                                                            u32 resolution,
                                                            u32 authoring_version,
                                                            u64 window_start,
                                                            u64 window_ticks)
{
    if (!cache || !cache->entries) {
        return (const dom_vegetation_tile*)0;
    }
    for (u32 i = 0u; i < cache->capacity; ++i) {
        const dom_vegetation_cache_entry* entry = &cache->entries[i];
        if (!entry->valid) {
            continue;
        }
        if (entry->domain_id == domain_id &&
            entry->tile_id == tile_id &&
            entry->resolution == resolution &&
            entry->authoring_version == authoring_version &&
            entry->window_start == window_start &&
            entry->window_ticks == window_ticks) {
            return &entry->tile;
        }
    }
    return (const dom_vegetation_tile*)0;
}

static const dom_vegetation_tile* dom_vegetation_cache_get(dom_vegetation_cache* cache,
                                                           dom_domain_id domain_id,
                                                           u64 tile_id,
                                                           u32 resolution,
                                                           u32 authoring_version,
                                                           u64 window_start,
                                                           u64 window_ticks)
{
    dom_vegetation_cache_entry* entry;
    if (!cache) {
        return (const dom_vegetation_tile*)0;
    }
    entry = dom_vegetation_cache_find_entry(cache, domain_id, tile_id, resolution,
                                            authoring_version, window_start, window_ticks);
    if (!entry) {
        return (const dom_vegetation_tile*)0;
    }
    cache->use_counter += 1u;
    entry->last_used = cache->use_counter;
    return &entry->tile;
}

static dom_vegetation_cache_entry* dom_vegetation_cache_select_slot(dom_vegetation_cache* cache)
{
    dom_vegetation_cache_entry* best = (dom_vegetation_cache_entry*)0;
    if (!cache || !cache->entries || cache->capacity == 0u) {
        return (dom_vegetation_cache_entry*)0;
    }
    for (u32 i = 0u; i < cache->capacity; ++i) {
        dom_vegetation_cache_entry* entry = &cache->entries[i];
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

static dom_vegetation_tile* dom_vegetation_cache_put(dom_vegetation_cache* cache,
                                                     dom_domain_id domain_id,
                                                     dom_vegetation_tile* tile)
{
    dom_vegetation_cache_entry* entry;
    if (!cache || !tile) {
        return (dom_vegetation_tile*)0;
    }
    if (!cache->entries || cache->capacity == 0u) {
        return (dom_vegetation_tile*)0;
    }
    entry = dom_vegetation_cache_find_entry(cache, domain_id, tile->tile_id,
                                            tile->resolution, tile->authoring_version,
                                            tile->window_start, tile->window_ticks);
    if (!entry) {
        entry = dom_vegetation_cache_select_slot(cache);
    }
    if (!entry) {
        return (dom_vegetation_tile*)0;
    }
    if (entry->valid) {
        dom_vegetation_tile_free(&entry->tile);
    } else {
        cache->count += 1u;
        entry->insert_order = cache->next_insert_order++;
    }

    entry->domain_id = domain_id;
    entry->tile_id = tile->tile_id;
    entry->resolution = tile->resolution;
    entry->authoring_version = tile->authoring_version;
    entry->window_start = tile->window_start;
    entry->window_ticks = tile->window_ticks;
    entry->tile = *tile;
    entry->valid = D_TRUE;

    cache->use_counter += 1u;
    entry->last_used = cache->use_counter;

    dom_vegetation_tile_init(tile);
    return &entry->tile;
}

static void dom_vegetation_cache_invalidate_domain(dom_vegetation_cache* cache, dom_domain_id domain_id)
{
    if (!cache || !cache->entries) {
        return;
    }
    for (u32 i = 0u; i < cache->capacity; ++i) {
        dom_vegetation_cache_entry* entry = &cache->entries[i];
        if (entry->valid && entry->domain_id == domain_id) {
            dom_vegetation_tile_free(&entry->tile);
            entry->valid = D_FALSE;
            if (cache->count > 0u) {
                cache->count -= 1u;
            }
        }
    }
}

static q16_16 dom_veg_step_from_extent(q16_16 extent, u32 sample_dim)
{
    if (sample_dim <= 1u) {
        return 0;
    }
    return (q16_16)((i64)extent / (i64)(sample_dim - 1u));
}

static u32 dom_veg_sample_index_from_coord(q16_16 coord,
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

static void dom_veg_query_meta_refused(dom_domain_query_meta* meta,
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

static void dom_veg_query_meta_ok(dom_domain_query_meta* meta,
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

static d_bool dom_veg_resolution_allowed(u32 max_resolution, u32 resolution)
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

static d_bool dom_veg_domain_is_active(const dom_vegetation_domain* domain)
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

static q16_16 dom_veg_range_factor(q16_16 value, q16_16 minv, q16_16 maxv)
{
    q16_16 mid;
    q16_16 half;
    q16_16 diff;
    if (maxv <= minv) {
        return d_q16_16_from_int(1);
    }
    if (value < minv || value > maxv) {
        return 0;
    }
    half = d_fixed_div_q16_16(d_q16_16_sub(maxv, minv), d_q16_16_from_int(2));
    if (half <= 0) {
        return d_q16_16_from_int(1);
    }
    mid = d_q16_16_add(minv, half);
    diff = dom_veg_abs_q16_16(d_q16_16_sub(value, mid));
    if (diff >= half) {
        return 0;
    }
    return d_q16_16_sub(d_q16_16_from_int(1), d_fixed_div_q16_16(diff, half));
}

static q16_16 dom_veg_elevation_ratio(const dom_terrain_shape_desc* shape,
                                      const dom_domain_point* point,
                                      u32* out_unknown_flag)
{
    dom_terrain_latlon latlon;
    q16_16 denom;
    q16_16 ratio;
    if (out_unknown_flag) {
        *out_unknown_flag = 0u;
    }
    if (!shape || !point) {
        if (out_unknown_flag) {
            *out_unknown_flag = 1u;
        }
        return DOM_VEG_UNKNOWN_Q16;
    }
    if (shape->kind == DOM_TERRAIN_SHAPE_SLAB) {
        denom = shape->slab_half_thickness;
    } else {
        denom = shape->radius_equatorial;
        if (shape->radius_polar > denom) {
            denom = shape->radius_polar;
        }
    }
    if (denom <= 0) {
        denom = d_q16_16_from_int(1);
    }
    latlon = dom_terrain_local_to_latlon(shape, point);
    if (!latlon.valid) {
        if (out_unknown_flag) {
            *out_unknown_flag = 1u;
        }
        return DOM_VEG_UNKNOWN_Q16;
    }
    if (latlon.altitude < 0) {
        latlon.altitude = 0;
    }
    ratio = d_fixed_div_q16_16(latlon.altitude, denom);
    return dom_veg_clamp_q16_16(ratio, 0, d_q16_16_from_int(1));
}

static q16_16 dom_veg_recent_wetness(const dom_weather_domain* domain,
                                     u64 window_start,
                                     u64 window_ticks)
{
    dom_weather_event_list events;
    q16_16 sum = 0;
    u32 count = 0u;
    if (!domain || window_ticks == 0u) {
        return 0;
    }
    if (dom_weather_events_in_window(domain, window_start, window_ticks, &events) != 0) {
        return 0;
    }
    for (u32 i = 0u; i < events.count; ++i) {
        const dom_weather_event* event = &events.events[i];
        if (event->event_type == DOM_WEATHER_EVENT_RAIN ||
            event->event_type == DOM_WEATHER_EVENT_SNOW) {
            sum = d_q16_16_add(sum, event->intensity);
            count += 1u;
        }
    }
    if (count == 0u) {
        return 0;
    }
    return (q16_16)((i64)sum / (i64)count);
}

static q16_16 dom_veg_moisture_proxy(const dom_climate_sample* climate,
                                     const dom_weather_sample* weather,
                                     q16_16 recent_wetness,
                                     u32* out_flags)
{
    q16_16 moisture = 0;
    u32 flags = 0u;
    if (!climate || (climate->flags & DOM_CLIMATE_SAMPLE_FIELDS_UNKNOWN)) {
        flags |= DOM_CLIMATE_BIOME_INPUT_MOISTURE_UNKNOWN;
    }
    if (!weather || (weather->flags & DOM_WEATHER_SAMPLE_FIELDS_UNKNOWN)) {
        flags |= DOM_CLIMATE_BIOME_INPUT_MOISTURE_UNKNOWN;
    }
    if ((flags & DOM_CLIMATE_BIOME_INPUT_MOISTURE_UNKNOWN) == 0u) {
        moisture = d_q16_16_add(climate->precipitation_mean, weather->surface_wetness);
        moisture = d_q16_16_add(moisture, recent_wetness);
        moisture = (q16_16)((i64)moisture / 3);
        moisture = dom_veg_clamp_q16_16(moisture, 0, d_q16_16_from_int(1));
    }
    if (out_flags) {
        *out_flags = flags;
    }
    return moisture;
}

static d_bool dom_veg_biome_allowed(const dom_vegetation_species_desc* species, u32 biome_id)
{
    if (!species) {
        return D_FALSE;
    }
    if (species->preferred_biome_count == 0u) {
        return D_TRUE;
    }
    if (biome_id == 0u) {
        return D_FALSE;
    }
    for (u32 i = 0u; i < species->preferred_biome_count && i < DOM_VEG_MAX_BIOMES; ++i) {
        if (species->preferred_biomes[i] == biome_id) {
            return D_TRUE;
        }
    }
    return D_FALSE;
}

static q16_16 dom_veg_species_suitability(const dom_vegetation_species_desc* species,
                                          const dom_terrain_sample* terrain,
                                          const dom_climate_sample* climate,
                                          const dom_weather_sample* weather,
                                          const dom_geology_sample* geology,
                                          q16_16 moisture,
                                          u32 biome_id)
{
    q16_16 factor = d_q16_16_from_int(1);
    if (!species || !terrain || !climate || !weather || !geology) {
        return 0;
    }
    if (!dom_veg_biome_allowed(species, biome_id)) {
        return 0;
    }
    {
        q16_16 temp_factor = dom_veg_range_factor(climate->temperature_mean,
                                                  species->climate_tolerance.temperature_min,
                                                  species->climate_tolerance.temperature_max);
        q16_16 moisture_factor = dom_veg_range_factor(moisture,
                                                      species->climate_tolerance.moisture_min,
                                                      species->climate_tolerance.moisture_max);
        factor = d_q16_16_mul(factor, temp_factor);
        factor = d_q16_16_mul(factor, moisture_factor);
    }
    if (species->slope_max > 0) {
        if (terrain->slope >= species->slope_max) {
            return 0;
        }
        factor = d_q16_16_mul(factor,
                              d_q16_16_sub(d_q16_16_from_int(1),
                                          d_fixed_div_q16_16(terrain->slope, species->slope_max)));
    }
    if (species->material_mask != 0u) {
        u32 bit = 1u << (terrain->material_primary & 31u);
        if ((species->material_mask & bit) == 0u) {
            return 0;
        }
    }
    if (species->hardness_max > 0 || species->hardness_min > 0) {
        if (geology->hardness < species->hardness_min ||
            geology->hardness > species->hardness_max) {
            return 0;
        }
    }
    return dom_veg_clamp_q16_16(factor, 0, d_q16_16_from_int(1));
}

static d_bool dom_veg_instance_alive(const dom_vegetation_surface_desc* surface,
                                     const dom_vegetation_species_desc* species,
                                     u64 tick,
                                     u64 cell_key,
                                     u64* out_age)
{
    u64 regen = 0u;
    u64 lifespan = 0u;
    u64 birth_offset = 0u;
    u64 cycle_index = 0u;
    u64 phase = 0u;
    d_rng_state rng;
    if (!surface || !species || !out_age) {
        return D_FALSE;
    }
    *out_age = 0u;
    if (surface->mode == DOM_VEG_MODE_STATIC) {
        return D_TRUE;
    }
    regen = species->regen_period_ticks;
    lifespan = species->lifespan_ticks;
    if (regen == 0u) {
        if (lifespan == 0u) {
            *out_age = tick;
            return D_TRUE;
        }
        if (tick < lifespan) {
            *out_age = tick;
            return D_TRUE;
        }
        return D_FALSE;
    }
    dom_veg_rng_state_for_cell(&rng, surface, "birth", cell_key, species->species_id, 0u);
    birth_offset = dom_veg_rng_u64(&rng) % regen;
    if (tick < birth_offset) {
        return D_FALSE;
    }
    {
        u64 since_birth = tick - birth_offset;
        cycle_index = since_birth / regen;
        phase = since_birth % regen;
    }
    if (lifespan > 0u && phase >= lifespan) {
        return D_FALSE;
    }
    if (species->regen_chance <= 0) {
        return D_FALSE;
    }
    if (species->regen_chance < d_q16_16_from_int(1)) {
        q16_16 ratio;
        dom_veg_rng_state_for_cell(&rng, surface, "regen", cell_key, species->species_id, cycle_index);
        ratio = dom_veg_ratio_from_u32(d_rng_next_u32(&rng));
        if (ratio > species->regen_chance) {
            return D_FALSE;
        }
    }
    if (species->death_rate > 0 && species->die_period_ticks > 0u && lifespan > 0u) {
        u64 max_events = lifespan / species->die_period_ticks;
        if (max_events > 0u) {
            q16_16 ratio;
            dom_veg_rng_state_for_cell(&rng, surface, "die", cell_key, species->species_id, cycle_index);
            ratio = dom_veg_ratio_from_u32(d_rng_next_u32(&rng));
            if (ratio < species->death_rate) {
                u64 event_index = dom_veg_rng_u64(&rng) % max_events;
                u64 death_offset = event_index * species->die_period_ticks;
                if (phase >= death_offset) {
                    return D_FALSE;
                }
            }
        }
    }
    *out_age = phase;
    return D_TRUE;
}

static d_bool dom_veg_instance_build(const dom_vegetation_surface_desc* surface,
                                     const dom_vegetation_species_desc* species,
                                     u64 tick,
                                     u64 cell_key,
                                     q16_16 suitability,
                                     const dom_domain_point* cell_center,
                                     dom_vegetation_instance* out_instance)
{
    u64 age = 0u;
    q16_16 size = 0;
    q16_16 health = 0;
    if (!surface || !species || !cell_center || !out_instance) {
        return D_FALSE;
    }
    if (!dom_veg_instance_alive(surface, species, tick, cell_key, &age)) {
        return D_FALSE;
    }
    if (surface->mode == DOM_VEG_MODE_STATIC) {
        age = 0u;
        size = d_q16_16_mul(species->max_size, suitability);
    } else {
        if (species->grow_period_ticks > 0u) {
            u64 steps = (age / species->grow_period_ticks) + 1u;
            i64 scaled = (i64)species->growth_rate * (i64)steps;
            if (scaled < 0) {
                scaled = 0;
            }
            if (scaled > species->max_size) {
                scaled = species->max_size;
            }
            size = (q16_16)scaled;
        } else {
            size = species->max_size;
        }
        size = d_q16_16_mul(size, suitability);
    }
    if (size > species->max_size) {
        size = species->max_size;
    }
    health = suitability;
    if (species->lifespan_ticks > 0u) {
        q16_16 age_ratio = (q16_16)(((u64)age << 16) / species->lifespan_ticks);
        age_ratio = dom_veg_clamp_q16_16(age_ratio, 0, d_q16_16_from_int(1));
        health = d_q16_16_mul(health, d_q16_16_sub(d_q16_16_from_int(1), age_ratio));
    }
    memset(out_instance, 0, sizeof(*out_instance));
    out_instance->species_id = species->species_id;
    out_instance->location = *cell_center;
    out_instance->size = size;
    out_instance->health = health;
    out_instance->age_ticks = age;
    out_instance->flags = 0u;
    return D_TRUE;
}

static void dom_vegetation_sample_init(dom_vegetation_sample* sample)
{
    if (!sample) {
        return;
    }
    memset(sample, 0, sizeof(*sample));
    sample->coverage = DOM_VEG_UNKNOWN_Q16;
    sample->suitability = DOM_VEG_UNKNOWN_Q16;
    sample->biome_id = 0u;
}

static u64 dom_veg_window_start(u64 tick, u64 window_ticks)
{
    if (window_ticks == 0u) {
        return tick;
    }
    return tick - (tick % window_ticks);
}

static int dom_vegetation_build_tile_desc(const dom_vegetation_domain* domain,
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
    source = dom_terrain_surface_sdf(&domain->terrain_domain.surface);
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
    tx = dom_veg_floor_div_q16((q16_16)(point->x - source->bounds.min.x), tile_size);
    ty = dom_veg_floor_div_q16((q16_16)(point->y - source->bounds.min.y), tile_size);
    tz = dom_veg_floor_div_q16((q16_16)(point->z - source->bounds.min.z), tile_size);
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

static const dom_vegetation_tile* dom_vegetation_tile_get(dom_vegetation_domain* domain,
                                                          const dom_domain_tile_desc* desc,
                                                          u64 window_start,
                                                          u64 window_ticks,
                                                          d_bool allow_build);

static void dom_veg_eval_fields(const dom_vegetation_domain* domain,
                                const dom_domain_point* point,
                                u64 tick,
                                dom_domain_budget* budget,
                                dom_vegetation_sample* out_sample)
{
    dom_terrain_sample terrain;
    dom_climate_sample climate;
    dom_weather_sample weather;
    dom_geology_sample geology;
    dom_domain_budget local_budget;
    u32 moisture_flags = 0u;
    q16_16 moisture_proxy = DOM_VEG_UNKNOWN_Q16;
    q16_16 recent_wetness = 0;
    q16_16 elevation = DOM_VEG_UNKNOWN_Q16;
    u32 elevation_unknown = 0u;
    u32 biome_id = 0u;
    dom_climate_biome_result biome_result;
    dom_domain_budget* use_budget = budget;
    q16_16 max_suitability = 0;
    q16_16 best_coverage = 0;
    q16_16 selected_score = 0;
    d_bool has_instance = D_FALSE;
    dom_vegetation_instance instance;
    u32 best_species_index = 0u;
    i32 cx = 0;
    i32 cy = 0;
    i32 cz = 0;
    u64 cell_key = 0u;
    dom_domain_point cell_center;
    q16_16 cell_size;
    q16_16 phi_abs;
    if (!domain || !point || !out_sample) {
        return;
    }
    if (!use_budget) {
        dom_domain_budget_init(&local_budget, 0xFFFFFFFFu);
        use_budget = &local_budget;
    }

    dom_terrain_sample_query(&domain->terrain_domain, point, use_budget, &terrain);
    if (terrain.meta.status == DOM_DOMAIN_QUERY_REFUSED ||
        (terrain.flags & DOM_TERRAIN_SAMPLE_FIELDS_UNKNOWN)) {
        out_sample->flags |= DOM_VEG_SAMPLE_FIELDS_UNKNOWN;
        return;
    }

    cell_size = domain->surface.placement_cell_size;
    if (cell_size <= 0) {
        cell_size = d_q16_16_from_int(1);
    }
    phi_abs = dom_veg_abs_q16_16(terrain.phi);
    if (terrain.phi > 0 || phi_abs > cell_size) {
        out_sample->coverage = 0;
        out_sample->suitability = 0;
        out_sample->biome_id = 0u;
        out_sample->flags &= ~DOM_VEG_SAMPLE_FIELDS_UNKNOWN;
        return;
    }

    dom_climate_sample_query(&domain->climate_domain, point, use_budget, &climate);
    if (climate.meta.status == DOM_DOMAIN_QUERY_REFUSED ||
        (climate.flags & DOM_CLIMATE_SAMPLE_FIELDS_UNKNOWN)) {
        out_sample->flags |= DOM_VEG_SAMPLE_FIELDS_UNKNOWN;
        return;
    }

    dom_weather_sample_query(&domain->weather_domain, point, tick, use_budget, &weather);
    if (weather.meta.status == DOM_DOMAIN_QUERY_REFUSED ||
        (weather.flags & DOM_WEATHER_SAMPLE_FIELDS_UNKNOWN)) {
        out_sample->flags |= DOM_VEG_SAMPLE_FIELDS_UNKNOWN;
        return;
    }

    dom_geology_sample_query(&domain->geology_domain, point, use_budget, &geology);
    if (geology.meta.status == DOM_DOMAIN_QUERY_REFUSED ||
        (geology.flags & DOM_GEOLOGY_SAMPLE_FIELDS_UNKNOWN)) {
        out_sample->flags |= DOM_VEG_SAMPLE_FIELDS_UNKNOWN;
        return;
    }

    recent_wetness = dom_veg_recent_wetness(&domain->weather_domain,
                                            dom_veg_window_start(tick, domain->surface.weather_window_ticks),
                                            domain->surface.weather_window_ticks);
    moisture_proxy = dom_veg_moisture_proxy(&climate, &weather, recent_wetness, &moisture_flags);
    elevation = dom_veg_elevation_ratio(&domain->surface.shape, point, &elevation_unknown);
    if (elevation_unknown) {
        moisture_flags |= DOM_CLIMATE_BIOME_INPUT_ELEVATION_UNKNOWN;
    }

    memset(&biome_result, 0, sizeof(biome_result));
    if (domain->surface.biome_catalog.biome_count > 0u) {
        dom_climate_biome_inputs inputs;
        memset(&inputs, 0, sizeof(inputs));
        inputs.climate = &climate;
        inputs.terrain = &terrain;
        inputs.geology = &geology;
        inputs.elevation = elevation;
        inputs.moisture_proxy = moisture_proxy;
        inputs.flags = moisture_flags;
        (void)dom_climate_biome_resolve(&domain->surface.biome_catalog, &inputs, &biome_result);
        if ((biome_result.flags & DOM_CLIMATE_BIOME_RESULT_UNKNOWN) == 0u) {
            biome_id = biome_result.biome_id;
        }
    }

    dom_veg_cell_coord(cell_size, point, &cx, &cy, &cz);
    cell_key = dom_veg_cell_key(cx, cy, cz);
    cell_center = dom_veg_cell_center(cell_size, cx, cy, cz);

    for (u32 i = 0u; i < domain->surface.species_count && i < DOM_VEG_MAX_SPECIES; ++i) {
        const dom_vegetation_species_desc* species = &domain->surface.species[i];
        q16_16 suitability = dom_veg_species_suitability(species, &terrain, &climate,
                                                         &weather, &geology, moisture_proxy, biome_id);
        q16_16 coverage;
        d_rng_state rng;
        q16_16 ratio;
        q16_16 select_score;
        if (suitability <= 0) {
            continue;
        }
        coverage = d_q16_16_mul(domain->surface.density_base, suitability);
        coverage = dom_veg_clamp_q16_16(coverage, 0, d_q16_16_from_int(1));
        if (coverage > best_coverage) {
            best_coverage = coverage;
        }
        if (suitability > max_suitability) {
            max_suitability = suitability;
        }
        dom_veg_rng_state_for_cell(&rng, &domain->surface, "placement", cell_key,
                                   species->species_id, 0u);
        ratio = dom_veg_ratio_from_u32(d_rng_next_u32(&rng));
        if (ratio > coverage) {
            continue;
        }
        select_score = suitability;
        if (!has_instance ||
            select_score > selected_score ||
            (select_score == selected_score && species->species_id < domain->surface.species[best_species_index].species_id)) {
            if (dom_veg_instance_build(&domain->surface, species, tick, cell_key,
                                       suitability, &cell_center, &instance)) {
                has_instance = D_TRUE;
                best_species_index = i;
                selected_score = select_score;
            }
        }
    }

    out_sample->coverage = best_coverage;
    out_sample->suitability = max_suitability;
    out_sample->biome_id = biome_id;
    if (has_instance) {
        out_sample->instance = instance;
        out_sample->flags |= DOM_VEG_SAMPLE_INSTANCE_PRESENT;
    }
}

static d_bool dom_veg_tile_cached(const dom_vegetation_domain* domain,
                                  const dom_domain_tile_desc* desc,
                                  u64 window_start,
                                  u64 window_ticks)
{
    if (!domain || !desc) {
        return D_FALSE;
    }
    return dom_vegetation_cache_peek(&domain->cache,
                                     domain->surface.domain_id,
                                     desc->tile_id,
                                     desc->resolution,
                                     desc->authoring_version,
                                     window_start,
                                     window_ticks) != (const dom_vegetation_tile*)0;
}

static void dom_vegetation_sample_from_tile(const dom_vegetation_domain* domain,
                                            const dom_vegetation_tile* tile,
                                            const dom_domain_point* point,
                                            dom_vegetation_sample* out_sample)
{
    u32 ix;
    u32 iy;
    u32 iz;
    q16_16 step_x;
    q16_16 step_y;
    q16_16 step_z;
    u32 dim;
    u32 idx;
    i32 cx = 0;
    i32 cy = 0;
    i32 cz = 0;
    dom_domain_point cell_center;
    if (!tile || !point || !out_sample || !domain) {
        return;
    }
    dim = tile->sample_dim;
    step_x = dom_veg_step_from_extent((q16_16)(tile->bounds.max.x - tile->bounds.min.x), dim);
    step_y = dom_veg_step_from_extent((q16_16)(tile->bounds.max.y - tile->bounds.min.y), dim);
    step_z = dom_veg_step_from_extent((q16_16)(tile->bounds.max.z - tile->bounds.min.z), dim);
    ix = dom_veg_sample_index_from_coord(point->x, tile->bounds.min.x, tile->bounds.max.x, step_x, dim);
    iy = dom_veg_sample_index_from_coord(point->y, tile->bounds.min.y, tile->bounds.max.y, step_y, dim);
    iz = dom_veg_sample_index_from_coord(point->z, tile->bounds.min.z, tile->bounds.max.z, step_z, dim);
    idx = ix + iy * dim + iz * dim * dim;
    if (idx >= tile->sample_count) {
        return;
    }
    dom_vegetation_sample_init(out_sample);
    out_sample->coverage = tile->coverage[idx];
    out_sample->suitability = tile->suitability[idx];
    out_sample->biome_id = tile->biome_id[idx];
    out_sample->flags = tile->flags[idx] & DOM_VEG_SAMPLE_INSTANCE_PRESENT;
    if (out_sample->coverage == DOM_VEG_UNKNOWN_Q16 ||
        out_sample->suitability == DOM_VEG_UNKNOWN_Q16) {
        out_sample->flags |= DOM_VEG_SAMPLE_FIELDS_UNKNOWN;
    }
    if (out_sample->flags & DOM_VEG_SAMPLE_INSTANCE_PRESENT) {
        dom_veg_cell_coord(domain->surface.placement_cell_size, point, &cx, &cy, &cz);
        cell_center = dom_veg_cell_center(domain->surface.placement_cell_size, cx, cy, cz);
        out_sample->instance.species_id = tile->species_id[idx];
        out_sample->instance.location = cell_center;
        out_sample->instance.size = tile->size[idx];
        out_sample->instance.health = tile->health[idx];
        out_sample->instance.age_ticks = tile->age_ticks[idx];
        out_sample->instance.flags = 0u;
    }
}

static int dom_veg_tile_build(dom_vegetation_tile* tile,
                              const dom_domain_tile_desc* desc,
                              const dom_vegetation_domain* domain,
                              u64 tick,
                              u64 window_start,
                              u64 window_ticks)
{
    u32 sample_dim;
    u32 sample_count;
    q16_16 step_x;
    q16_16 step_y;
    q16_16 step_z;
    dom_domain_budget budget;
    if (!tile || !desc || !domain) {
        return -1;
    }
    sample_dim = desc->sample_dim;
    sample_count = sample_dim * sample_dim * sample_dim;
    if (sample_dim == 0u || sample_count == 0u) {
        return -1;
    }

    dom_vegetation_tile_init(tile);
    tile->tile_id = desc->tile_id;
    tile->resolution = desc->resolution;
    tile->sample_dim = sample_dim;
    tile->bounds = desc->bounds;
    tile->authoring_version = desc->authoring_version;
    tile->window_start = window_start;
    tile->window_ticks = window_ticks;
    tile->sample_count = sample_count;

    tile->data_q16 = (q16_16*)malloc(sizeof(q16_16) * sample_count * 4u);
    if (!tile->data_q16) {
        dom_vegetation_tile_free(tile);
        return -1;
    }
    tile->coverage = tile->data_q16;
    tile->suitability = tile->coverage + sample_count;
    tile->size = tile->suitability + sample_count;
    tile->health = tile->size + sample_count;

    tile->data_u32 = (u32*)malloc(sizeof(u32) * sample_count * 3u);
    if (!tile->data_u32) {
        dom_vegetation_tile_free(tile);
        return -1;
    }
    tile->biome_id = tile->data_u32;
    tile->species_id = tile->biome_id + sample_count;
    tile->flags = tile->species_id + sample_count;

    tile->age_ticks = (u64*)malloc(sizeof(u64) * sample_count);
    if (!tile->age_ticks) {
        dom_vegetation_tile_free(tile);
        return -1;
    }

    step_x = dom_veg_step_from_extent((q16_16)(desc->bounds.max.x - desc->bounds.min.x), sample_dim);
    step_y = dom_veg_step_from_extent((q16_16)(desc->bounds.max.y - desc->bounds.min.y), sample_dim);
    step_z = dom_veg_step_from_extent((q16_16)(desc->bounds.max.z - desc->bounds.min.z), sample_dim);

    for (u32 z = 0u; z < sample_dim; ++z) {
        q16_16 zpos = d_q16_16_add(desc->bounds.min.z, (q16_16)((i64)step_z * (i64)z));
        for (u32 y = 0u; y < sample_dim; ++y) {
            q16_16 ypos = d_q16_16_add(desc->bounds.min.y, (q16_16)((i64)step_y * (i64)y));
            for (u32 x = 0u; x < sample_dim; ++x) {
                q16_16 xpos = d_q16_16_add(desc->bounds.min.x, (q16_16)((i64)step_x * (i64)x));
                u32 idx = x + y * sample_dim + z * sample_dim * sample_dim;
                dom_domain_point p;
                dom_vegetation_sample sample;
                p.x = xpos;
                p.y = ypos;
                p.z = zpos;
                dom_domain_budget_init(&budget, 0xFFFFFFFFu);
                dom_vegetation_sample_init(&sample);
                dom_veg_eval_fields(domain, &p, tick, &budget, &sample);
                tile->coverage[idx] = sample.coverage;
                tile->suitability[idx] = sample.suitability;
                tile->biome_id[idx] = sample.biome_id;
                tile->flags[idx] = sample.flags & DOM_VEG_SAMPLE_INSTANCE_PRESENT;
                if (sample.flags & DOM_VEG_SAMPLE_INSTANCE_PRESENT) {
                    tile->species_id[idx] = sample.instance.species_id;
                    tile->size[idx] = sample.instance.size;
                    tile->health[idx] = sample.instance.health;
                    tile->age_ticks[idx] = sample.instance.age_ticks;
                } else {
                    tile->species_id[idx] = 0u;
                    tile->size[idx] = 0;
                    tile->health[idx] = 0;
                    tile->age_ticks[idx] = 0u;
                }
            }
        }
    }
    return 0;
}

static const dom_vegetation_tile* dom_vegetation_tile_get(dom_vegetation_domain* domain,
                                                          const dom_domain_tile_desc* desc,
                                                          u64 window_start,
                                                          u64 window_ticks,
                                                          d_bool allow_build)
{
    if (!domain || !desc) {
        return (const dom_vegetation_tile*)0;
    }
    if (domain->cache.entries) {
        const dom_vegetation_tile* cached = dom_vegetation_cache_get(&domain->cache,
                                                                     domain->surface.domain_id,
                                                                     desc->tile_id,
                                                                     desc->resolution,
                                                                     desc->authoring_version,
                                                                     window_start,
                                                                     window_ticks);
        if (cached) {
            return cached;
        }
        if (!allow_build) {
            return (const dom_vegetation_tile*)0;
        }
        {
            dom_vegetation_tile temp;
            dom_vegetation_tile_init(&temp);
            if (dom_veg_tile_build(&temp, desc, domain, window_start, window_start, window_ticks) != 0) {
                dom_vegetation_tile_free(&temp);
                return (const dom_vegetation_tile*)0;
            }
            cached = dom_vegetation_cache_put(&domain->cache, domain->surface.domain_id, &temp);
            if (!cached) {
                dom_vegetation_tile_free(&temp);
                return (const dom_vegetation_tile*)0;
            }
            return cached;
        }
    }
    return (const dom_vegetation_tile*)0;
}

void dom_vegetation_surface_desc_init(dom_vegetation_surface_desc* desc)
{
    dom_weather_surface_desc weather_desc;
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
    dom_climate_surface_desc_init(&desc->climate_desc);
    dom_geology_surface_desc_init(&desc->geology_desc);
    dom_weather_surface_desc_init(&weather_desc);
    desc->weather_schedule = weather_desc.schedule;

    desc->terrain_desc.domain_id = desc->domain_id;
    desc->terrain_desc.world_seed = desc->world_seed;
    desc->terrain_desc.meters_per_unit = desc->meters_per_unit;
    desc->terrain_desc.shape = desc->shape;

    desc->climate_desc.domain_id = desc->domain_id;
    desc->climate_desc.world_seed = desc->world_seed;
    desc->climate_desc.meters_per_unit = desc->meters_per_unit;
    desc->climate_desc.shape = desc->shape;

    desc->geology_desc.domain_id = desc->domain_id;
    desc->geology_desc.world_seed = desc->world_seed;
    desc->geology_desc.meters_per_unit = desc->meters_per_unit;
    desc->geology_desc.shape = desc->shape;

    desc->biome_catalog.biome_count = 0u;
    desc->species_count = 0u;
    desc->placement_cell_size = d_q16_16_from_int(8);
    desc->density_base = d_q16_16_from_double(0.2);
    desc->weather_window_ticks = 240u;
    desc->cache_capacity = 128u;
    desc->mode = DOM_VEG_MODE_STATIC;
}

void dom_vegetation_domain_init(dom_vegetation_domain* domain,
                                const dom_vegetation_surface_desc* desc)
{
    dom_vegetation_surface_desc normalized;
    dom_terrain_surface_desc terrain_desc;
    dom_climate_surface_desc climate_desc;
    dom_geology_surface_desc geology_desc;
    dom_weather_surface_desc weather_desc;
    u32 cache_capacity = 0u;
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

    climate_desc = desc->climate_desc;
    climate_desc.domain_id = desc->domain_id;
    climate_desc.world_seed = desc->world_seed;
    climate_desc.meters_per_unit = desc->meters_per_unit;
    climate_desc.shape = desc->shape;

    geology_desc = desc->geology_desc;
    geology_desc.domain_id = desc->domain_id;
    geology_desc.world_seed = desc->world_seed;
    geology_desc.meters_per_unit = desc->meters_per_unit;
    geology_desc.shape = desc->shape;

    dom_weather_surface_desc_init(&weather_desc);
    weather_desc.climate_desc = climate_desc;
    weather_desc.schedule = desc->weather_schedule;

    memset(domain, 0, sizeof(*domain));
    domain->surface = normalized;
    cache_capacity = desc->cache_capacity;
    dom_terrain_domain_init(&domain->terrain_domain, &terrain_desc, cache_capacity);
    dom_climate_domain_init(&domain->climate_domain, &climate_desc, cache_capacity);
    dom_weather_domain_init(&domain->weather_domain, &weather_desc, cache_capacity);
    dom_geology_domain_init(&domain->geology_domain, &geology_desc, cache_capacity);
    dom_domain_policy_init(&domain->policy);
    domain->existence_state = DOM_DOMAIN_EXISTENCE_REALIZED;
    domain->archival_state = DOM_DOMAIN_ARCHIVAL_LIVE;
    domain->authoring_version = 1u;
    dom_vegetation_cache_init(&domain->cache);
    if (cache_capacity > 0u) {
        dom_vegetation_cache_reserve(&domain->cache, cache_capacity);
    }
    domain->capsule_count = 0u;
}

void dom_vegetation_domain_free(dom_vegetation_domain* domain)
{
    if (!domain) {
        return;
    }
    dom_vegetation_cache_free(&domain->cache);
    dom_terrain_domain_free(&domain->terrain_domain);
    dom_climate_domain_free(&domain->climate_domain);
    dom_weather_domain_free(&domain->weather_domain);
    dom_geology_domain_free(&domain->geology_domain);
    domain->capsule_count = 0u;
}

void dom_vegetation_domain_set_state(dom_vegetation_domain* domain,
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
        dom_climate_domain_set_state(&domain->climate_domain, existence_state, archival_state);
        dom_weather_domain_set_state(&domain->weather_domain, existence_state, archival_state);
        dom_geology_domain_set_state(&domain->geology_domain, existence_state, archival_state);
        dom_vegetation_cache_invalidate_domain(&domain->cache, domain->surface.domain_id);
    }
}

void dom_vegetation_domain_set_policy(dom_vegetation_domain* domain,
                                      const dom_domain_policy* policy)
{
    if (!domain || !policy) {
        return;
    }
    domain->policy = *policy;
    dom_terrain_domain_set_policy(&domain->terrain_domain, policy);
    dom_climate_domain_set_policy(&domain->climate_domain, policy);
    dom_weather_domain_set_policy(&domain->weather_domain, policy);
    dom_geology_domain_set_policy(&domain->geology_domain, policy);
    dom_vegetation_cache_invalidate_domain(&domain->cache, domain->surface.domain_id);
}

int dom_vegetation_sample_query(const dom_vegetation_domain* domain,
                                const dom_domain_point* point,
                                u64 tick,
                                dom_domain_budget* budget,
                                dom_vegetation_sample* out_sample)
{
    dom_domain_tile_desc desc;
    const dom_domain_sdf_source* source;
    u32 budget_before = 0u;
    u32 cost_units = 0u;
    d_bool collapsed = D_FALSE;
    u64 window_ticks;
    u64 window_start;
    u64 eval_tick;
    if (!domain || !point || !out_sample) {
        return -1;
    }
    dom_vegetation_sample_init(out_sample);
    if (budget) {
        budget_before = budget->used_units;
    }
    if (!dom_veg_domain_is_active(domain)) {
        dom_veg_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_DOMAIN_INACTIVE, budget);
        out_sample->flags |= DOM_VEG_SAMPLE_FIELDS_UNKNOWN;
        return 0;
    }
    source = dom_terrain_surface_sdf(&domain->terrain_domain.surface);
    if (!source || !source->eval) {
        dom_veg_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_NO_SOURCE, budget);
        out_sample->flags |= DOM_VEG_SAMPLE_FIELDS_UNKNOWN;
        return 0;
    }
    if (!dom_domain_aabb_contains(&source->bounds, point)) {
        dom_veg_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_COARSE,
                              DOM_DOMAIN_CONFIDENCE_LOWER_BOUND, 0u, budget);
        out_sample->flags |= DOM_VEG_SAMPLE_FIELDS_UNKNOWN;
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
        dom_veg_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                              DOM_DOMAIN_CONFIDENCE_UNKNOWN, 0u, budget);
        out_sample->flags |= DOM_VEG_SAMPLE_FIELDS_UNKNOWN | DOM_VEG_SAMPLE_COLLAPSED;
        return 0;
    }

    window_ticks = domain->surface.weather_window_ticks;
    window_start = dom_veg_window_start(tick, window_ticks);
    eval_tick = window_start;

    if (dom_veg_resolution_allowed(domain->policy.max_resolution, DOM_DOMAIN_RES_FULL)) {
        if (dom_domain_budget_consume(budget, domain->policy.cost_full)) {
            dom_veg_eval_fields(domain, point, eval_tick, budget, out_sample);
            if (budget) {
                cost_units = budget->used_units - budget_before;
            }
            dom_veg_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_FULL,
                                  DOM_DOMAIN_CONFIDENCE_EXACT, cost_units, budget);
            return 0;
        }
    }

    if (dom_veg_resolution_allowed(domain->policy.max_resolution, DOM_DOMAIN_RES_MEDIUM)) {
        u32 cost = domain->policy.cost_medium;
        if (dom_vegetation_build_tile_desc(domain, point, DOM_DOMAIN_RES_MEDIUM, &desc) == 0) {
            if (!dom_veg_tile_cached(domain, &desc, window_start, window_ticks)) {
                cost += domain->policy.tile_build_cost_medium;
            }
            if (dom_domain_budget_consume(budget, cost)) {
                const dom_vegetation_tile* tile = dom_vegetation_tile_get((dom_vegetation_domain*)domain,
                                                                          &desc, window_start, window_ticks,
                                                                          D_TRUE);
                if (!tile) {
                    dom_veg_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_INTERNAL, budget);
                    out_sample->flags |= DOM_VEG_SAMPLE_FIELDS_UNKNOWN;
                    return 0;
                }
                dom_vegetation_sample_from_tile(domain, tile, point, out_sample);
                if (budget) {
                    cost_units = budget->used_units - budget_before;
                }
                dom_veg_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_MEDIUM,
                                      DOM_DOMAIN_CONFIDENCE_LOWER_BOUND, cost_units, budget);
                return 0;
            }
        }
    }

    if (dom_veg_resolution_allowed(domain->policy.max_resolution, DOM_DOMAIN_RES_COARSE)) {
        u32 cost = domain->policy.cost_coarse;
        if (dom_vegetation_build_tile_desc(domain, point, DOM_DOMAIN_RES_COARSE, &desc) == 0) {
            if (!dom_veg_tile_cached(domain, &desc, window_start, window_ticks)) {
                cost += domain->policy.tile_build_cost_coarse;
            }
            if (dom_domain_budget_consume(budget, cost)) {
                const dom_vegetation_tile* tile = dom_vegetation_tile_get((dom_vegetation_domain*)domain,
                                                                          &desc, window_start, window_ticks,
                                                                          D_TRUE);
                if (!tile) {
                    dom_veg_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_INTERNAL, budget);
                    out_sample->flags |= DOM_VEG_SAMPLE_FIELDS_UNKNOWN;
                    return 0;
                }
                dom_vegetation_sample_from_tile(domain, tile, point, out_sample);
                if (budget) {
                    cost_units = budget->used_units - budget_before;
                }
                dom_veg_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_COARSE,
                                      DOM_DOMAIN_CONFIDENCE_LOWER_BOUND, cost_units, budget);
                return 0;
            }
        }
    }

    if (dom_veg_resolution_allowed(domain->policy.max_resolution, DOM_DOMAIN_RES_ANALYTIC)) {
        if (dom_domain_budget_consume(budget, domain->policy.cost_analytic)) {
            dom_veg_eval_fields(domain, point, eval_tick, budget, out_sample);
            if (budget) {
                cost_units = budget->used_units - budget_before;
            }
            dom_veg_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                                  DOM_DOMAIN_CONFIDENCE_EXACT, cost_units, budget);
            return 0;
        }
    }

    dom_veg_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_BUDGET, budget);
    out_sample->flags |= DOM_VEG_SAMPLE_FIELDS_UNKNOWN;
    return 0;
}

static q16_16 dom_veg_hist_bin_ratio(u32 count, u32 total)
{
    if (total == 0u) {
        return 0;
    }
    return (q16_16)(((u64)count << 16) / total);
}

static u32 dom_veg_hist_bin(q16_16 value)
{
    q16_16 clamped = dom_veg_clamp_q16_16(value, 0, d_q16_16_from_int(1));
    u32 scaled = (u32)(((i64)clamped * (DOM_VEG_HIST_BINS - 1u)) >> 16);
    if (scaled >= DOM_VEG_HIST_BINS) {
        scaled = DOM_VEG_HIST_BINS - 1u;
    }
    return scaled;
}

static u32 dom_veg_species_index(const dom_vegetation_surface_desc* surface, u32 species_id)
{
    if (!surface) {
        return DOM_VEG_MAX_SPECIES;
    }
    for (u32 i = 0u; i < surface->species_count && i < DOM_VEG_MAX_SPECIES; ++i) {
        if (surface->species[i].species_id == species_id) {
            return i;
        }
    }
    return DOM_VEG_MAX_SPECIES;
}

static u32 dom_veg_rng_cursor(const dom_vegetation_surface_desc* surface,
                              const dom_vegetation_species_desc* species,
                              u64 tick)
{
    d_rng_state rng;
    u64 period = 1u;
    u64 event_index = 0u;
    if (!surface || !species) {
        return 0u;
    }
    if (species->regen_period_ticks > 0u) {
        period = species->regen_period_ticks;
    }
    if (period > 0u) {
        event_index = tick / period;
    }
    dom_veg_rng_state_for_cell(&rng, surface, "regen", 0u, species->species_id, event_index);
    return rng.state;
}

static int dom_veg_capsule_store(dom_vegetation_domain* domain,
                                 const dom_domain_tile_desc* desc,
                                 u64 tick,
                                 u64 window_ticks)
{
    dom_vegetation_macro_capsule capsule;
    dom_vegetation_tile tile;
    u32 size_bins[DOM_VEG_MAX_SPECIES][DOM_VEG_HIST_BINS];
    u32 age_bins[DOM_VEG_MAX_SPECIES][DOM_VEG_HIST_BINS];
    q16_16 coverage_sum = 0;
    u32 sample_count;
    if (!domain || !desc) {
        return -1;
    }
    if (domain->capsule_count >= DOM_VEG_MAX_CAPSULES) {
        return -2;
    }
    memset(size_bins, 0, sizeof(size_bins));
    memset(age_bins, 0, sizeof(age_bins));
    dom_vegetation_tile_init(&tile);
    if (dom_veg_tile_build(&tile, desc, domain, tick, tick, window_ticks) != 0) {
        dom_vegetation_tile_free(&tile);
        return -1;
    }
    sample_count = tile.sample_count;
    for (u32 i = 0u; i < sample_count; ++i) {
        coverage_sum = d_q16_16_add(coverage_sum, tile.coverage[i]);
        if (tile.flags[i] & DOM_VEG_SAMPLE_INSTANCE_PRESENT) {
            u32 species_index = dom_veg_species_index(&domain->surface, tile.species_id[i]);
            if (species_index < DOM_VEG_MAX_SPECIES) {
                q16_16 size_ratio = 0;
                q16_16 age_ratio = 0;
                const dom_vegetation_species_desc* species = &domain->surface.species[species_index];
                if (species->max_size > 0) {
                    size_ratio = d_fixed_div_q16_16(tile.size[i], species->max_size);
                }
                if (species->lifespan_ticks > 0u) {
                    age_ratio = (q16_16)(((u64)tile.age_ticks[i] << 16) / species->lifespan_ticks);
                }
                size_bins[species_index][dom_veg_hist_bin(size_ratio)] += 1u;
                age_bins[species_index][dom_veg_hist_bin(age_ratio)] += 1u;
            }
        }
    }

    memset(&capsule, 0, sizeof(capsule));
    capsule.capsule_id = desc->tile_id;
    capsule.tile_id = desc->tile_id;
    capsule.tick = tick;
    capsule.bounds = desc->bounds;
    capsule.coverage_avg = (sample_count > 0u) ? (q16_16)((i64)coverage_sum / (i64)sample_count) : 0;
    capsule.species_count = domain->surface.species_count;
    if (capsule.species_count > DOM_VEG_MAX_SPECIES) {
        capsule.species_count = DOM_VEG_MAX_SPECIES;
    }
    for (u32 s = 0u; s < capsule.species_count; ++s) {
        capsule.species_ids[s] = domain->surface.species[s].species_id;
        for (u32 b = 0u; b < DOM_VEG_HIST_BINS; ++b) {
            capsule.size_hist[s][b] = dom_veg_hist_bin_ratio(size_bins[s][b], sample_count);
            capsule.age_hist[s][b] = dom_veg_hist_bin_ratio(age_bins[s][b], sample_count);
        }
        capsule.rng_cursor[s] = dom_veg_rng_cursor(&domain->surface, &domain->surface.species[s], tick);
    }

    dom_vegetation_tile_free(&tile);
    domain->capsules[domain->capsule_count++] = capsule;
    return 0;
}

int dom_vegetation_domain_collapse_tile(dom_vegetation_domain* domain,
                                        const dom_domain_tile_desc* desc,
                                        u64 tick)
{
    if (!domain || !desc) {
        return -1;
    }
    if (domain->cache.entries) {
        for (u32 i = 0u; i < domain->cache.capacity; ++i) {
            dom_vegetation_cache_entry* entry = &domain->cache.entries[i];
            if (!entry->valid) {
                continue;
            }
            if (entry->domain_id == domain->surface.domain_id &&
                entry->tile_id == desc->tile_id) {
                dom_vegetation_tile_free(&entry->tile);
                entry->valid = D_FALSE;
                if (domain->cache.count > 0u) {
                    domain->cache.count -= 1u;
                }
            }
        }
    }
    return dom_veg_capsule_store(domain, desc, dom_veg_window_start(tick, domain->surface.weather_window_ticks),
                                 domain->surface.weather_window_ticks);
}

int dom_vegetation_domain_expand_tile(dom_vegetation_domain* domain, u64 tile_id)
{
    if (!domain) {
        return -1;
    }
    for (u32 i = 0u; i < domain->capsule_count; ++i) {
        if (domain->capsules[i].tile_id == tile_id) {
            domain->capsules[i] = domain->capsules[domain->capsule_count - 1u];
            domain->capsule_count -= 1u;
            return 0;
        }
    }
    return -2;
}

u32 dom_vegetation_domain_capsule_count(const dom_vegetation_domain* domain)
{
    return domain ? domain->capsule_count : 0u;
}

const dom_vegetation_macro_capsule* dom_vegetation_domain_capsule_at(const dom_vegetation_domain* domain,
                                                                     u32 index)
{
    if (!domain || index >= domain->capsule_count) {
        return (const dom_vegetation_macro_capsule*)0;
    }
    return &domain->capsules[index];
}
