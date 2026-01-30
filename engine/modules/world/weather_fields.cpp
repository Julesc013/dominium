/*
FILE: source/domino/world/weather_fields.cpp
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / world/weather_fields
RESPONSIBILITY: Implements deterministic weather event sampling and climate perturbations.
ALLOWED DEPENDENCIES: `include/domino/**` and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: Engine private headers outside world.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: Fixed-point only; deterministic ordering and math.
*/
#include "domino/world/weather_fields.h"

#include "domino/core/fixed_math.h"
#include "domino/core/rng_model.h"

#include <stdlib.h>
#include <string.h>
#include <stdio.h>

static const char* dom_weather_event_name(u32 event_type)
{
    switch (event_type) {
        case DOM_WEATHER_EVENT_RAIN: return "rain";
        case DOM_WEATHER_EVENT_SNOW: return "snow";
        case DOM_WEATHER_EVENT_HEATWAVE: return "heatwave";
        case DOM_WEATHER_EVENT_COLD_SNAP: return "cold_snap";
        case DOM_WEATHER_EVENT_WIND_SHIFT: return "wind_shift";
        default: return "unknown";
    }
}

static q16_16 dom_weather_clamp_q16_16(q16_16 v, q16_16 lo, q16_16 hi)
{
    if (v < lo) {
        return lo;
    }
    if (v > hi) {
        return hi;
    }
    return v;
}

static q16_16 dom_weather_lerp(q16_16 a, q16_16 b, q16_16 t)
{
    return d_q16_16_add(a, d_q16_16_mul(d_q16_16_sub(b, a), t));
}

static q16_16 dom_weather_ratio_from_u32(u32 value)
{
    return (q16_16)(value >> 16);
}

static u64 dom_weather_rng_u64(d_rng_state* rng)
{
    u64 hi = (u64)d_rng_next_u32(rng);
    u64 lo = (u64)d_rng_next_u32(rng);
    return (hi << 32) | lo;
}

static q16_16 dom_weather_rng_range_q16(d_rng_state* rng, q16_16 minv, q16_16 maxv)
{
    q16_16 ratio = dom_weather_ratio_from_u32(d_rng_next_u32(rng));
    if (maxv < minv) {
        q16_16 tmp = minv;
        minv = maxv;
        maxv = tmp;
    }
    return dom_weather_lerp(minv, maxv, ratio);
}

static q16_16 dom_weather_shape_scale(const dom_terrain_shape_desc* shape)
{
    if (!shape) {
        return d_q16_16_from_int(1);
    }
    if (shape->kind == DOM_TERRAIN_SHAPE_SLAB) {
        if (shape->slab_half_extent > 0) {
            return shape->slab_half_extent;
        }
        return d_q16_16_from_int(256);
    }
    if (shape->radius_equatorial > 0) {
        return shape->radius_equatorial;
    }
    if (shape->radius_polar > 0) {
        return shape->radius_polar;
    }
    return d_q16_16_from_int(256);
}

static void dom_weather_stream_name(char* out_name, size_t cap,
                                    dom_domain_id domain_id,
                                    u32 event_type)
{
    if (!out_name || cap == 0u) {
        return;
    }
    out_name[0] = '\0';
    (void)domain_id;
    (void)event_type;
    {
        const char* name = dom_weather_event_name(event_type);
        sprintf(out_name, "noise.stream.weather.%llu.%s",
                (unsigned long long)domain_id,
                name ? name : "unknown");
        out_name[cap - 1u] = '\0';
    }
}

static void dom_weather_rng_state_for_event(d_rng_state* rng,
                                            const dom_weather_domain* domain,
                                            u32 event_type,
                                            u64 event_index)
{
    char stream[96];
    u64 base_seed;
    if (!rng || !domain) {
        return;
    }
    dom_weather_stream_name(stream, sizeof(stream), domain->climate_domain.surface.domain_id, event_type);
    D_DET_GUARD_RNG_STREAM_NAME(stream);
    base_seed = domain->climate_domain.surface.world_seed ^ domain->schedule.seed;
    d_rng_state_from_context(rng,
                             base_seed,
                             domain->climate_domain.surface.domain_id,
                             0u,
                             event_index,
                             stream,
                             D_RNG_MIX_DOMAIN | D_RNG_MIX_TICK | D_RNG_MIX_STREAM);
}

static d_bool dom_weather_profile_valid(const dom_weather_event_profile* profile)
{
    if (!profile) {
        return D_FALSE;
    }
    if (profile->period_ticks == 0u || profile->duration_ticks == 0u) {
        return D_FALSE;
    }
    return D_TRUE;
}

static dom_domain_point dom_weather_event_center(const dom_weather_domain* domain,
                                                 d_rng_state* rng)
{
    dom_domain_point center;
    memset(&center, 0, sizeof(center));
    if (!domain || !rng) {
        return center;
    }
    if (domain->climate_domain.surface.shape.kind == DOM_TERRAIN_SHAPE_SLAB) {
        q16_16 half_turn = d_q16_16_from_double(0.5);
        q16_16 span = d_q16_16_mul(domain->climate_domain.surface.shape.slab_half_extent,
                                   d_q16_16_from_int(2));
        q16_16 rx = dom_weather_ratio_from_u32(d_rng_next_u32(rng));
        q16_16 ry = dom_weather_ratio_from_u32(d_rng_next_u32(rng));
        center.x = d_q16_16_mul(d_q16_16_sub(rx, half_turn), span);
        center.y = d_q16_16_mul(d_q16_16_sub(ry, half_turn), span);
        center.z = 0;
        return center;
    }
    {
        q16_16 half_turn = d_q16_16_from_double(0.5);
        q16_16 quarter_turn = d_q16_16_from_double(0.25);
        q16_16 rlat = dom_weather_ratio_from_u32(d_rng_next_u32(rng));
        q16_16 rlon = dom_weather_ratio_from_u32(d_rng_next_u32(rng));
        q16_16 lat = d_q16_16_sub(d_q16_16_mul(rlat, half_turn), quarter_turn);
        q16_16 lon = d_q16_16_sub(rlon, half_turn);
        center = dom_terrain_latlon_to_local(&domain->climate_domain.surface.shape, lat, lon, 0);
        return center;
    }
}

static q16_16 dom_weather_event_radius(const dom_weather_domain* domain,
                                       const dom_weather_event_profile* profile,
                                       d_rng_state* rng)
{
    q16_16 ratio;
    q16_16 scale;
    if (!domain || !profile || !rng) {
        return d_q16_16_from_int(1);
    }
    ratio = dom_weather_rng_range_q16(rng, profile->radius_ratio_min, profile->radius_ratio_max);
    scale = dom_weather_shape_scale(&domain->climate_domain.surface.shape);
    if (scale <= 0) {
        scale = d_q16_16_from_int(1);
    }
    return d_q16_16_mul(ratio, scale);
}

static u32 dom_weather_event_wind_dir(d_rng_state* rng)
{
    u32 value;
    if (!rng) {
        return DOM_WEATHER_WIND_UNKNOWN;
    }
    value = d_rng_next_u32(rng);
    return (value % 8u) + 1u;
}

static u64 dom_weather_hash_u64(u64 h, u64 v)
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

static u64 dom_weather_event_id(dom_domain_id domain_id,
                                u32 event_type,
                                u64 start_tick)
{
    u64 h = 14695981039346656037ULL;
    h = dom_weather_hash_u64(h, (u64)domain_id);
    h = dom_weather_hash_u64(h, (u64)event_type);
    h = dom_weather_hash_u64(h, start_tick);
    return h;
}

static d_bool dom_weather_event_build(const dom_weather_domain* domain,
                                      u32 event_type,
                                      u64 event_index,
                                      dom_weather_event* out_event)
{
    const dom_weather_event_profile* profile;
    u64 period;
    u64 duration;
    u64 jitter_max;
    u64 jitter;
    d_rng_state rng;
    dom_domain_point center;
    q16_16 intensity;
    q16_16 radius;
    if (!domain || !out_event || event_type >= DOM_WEATHER_EVENT_TYPE_COUNT) {
        return D_FALSE;
    }
    profile = &domain->schedule.profiles[event_type];
    if (!dom_weather_profile_valid(profile)) {
        return D_FALSE;
    }
    period = profile->period_ticks;
    duration = profile->duration_ticks;
    if (duration > period) {
        duration = period;
    }
    if (period == 0u || duration == 0u) {
        return D_FALSE;
    }
    jitter_max = period - duration;
    dom_weather_rng_state_for_event(&rng, domain, event_type, event_index);
    jitter = (jitter_max > 0u) ? (dom_weather_rng_u64(&rng) % (jitter_max + 1u)) : 0u;
    intensity = dom_weather_rng_range_q16(&rng, profile->intensity_min, profile->intensity_max);
    center = dom_weather_event_center(domain, &rng);
    radius = dom_weather_event_radius(domain, profile, &rng);

    memset(out_event, 0, sizeof(*out_event));
    out_event->event_type = event_type;
    out_event->domain_id = domain->climate_domain.surface.domain_id;
    out_event->start_tick = (event_index * period) + jitter;
    out_event->duration_ticks = duration;
    out_event->intensity = intensity;
    out_event->center = center;
    out_event->radius = radius;
    out_event->wind_dir = DOM_WEATHER_WIND_UNKNOWN;
    if (event_type == DOM_WEATHER_EVENT_WIND_SHIFT) {
        out_event->wind_dir = dom_weather_event_wind_dir(&rng);
    }
    out_event->event_id = dom_weather_event_id(out_event->domain_id, event_type, out_event->start_tick);
    return D_TRUE;
}

static d_bool dom_weather_point_within_radius(const dom_domain_point* point,
                                              const dom_domain_point* center,
                                              q16_16 radius)
{
    i64 dx;
    i64 dy;
    i64 dz;
    i64 dist2;
    i64 r;
    i64 r2;
    if (!point || !center) {
        return D_FALSE;
    }
    r = (i64)radius;
    if (r <= 0) {
        return D_FALSE;
    }
    dx = (i64)point->x - (i64)center->x;
    dy = (i64)point->y - (i64)center->y;
    dz = (i64)point->z - (i64)center->z;
    dist2 = dx * dx + dy * dy + dz * dz;
    r2 = r * r;
    return dist2 <= r2 ? D_TRUE : D_FALSE;
}

static d_bool dom_weather_event_active_at(const dom_weather_domain* domain,
                                          u32 event_type,
                                          const dom_domain_point* point,
                                          u64 tick,
                                          dom_weather_event* out_event)
{
    const dom_weather_event_profile* profile;
    u64 period;
    u64 duration;
    u64 event_index;
    dom_weather_event event;
    if (!domain || !out_event || event_type >= DOM_WEATHER_EVENT_TYPE_COUNT) {
        return D_FALSE;
    }
    profile = &domain->schedule.profiles[event_type];
    if (!dom_weather_profile_valid(profile)) {
        return D_FALSE;
    }
    period = profile->period_ticks;
    duration = profile->duration_ticks;
    if (duration > period) {
        duration = period;
    }
    if (period == 0u || duration == 0u) {
        return D_FALSE;
    }
    event_index = tick / period;
    if (!dom_weather_event_build(domain, event_type, event_index, &event)) {
        return D_FALSE;
    }
    if (tick < event.start_tick || tick >= (event.start_tick + event.duration_ticks)) {
        return D_FALSE;
    }
    if (point && !dom_weather_point_within_radius(point, &event.center, event.radius)) {
        return D_FALSE;
    }
    *out_event = event;
    return D_TRUE;
}

static void dom_weather_sample_init(dom_weather_sample* sample)
{
    if (!sample) {
        return;
    }
    memset(sample, 0, sizeof(*sample));
    sample->temperature_current = DOM_WEATHER_UNKNOWN_Q16;
    sample->precipitation_current = DOM_WEATHER_UNKNOWN_Q16;
    sample->surface_wetness = DOM_WEATHER_UNKNOWN_Q16;
    sample->wind_current = DOM_WEATHER_WIND_UNKNOWN;
}

static void dom_weather_query_meta_refused(dom_domain_query_meta* meta,
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

static void dom_weather_query_meta_ok(dom_domain_query_meta* meta,
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

static d_bool dom_weather_domain_is_active(const dom_weather_domain* domain)
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

static void dom_weather_cache_init(dom_weather_cache* cache)
{
    if (!cache) {
        return;
    }
    memset(cache, 0, sizeof(*cache));
}

static void dom_weather_cache_free(dom_weather_cache* cache)
{
    if (!cache) {
        return;
    }
    if (cache->entries) {
        free(cache->entries);
        cache->entries = (dom_weather_cache_entry*)0;
    }
    cache->capacity = 0u;
    cache->count = 0u;
    cache->use_counter = 0u;
    cache->next_insert_order = 0u;
}

static int dom_weather_cache_reserve(dom_weather_cache* cache, u32 capacity)
{
    dom_weather_cache_entry* new_entries;
    u32 old_cap;
    if (!cache) {
        return -1;
    }
    if (capacity <= cache->capacity) {
        return 0;
    }
    new_entries = (dom_weather_cache_entry*)realloc(cache->entries,
                                                   capacity * sizeof(dom_weather_cache_entry));
    if (!new_entries) {
        return -1;
    }
    old_cap = cache->capacity;
    cache->entries = new_entries;
    cache->capacity = capacity;
    for (u32 i = old_cap; i < cache->capacity; ++i) {
        memset(&cache->entries[i], 0, sizeof(dom_weather_cache_entry));
        cache->entries[i].valid = D_FALSE;
    }
    return 0;
}

static dom_weather_cache_entry* dom_weather_cache_find_entry(dom_weather_cache* cache,
                                                             dom_domain_id domain_id,
                                                             u64 window_id,
                                                             u32 authoring_version)
{
    if (!cache || !cache->entries) {
        return (dom_weather_cache_entry*)0;
    }
    for (u32 i = 0u; i < cache->capacity; ++i) {
        dom_weather_cache_entry* entry = &cache->entries[i];
        if (!entry->valid) {
            continue;
        }
        if (entry->domain_id == domain_id &&
            entry->window_id == window_id &&
            entry->authoring_version == authoring_version) {
            return entry;
        }
    }
    return (dom_weather_cache_entry*)0;
}

static const dom_weather_event_list* dom_weather_cache_get(dom_weather_cache* cache,
                                                           dom_domain_id domain_id,
                                                           u64 window_id,
                                                           u32 authoring_version)
{
    dom_weather_cache_entry* entry;
    if (!cache) {
        return (const dom_weather_event_list*)0;
    }
    entry = dom_weather_cache_find_entry(cache, domain_id, window_id, authoring_version);
    if (!entry) {
        return (const dom_weather_event_list*)0;
    }
    cache->use_counter += 1u;
    entry->last_used = cache->use_counter;
    return &entry->events;
}

static dom_weather_cache_entry* dom_weather_cache_select_slot(dom_weather_cache* cache)
{
    dom_weather_cache_entry* best = (dom_weather_cache_entry*)0;
    if (!cache || !cache->entries || cache->capacity == 0u) {
        return (dom_weather_cache_entry*)0;
    }
    for (u32 i = 0u; i < cache->capacity; ++i) {
        dom_weather_cache_entry* entry = &cache->entries[i];
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

static dom_weather_event_list* dom_weather_cache_put(dom_weather_cache* cache,
                                                     dom_domain_id domain_id,
                                                     u64 window_id,
                                                     u32 authoring_version,
                                                     const dom_weather_event_list* events)
{
    dom_weather_cache_entry* entry;
    if (!cache || !events) {
        return (dom_weather_event_list*)0;
    }
    if (!cache->entries || cache->capacity == 0u) {
        return (dom_weather_event_list*)0;
    }
    entry = dom_weather_cache_find_entry(cache, domain_id, window_id, authoring_version);
    if (!entry) {
        entry = dom_weather_cache_select_slot(cache);
    }
    if (!entry) {
        return (dom_weather_event_list*)0;
    }
    if (!entry->valid) {
        cache->count += 1u;
        entry->insert_order = cache->next_insert_order++;
    }
    entry->domain_id = domain_id;
    entry->window_id = window_id;
    entry->authoring_version = authoring_version;
    entry->events = *events;
    entry->valid = D_TRUE;
    cache->use_counter += 1u;
    entry->last_used = cache->use_counter;
    return &entry->events;
}

static void dom_weather_cache_invalidate_domain(dom_weather_cache* cache, dom_domain_id domain_id)
{
    if (!cache || !cache->entries) {
        return;
    }
    for (u32 i = 0u; i < cache->capacity; ++i) {
        dom_weather_cache_entry* entry = &cache->entries[i];
        if (entry->valid && entry->domain_id == domain_id) {
            entry->valid = D_FALSE;
            if (cache->count > 0u) {
                cache->count -= 1u;
            }
        }
    }
}

static u64 dom_weather_window_id(u64 start_tick, u64 window_ticks)
{
    u64 h = 14695981039346656037ULL;
    h = dom_weather_hash_u64(h, start_tick);
    h = dom_weather_hash_u64(h, window_ticks);
    return h;
}

static d_bool dom_weather_window_overlaps(u64 start_tick,
                                          u64 window_ticks,
                                          u64 event_start,
                                          u64 event_duration)
{
    u64 window_end;
    u64 event_end;
    if (window_ticks == 0u || event_duration == 0u) {
        return D_FALSE;
    }
    window_end = start_tick + window_ticks;
    if (window_end < start_tick) {
        window_end = (u64)-1;
    }
    event_end = event_start + event_duration;
    if (event_end < event_start) {
        event_end = (u64)-1;
    }
    if (event_start >= window_end) {
        return D_FALSE;
    }
    if (event_end <= start_tick) {
        return D_FALSE;
    }
    return D_TRUE;
}

static void dom_weather_apply_event(const dom_weather_event* event,
                                    const dom_weather_event_profile* profile,
                                    const dom_climate_sample* climate,
                                    dom_weather_sample* out_sample)
{
    q16_16 temp_range;
    q16_16 precip_range;
    q16_16 temp_delta;
    q16_16 precip_delta;
    if (!event || !profile || !climate || !out_sample) {
        return;
    }
    temp_range = climate->temperature_range;
    precip_range = climate->precipitation_range;
    temp_delta = d_q16_16_mul(temp_range, d_q16_16_mul(event->intensity, profile->temp_scale));
    precip_delta = d_q16_16_mul(precip_range, d_q16_16_mul(event->intensity, profile->precip_scale));

    switch (event->event_type) {
        case DOM_WEATHER_EVENT_RAIN:
            out_sample->precipitation_current = d_q16_16_add(out_sample->precipitation_current, precip_delta);
            out_sample->surface_wetness = d_q16_16_add(out_sample->surface_wetness,
                                                       d_q16_16_mul(event->intensity, profile->wetness_scale));
            break;
        case DOM_WEATHER_EVENT_SNOW:
            out_sample->precipitation_current = d_q16_16_add(out_sample->precipitation_current, precip_delta);
            out_sample->temperature_current = d_q16_16_sub(out_sample->temperature_current, temp_delta);
            out_sample->surface_wetness = d_q16_16_add(out_sample->surface_wetness,
                                                       d_q16_16_mul(event->intensity, profile->wetness_scale));
            break;
        case DOM_WEATHER_EVENT_HEATWAVE:
            out_sample->temperature_current = d_q16_16_add(out_sample->temperature_current, temp_delta);
            break;
        case DOM_WEATHER_EVENT_COLD_SNAP:
            out_sample->temperature_current = d_q16_16_sub(out_sample->temperature_current, temp_delta);
            break;
        case DOM_WEATHER_EVENT_WIND_SHIFT:
            if (event->wind_dir != DOM_WEATHER_WIND_UNKNOWN) {
                out_sample->wind_current = event->wind_dir;
                out_sample->flags &= ~DOM_WEATHER_SAMPLE_WIND_UNKNOWN;
            }
            break;
        default:
            break;
    }
}

static q16_16 dom_weather_hist_bin_ratio(u32 count, u32 total)
{
    if (total == 0u) {
        return 0;
    }
    return (q16_16)(((u64)count << 16) / total);
}

static u32 dom_weather_hist_bin(q16_16 value)
{
    q16_16 clamped = dom_weather_clamp_q16_16(value, 0, d_q16_16_from_int(1));
    u32 scaled = (u32)(((i64)clamped * (DOM_WEATHER_HIST_BINS - 1u)) >> 16);
    if (scaled >= DOM_WEATHER_HIST_BINS) {
        scaled = DOM_WEATHER_HIST_BINS - 1u;
    }
    return scaled;
}

static d_bool dom_weather_domain_collapsed(const dom_weather_domain* domain, u64 tick)
{
    if (!domain) {
        return D_FALSE;
    }
    for (u32 i = 0u; i < domain->capsule_count; ++i) {
        const dom_weather_macro_capsule* capsule = &domain->capsules[i];
        if (tick >= capsule->start_tick &&
            tick < (capsule->start_tick + capsule->window_ticks)) {
            return D_TRUE;
        }
    }
    return D_FALSE;
}

void dom_weather_surface_desc_init(dom_weather_surface_desc* desc)
{
    if (!desc) {
        return;
    }
    memset(desc, 0, sizeof(*desc));
    dom_climate_surface_desc_init(&desc->climate_desc);
    desc->schedule.seed = 1u;

    for (u32 i = 0u; i < DOM_WEATHER_EVENT_TYPE_COUNT; ++i) {
        dom_weather_event_profile* profile = &desc->schedule.profiles[i];
        profile->period_ticks = 0u;
        profile->duration_ticks = 0u;
        profile->intensity_min = d_q16_16_from_double(0.2);
        profile->intensity_max = d_q16_16_from_double(0.8);
        profile->radius_ratio_min = d_q16_16_from_double(0.1);
        profile->radius_ratio_max = d_q16_16_from_double(0.4);
        profile->temp_scale = d_q16_16_from_double(0.4);
        profile->precip_scale = d_q16_16_from_double(0.6);
        profile->wetness_scale = d_q16_16_from_double(0.5);
    }

    desc->schedule.profiles[DOM_WEATHER_EVENT_RAIN].period_ticks = 240u;
    desc->schedule.profiles[DOM_WEATHER_EVENT_RAIN].duration_ticks = 80u;
    desc->schedule.profiles[DOM_WEATHER_EVENT_RAIN].temp_scale = d_q16_16_from_double(0.1);
    desc->schedule.profiles[DOM_WEATHER_EVENT_RAIN].precip_scale = d_q16_16_from_double(0.8);
    desc->schedule.profiles[DOM_WEATHER_EVENT_RAIN].wetness_scale = d_q16_16_from_double(0.7);

    desc->schedule.profiles[DOM_WEATHER_EVENT_SNOW].period_ticks = 300u;
    desc->schedule.profiles[DOM_WEATHER_EVENT_SNOW].duration_ticks = 90u;
    desc->schedule.profiles[DOM_WEATHER_EVENT_SNOW].temp_scale = d_q16_16_from_double(0.3);
    desc->schedule.profiles[DOM_WEATHER_EVENT_SNOW].precip_scale = d_q16_16_from_double(0.7);
    desc->schedule.profiles[DOM_WEATHER_EVENT_SNOW].wetness_scale = d_q16_16_from_double(0.6);

    desc->schedule.profiles[DOM_WEATHER_EVENT_HEATWAVE].period_ticks = 420u;
    desc->schedule.profiles[DOM_WEATHER_EVENT_HEATWAVE].duration_ticks = 120u;
    desc->schedule.profiles[DOM_WEATHER_EVENT_HEATWAVE].temp_scale = d_q16_16_from_double(0.6);
    desc->schedule.profiles[DOM_WEATHER_EVENT_HEATWAVE].precip_scale = 0;
    desc->schedule.profiles[DOM_WEATHER_EVENT_HEATWAVE].wetness_scale = 0;

    desc->schedule.profiles[DOM_WEATHER_EVENT_COLD_SNAP].period_ticks = 360u;
    desc->schedule.profiles[DOM_WEATHER_EVENT_COLD_SNAP].duration_ticks = 100u;
    desc->schedule.profiles[DOM_WEATHER_EVENT_COLD_SNAP].temp_scale = d_q16_16_from_double(0.6);
    desc->schedule.profiles[DOM_WEATHER_EVENT_COLD_SNAP].precip_scale = 0;
    desc->schedule.profiles[DOM_WEATHER_EVENT_COLD_SNAP].wetness_scale = 0;

    desc->schedule.profiles[DOM_WEATHER_EVENT_WIND_SHIFT].period_ticks = 200u;
    desc->schedule.profiles[DOM_WEATHER_EVENT_WIND_SHIFT].duration_ticks = 60u;
    desc->schedule.profiles[DOM_WEATHER_EVENT_WIND_SHIFT].temp_scale = 0;
    desc->schedule.profiles[DOM_WEATHER_EVENT_WIND_SHIFT].precip_scale = 0;
    desc->schedule.profiles[DOM_WEATHER_EVENT_WIND_SHIFT].wetness_scale = 0;
}

void dom_weather_domain_init(dom_weather_domain* domain,
                             const dom_weather_surface_desc* desc,
                             u32 cache_capacity)
{
    if (!domain || !desc) {
        return;
    }
    memset(domain, 0, sizeof(*domain));
    dom_climate_domain_init(&domain->climate_domain, &desc->climate_desc, cache_capacity);
    dom_domain_policy_init(&domain->policy);
    domain->existence_state = DOM_DOMAIN_EXISTENCE_REALIZED;
    domain->archival_state = DOM_DOMAIN_ARCHIVAL_LIVE;
    domain->authoring_version = 1u;
    domain->schedule = desc->schedule;
    dom_weather_cache_init(&domain->cache);
    if (cache_capacity > 0u) {
        dom_weather_cache_reserve(&domain->cache, cache_capacity);
    }
    domain->capsule_count = 0u;
}

void dom_weather_domain_free(dom_weather_domain* domain)
{
    if (!domain) {
        return;
    }
    dom_weather_cache_free(&domain->cache);
    dom_climate_domain_free(&domain->climate_domain);
    domain->capsule_count = 0u;
}

void dom_weather_domain_set_state(dom_weather_domain* domain,
                                  u32 existence_state,
                                  u32 archival_state)
{
    if (!domain) {
        return;
    }
    if (domain->existence_state != existence_state || domain->archival_state != archival_state) {
        domain->existence_state = existence_state;
        domain->archival_state = archival_state;
        dom_climate_domain_set_state(&domain->climate_domain, existence_state, archival_state);
        dom_weather_cache_invalidate_domain(&domain->cache, domain->climate_domain.surface.domain_id);
    }
}

void dom_weather_domain_set_policy(dom_weather_domain* domain,
                                   const dom_domain_policy* policy)
{
    if (!domain || !policy) {
        return;
    }
    domain->policy = *policy;
    dom_climate_domain_set_policy(&domain->climate_domain, policy);
    dom_weather_cache_invalidate_domain(&domain->cache, domain->climate_domain.surface.domain_id);
}

int dom_weather_sample_query(const dom_weather_domain* domain,
                             const dom_domain_point* point,
                             u64 tick,
                             dom_domain_budget* budget,
                             dom_weather_sample* out_sample)
{
    dom_climate_sample climate;
    u32 budget_before = 0u;
    u32 cost_units = 0u;
    if (!domain || !point || !out_sample) {
        return -1;
    }
    dom_weather_sample_init(out_sample);
    if (budget) {
        budget_before = budget->used_units;
    }
    if (!dom_weather_domain_is_active(domain)) {
        dom_weather_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_DOMAIN_INACTIVE, budget);
        out_sample->flags |= DOM_WEATHER_SAMPLE_FIELDS_UNKNOWN |
                             DOM_WEATHER_SAMPLE_WIND_UNKNOWN |
                             DOM_WEATHER_SAMPLE_EVENTS_UNKNOWN;
        return 0;
    }
    if (dom_weather_domain_collapsed(domain, tick)) {
        dom_weather_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                                  DOM_DOMAIN_CONFIDENCE_UNKNOWN, 0u, budget);
        out_sample->flags |= DOM_WEATHER_SAMPLE_FIELDS_UNKNOWN |
                             DOM_WEATHER_SAMPLE_WIND_UNKNOWN |
                             DOM_WEATHER_SAMPLE_EVENTS_UNKNOWN |
                             DOM_WEATHER_SAMPLE_COLLAPSED;
        return 0;
    }

    dom_climate_sample_query(&domain->climate_domain, point, budget, &climate);
    if (climate.meta.status == DOM_DOMAIN_QUERY_REFUSED ||
        (climate.flags & DOM_CLIMATE_SAMPLE_FIELDS_UNKNOWN)) {
        out_sample->flags |= DOM_WEATHER_SAMPLE_FIELDS_UNKNOWN |
                             DOM_WEATHER_SAMPLE_EVENTS_UNKNOWN;
        if (climate.flags & DOM_CLIMATE_SAMPLE_WIND_UNKNOWN) {
            out_sample->flags |= DOM_WEATHER_SAMPLE_WIND_UNKNOWN;
        }
        out_sample->meta = climate.meta;
        return 0;
    }

    if (!dom_domain_budget_consume(budget, domain->policy.cost_analytic)) {
        dom_weather_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_BUDGET, budget);
        out_sample->flags |= DOM_WEATHER_SAMPLE_FIELDS_UNKNOWN |
                             DOM_WEATHER_SAMPLE_WIND_UNKNOWN |
                             DOM_WEATHER_SAMPLE_EVENTS_UNKNOWN;
        return 0;
    }

    out_sample->temperature_current = climate.temperature_mean;
    out_sample->precipitation_current = climate.precipitation_mean;
    out_sample->surface_wetness = 0;
    out_sample->wind_current = (climate.flags & DOM_CLIMATE_SAMPLE_WIND_UNKNOWN) ?
                               DOM_WEATHER_WIND_UNKNOWN : climate.wind_prevailing;
    if (climate.flags & DOM_CLIMATE_SAMPLE_WIND_UNKNOWN) {
        out_sample->flags |= DOM_WEATHER_SAMPLE_WIND_UNKNOWN;
    }

    for (u32 i = 0u; i < DOM_WEATHER_EVENT_TYPE_COUNT; ++i) {
        dom_weather_event event;
        if (dom_weather_event_active_at(domain, i, point, tick, &event)) {
            out_sample->active_event_mask |= (1u << i);
            out_sample->active_event_count += 1u;
            dom_weather_apply_event(&event, &domain->schedule.profiles[i], &climate, out_sample);
        }
    }

    {
        q16_16 temp_min = d_q16_16_sub(climate.temperature_mean, climate.temperature_range);
        q16_16 temp_max = d_q16_16_add(climate.temperature_mean, climate.temperature_range);
        q16_16 precip_min = d_q16_16_sub(climate.precipitation_mean, climate.precipitation_range);
        q16_16 precip_max = d_q16_16_add(climate.precipitation_mean, climate.precipitation_range);
        q16_16 wetness = out_sample->surface_wetness;
        q16_16 base_wetness = 0;
        if (precip_min < 0) {
            precip_min = 0;
        }
        if (precip_max < 0) {
            precip_max = 0;
        }
        out_sample->temperature_current = dom_weather_clamp_q16_16(out_sample->temperature_current,
                                                                   temp_min, temp_max);
        out_sample->precipitation_current = dom_weather_clamp_q16_16(out_sample->precipitation_current,
                                                                     precip_min, precip_max);
        {
            q16_16 denom = d_q16_16_add(climate.precipitation_mean, climate.precipitation_range);
            if (denom > 0) {
                base_wetness = d_fixed_div_q16_16(out_sample->precipitation_current, denom);
            }
        }
        wetness = d_q16_16_add(base_wetness, wetness);
        out_sample->surface_wetness = dom_weather_clamp_q16_16(wetness, 0, d_q16_16_from_int(1));
    }

    if (budget) {
        cost_units = budget->used_units - budget_before;
    }
    dom_weather_query_meta_ok(&out_sample->meta,
                              climate.meta.resolution,
                              climate.meta.confidence,
                              cost_units,
                              budget);
    return 0;
}

int dom_weather_events_at(const dom_weather_domain* domain,
                          const dom_domain_point* point,
                          u64 tick,
                          dom_weather_event_list* out_list)
{
    if (!domain || !out_list) {
        return -1;
    }
    out_list->count = 0u;
    if (!dom_weather_domain_is_active(domain)) {
        return 0;
    }
    for (u32 i = 0u; i < DOM_WEATHER_EVENT_TYPE_COUNT; ++i) {
        dom_weather_event event;
        if (out_list->count >= DOM_WEATHER_MAX_EVENTS) {
            break;
        }
        if (dom_weather_event_active_at(domain, i, point, tick, &event)) {
            out_list->events[out_list->count++] = event;
        }
    }
    return 0;
}

int dom_weather_events_in_window(const dom_weather_domain* domain,
                                 u64 start_tick,
                                 u64 window_ticks,
                                 dom_weather_event_list* out_list)
{
    const dom_weather_event_list* cached;
    u64 window_id;
    if (!domain || !out_list) {
        return -1;
    }
    out_list->count = 0u;
    if (!dom_weather_domain_is_active(domain) || window_ticks == 0u) {
        return 0;
    }
    window_id = dom_weather_window_id(start_tick, window_ticks);
    cached = dom_weather_cache_get((dom_weather_cache*)&domain->cache,
                                   domain->climate_domain.surface.domain_id,
                                   window_id,
                                   domain->authoring_version);
    if (cached) {
        *out_list = *cached;
        return 0;
    }

    for (u32 event_type = 0u; event_type < DOM_WEATHER_EVENT_TYPE_COUNT; ++event_type) {
        const dom_weather_event_profile* profile = &domain->schedule.profiles[event_type];
        u64 period = profile->period_ticks;
        u64 duration = profile->duration_ticks;
        u64 start_index;
        u64 end_index;
        if (!dom_weather_profile_valid(profile) || period == 0u) {
            continue;
        }
        if (duration > period) {
            duration = period;
        }
        start_index = start_tick / period;
        {
            u64 window_end = start_tick + window_ticks;
            if (window_end < start_tick) {
                window_end = (u64)-1;
            }
            if (window_end == 0u) {
                end_index = 0u;
            } else {
                end_index = (window_end - 1u) / period;
            }
        }
        for (u64 idx = start_index; idx <= end_index; ++idx) {
            dom_weather_event event;
            if (out_list->count >= DOM_WEATHER_MAX_EVENTS) {
                break;
            }
            if (!dom_weather_event_build(domain, event_type, idx, &event)) {
                continue;
            }
            if (!dom_weather_window_overlaps(start_tick, window_ticks, event.start_tick, event.duration_ticks)) {
                continue;
            }
            out_list->events[out_list->count++] = event;
        }
    }

    dom_weather_cache_put((dom_weather_cache*)&domain->cache,
                          domain->climate_domain.surface.domain_id,
                          window_id,
                          domain->authoring_version,
                          out_list);
    return 0;
}

static int dom_weather_capsule_store(dom_weather_domain* domain,
                                     u64 start_tick,
                                     u64 window_ticks)
{
    dom_weather_event_list events;
    dom_weather_macro_capsule capsule;
    u32 bin_counts[DOM_WEATHER_EVENT_TYPE_COUNT][DOM_WEATHER_HIST_BINS];
    u32 type_counts[DOM_WEATHER_EVENT_TYPE_COUNT];
    i64 cumulative_precip = 0;
    i64 cumulative_temp = 0;
    if (!domain || window_ticks == 0u) {
        return -1;
    }
    if (domain->capsule_count >= DOM_WEATHER_MAX_CAPSULES) {
        return -2;
    }
    memset(&events, 0, sizeof(events));
    if (dom_weather_events_in_window(domain, start_tick, window_ticks, &events) != 0) {
        return -1;
    }
    memset(bin_counts, 0, sizeof(bin_counts));
    memset(type_counts, 0, sizeof(type_counts));

    for (u32 i = 0u; i < events.count; ++i) {
        dom_weather_event* event = &events.events[i];
        u32 t = event->event_type;
        if (t >= DOM_WEATHER_EVENT_TYPE_COUNT) {
            continue;
        }
        type_counts[t] += 1u;
        bin_counts[t][dom_weather_hist_bin(event->intensity)] += 1u;
        {
            const dom_weather_event_profile* profile = &domain->schedule.profiles[t];
            q16_16 temp_delta = d_q16_16_mul(event->intensity, profile->temp_scale);
            q16_16 precip_delta = d_q16_16_mul(event->intensity, profile->precip_scale);
            if (t == DOM_WEATHER_EVENT_SNOW) {
                cumulative_temp -= (i64)temp_delta * (i64)event->duration_ticks;
                cumulative_precip += (i64)precip_delta * (i64)event->duration_ticks;
            } else if (t == DOM_WEATHER_EVENT_RAIN) {
                cumulative_precip += (i64)precip_delta * (i64)event->duration_ticks;
            } else if (t == DOM_WEATHER_EVENT_HEATWAVE) {
                cumulative_temp += (i64)temp_delta * (i64)event->duration_ticks;
            } else if (t == DOM_WEATHER_EVENT_COLD_SNAP) {
                cumulative_temp -= (i64)temp_delta * (i64)event->duration_ticks;
            }
        }
    }

    memset(&capsule, 0, sizeof(capsule));
    capsule.capsule_id = dom_weather_window_id(start_tick, window_ticks);
    capsule.window_id = capsule.capsule_id;
    capsule.start_tick = start_tick;
    capsule.window_ticks = window_ticks;
    capsule.cumulative_precip_q16 = cumulative_precip;
    capsule.cumulative_temp_dev_q16 = cumulative_temp;
    for (u32 t = 0u; t < DOM_WEATHER_EVENT_TYPE_COUNT; ++t) {
        capsule.event_counts[t] = type_counts[t];
        for (u32 b = 0u; b < DOM_WEATHER_HIST_BINS; ++b) {
            capsule.intensity_hist[t][b] = dom_weather_hist_bin_ratio(bin_counts[t][b], type_counts[t]);
        }
        if (domain->schedule.profiles[t].period_ticks > 0u) {
            u64 end_tick = start_tick + window_ticks;
            u64 event_index = end_tick / domain->schedule.profiles[t].period_ticks;
            d_rng_state rng;
            dom_weather_rng_state_for_event(&rng, domain, t, event_index);
            capsule.rng_cursor[t] = rng.state;
        } else {
            capsule.rng_cursor[t] = 0u;
        }
    }

    domain->capsules[domain->capsule_count++] = capsule;
    return 0;
}

int dom_weather_domain_collapse_window(dom_weather_domain* domain,
                                       u64 start_tick,
                                       u64 window_ticks)
{
    if (!domain || window_ticks == 0u) {
        return -1;
    }
    return dom_weather_capsule_store(domain, start_tick, window_ticks);
}

int dom_weather_domain_expand_window(dom_weather_domain* domain,
                                     u64 window_id)
{
    if (!domain) {
        return -1;
    }
    for (u32 i = 0u; i < domain->capsule_count; ++i) {
        if (domain->capsules[i].window_id == window_id) {
            domain->capsules[i] = domain->capsules[domain->capsule_count - 1u];
            domain->capsule_count -= 1u;
            return 0;
        }
    }
    return -2;
}

u32 dom_weather_domain_capsule_count(const dom_weather_domain* domain)
{
    return domain ? domain->capsule_count : 0u;
}

const dom_weather_macro_capsule* dom_weather_domain_capsule_at(const dom_weather_domain* domain,
                                                               u32 index)
{
    if (!domain || index >= domain->capsule_count) {
        return (const dom_weather_macro_capsule*)0;
    }
    return &domain->capsules[index];
}
