/*
FILE: source/domino/world/animal_agents.cpp
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / world/animal_agents
RESPONSIBILITY: Implements deterministic animal agents with coarse, event-driven lifecycle sampling.
ALLOWED DEPENDENCIES: `include/domino/**` and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: Engine private headers outside world.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: Fixed-point only; deterministic ordering and math.
*/
#include "domino/world/animal_agents.h"

#include "domino/core/fixed_math.h"
#include "domino/core/rng_model.h"

#include <stdlib.h>
#include <string.h>
#include <stdio.h>

static q16_16 dom_animal_abs_q16_16(q16_16 v)
{
    return (v < 0) ? (q16_16)-v : v;
}

static q16_16 dom_animal_clamp_q16_16(q16_16 v, q16_16 lo, q16_16 hi)
{
    if (v < lo) {
        return lo;
    }
    if (v > hi) {
        return hi;
    }
    return v;
}

static i32 dom_animal_floor_div_q16(q16_16 value, q16_16 denom)
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

static u64 dom_animal_hash_u64(u64 h, u64 v)
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

static u64 dom_animal_cell_key(i32 cx, i32 cy, i32 cz)
{
    u64 h = 14695981039346656037ULL;
    h = dom_animal_hash_u64(h, (u64)(u32)cx);
    h = dom_animal_hash_u64(h, (u64)(u32)cy);
    h = dom_animal_hash_u64(h, (u64)(u32)cz);
    return h;
}

static q16_16 dom_animal_ratio_from_u32(u32 value)
{
    return (q16_16)(value >> 16);
}

static u64 dom_animal_rng_u64(d_rng_state* rng)
{
    u64 hi = (u64)d_rng_next_u32(rng);
    u64 lo = (u64)d_rng_next_u32(rng);
    return (hi << 32) | lo;
}

static void dom_animal_stream_name(char* out_name, size_t cap,
                                   dom_domain_id domain_id,
                                   const char* purpose)
{
    if (!out_name || cap == 0u) {
        return;
    }
    if (!purpose || !purpose[0]) {
        purpose = "unknown";
    }
    sprintf(out_name, "noise.stream.%llu.animal.%s",
            (unsigned long long)domain_id,
            purpose);
    out_name[cap - 1u] = '\0';
}

static void dom_animal_rng_state_for_cell(d_rng_state* rng,
                                          const dom_animal_surface_desc* surface,
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
    dom_animal_stream_name(stream, sizeof(stream), surface->domain_id, purpose);
    D_DET_GUARD_RNG_STREAM_NAME(stream);
    tick_index = dom_animal_hash_u64(cell_key, event_index);
    d_rng_state_from_context(rng,
                             surface->world_seed,
                             surface->domain_id,
                             (u64)species_id,
                             tick_index,
                             stream,
                             D_RNG_MIX_DOMAIN | D_RNG_MIX_PROCESS | D_RNG_MIX_TICK | D_RNG_MIX_STREAM);
}

static void dom_animal_cell_coord(q16_16 cell_size,
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
    *out_cx = dom_animal_floor_div_q16(point->x, cell_size);
    *out_cy = dom_animal_floor_div_q16(point->y, cell_size);
    *out_cz = dom_animal_floor_div_q16(point->z, cell_size);
}

static dom_domain_point dom_animal_cell_center(q16_16 cell_size, i32 cx, i32 cy, i32 cz)
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

static void dom_animal_cache_init(dom_animal_cache* cache)
{
    if (!cache) {
        return;
    }
    memset(cache, 0, sizeof(*cache));
}

static void dom_animal_tile_init(dom_animal_tile* tile)
{
    if (!tile) {
        return;
    }
    memset(tile, 0, sizeof(*tile));
}

static void dom_animal_tile_free(dom_animal_tile* tile)
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
    tile->suitability = (q16_16*)0;
    tile->vegetation_coverage = (q16_16*)0;
    tile->vegetation_consumed = (q16_16*)0;
    tile->energy = (q16_16*)0;
    tile->health = (q16_16*)0;
    tile->biome_id = (u32*)0;
    tile->species_id = (u32*)0;
    tile->need = (u32*)0;
    tile->movement_mode = (u32*)0;
    tile->death_reason = (u32*)0;
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

static void dom_animal_cache_free(dom_animal_cache* cache)
{
    if (!cache) {
        return;
    }
    if (cache->entries) {
        for (u32 i = 0u; i < cache->capacity; ++i) {
            dom_animal_tile_free(&cache->entries[i].tile);
        }
        free(cache->entries);
        cache->entries = (dom_animal_cache_entry*)0;
    }
    cache->capacity = 0u;
    cache->count = 0u;
    cache->use_counter = 0u;
    cache->next_insert_order = 0u;
}

static int dom_animal_cache_reserve(dom_animal_cache* cache, u32 capacity)
{
    dom_animal_cache_entry* new_entries;
    u32 old_cap;
    if (!cache) {
        return -1;
    }
    if (capacity <= cache->capacity) {
        return 0;
    }
    new_entries = (dom_animal_cache_entry*)realloc(cache->entries,
                                                   capacity * sizeof(dom_animal_cache_entry));
    if (!new_entries) {
        return -1;
    }
    old_cap = cache->capacity;
    cache->entries = new_entries;
    cache->capacity = capacity;
    for (u32 i = old_cap; i < cache->capacity; ++i) {
        memset(&cache->entries[i], 0, sizeof(dom_animal_cache_entry));
        dom_animal_tile_init(&cache->entries[i].tile);
        cache->entries[i].valid = D_FALSE;
    }
    return 0;
}

static dom_animal_cache_entry* dom_animal_cache_find_entry(dom_animal_cache* cache,
                                                           dom_domain_id domain_id,
                                                           u64 tile_id,
                                                           u32 resolution,
                                                           u32 authoring_version,
                                                           u64 window_start,
                                                           u64 window_ticks)
{
    if (!cache || !cache->entries) {
        return (dom_animal_cache_entry*)0;
    }
    for (u32 i = 0u; i < cache->capacity; ++i) {
        dom_animal_cache_entry* entry = &cache->entries[i];
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
    return (dom_animal_cache_entry*)0;
}

static const dom_animal_tile* dom_animal_cache_peek(const dom_animal_cache* cache,
                                                    dom_domain_id domain_id,
                                                    u64 tile_id,
                                                    u32 resolution,
                                                    u32 authoring_version,
                                                    u64 window_start,
                                                    u64 window_ticks)
{
    if (!cache || !cache->entries) {
        return (const dom_animal_tile*)0;
    }
    for (u32 i = 0u; i < cache->capacity; ++i) {
        const dom_animal_cache_entry* entry = &cache->entries[i];
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
    return (const dom_animal_tile*)0;
}

static const dom_animal_tile* dom_animal_cache_get(dom_animal_cache* cache,
                                                   dom_domain_id domain_id,
                                                   u64 tile_id,
                                                   u32 resolution,
                                                   u32 authoring_version,
                                                   u64 window_start,
                                                   u64 window_ticks)
{
    dom_animal_cache_entry* entry;
    if (!cache) {
        return (const dom_animal_tile*)0;
    }
    entry = dom_animal_cache_find_entry(cache, domain_id, tile_id, resolution,
                                        authoring_version, window_start, window_ticks);
    if (!entry) {
        return (const dom_animal_tile*)0;
    }
    cache->use_counter += 1u;
    entry->last_used = cache->use_counter;
    return &entry->tile;
}

static dom_animal_cache_entry* dom_animal_cache_select_slot(dom_animal_cache* cache)
{
    dom_animal_cache_entry* best = (dom_animal_cache_entry*)0;
    if (!cache || !cache->entries || cache->capacity == 0u) {
        return (dom_animal_cache_entry*)0;
    }
    for (u32 i = 0u; i < cache->capacity; ++i) {
        dom_animal_cache_entry* entry = &cache->entries[i];
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

static dom_animal_tile* dom_animal_cache_put(dom_animal_cache* cache,
                                             dom_domain_id domain_id,
                                             dom_animal_tile* tile)
{
    dom_animal_cache_entry* entry;
    if (!cache || !tile) {
        return (dom_animal_tile*)0;
    }
    if (!cache->entries || cache->capacity == 0u) {
        return (dom_animal_tile*)0;
    }
    entry = dom_animal_cache_find_entry(cache, domain_id, tile->tile_id,
                                        tile->resolution, tile->authoring_version,
                                        tile->window_start, tile->window_ticks);
    if (!entry) {
        entry = dom_animal_cache_select_slot(cache);
    }
    if (!entry) {
        return (dom_animal_tile*)0;
    }
    if (entry->valid) {
        dom_animal_tile_free(&entry->tile);
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

    dom_animal_tile_init(tile);
    return &entry->tile;
}

static void dom_animal_cache_invalidate_domain(dom_animal_cache* cache, dom_domain_id domain_id)
{
    if (!cache || !cache->entries) {
        return;
    }
    for (u32 i = 0u; i < cache->capacity; ++i) {
        dom_animal_cache_entry* entry = &cache->entries[i];
        if (entry->valid && entry->domain_id == domain_id) {
            dom_animal_tile_free(&entry->tile);
            entry->valid = D_FALSE;
            if (cache->count > 0u) {
                cache->count -= 1u;
            }
        }
    }
}

static q16_16 dom_animal_step_from_extent(q16_16 extent, u32 sample_dim)
{
    if (sample_dim <= 1u) {
        return 0;
    }
    return (q16_16)((i64)extent / (i64)(sample_dim - 1u));
}

static u32 dom_animal_sample_index_from_coord(q16_16 coord,
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

static void dom_animal_query_meta_refused(dom_domain_query_meta* meta,
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

static void dom_animal_query_meta_ok(dom_domain_query_meta* meta,
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

static d_bool dom_animal_resolution_allowed(u32 max_resolution, u32 resolution)
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

static d_bool dom_animal_domain_is_active(const dom_animal_domain* domain)
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

static q16_16 dom_animal_range_factor(q16_16 value, q16_16 minv, q16_16 maxv)
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
    diff = dom_animal_abs_q16_16(d_q16_16_sub(value, mid));
    if (diff >= half) {
        return 0;
    }
    return d_q16_16_sub(d_q16_16_from_int(1), d_fixed_div_q16_16(diff, half));
}

static q16_16 dom_animal_elevation_ratio(const dom_terrain_shape_desc* shape,
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
        return DOM_ANIMAL_UNKNOWN_Q16;
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
        return DOM_ANIMAL_UNKNOWN_Q16;
    }
    if (latlon.altitude < 0) {
        latlon.altitude = 0;
    }
    ratio = d_fixed_div_q16_16(latlon.altitude, denom);
    return dom_animal_clamp_q16_16(ratio, 0, d_q16_16_from_int(1));
}

static q16_16 dom_animal_moisture_proxy(const dom_climate_sample* climate,
                                        const dom_weather_sample* weather,
                                        u32* out_flags)
{
    q16_16 moisture = 0;
    u32 flags = 0u;
    if (!climate || (climate->flags & DOM_CLIMATE_SAMPLE_FIELDS_UNKNOWN)) {
        flags |= 1u;
    }
    if (!weather || (weather->flags & DOM_WEATHER_SAMPLE_FIELDS_UNKNOWN)) {
        flags |= 2u;
    }
    if (climate && !(climate->flags & DOM_CLIMATE_SAMPLE_FIELDS_UNKNOWN)) {
        moisture = climate->precipitation_mean;
    }
    if (weather && !(weather->flags & DOM_WEATHER_SAMPLE_FIELDS_UNKNOWN)) {
        moisture = d_fixed_div_q16_16(d_q16_16_add(moisture, weather->surface_wetness),
                                      d_q16_16_from_int(2));
    }
    moisture = dom_animal_clamp_q16_16(moisture, 0, d_q16_16_from_int(1));
    if (out_flags) {
        *out_flags = flags;
    }
    return moisture;
}

static void dom_animal_sample_init(dom_animal_sample* sample)
{
    if (!sample) {
        return;
    }
    memset(sample, 0, sizeof(*sample));
    sample->suitability = 0;
    sample->biome_id = 0u;
    sample->vegetation_coverage = DOM_ANIMAL_UNKNOWN_Q16;
    sample->vegetation_consumed = 0;
    sample->agent.species_id = 0u;
    sample->agent.location.x = 0;
    sample->agent.location.y = 0;
    sample->agent.location.z = 0;
    sample->agent.energy = DOM_ANIMAL_UNKNOWN_Q16;
    sample->agent.health = DOM_ANIMAL_UNKNOWN_Q16;
    sample->agent.age_ticks = 0u;
    sample->agent.current_need = DOM_ANIMAL_NEED_UNKNOWN;
    sample->agent.movement_mode = DOM_ANIMAL_MOVE_LAND;
    sample->death_reason = DOM_ANIMAL_DEATH_NONE;
}

static u64 dom_animal_window_start(u64 tick, u64 window_ticks)
{
    if (window_ticks == 0u) {
        return tick;
    }
    return tick - (tick % window_ticks);
}

static u64 dom_animal_spawn_period(const dom_animal_surface_desc* surface,
                                   const dom_animal_species_desc* species)
{
    u64 period = 0u;
    if (species) {
        period = species->reproduction.gestation_ticks;
        if (period == 0u) {
            period = species->lifespan_ticks;
        }
    }
    if (period == 0u && surface) {
        period = surface->decision_period_ticks;
    }
    if (period == 0u) {
        period = 1u;
    }
    return period;
}

static q16_16 dom_animal_need_threshold_eat(void)
{
    return d_q16_16_from_double(0.3);
}

static q16_16 dom_animal_need_threshold_repro(void)
{
    return d_q16_16_from_double(0.6);
}

static q16_16 dom_animal_need_threshold_stress(void)
{
    return d_q16_16_from_double(0.1);
}

static u32 dom_animal_species_index(const dom_animal_surface_desc* surface, u32 species_id)
{
    if (!surface) {
        return DOM_ANIMAL_MAX_SPECIES;
    }
    for (u32 i = 0u; i < surface->species_count && i < DOM_ANIMAL_MAX_SPECIES; ++i) {
        if (surface->species[i].species_id == species_id) {
            return i;
        }
    }
    return DOM_ANIMAL_MAX_SPECIES;
}

static d_bool dom_animal_diet_allows(const dom_animal_species_desc* species,
                                     const dom_vegetation_sample* vegetation)
{
    if (!species) {
        return D_TRUE;
    }
    if (species->diet_count == 0u) {
        return D_TRUE;
    }
    if (!vegetation || !(vegetation->flags & DOM_VEG_SAMPLE_INSTANCE_PRESENT)) {
        return D_FALSE;
    }
    for (u32 i = 0u; i < species->diet_count && i < DOM_ANIMAL_MAX_DIET; ++i) {
        if (species->diet_species[i] == vegetation->instance.species_id) {
            return D_TRUE;
        }
    }
    return D_FALSE;
}

static q16_16 dom_animal_hist_bin_ratio(u32 count, u32 total)
{
    if (total == 0u) {
        return 0;
    }
    return (q16_16)(((u64)count << 16) / total);
}

static u32 dom_animal_hist_bin(q16_16 value)
{
    q16_16 clamped = dom_animal_clamp_q16_16(value, 0, d_q16_16_from_int(1));
    u32 scaled = (u32)(((i64)clamped * (DOM_ANIMAL_HIST_BINS - 1u)) >> 16);
    if (scaled >= DOM_ANIMAL_HIST_BINS) {
        scaled = DOM_ANIMAL_HIST_BINS - 1u;
    }
    return scaled;
}

static u32 dom_animal_rng_cursor(const dom_animal_surface_desc* surface,
                                 const dom_animal_species_desc* species,
                                 u64 tick)
{
    d_rng_state rng;
    u64 period = dom_animal_spawn_period(surface, species);
    u64 event_index = 0u;
    if (!surface || !species) {
        return 0u;
    }
    if (period > 0u) {
        event_index = tick / period;
    }
    dom_animal_rng_state_for_cell(&rng, surface, "spawn", 0u, species->species_id, event_index);
    return rng.state;
}

static void dom_animal_eval_fields(const dom_animal_domain* domain,
                                   const dom_domain_point* point,
                                   u64 tick,
                                   dom_domain_budget* budget,
                                   dom_animal_sample* out_sample)
{
    dom_terrain_sample terrain;
    dom_climate_sample climate;
    dom_weather_sample weather;
    dom_vegetation_sample vegetation;
    dom_climate_biome_inputs biome_inputs;
    dom_climate_biome_result biome_result;
    q16_16 temperature;
    q16_16 moisture;
    q16_16 elevation;
    q16_16 veg_coverage;
    q16_16 veg_consumed = 0;
    q16_16 climate_factor = d_q16_16_from_double(0.5);
    q16_16 suitability = 0;
    q16_16 best_weight = 0;
    q16_16 density;
    q16_16 base_density;
    u32 best_index = DOM_ANIMAL_MAX_SPECIES;
    u32 biome_unknown = 1u;
    u32 moisture_flags = 0u;
    u32 elevation_unknown = 0u;
    u32 fields_unknown = 0u;
    i32 cell_x = 0;
    i32 cell_y = 0;
    i32 cell_z = 0;
    u64 cell_key = 0u;
    dom_domain_point cell_center;
    if (!domain || !point || !out_sample) {
        return;
    }
    dom_animal_sample_init(out_sample);

    (void)dom_terrain_sample_query(&domain->vegetation_domain.terrain_domain, point, budget, &terrain);
    if (terrain.meta.status == DOM_DOMAIN_QUERY_REFUSED ||
        (terrain.flags & DOM_TERRAIN_SAMPLE_FIELDS_UNKNOWN)) {
        out_sample->flags |= DOM_ANIMAL_SAMPLE_FIELDS_UNKNOWN;
        out_sample->meta = terrain.meta;
        return;
    }

    (void)dom_climate_sample_query(&domain->vegetation_domain.climate_domain, point, budget, &climate);
    if (climate.meta.status == DOM_DOMAIN_QUERY_REFUSED ||
        (climate.flags & DOM_CLIMATE_SAMPLE_FIELDS_UNKNOWN)) {
        out_sample->flags |= DOM_ANIMAL_SAMPLE_FIELDS_UNKNOWN;
        out_sample->meta = climate.meta;
        return;
    }

    (void)dom_weather_sample_query(&domain->vegetation_domain.weather_domain, point, tick, budget, &weather);
    if (weather.meta.status == DOM_DOMAIN_QUERY_REFUSED ||
        (weather.flags & DOM_WEATHER_SAMPLE_FIELDS_UNKNOWN)) {
        fields_unknown = 1u;
    }

    (void)dom_vegetation_sample_query(&domain->vegetation_domain, point, tick, budget, &vegetation);
    if (vegetation.meta.status == DOM_DOMAIN_QUERY_REFUSED ||
        (vegetation.flags & DOM_VEG_SAMPLE_FIELDS_UNKNOWN)) {
        fields_unknown = 1u;
    }

    temperature = climate.temperature_mean;
    if (!(weather.flags & DOM_WEATHER_SAMPLE_FIELDS_UNKNOWN)) {
        temperature = weather.temperature_current;
    }

    moisture = dom_animal_moisture_proxy(&climate, &weather, &moisture_flags);
    if (moisture_flags) {
        fields_unknown = 1u;
    }

    elevation = dom_animal_elevation_ratio(&domain->surface.shape, point, &elevation_unknown);
    if (elevation_unknown) {
        fields_unknown = 1u;
    }

    memset(&biome_inputs, 0, sizeof(biome_inputs));
    biome_inputs.climate = &climate;
    biome_inputs.terrain = &terrain;
    biome_inputs.geology = (const dom_geology_sample*)0;
    biome_inputs.elevation = elevation;
    biome_inputs.moisture_proxy = moisture;
    if (elevation_unknown) {
        biome_inputs.flags |= DOM_CLIMATE_BIOME_INPUT_ELEVATION_UNKNOWN;
    }
    if (moisture_flags) {
        biome_inputs.flags |= DOM_CLIMATE_BIOME_INPUT_MOISTURE_UNKNOWN;
    }
    (void)dom_climate_biome_resolve(&domain->surface.vegetation_desc.biome_catalog,
                                    &biome_inputs,
                                    &biome_result);
    if (!(biome_result.flags & DOM_CLIMATE_BIOME_RESULT_UNKNOWN)) {
        out_sample->biome_id = biome_result.biome_id;
        biome_unknown = 0u;
    }

    veg_coverage = vegetation.coverage;
    if (vegetation.flags & DOM_VEG_SAMPLE_FIELDS_UNKNOWN) {
        veg_coverage = 0;
    }
    out_sample->vegetation_coverage = veg_coverage;

    base_density = domain->surface.density_base;
    dom_animal_cell_coord(domain->surface.placement_cell_size, point, &cell_x, &cell_y, &cell_z);
    cell_key = dom_animal_cell_key(cell_x, cell_y, cell_z);
    cell_center = dom_animal_cell_center(domain->surface.placement_cell_size, cell_x, cell_y, cell_z);

    for (u32 i = 0u; i < domain->surface.species_count && i < DOM_ANIMAL_MAX_SPECIES; ++i) {
        const dom_animal_species_desc* species = &domain->surface.species[i];
        q16_16 temp_factor = dom_animal_range_factor(temperature,
                                                     species->climate_tolerance.temperature_min,
                                                     species->climate_tolerance.temperature_max);
        q16_16 moisture_factor = dom_animal_range_factor(moisture,
                                                         species->climate_tolerance.moisture_min,
                                                         species->climate_tolerance.moisture_max);
        q16_16 biome_factor = d_q16_16_from_int(1);
        q16_16 veg_factor = d_q16_16_from_int(1);
        q16_16 walk_factor = d_q16_16_from_int(1);
        q16_16 local_suitability = 0;

        if (biome_unknown && species->preferred_biome_count > 0u) {
            biome_factor = d_q16_16_from_double(0.5);
        } else if (species->preferred_biome_count > 0u) {
            biome_factor = 0;
            for (u32 b = 0u; b < species->preferred_biome_count && b < DOM_ANIMAL_MAX_BIOMES; ++b) {
                if (species->preferred_biomes[b] == out_sample->biome_id) {
                    biome_factor = d_q16_16_from_int(1);
                    break;
                }
            }
        }

        if (fields_unknown) {
            veg_factor = d_q16_16_from_double(0.5);
        } else {
            veg_factor = dom_animal_clamp_q16_16(veg_coverage, 0, d_q16_16_from_int(1));
        }

        if (!dom_animal_diet_allows(species, &vegetation)) {
            veg_factor = 0;
        }

        if (species->movement_mode == DOM_ANIMAL_MOVE_LAND) {
            q16_16 slope_max = species->slope_max;
            if (slope_max <= 0) {
                slope_max = domain->vegetation_domain.terrain_domain.surface.walkable_max_slope;
            }
            if (terrain.slope > slope_max || terrain.phi > 0) {
                walk_factor = 0;
            }
        } else if (species->movement_mode == DOM_ANIMAL_MOVE_WATER) {
            if (terrain.phi <= 0) {
                walk_factor = 0;
            }
        }

        local_suitability = d_q16_16_mul(temp_factor, moisture_factor);
        local_suitability = d_q16_16_mul(local_suitability, biome_factor);
        local_suitability = d_q16_16_mul(local_suitability, veg_factor);
        local_suitability = d_q16_16_mul(local_suitability, walk_factor);

        if (local_suitability <= 0) {
            continue;
        }

        density = d_q16_16_mul(base_density, local_suitability);
        if (density <= 0) {
            continue;
        }

        {
            d_rng_state rng;
            q16_16 roll;
            u64 period = dom_animal_spawn_period(&domain->surface, species);
            u64 event_index = (period > 0u) ? (tick / period) : 0u;
            dom_animal_rng_state_for_cell(&rng, &domain->surface, "spawn", cell_key,
                                          species->species_id, event_index);
            roll = dom_animal_ratio_from_u32(d_rng_next_u32(&rng));
            if (roll < density) {
                q16_16 weight = d_q16_16_sub(density, roll);
                if (best_index == DOM_ANIMAL_MAX_SPECIES || weight > best_weight) {
                    best_index = i;
                    best_weight = weight;
                    suitability = local_suitability;
                }
            }
        }
    }

    out_sample->suitability = suitability;
    if (best_index == DOM_ANIMAL_MAX_SPECIES) {
        if (fields_unknown) {
            out_sample->flags |= DOM_ANIMAL_SAMPLE_FIELDS_UNKNOWN;
        }
        return;
    }

    {
        const dom_animal_species_desc* species = &domain->surface.species[best_index];
        u64 period = dom_animal_spawn_period(&domain->surface, species);
        u64 event_index = (period > 0u) ? (tick / period) : 0u;
        d_rng_state rng;
        u64 birth_tick = 0u;
        u64 age_ticks = 0u;
        q16_16 energy;
        q16_16 health;
        u32 need = DOM_ANIMAL_NEED_WANDER;
        q16_16 rest_req = species->metabolism.rest_requirement;
        q16_16 temperature_factor = dom_animal_range_factor(temperature,
                                                            species->climate_tolerance.temperature_min,
                                                            species->climate_tolerance.temperature_max);
        q16_16 moisture_factor = dom_animal_range_factor(moisture,
                                                         species->climate_tolerance.moisture_min,
                                                         species->climate_tolerance.moisture_max);
        climate_factor = d_q16_16_mul(temperature_factor, moisture_factor);

        dom_animal_rng_state_for_cell(&rng, &domain->surface, "birth", cell_key,
                                      species->species_id, event_index);
        if (period > 0u) {
            birth_tick = (event_index * period) + (dom_animal_rng_u64(&rng) % period);
        }
        if (tick < birth_tick) {
            if (fields_unknown) {
                out_sample->flags |= DOM_ANIMAL_SAMPLE_FIELDS_UNKNOWN;
            }
            return;
        }
        age_ticks = tick - birth_tick;
        if (species->lifespan_ticks > 0u && age_ticks >= species->lifespan_ticks) {
            out_sample->death_reason = DOM_ANIMAL_DEATH_AGE;
            out_sample->flags |= DOM_ANIMAL_SAMPLE_DEAD;
            if (fields_unknown) {
                out_sample->flags |= DOM_ANIMAL_SAMPLE_FIELDS_UNKNOWN;
            }
            return;
        }

        if (veg_coverage < 0) {
            veg_coverage = 0;
        }
        veg_consumed = species->metabolism.energy_consumption_rate;
        if (veg_consumed < 0) {
            veg_consumed = 0;
        }
        if (veg_consumed > veg_coverage) {
            veg_consumed = veg_coverage;
        }
        out_sample->vegetation_consumed = veg_consumed;

        energy = dom_animal_clamp_q16_16(veg_coverage, 0, d_q16_16_from_int(1));
        energy = d_q16_16_mul(energy, suitability);
        if (terrain.travel_cost > 0) {
            q16_16 penalty = dom_animal_clamp_q16_16(terrain.travel_cost, 0, d_q16_16_from_int(1));
            energy = d_q16_16_sub(energy, d_q16_16_mul(penalty, d_q16_16_from_double(0.2)));
        }
        energy = d_q16_16_add(energy, veg_consumed);
        energy = d_q16_16_sub(energy, species->metabolism.energy_consumption_rate);
        energy = dom_animal_clamp_q16_16(energy, 0, d_q16_16_from_int(1));

        health = d_q16_16_mul(energy, climate_factor);
        health = dom_animal_clamp_q16_16(health, 0, d_q16_16_from_int(1));

        if (energy <= 0) {
            out_sample->death_reason = DOM_ANIMAL_DEATH_STARVATION;
            out_sample->flags |= DOM_ANIMAL_SAMPLE_DEAD;
            if (fields_unknown) {
                out_sample->flags |= DOM_ANIMAL_SAMPLE_FIELDS_UNKNOWN;
            }
            return;
        }
        if (climate_factor <= dom_animal_need_threshold_stress()) {
            out_sample->death_reason = DOM_ANIMAL_DEATH_STRESS;
            out_sample->flags |= DOM_ANIMAL_SAMPLE_DEAD;
            if (fields_unknown) {
                out_sample->flags |= DOM_ANIMAL_SAMPLE_FIELDS_UNKNOWN;
            }
            return;
        }

        if (energy < dom_animal_need_threshold_eat()) {
            need = DOM_ANIMAL_NEED_EAT;
        } else if (rest_req > 0 && energy < rest_req) {
            need = DOM_ANIMAL_NEED_REST;
        } else if (age_ticks >= species->reproduction.maturity_age_ticks &&
                   energy > dom_animal_need_threshold_repro()) {
            need = DOM_ANIMAL_NEED_REPRODUCE;
        } else {
            need = DOM_ANIMAL_NEED_WANDER;
        }

        {
            dom_domain_point location = cell_center;
            q16_16 move_speed = species->movement_speed;
            q16_16 cell_size = domain->surface.placement_cell_size;
            q16_16 half = d_q16_16_from_double(0.5);
            q16_16 span = d_q16_16_from_int(2);
            q16_16 move_radius;
            u64 decision_period = domain->surface.decision_period_ticks;
            u64 decision_index = 0u;
            d_rng_state move_rng;
            if (move_speed <= 0) {
                move_speed = d_q16_16_from_double(0.2);
            }
            if (cell_size <= 0) {
                cell_size = d_q16_16_from_int(1);
            }
            move_radius = d_q16_16_mul(cell_size, move_speed);
            if (move_radius > d_fixed_div_q16_16(cell_size, d_q16_16_from_int(2))) {
                move_radius = d_fixed_div_q16_16(cell_size, d_q16_16_from_int(2));
            }
            if (decision_period == 0u) {
                decision_period = 1u;
            }
            decision_index = tick / decision_period;
            dom_animal_rng_state_for_cell(&move_rng, &domain->surface, "move", cell_key,
                                          species->species_id, decision_index);
            {
                q16_16 rx = dom_animal_ratio_from_u32(d_rng_next_u32(&move_rng));
                q16_16 ry = dom_animal_ratio_from_u32(d_rng_next_u32(&move_rng));
                q16_16 rz = dom_animal_ratio_from_u32(d_rng_next_u32(&move_rng));
                q16_16 ox = d_q16_16_mul(d_q16_16_mul(d_q16_16_sub(rx, half), span), move_radius);
                q16_16 oy = d_q16_16_mul(d_q16_16_mul(d_q16_16_sub(ry, half), span), move_radius);
                q16_16 oz = d_q16_16_mul(d_q16_16_mul(d_q16_16_sub(rz, half), span), move_radius);
                if (species->movement_mode == DOM_ANIMAL_MOVE_LAND) {
                    if (terrain.slope <= domain->vegetation_domain.terrain_domain.surface.walkable_max_slope &&
                        terrain.phi <= 0) {
                        location.x = d_q16_16_add(location.x, ox);
                        location.y = d_q16_16_add(location.y, oy);
                        location.z = d_q16_16_add(location.z, oz);
                    }
                } else if (species->movement_mode == DOM_ANIMAL_MOVE_WATER) {
                    if (terrain.phi > 0) {
                        location.x = d_q16_16_add(location.x, ox);
                        location.y = d_q16_16_add(location.y, oy);
                        location.z = d_q16_16_add(location.z, oz);
                    }
                } else {
                    location.x = d_q16_16_add(location.x, ox);
                    location.y = d_q16_16_add(location.y, oy);
                    location.z = d_q16_16_add(location.z, oz);
                }
            }

            out_sample->flags |= DOM_ANIMAL_SAMPLE_AGENT_PRESENT;
            if (fields_unknown) {
                out_sample->flags |= DOM_ANIMAL_SAMPLE_FIELDS_UNKNOWN;
            }
            out_sample->agent.species_id = species->species_id;
            out_sample->agent.location = location;
            out_sample->agent.energy = energy;
            out_sample->agent.health = health;
            out_sample->agent.age_ticks = age_ticks;
            out_sample->agent.current_need = need;
            out_sample->agent.movement_mode = species->movement_mode;
        }
    }
}

static void dom_animal_sample_from_tile(const dom_animal_domain* domain,
                                        const dom_animal_tile* tile,
                                        const dom_domain_point* point,
                                        dom_animal_sample* out_sample)
{
    u32 ix;
    u32 iy;
    u32 iz;
    u32 sample_dim;
    u32 index;
    q16_16 step_x;
    q16_16 step_y;
    q16_16 step_z;
    if (!domain || !tile || !point || !out_sample || tile->sample_count == 0u) {
        return;
    }
    sample_dim = tile->sample_dim;
    step_x = dom_animal_step_from_extent((q16_16)(tile->bounds.max.x - tile->bounds.min.x), sample_dim);
    step_y = dom_animal_step_from_extent((q16_16)(tile->bounds.max.y - tile->bounds.min.y), sample_dim);
    step_z = dom_animal_step_from_extent((q16_16)(tile->bounds.max.z - tile->bounds.min.z), sample_dim);

    ix = dom_animal_sample_index_from_coord(point->x, tile->bounds.min.x, tile->bounds.max.x, step_x, sample_dim);
    iy = dom_animal_sample_index_from_coord(point->y, tile->bounds.min.y, tile->bounds.max.y, step_y, sample_dim);
    iz = dom_animal_sample_index_from_coord(point->z, tile->bounds.min.z, tile->bounds.max.z, step_z, sample_dim);
    index = (iz * sample_dim + iy) * sample_dim + ix;
    if (index >= tile->sample_count) {
        index = tile->sample_count - 1u;
    }

    dom_animal_sample_init(out_sample);
    out_sample->suitability = tile->suitability[index];
    out_sample->biome_id = tile->biome_id[index];
    out_sample->vegetation_coverage = tile->vegetation_coverage[index];
    out_sample->vegetation_consumed = tile->vegetation_consumed[index];
    out_sample->agent.species_id = tile->species_id[index];
    out_sample->agent.energy = tile->energy[index];
    out_sample->agent.health = tile->health[index];
    out_sample->agent.age_ticks = tile->age_ticks[index];
    out_sample->agent.current_need = tile->need[index];
    out_sample->agent.movement_mode = tile->movement_mode[index];
    out_sample->death_reason = tile->death_reason[index];
    out_sample->flags = tile->flags[index];
    out_sample->agent.location = *point;
}

static int dom_animal_tile_build(dom_animal_tile* tile,
                                 const dom_domain_tile_desc* desc,
                                 const dom_animal_domain* domain,
                                 u64 eval_tick,
                                 u64 window_start,
                                 u64 window_ticks)
{
    u32 sample_dim;
    u32 sample_count;
    q16_16 step_x;
    q16_16 step_y;
    q16_16 step_z;
    q16_16* qptr;
    u32* uptr;
    if (!tile || !desc || !domain) {
        return -1;
    }
    sample_dim = desc->sample_dim;
    if (sample_dim == 0u) {
        return -1;
    }
    sample_count = sample_dim * sample_dim * sample_dim;
    if (sample_count == 0u) {
        return -1;
    }

    dom_animal_tile_init(tile);
    tile->tile_id = desc->tile_id;
    tile->resolution = desc->resolution;
    tile->sample_dim = sample_dim;
    tile->bounds = desc->bounds;
    tile->authoring_version = desc->authoring_version;
    tile->window_start = window_start;
    tile->window_ticks = window_ticks;
    tile->sample_count = sample_count;

    tile->data_q16 = (q16_16*)malloc(sample_count * 5u * sizeof(q16_16));
    tile->data_u32 = (u32*)malloc(sample_count * 6u * sizeof(u32));
    tile->age_ticks = (u64*)malloc(sample_count * sizeof(u64));
    if (!tile->data_q16 || !tile->data_u32 || !tile->age_ticks) {
        dom_animal_tile_free(tile);
        return -1;
    }

    qptr = tile->data_q16;
    tile->suitability = qptr;
    qptr += sample_count;
    tile->vegetation_coverage = qptr;
    qptr += sample_count;
    tile->vegetation_consumed = qptr;
    qptr += sample_count;
    tile->energy = qptr;
    qptr += sample_count;
    tile->health = qptr;
    qptr += sample_count;

    uptr = tile->data_u32;
    tile->biome_id = uptr;
    uptr += sample_count;
    tile->species_id = uptr;
    uptr += sample_count;
    tile->need = uptr;
    uptr += sample_count;
    tile->movement_mode = uptr;
    uptr += sample_count;
    tile->death_reason = uptr;
    uptr += sample_count;
    tile->flags = uptr;

    step_x = dom_animal_step_from_extent((q16_16)(tile->bounds.max.x - tile->bounds.min.x), sample_dim);
    step_y = dom_animal_step_from_extent((q16_16)(tile->bounds.max.y - tile->bounds.min.y), sample_dim);
    step_z = dom_animal_step_from_extent((q16_16)(tile->bounds.max.z - tile->bounds.min.z), sample_dim);

    {
        u32 index = 0u;
        for (u32 iz = 0u; iz < sample_dim; ++iz) {
            q16_16 z = (q16_16)(tile->bounds.min.z + (q16_16)((i64)step_z * (i64)iz));
            for (u32 iy = 0u; iy < sample_dim; ++iy) {
                q16_16 y = (q16_16)(tile->bounds.min.y + (q16_16)((i64)step_y * (i64)iy));
                for (u32 ix = 0u; ix < sample_dim; ++ix) {
                    q16_16 x = (q16_16)(tile->bounds.min.x + (q16_16)((i64)step_x * (i64)ix));
                    dom_domain_point point;
                    dom_animal_sample sample;
                    point.x = x;
                    point.y = y;
                    point.z = z;
                    dom_animal_eval_fields(domain, &point, eval_tick, (dom_domain_budget*)0, &sample);

                    tile->suitability[index] = sample.suitability;
                    tile->biome_id[index] = sample.biome_id;
                    tile->vegetation_coverage[index] = sample.vegetation_coverage;
                    tile->vegetation_consumed[index] = sample.vegetation_consumed;
                    tile->species_id[index] = sample.agent.species_id;
                    tile->energy[index] = sample.agent.energy;
                    tile->health[index] = sample.agent.health;
                    tile->age_ticks[index] = sample.agent.age_ticks;
                    tile->need[index] = sample.agent.current_need;
                    tile->movement_mode[index] = sample.agent.movement_mode;
                    tile->death_reason[index] = sample.death_reason;
                    tile->flags[index] = sample.flags;
                    index += 1u;
                }
            }
        }
    }
    return 0;
}

static int dom_animal_build_tile_desc(const dom_animal_domain* domain,
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
    source = dom_terrain_surface_sdf(&domain->vegetation_domain.terrain_domain.surface);
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
    tx = dom_animal_floor_div_q16((q16_16)(point->x - source->bounds.min.x), tile_size);
    ty = dom_animal_floor_div_q16((q16_16)(point->y - source->bounds.min.y), tile_size);
    tz = dom_animal_floor_div_q16((q16_16)(point->z - source->bounds.min.z), tile_size);
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

static d_bool dom_animal_tile_cached(const dom_animal_domain* domain,
                                     const dom_domain_tile_desc* desc,
                                     u64 window_start,
                                     u64 window_ticks)
{
    if (!domain || !desc) {
        return D_FALSE;
    }
    return dom_animal_cache_peek(&domain->cache, domain->surface.domain_id,
                                 desc->tile_id, desc->resolution, desc->authoring_version,
                                 window_start, window_ticks) != (const dom_animal_tile*)0;
}

static const dom_animal_tile* dom_animal_tile_get(dom_animal_domain* domain,
                                                  const dom_domain_tile_desc* desc,
                                                  u64 window_start,
                                                  u64 window_ticks,
                                                  d_bool allow_build)
{
    if (!domain || !desc) {
        return (const dom_animal_tile*)0;
    }
    {
        const dom_animal_tile* cached = dom_animal_cache_get(&domain->cache,
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
            return (const dom_animal_tile*)0;
        }
        {
            dom_animal_tile temp;
            dom_animal_tile_init(&temp);
            if (dom_animal_tile_build(&temp, desc, domain, window_start, window_start, window_ticks) != 0) {
                dom_animal_tile_free(&temp);
                return (const dom_animal_tile*)0;
            }
            cached = dom_animal_cache_put(&domain->cache, domain->surface.domain_id, &temp);
            if (!cached) {
                dom_animal_tile_free(&temp);
                return (const dom_animal_tile*)0;
            }
            return cached;
        }
    }
}

void dom_animal_surface_desc_init(dom_animal_surface_desc* desc)
{
    dom_vegetation_surface_desc veg_desc;
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

    dom_vegetation_surface_desc_init(&veg_desc);
    veg_desc.domain_id = desc->domain_id;
    veg_desc.world_seed = desc->world_seed;
    veg_desc.meters_per_unit = desc->meters_per_unit;
    veg_desc.shape = desc->shape;
    veg_desc.cache_capacity = 128u;
    veg_desc.mode = DOM_VEG_MODE_STATIC;
    if (veg_desc.species_count == 0u) {
        veg_desc.species_count = 1u;
        veg_desc.species[0].species_id = d_rng_hash_str32("veg.generic");
        veg_desc.species[0].climate_tolerance.temperature_min = d_q16_16_from_int(-1);
        veg_desc.species[0].climate_tolerance.temperature_max = d_q16_16_from_int(2);
        veg_desc.species[0].climate_tolerance.moisture_min = d_q16_16_from_int(-1);
        veg_desc.species[0].climate_tolerance.moisture_max = d_q16_16_from_int(2);
    }

    desc->vegetation_desc = veg_desc;
    desc->species_count = 0u;
    desc->placement_cell_size = d_q16_16_from_int(12);
    desc->density_base = d_q16_16_from_double(0.25);
    desc->decision_period_ticks = 120u;
    desc->cache_capacity = 128u;
}

static void dom_animal_species_defaults(dom_animal_species_desc* species)
{
    if (!species) {
        return;
    }
    memset(species, 0, sizeof(*species));
    species->climate_tolerance.temperature_min = d_q16_16_from_int(0);
    species->climate_tolerance.temperature_max = d_q16_16_from_int(1);
    species->climate_tolerance.moisture_min = d_q16_16_from_int(0);
    species->climate_tolerance.moisture_max = d_q16_16_from_int(1);
    species->movement_mode = DOM_ANIMAL_MOVE_LAND;
    species->metabolism.energy_consumption_rate = d_q16_16_from_double(0.1);
    species->metabolism.rest_requirement = d_q16_16_from_double(0.4);
    species->reproduction.maturity_age_ticks = 400u;
    species->reproduction.gestation_ticks = 200u;
    species->reproduction.offspring_min = 1u;
    species->reproduction.offspring_max = 2u;
    species->reproduction.reproduction_chance = d_q16_16_from_double(0.5);
    species->lifespan_ticks = 1600u;
    species->size_class = 0u;
    species->movement_speed = d_q16_16_from_double(0.2);
    species->slope_max = d_q16_16_from_double(0.8);
    species->death_rate = d_q16_16_from_double(0.1);
    species->maturity_tag = 0u;
}

void dom_animal_domain_init(dom_animal_domain* domain,
                            const dom_animal_surface_desc* desc)
{
    dom_animal_surface_desc normalized;
    dom_vegetation_surface_desc veg_desc;
    u32 cache_capacity = 0u;
    if (!domain || !desc) {
        return;
    }
    normalized = *desc;
    normalized.domain_id = desc->domain_id;
    normalized.world_seed = desc->world_seed;
    normalized.meters_per_unit = desc->meters_per_unit;
    normalized.shape = desc->shape;

    veg_desc = desc->vegetation_desc;
    veg_desc.domain_id = desc->domain_id;
    veg_desc.world_seed = desc->world_seed;
    veg_desc.meters_per_unit = desc->meters_per_unit;
    veg_desc.shape = desc->shape;

    veg_desc.terrain_desc.domain_id = desc->domain_id;
    veg_desc.terrain_desc.world_seed = desc->world_seed;
    veg_desc.terrain_desc.meters_per_unit = desc->meters_per_unit;
    veg_desc.terrain_desc.shape = desc->shape;

    veg_desc.climate_desc.domain_id = desc->domain_id;
    veg_desc.climate_desc.world_seed = desc->world_seed;
    veg_desc.climate_desc.meters_per_unit = desc->meters_per_unit;
    veg_desc.climate_desc.shape = desc->shape;

    veg_desc.geology_desc.domain_id = desc->domain_id;
    veg_desc.geology_desc.world_seed = desc->world_seed;
    veg_desc.geology_desc.meters_per_unit = desc->meters_per_unit;
    veg_desc.geology_desc.shape = desc->shape;

    if (normalized.species_count == 0u) {
        for (u32 i = 0u; i < DOM_ANIMAL_MAX_SPECIES; ++i) {
            dom_animal_species_defaults(&normalized.species[i]);
        }
    }

    memset(domain, 0, sizeof(*domain));
    domain->surface = normalized;
    domain->surface.vegetation_desc = veg_desc;
    cache_capacity = desc->cache_capacity;
    dom_vegetation_domain_init(&domain->vegetation_domain, &veg_desc);
    dom_domain_policy_init(&domain->policy);
    domain->existence_state = DOM_DOMAIN_EXISTENCE_REALIZED;
    domain->archival_state = DOM_DOMAIN_ARCHIVAL_LIVE;
    domain->authoring_version = 1u;
    dom_animal_cache_init(&domain->cache);
    if (cache_capacity > 0u) {
        dom_animal_cache_reserve(&domain->cache, cache_capacity);
    }
    domain->capsule_count = 0u;
}

void dom_animal_domain_free(dom_animal_domain* domain)
{
    if (!domain) {
        return;
    }
    dom_animal_cache_free(&domain->cache);
    dom_vegetation_domain_free(&domain->vegetation_domain);
    domain->capsule_count = 0u;
}

void dom_animal_domain_set_state(dom_animal_domain* domain,
                                 u32 existence_state,
                                 u32 archival_state)
{
    if (!domain) {
        return;
    }
    if (domain->existence_state != existence_state || domain->archival_state != archival_state) {
        domain->existence_state = existence_state;
        domain->archival_state = archival_state;
        dom_vegetation_domain_set_state(&domain->vegetation_domain, existence_state, archival_state);
        dom_animal_cache_invalidate_domain(&domain->cache, domain->surface.domain_id);
    }
}

void dom_animal_domain_set_policy(dom_animal_domain* domain,
                                  const dom_domain_policy* policy)
{
    if (!domain || !policy) {
        return;
    }
    domain->policy = *policy;
    dom_vegetation_domain_set_policy(&domain->vegetation_domain, policy);
    dom_animal_cache_invalidate_domain(&domain->cache, domain->surface.domain_id);
}

int dom_animal_sample_query(const dom_animal_domain* domain,
                            const dom_domain_point* point,
                            u64 tick,
                            dom_domain_budget* budget,
                            dom_animal_sample* out_sample)
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
    dom_animal_sample_init(out_sample);
    if (budget) {
        budget_before = budget->used_units;
    }
    if (!dom_animal_domain_is_active(domain)) {
        dom_animal_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_DOMAIN_INACTIVE, budget);
        out_sample->flags |= DOM_ANIMAL_SAMPLE_FIELDS_UNKNOWN;
        return 0;
    }
    source = dom_terrain_surface_sdf(&domain->vegetation_domain.terrain_domain.surface);
    if (!source || !source->eval) {
        dom_animal_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_NO_SOURCE, budget);
        out_sample->flags |= DOM_ANIMAL_SAMPLE_FIELDS_UNKNOWN;
        return 0;
    }
    if (!dom_domain_aabb_contains(&source->bounds, point)) {
        dom_animal_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_COARSE,
                                 DOM_DOMAIN_CONFIDENCE_LOWER_BOUND, 0u, budget);
        out_sample->flags |= DOM_ANIMAL_SAMPLE_FIELDS_UNKNOWN;
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
        dom_animal_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                                 DOM_DOMAIN_CONFIDENCE_UNKNOWN, 0u, budget);
        out_sample->flags |= DOM_ANIMAL_SAMPLE_FIELDS_UNKNOWN | DOM_ANIMAL_SAMPLE_COLLAPSED;
        return 0;
    }

    window_ticks = domain->surface.decision_period_ticks;
    if (window_ticks == 0u) {
        window_ticks = 1u;
    }
    window_start = dom_animal_window_start(tick, window_ticks);
    eval_tick = window_start;

    if (dom_animal_resolution_allowed(domain->policy.max_resolution, DOM_DOMAIN_RES_FULL)) {
        if (dom_domain_budget_consume(budget, domain->policy.cost_full)) {
            dom_animal_eval_fields(domain, point, eval_tick, budget, out_sample);
            if (budget) {
                cost_units = budget->used_units - budget_before;
            }
            dom_animal_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_FULL,
                                     DOM_DOMAIN_CONFIDENCE_EXACT, cost_units, budget);
            return 0;
        }
    }

    if (dom_animal_resolution_allowed(domain->policy.max_resolution, DOM_DOMAIN_RES_MEDIUM)) {
        u32 cost = domain->policy.cost_medium;
        if (dom_animal_build_tile_desc(domain, point, DOM_DOMAIN_RES_MEDIUM, &desc) == 0) {
            if (!dom_animal_tile_cached(domain, &desc, window_start, window_ticks)) {
                cost += domain->policy.tile_build_cost_medium;
            }
            if (dom_domain_budget_consume(budget, cost)) {
                const dom_animal_tile* tile = dom_animal_tile_get((dom_animal_domain*)domain,
                                                                  &desc,
                                                                  window_start,
                                                                  window_ticks,
                                                                  D_TRUE);
                if (!tile) {
                    dom_animal_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_INTERNAL, budget);
                    out_sample->flags |= DOM_ANIMAL_SAMPLE_FIELDS_UNKNOWN;
                    return 0;
                }
                dom_animal_sample_from_tile(domain, tile, point, out_sample);
                if (budget) {
                    cost_units = budget->used_units - budget_before;
                }
                dom_animal_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_MEDIUM,
                                         DOM_DOMAIN_CONFIDENCE_LOWER_BOUND, cost_units, budget);
                return 0;
            }
        }
    }

    if (dom_animal_resolution_allowed(domain->policy.max_resolution, DOM_DOMAIN_RES_COARSE)) {
        u32 cost = domain->policy.cost_coarse;
        if (dom_animal_build_tile_desc(domain, point, DOM_DOMAIN_RES_COARSE, &desc) == 0) {
            if (!dom_animal_tile_cached(domain, &desc, window_start, window_ticks)) {
                cost += domain->policy.tile_build_cost_coarse;
            }
            if (dom_domain_budget_consume(budget, cost)) {
                const dom_animal_tile* tile = dom_animal_tile_get((dom_animal_domain*)domain,
                                                                  &desc,
                                                                  window_start,
                                                                  window_ticks,
                                                                  D_TRUE);
                if (!tile) {
                    dom_animal_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_INTERNAL, budget);
                    out_sample->flags |= DOM_ANIMAL_SAMPLE_FIELDS_UNKNOWN;
                    return 0;
                }
                dom_animal_sample_from_tile(domain, tile, point, out_sample);
                if (budget) {
                    cost_units = budget->used_units - budget_before;
                }
                dom_animal_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_COARSE,
                                         DOM_DOMAIN_CONFIDENCE_LOWER_BOUND, cost_units, budget);
                return 0;
            }
        }
    }

    if (dom_animal_resolution_allowed(domain->policy.max_resolution, DOM_DOMAIN_RES_ANALYTIC)) {
        if (dom_domain_budget_consume(budget, domain->policy.cost_analytic)) {
            dom_animal_eval_fields(domain, point, eval_tick, budget, out_sample);
            if (budget) {
                cost_units = budget->used_units - budget_before;
            }
            dom_animal_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                                     DOM_DOMAIN_CONFIDENCE_EXACT, cost_units, budget);
            return 0;
        }
    }

    dom_animal_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_BUDGET, budget);
    out_sample->flags |= DOM_ANIMAL_SAMPLE_FIELDS_UNKNOWN;
    return 0;
}

static int dom_animal_capsule_store(dom_animal_domain* domain,
                                    const dom_domain_tile_desc* desc,
                                    u64 tick,
                                    u64 window_ticks)
{
    dom_animal_macro_capsule capsule;
    dom_animal_tile tile;
    u32 energy_bins[DOM_ANIMAL_MAX_SPECIES][DOM_ANIMAL_HIST_BINS];
    u32 age_bins[DOM_ANIMAL_MAX_SPECIES][DOM_ANIMAL_HIST_BINS];
    u32 population_counts[DOM_ANIMAL_MAX_SPECIES];
    u32 sample_count;
    if (!domain || !desc) {
        return -1;
    }
    if (domain->capsule_count >= DOM_ANIMAL_MAX_CAPSULES) {
        return -2;
    }
    memset(energy_bins, 0, sizeof(energy_bins));
    memset(age_bins, 0, sizeof(age_bins));
    memset(population_counts, 0, sizeof(population_counts));

    dom_animal_tile_init(&tile);
    if (dom_animal_tile_build(&tile, desc, domain, tick, tick, window_ticks) != 0) {
        dom_animal_tile_free(&tile);
        return -1;
    }

    sample_count = tile.sample_count;
    for (u32 i = 0u; i < sample_count; ++i) {
        if (tile.flags[i] & DOM_ANIMAL_SAMPLE_AGENT_PRESENT) {
            u32 species_index = dom_animal_species_index(&domain->surface, tile.species_id[i]);
            if (species_index < DOM_ANIMAL_MAX_SPECIES) {
                const dom_animal_species_desc* species = &domain->surface.species[species_index];
                q16_16 age_ratio = 0;
                q16_16 energy_ratio = dom_animal_clamp_q16_16(tile.energy[i], 0, d_q16_16_from_int(1));
                population_counts[species_index] += 1u;
                if (species->lifespan_ticks > 0u) {
                    age_ratio = (q16_16)(((u64)tile.age_ticks[i] << 16) / species->lifespan_ticks);
                }
                age_bins[species_index][dom_animal_hist_bin(age_ratio)] += 1u;
                energy_bins[species_index][dom_animal_hist_bin(energy_ratio)] += 1u;
            }
        }
    }

    memset(&capsule, 0, sizeof(capsule));
    capsule.capsule_id = desc->tile_id;
    capsule.tile_id = desc->tile_id;
    capsule.tick = tick;
    capsule.bounds = desc->bounds;
    capsule.species_count = domain->surface.species_count;
    if (capsule.species_count > DOM_ANIMAL_MAX_SPECIES) {
        capsule.species_count = DOM_ANIMAL_MAX_SPECIES;
    }
    for (u32 s = 0u; s < capsule.species_count; ++s) {
        capsule.species_ids[s] = domain->surface.species[s].species_id;
        capsule.population_counts[s] = population_counts[s];
        for (u32 b = 0u; b < DOM_ANIMAL_HIST_BINS; ++b) {
            capsule.energy_hist[s][b] = dom_animal_hist_bin_ratio(energy_bins[s][b], population_counts[s]);
            capsule.age_hist[s][b] = dom_animal_hist_bin_ratio(age_bins[s][b], population_counts[s]);
        }
        capsule.rng_cursor[s] = dom_animal_rng_cursor(&domain->surface, &domain->surface.species[s], tick);
    }

    dom_animal_tile_free(&tile);
    domain->capsules[domain->capsule_count++] = capsule;
    return 0;
}

int dom_animal_domain_collapse_tile(dom_animal_domain* domain,
                                    const dom_domain_tile_desc* desc,
                                    u64 tick)
{
    if (!domain || !desc) {
        return -1;
    }
    if (domain->cache.entries) {
        for (u32 i = 0u; i < domain->cache.capacity; ++i) {
            dom_animal_cache_entry* entry = &domain->cache.entries[i];
            if (!entry->valid) {
                continue;
            }
            if (entry->domain_id == domain->surface.domain_id &&
                entry->tile_id == desc->tile_id) {
                dom_animal_tile_free(&entry->tile);
                entry->valid = D_FALSE;
                if (domain->cache.count > 0u) {
                    domain->cache.count -= 1u;
                }
            }
        }
    }
    return dom_animal_capsule_store(domain, desc, dom_animal_window_start(tick, domain->surface.decision_period_ticks),
                                    domain->surface.decision_period_ticks);
}

int dom_animal_domain_expand_tile(dom_animal_domain* domain, u64 tile_id)
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

u32 dom_animal_domain_capsule_count(const dom_animal_domain* domain)
{
    return domain ? domain->capsule_count : 0u;
}

const dom_animal_macro_capsule* dom_animal_domain_capsule_at(const dom_animal_domain* domain,
                                                             u32 index)
{
    if (!domain || index >= domain->capsule_count) {
        return (const dom_animal_macro_capsule*)0;
    }
    return &domain->capsules[index];
}
