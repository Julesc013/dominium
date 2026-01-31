/*
FILE: source/domino/world/travel_fields.cpp
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / world/travel_fields
RESPONSIBILITY: Implements deterministic travel sampling and bounded pathfinding.
ALLOWED DEPENDENCIES: `include/domino/**` and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: Engine private headers outside world.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: Fixed-point only; deterministic ordering and math.
*/
#include "domino/world/travel_fields.h"

#include "domino/core/fixed_math.h"

#include <stdlib.h>
#include <string.h>
#include <stdio.h>

#define DOM_TRAVEL_DIAG_Q16 ((q16_16)92682) /* ~1.4142 in Q16.16 */

typedef struct dom_travel_tile {
    u64 tile_id;
    u32 resolution;
    u32 sample_dim;
    dom_domain_aabb bounds;
    u32 authoring_version;
    u32 sample_count;
    q16_16* travel_cost;
    u32* flags;
} dom_travel_tile;

typedef struct dom_travel_node {
    i32 gx;
    i32 gy;
    q16_16 g_cost;
    q16_16 f_cost;
    i32 parent;
    u32 flags;
} dom_travel_node;

enum {
    DOM_TRAVEL_NODE_OPEN = 1u << 0u,
    DOM_TRAVEL_NODE_CLOSED = 1u << 1u
};

static q16_16 dom_travel_clamp_q16_16(q16_16 v, q16_16 lo, q16_16 hi)
{
    if (v < lo) {
        return lo;
    }
    if (v > hi) {
        return hi;
    }
    return v;
}

static i32 dom_travel_floor_div_q16(q16_16 value, q16_16 denom)
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

static void dom_travel_tile_init(dom_travel_tile* tile)
{
    if (!tile) {
        return;
    }
    memset(tile, 0, sizeof(*tile));
}

static void dom_travel_tile_free(dom_travel_tile* tile)
{
    if (!tile) {
        return;
    }
    if (tile->travel_cost) {
        free(tile->travel_cost);
        tile->travel_cost = (q16_16*)0;
    }
    if (tile->flags) {
        free(tile->flags);
        tile->flags = (u32*)0;
    }
    tile->sample_count = 0u;
    tile->sample_dim = 0u;
    tile->tile_id = 0u;
    tile->resolution = DOM_DOMAIN_RES_REFUSED;
    memset(&tile->bounds, 0, sizeof(tile->bounds));
    tile->authoring_version = 0u;
}

static void dom_travel_sample_init(dom_travel_sample* sample)
{
    if (!sample) {
        return;
    }
    memset(sample, 0, sizeof(*sample));
    sample->travel_cost = DOM_TRAVEL_UNKNOWN_Q16;
    sample->weather_modifier = DOM_TRAVEL_UNKNOWN_Q16;
    sample->mode_modifier = DOM_TRAVEL_UNKNOWN_Q16;
    sample->total_cost = DOM_TRAVEL_UNKNOWN_Q16;
    sample->obstacle = 0;
    sample->slope = DOM_TRAVEL_UNKNOWN_Q16;
    sample->roughness = DOM_TRAVEL_UNKNOWN_Q16;
    sample->material_primary = 0u;
    sample->structure_id = 0u;
    sample->mode_id = 0u;
    sample->flags = 0u;
}

static void dom_travel_path_init(dom_travel_path* path)
{
    if (!path) {
        return;
    }
    memset(path, 0, sizeof(*path));
}

static void dom_travel_query_meta_refused(dom_domain_query_meta* meta,
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

static void dom_travel_query_meta_ok(dom_domain_query_meta* meta,
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

static d_bool dom_travel_domain_is_active(const dom_travel_domain* domain)
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

static void dom_travel_mode_defaults(dom_travel_mode_desc* mode)
{
    if (!mode) {
        return;
    }
    memset(mode, 0, sizeof(*mode));
    mode->mode_id = 1u;
    mode->mode_kind = DOM_TRAVEL_MODE_WALK;
    mode->slope_max = d_q16_16_from_int(1);
    mode->cost_scale = d_q16_16_from_int(1);
    mode->cost_add = 0;
    mode->mass = 0;
    mode->inertia = d_q16_16_from_int(1);
    mode->damage_threshold = d_q16_16_from_int(1);
    mode->vehicle_structure_id = 0u;
    mode->maturity_tag = 1u;
}

static const dom_travel_mode_desc* dom_travel_mode_lookup(const dom_travel_surface_desc* surface,
                                                          u32 mode_id,
                                                          u32* out_index)
{
    if (out_index) {
        *out_index = 0u;
    }
    if (!surface || surface->mode_count == 0u) {
        return (const dom_travel_mode_desc*)0;
    }
    if (mode_id == 0u) {
        return &surface->modes[0];
    }
    for (u32 i = 0u; i < surface->mode_count && i < DOM_TRAVEL_MAX_MODES; ++i) {
        if (surface->modes[i].mode_id == mode_id) {
            if (out_index) {
                *out_index = i;
            }
            return &surface->modes[i];
        }
    }
    return &surface->modes[0];
}

static d_bool dom_travel_structure_has_id(const u32* list, u32 count, u32 id)
{
    if (!list || id == 0u) {
        return D_FALSE;
    }
    for (u32 i = 0u; i < count; ++i) {
        if (list[i] == id) {
            return D_TRUE;
        }
    }
    return D_FALSE;
}

static q16_16 dom_travel_weather_modifier(const dom_travel_surface_desc* surface,
                                          const dom_weather_sample* weather,
                                          u32* in_out_flags)
{
    q16_16 modifier = 0;
    if (!surface || !weather) {
        if (in_out_flags) {
            *in_out_flags |= DOM_TRAVEL_SAMPLE_FIELDS_UNKNOWN;
        }
        return DOM_TRAVEL_UNKNOWN_Q16;
    }
    if (weather->flags & DOM_WEATHER_SAMPLE_FIELDS_UNKNOWN) {
        if (in_out_flags) {
            *in_out_flags |= DOM_TRAVEL_SAMPLE_FIELDS_UNKNOWN;
        }
        return DOM_TRAVEL_UNKNOWN_Q16;
    }
    modifier = d_q16_16_add(modifier,
                            d_q16_16_mul(weather->precipitation_current,
                                         surface->weather_precip_scale));
    modifier = d_q16_16_add(modifier,
                            d_q16_16_mul(weather->surface_wetness,
                                         surface->weather_wetness_scale));
    if (weather->temperature_current != DOM_WEATHER_UNKNOWN_Q16) {
        if (weather->temperature_current < surface->comfort_temp_min) {
            q16_16 delta = d_q16_16_sub(surface->comfort_temp_min, weather->temperature_current);
            modifier = d_q16_16_add(modifier, d_q16_16_mul(delta, surface->weather_temp_scale));
        } else if (weather->temperature_current > surface->comfort_temp_max) {
            q16_16 delta = d_q16_16_sub(weather->temperature_current, surface->comfort_temp_max);
            modifier = d_q16_16_add(modifier, d_q16_16_mul(delta, surface->weather_temp_scale));
        }
    }
    if (weather->wind_current != DOM_WEATHER_WIND_UNKNOWN) {
        q16_16 wind_ratio = (q16_16)(((u32)weather->wind_current << 16) / 8u);
        modifier = d_q16_16_add(modifier, d_q16_16_mul(wind_ratio, surface->weather_wind_scale));
    }
    return modifier;
}

static q16_16 dom_travel_mode_modifier(const dom_travel_mode_desc* mode,
                                       q16_16 base_cost,
                                       u32* in_out_flags)
{
    q16_16 scaled;
    if (!mode || base_cost == DOM_TRAVEL_UNKNOWN_Q16) {
        if (in_out_flags) {
            *in_out_flags |= DOM_TRAVEL_SAMPLE_MODE_UNKNOWN;
        }
        return DOM_TRAVEL_UNKNOWN_Q16;
    }
    scaled = d_q16_16_mul(base_cost, mode->cost_scale);
    return d_q16_16_add(d_q16_16_sub(scaled, base_cost), mode->cost_add);
}

static q16_16 dom_travel_obstacle_value(const dom_travel_surface_desc* surface,
                                        const dom_terrain_sample* terrain,
                                        const dom_structure_sample* structure,
                                        const dom_travel_mode_desc* mode,
                                        u32* in_out_flags)
{
    d_bool has_bridge = D_FALSE;
    d_bool is_obstacle = D_FALSE;
    u32 structure_id = 0u;
    if (!surface || !terrain || !mode) {
        if (in_out_flags) {
            *in_out_flags |= DOM_TRAVEL_SAMPLE_FIELDS_UNKNOWN;
        }
        return d_q16_16_from_int(1);
    }
    if (terrain->flags & (DOM_TERRAIN_SAMPLE_FIELDS_UNKNOWN | DOM_TERRAIN_SAMPLE_PHI_UNKNOWN)) {
        if (in_out_flags) {
            *in_out_flags |= DOM_TRAVEL_SAMPLE_FIELDS_UNKNOWN;
        }
        return d_q16_16_from_int(1);
    }
    if (structure && (structure->flags & DOM_STRUCTURE_SAMPLE_INSTANCE_PRESENT)) {
        structure_id = structure->structure_id;
        if (dom_travel_structure_has_id(surface->bridge_structure_ids, surface->bridge_count, structure_id)) {
            has_bridge = D_TRUE;
        }
        if (dom_travel_structure_has_id(surface->obstacle_structure_ids, surface->obstacle_count, structure_id)) {
            is_obstacle = D_TRUE;
        }
    }
    if (is_obstacle) {
        return d_q16_16_from_int(1);
    }
    if (!has_bridge && terrain->phi > 0) {
        return d_q16_16_from_int(1);
    }
    if (mode->slope_max > 0 && terrain->slope != DOM_TERRAIN_UNKNOWN_Q16 &&
        terrain->slope > mode->slope_max) {
        return d_q16_16_from_int(1);
    }
    return 0;
}

static q16_16 dom_travel_apply_structure_cost(const dom_travel_surface_desc* surface,
                                              u32 structure_id,
                                              u32* in_out_flags,
                                              q16_16 base_cost)
{
    q16_16 scale = d_q16_16_from_int(1);
    if (!surface || base_cost == DOM_TRAVEL_UNKNOWN_Q16) {
        return base_cost;
    }
    if (structure_id != 0u) {
        if (dom_travel_structure_has_id(surface->road_structure_ids, surface->road_count, structure_id)) {
            scale = surface->road_cost_scale;
            if (in_out_flags) {
                *in_out_flags |= DOM_TRAVEL_SAMPLE_ON_ROAD;
            }
        }
        if (dom_travel_structure_has_id(surface->bridge_structure_ids, surface->bridge_count, structure_id)) {
            if (surface->bridge_cost_scale < scale) {
                scale = surface->bridge_cost_scale;
            }
            if (in_out_flags) {
                *in_out_flags |= DOM_TRAVEL_SAMPLE_ON_BRIDGE;
            }
        }
    }
    if (scale <= 0) {
        scale = d_q16_16_from_int(1);
    }
    return d_q16_16_mul(base_cost, scale);
}

static q16_16 dom_travel_step_from_extent(q16_16 extent, u32 sample_dim)
{
    if (sample_dim <= 1u) {
        return 0;
    }
    return (q16_16)((i64)extent / (i64)(sample_dim - 1u));
}


static int dom_travel_tile_build(dom_travel_tile* tile,
                                 const dom_domain_tile_desc* desc,
                                 const dom_travel_domain* domain,
                                 u64 tick)
{
    q16_16 step_x;
    q16_16 step_y;
    q16_16 step_z;
    q16_16 span_x;
    q16_16 span_y;
    q16_16 span_z;
    q16_16 half_step;
    u32 sample_dim;
    u32 sample_count;
    dom_domain_budget budget;
    if (!tile || !desc || !domain) {
        return -1;
    }
    dom_travel_tile_free(tile);
    sample_dim = desc->sample_dim;
    if (sample_dim == 0u) {
        return -1;
    }
    span_x = d_q16_16_sub(desc->bounds.max.x, desc->bounds.min.x);
    span_y = d_q16_16_sub(desc->bounds.max.y, desc->bounds.min.y);
    span_z = d_q16_16_sub(desc->bounds.max.z, desc->bounds.min.z);
    step_x = dom_travel_step_from_extent(span_x, sample_dim);
    step_y = dom_travel_step_from_extent(span_y, sample_dim);
    step_z = dom_travel_step_from_extent(span_z, sample_dim);
    half_step = d_fixed_div_q16_16(step_x, d_q16_16_from_int(2));

    sample_count = sample_dim * sample_dim * sample_dim;
    tile->travel_cost = (q16_16*)malloc(sizeof(q16_16) * sample_count);
    tile->flags = (u32*)malloc(sizeof(u32) * sample_count);
    if (!tile->travel_cost || !tile->flags) {
        dom_travel_tile_free(tile);
        return -1;
    }
    dom_domain_budget_init(&budget, 0xFFFFFFFFu);
    for (u32 z = 0u; z < sample_dim; ++z) {
        q16_16 zoff = (q16_16)((i64)step_z * (i64)z);
        for (u32 y = 0u; y < sample_dim; ++y) {
            q16_16 yoff = (q16_16)((i64)step_y * (i64)y);
            for (u32 x = 0u; x < sample_dim; ++x) {
                q16_16 xoff = (q16_16)((i64)step_x * (i64)x);
                dom_domain_point p;
                dom_travel_sample sample;
                u32 index = (z * sample_dim * sample_dim) + (y * sample_dim) + x;
                p.x = d_q16_16_add(desc->bounds.min.x, d_q16_16_add(xoff, half_step));
                p.y = d_q16_16_add(desc->bounds.min.y, d_q16_16_add(yoff, half_step));
                p.z = d_q16_16_add(desc->bounds.min.z, d_q16_16_add(zoff, half_step));
                (void)dom_travel_sample_query(domain, &p, tick, 0u, &budget, &sample);
                tile->travel_cost[index] = sample.travel_cost;
                tile->flags[index] = sample.flags;
            }
        }
    }
    tile->tile_id = desc->tile_id;
    tile->resolution = desc->resolution;
    tile->sample_dim = sample_dim;
    tile->bounds = desc->bounds;
    tile->authoring_version = desc->authoring_version;
    tile->sample_count = sample_count;
    return 0;
}

static u32 dom_travel_hist_bin(q16_16 value)
{
    q16_16 clamped = dom_travel_clamp_q16_16(value, 0, d_q16_16_from_int(1));
    u32 scaled = (u32)(((i64)clamped * (DOM_TRAVEL_HIST_BINS - 1u)) >> 16);
    if (scaled >= DOM_TRAVEL_HIST_BINS) {
        scaled = DOM_TRAVEL_HIST_BINS - 1u;
    }
    return scaled;
}

static q16_16 dom_travel_hist_bin_ratio(u32 count, u32 total)
{
    if (total == 0u) {
        return 0;
    }
    return (q16_16)(((u64)count << 16) / total);
}

static int dom_travel_capsule_store(dom_travel_domain* domain,
                                    const dom_domain_tile_desc* desc,
                                    u64 tick)
{
    dom_travel_tile tile;
    dom_travel_macro_capsule capsule;
    u32 hist_bins[DOM_TRAVEL_HIST_BINS];
    u32 road_cells = 0u;
    u32 sample_count;
    q16_16 cost_sum = 0;
    if (!domain || !desc) {
        return -1;
    }
    if (domain->capsule_count >= DOM_TRAVEL_MAX_CAPSULES) {
        return -2;
    }
    memset(hist_bins, 0, sizeof(hist_bins));
    dom_travel_tile_init(&tile);
    if (dom_travel_tile_build(&tile, desc, domain, tick) != 0) {
        dom_travel_tile_free(&tile);
        return -1;
    }
    sample_count = tile.sample_count;
    for (u32 i = 0u; i < sample_count; ++i) {
        q16_16 cost = tile.travel_cost[i];
        if (cost != DOM_TRAVEL_UNKNOWN_Q16) {
            cost_sum = d_q16_16_add(cost_sum, cost);
            hist_bins[dom_travel_hist_bin(cost)] += 1u;
        }
        if (tile.flags[i] & DOM_TRAVEL_SAMPLE_ON_ROAD) {
            road_cells += 1u;
        }
    }

    memset(&capsule, 0, sizeof(capsule));
    capsule.capsule_id = desc->tile_id;
    capsule.tile_id = desc->tile_id;
    capsule.tick = tick;
    capsule.bounds = desc->bounds;
    if (sample_count > 0u) {
        capsule.travel_cost_avg = (q16_16)(((i64)cost_sum) / (i64)sample_count);
        for (u32 b = 0u; b < DOM_TRAVEL_HIST_BINS; ++b) {
            capsule.travel_cost_hist[b] = dom_travel_hist_bin_ratio(hist_bins[b], sample_count);
        }
    }
    if (sample_count > 0u) {
        q16_16 ratio = (q16_16)(((u64)road_cells << 16) / sample_count);
        q16_16 tile_span = d_q16_16_sub(desc->bounds.max.x, desc->bounds.min.x);
        capsule.road_length = d_q16_16_mul(tile_span, ratio);
    }

    dom_travel_tile_free(&tile);
    domain->capsule_count += 1u;
    domain->capsules[domain->capsule_count - 1u] = capsule;
    return 0;
}

static d_bool dom_travel_points_equal(const dom_domain_point* a,
                                      const dom_domain_point* b)
{
    if (!a || !b) {
        return D_FALSE;
    }
    return a->x == b->x && a->y == b->y && a->z == b->z;
}

static void dom_travel_path_cache_init(dom_travel_path_cache* cache)
{
    if (!cache) {
        return;
    }
    memset(cache, 0, sizeof(*cache));
}

static void dom_travel_path_cache_free(dom_travel_path_cache* cache)
{
    if (!cache) {
        return;
    }
    if (cache->entries) {
        free(cache->entries);
        cache->entries = (dom_travel_path_cache_entry*)0;
    }
    cache->capacity = 0u;
    cache->count = 0u;
    cache->use_counter = 0u;
    cache->next_insert_order = 0u;
}

static int dom_travel_path_cache_reserve(dom_travel_path_cache* cache, u32 capacity)
{
    dom_travel_path_cache_entry* entries;
    u32 old_cap;
    if (!cache) {
        return -1;
    }
    if (capacity <= cache->capacity) {
        return 0;
    }
    entries = (dom_travel_path_cache_entry*)realloc(cache->entries,
                                                    capacity * sizeof(dom_travel_path_cache_entry));
    if (!entries) {
        return -1;
    }
    old_cap = cache->capacity;
    cache->entries = entries;
    cache->capacity = capacity;
    for (u32 i = old_cap; i < cache->capacity; ++i) {
        memset(&cache->entries[i], 0, sizeof(dom_travel_path_cache_entry));
        cache->entries[i].valid = D_FALSE;
    }
    return 0;
}

static dom_travel_path_cache_entry* dom_travel_path_cache_find(dom_travel_path_cache* cache,
                                                               const dom_domain_point* origin,
                                                               const dom_domain_point* target,
                                                               u32 mode_id,
                                                               u64 tick)
{
    if (!cache || !cache->entries) {
        return (dom_travel_path_cache_entry*)0;
    }
    for (u32 i = 0u; i < cache->capacity; ++i) {
        dom_travel_path_cache_entry* entry = &cache->entries[i];
        if (!entry->valid) {
            continue;
        }
        if (entry->mode_id == mode_id &&
            entry->tick == tick &&
            dom_travel_points_equal(&entry->origin, origin) &&
            dom_travel_points_equal(&entry->target, target)) {
            return entry;
        }
    }
    return (dom_travel_path_cache_entry*)0;
}

static dom_travel_path_cache_entry* dom_travel_path_cache_select_slot(dom_travel_path_cache* cache)
{
    dom_travel_path_cache_entry* best = (dom_travel_path_cache_entry*)0;
    if (!cache || !cache->entries || cache->capacity == 0u) {
        return (dom_travel_path_cache_entry*)0;
    }
    for (u32 i = 0u; i < cache->capacity; ++i) {
        dom_travel_path_cache_entry* entry = &cache->entries[i];
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

static const dom_travel_path* dom_travel_path_cache_get(dom_travel_path_cache* cache,
                                                        const dom_domain_point* origin,
                                                        const dom_domain_point* target,
                                                        u32 mode_id,
                                                        u64 tick)
{
    dom_travel_path_cache_entry* entry;
    if (!cache) {
        return (const dom_travel_path*)0;
    }
    entry = dom_travel_path_cache_find(cache, origin, target, mode_id, tick);
    if (!entry) {
        return (const dom_travel_path*)0;
    }
    cache->use_counter += 1u;
    entry->last_used = cache->use_counter;
    return &entry->path;
}

static void dom_travel_path_cache_put(dom_travel_path_cache* cache,
                                      const dom_domain_point* origin,
                                      const dom_domain_point* target,
                                      u32 mode_id,
                                      u64 tick,
                                      const dom_travel_path* path)
{
    dom_travel_path_cache_entry* entry;
    if (!cache || !path) {
        return;
    }
    if (!cache->entries || cache->capacity == 0u) {
        return;
    }
    entry = dom_travel_path_cache_find(cache, origin, target, mode_id, tick);
    if (!entry) {
        entry = dom_travel_path_cache_select_slot(cache);
    }
    if (!entry) {
        return;
    }
    if (!entry->valid) {
        cache->count += 1u;
        entry->insert_order = cache->next_insert_order++;
    }
    entry->origin = *origin;
    entry->target = *target;
    entry->mode_id = mode_id;
    entry->tick = tick;
    entry->path = *path;
    entry->valid = D_TRUE;
    cache->use_counter += 1u;
    entry->last_used = cache->use_counter;
}

static i32 dom_travel_node_find(const dom_travel_node* nodes, u32 count, i32 gx, i32 gy)
{
    if (!nodes) {
        return -1;
    }
    for (u32 i = 0u; i < count; ++i) {
        if (nodes[i].gx == gx && nodes[i].gy == gy) {
            return (i32)i;
        }
    }
    return -1;
}

static i32 dom_travel_node_best_open(const dom_travel_node* nodes, u32 count)
{
    i32 best = -1;
    if (!nodes) {
        return -1;
    }
    for (u32 i = 0u; i < count; ++i) {
        if ((nodes[i].flags & DOM_TRAVEL_NODE_OPEN) == 0u) {
            continue;
        }
        if (best < 0) {
            best = (i32)i;
            continue;
        }
        if (nodes[i].f_cost < nodes[best].f_cost) {
            best = (i32)i;
        } else if (nodes[i].f_cost == nodes[best].f_cost) {
            if (nodes[i].g_cost < nodes[best].g_cost) {
                best = (i32)i;
            } else if (nodes[i].g_cost == nodes[best].g_cost) {
                if (nodes[i].gx < nodes[best].gx ||
                    (nodes[i].gx == nodes[best].gx && nodes[i].gy < nodes[best].gy)) {
                    best = (i32)i;
                }
            }
        }
    }
    return best;
}

static q16_16 dom_travel_heuristic_cost(q16_16 step_cost, i32 dx, i32 dy)
{
    u32 adx = (dx < 0) ? (u32)(-dx) : (u32)dx;
    u32 ady = (dy < 0) ? (u32)(-dy) : (u32)dy;
    u32 steps = adx + ady;
    if (step_cost == 0) {
        step_cost = d_q16_16_from_int(1);
    }
    return d_q16_16_mul(step_cost, d_q16_16_from_int((i32)steps));
}

static void dom_travel_grid_point(const dom_domain_point* origin,
                                  q16_16 step,
                                  i32 gx,
                                  i32 gy,
                                  dom_domain_point* out_point)
{
    if (!origin || !out_point) {
        return;
    }
    out_point->x = d_q16_16_add(origin->x, (q16_16)((i64)gx * (i64)step));
    out_point->y = d_q16_16_add(origin->y, (q16_16)((i64)gy * (i64)step));
    out_point->z = origin->z;
}

static int dom_travel_pathfind_internal(dom_travel_domain* domain,
                                        const dom_domain_point* origin,
                                        const dom_domain_point* target,
                                        u64 tick,
                                        u32 mode_id,
                                        dom_domain_budget* budget,
                                        q16_16 step,
                                        q16_16 max_distance,
                                        u32 max_nodes,
                                        u32 max_points,
                                        dom_travel_path* out_path)
{
    static const i32 offsets[8][2] = {
        { 1, 0 },
        { -1, 0 },
        { 0, 1 },
        { 0, -1 },
        { 1, 1 },
        { -1, 1 },
        { 1, -1 },
        { -1, -1 }
    };
    dom_travel_node nodes[DOM_TRAVEL_MAX_NODES];
    u32 node_count = 0u;
    i32 target_gx;
    i32 target_gy;
    q16_16 step_cost_est = d_q16_16_from_int(1);
    u32 local_max_nodes;
    u32 local_max_points;
    if (!domain || !origin || !target || !out_path) {
        return -1;
    }
    dom_travel_path_init(out_path);
    if (step <= 0) {
        step = d_q16_16_from_int(1);
    }
    if (max_distance <= 0) {
        max_distance = d_q16_16_mul(step, d_q16_16_from_int(32));
    }
    local_max_nodes = max_nodes;
    if (local_max_nodes == 0u || local_max_nodes > DOM_TRAVEL_MAX_NODES) {
        local_max_nodes = DOM_TRAVEL_MAX_NODES;
    }
    local_max_points = max_points;
    if (local_max_points == 0u || local_max_points > DOM_TRAVEL_MAX_PATH_POINTS) {
        local_max_points = DOM_TRAVEL_MAX_PATH_POINTS;
    }
    target_gx = dom_travel_floor_div_q16(d_q16_16_sub(target->x, origin->x), step);
    target_gy = dom_travel_floor_div_q16(d_q16_16_sub(target->y, origin->y), step);

    {
        dom_travel_sample base_sample;
        if (dom_travel_sample_query(domain, origin, tick, mode_id, budget, &base_sample) == 0 &&
            base_sample.total_cost != DOM_TRAVEL_UNKNOWN_Q16) {
            step_cost_est = base_sample.total_cost;
        }
    }

    memset(nodes, 0, sizeof(nodes));
    nodes[0].gx = 0;
    nodes[0].gy = 0;
    nodes[0].g_cost = 0;
    nodes[0].f_cost = dom_travel_heuristic_cost(step_cost_est, target_gx, target_gy);
    nodes[0].parent = -1;
    nodes[0].flags = DOM_TRAVEL_NODE_OPEN;
    node_count = 1u;

    for (u32 iter = 0u; iter < local_max_nodes; ++iter) {
        i32 best_index = dom_travel_node_best_open(nodes, node_count);
        if (best_index < 0) {
            break;
        }
        dom_travel_node* best = &nodes[best_index];
        if (best->gx == target_gx && best->gy == target_gy) {
            u32 path_count = 0u;
            i32 cursor = best_index;
            dom_domain_point points[DOM_TRAVEL_MAX_PATH_POINTS];
            while (cursor >= 0 && path_count < local_max_points) {
                dom_travel_grid_point(origin, step, nodes[cursor].gx, nodes[cursor].gy, &points[path_count]);
                path_count += 1u;
                cursor = nodes[cursor].parent;
            }
            if (cursor >= 0) {
                out_path->flags |= DOM_TRAVEL_PATH_BLOCKED;
                return -2;
            }
            for (u32 i = 0u; i < path_count; ++i) {
                out_path->points[i] = points[path_count - 1u - i];
            }
            out_path->point_count = path_count;
            out_path->total_cost = best->g_cost;
            out_path->visited_nodes = node_count;
            out_path->flags |= DOM_TRAVEL_PATH_FOUND;
            dom_travel_query_meta_ok(&out_path->meta, DOM_DOMAIN_RES_ANALYTIC,
                                     DOM_DOMAIN_CONFIDENCE_EXACT, 0u, budget);
            return 0;
        }

        best->flags &= ~DOM_TRAVEL_NODE_OPEN;
        best->flags |= DOM_TRAVEL_NODE_CLOSED;

        for (u32 n = 0u; n < 8u; ++n) {
            i32 ngx = best->gx + offsets[n][0];
            i32 ngy = best->gy + offsets[n][1];
            dom_domain_point np;
            dom_travel_sample sample;
            q16_16 step_cost;
            q16_16 diag_scale = d_q16_16_from_int(1);
            i32 index;
            {
                q16_16 dx = d_q16_16_mul(d_q16_16_from_int((ngx < 0) ? -ngx : ngx), step);
                q16_16 dy = d_q16_16_mul(d_q16_16_from_int((ngy < 0) ? -ngy : ngy), step);
                if (dx > max_distance || dy > max_distance) {
                    continue;
                }
            }
            dom_travel_grid_point(origin, step, ngx, ngy, &np);
            if (dom_travel_sample_query(domain, &np, tick, mode_id, budget, &sample) != 0) {
                continue;
            }
            if ((sample.flags & DOM_TRAVEL_SAMPLE_FIELDS_UNKNOWN) ||
                (sample.flags & DOM_TRAVEL_SAMPLE_OBSTACLE)) {
                continue;
            }
            if (sample.total_cost == DOM_TRAVEL_UNKNOWN_Q16) {
                continue;
            }
            step_cost = sample.total_cost;
            if (offsets[n][0] != 0 && offsets[n][1] != 0) {
                diag_scale = DOM_TRAVEL_DIAG_Q16;
            }
            step_cost = d_q16_16_mul(step_cost, step);
            step_cost = d_q16_16_mul(step_cost, diag_scale);
            index = dom_travel_node_find(nodes, node_count, ngx, ngy);
            if (index < 0) {
                if (node_count >= local_max_nodes) {
                    continue;
                }
                nodes[node_count].gx = ngx;
                nodes[node_count].gy = ngy;
                nodes[node_count].g_cost = d_q16_16_add(best->g_cost, step_cost);
                nodes[node_count].f_cost = d_q16_16_add(nodes[node_count].g_cost,
                                                        dom_travel_heuristic_cost(step_cost_est,
                                                                                   target_gx - ngx,
                                                                                   target_gy - ngy));
                nodes[node_count].parent = best_index;
                nodes[node_count].flags = DOM_TRAVEL_NODE_OPEN;
                node_count += 1u;
            } else if ((nodes[index].flags & DOM_TRAVEL_NODE_OPEN) &&
                       d_q16_16_add(best->g_cost, step_cost) < nodes[index].g_cost) {
                nodes[index].g_cost = d_q16_16_add(best->g_cost, step_cost);
                nodes[index].f_cost = d_q16_16_add(nodes[index].g_cost,
                                                   dom_travel_heuristic_cost(step_cost_est,
                                                                              target_gx - ngx,
                                                                              target_gy - ngy));
                nodes[index].parent = best_index;
            }
        }
    }

    out_path->visited_nodes = node_count;
    out_path->flags |= DOM_TRAVEL_PATH_BLOCKED;
    return -3;
}

void dom_travel_surface_desc_init(dom_travel_surface_desc* desc)
{
    if (!desc) {
        return;
    }
    memset(desc, 0, sizeof(*desc));
    dom_terrain_surface_desc_init(&desc->terrain_desc);
    dom_weather_surface_desc_init(&desc->weather_desc);
    dom_structure_surface_desc_init(&desc->structure_desc);
    desc->domain_id = 0u;
    desc->world_seed = 0u;
    desc->meters_per_unit = d_q16_16_from_int(1);
    desc->shape.kind = DOM_TERRAIN_SHAPE_SPHERE;
    desc->shape.radius_equatorial = d_q16_16_from_int(256);
    desc->shape.radius_polar = d_q16_16_from_int(256);
    desc->shape.slab_half_extent = d_q16_16_from_int(256);
    desc->shape.slab_half_thickness = d_q16_16_from_int(16);
    desc->terrain_desc.shape = desc->shape;
    desc->terrain_desc.meters_per_unit = desc->meters_per_unit;
    desc->weather_desc.climate_desc.shape = desc->shape;
    desc->weather_desc.climate_desc.meters_per_unit = desc->meters_per_unit;
    desc->structure_desc.shape = desc->shape;
    desc->structure_desc.meters_per_unit = desc->meters_per_unit;
    desc->structure_desc.terrain_desc = desc->terrain_desc;
    desc->structure_desc.geology_desc.shape = desc->shape;
    desc->structure_desc.geology_desc.meters_per_unit = desc->meters_per_unit;

    desc->mode_count = 1u;
    dom_travel_mode_defaults(&desc->modes[0]);
    desc->road_cost_scale = d_q16_16_from_double(0.7);
    desc->bridge_cost_scale = d_q16_16_from_double(0.85);
    desc->weather_precip_scale = d_q16_16_from_double(0.2);
    desc->weather_wetness_scale = d_q16_16_from_double(0.2);
    desc->weather_temp_scale = d_q16_16_from_double(0.1);
    desc->comfort_temp_min = d_q16_16_from_double(0.2);
    desc->comfort_temp_max = d_q16_16_from_double(0.8);
    desc->weather_wind_scale = d_q16_16_from_double(0.1);
    desc->path_step = d_q16_16_from_int(1);
    desc->path_coarse_step = d_q16_16_from_int(4);
    desc->path_max_distance = d_q16_16_from_int(64);
    desc->path_max_nodes = 256u;
    desc->path_max_points = 64u;
    desc->terrain_cache_capacity = 128u;
    desc->weather_cache_capacity = 128u;
    desc->structure_cache_capacity = 128u;
    desc->cache_capacity = 8u;
}

void dom_travel_domain_init(dom_travel_domain* domain,
                            const dom_travel_surface_desc* desc)
{
    dom_travel_surface_desc normalized;
    dom_terrain_surface_desc terrain_desc;
    dom_weather_surface_desc weather_desc;
    dom_structure_surface_desc structure_desc;
    u32 terrain_cache = 0u;
    u32 weather_cache = 0u;
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

    dom_weather_surface_desc_init(&weather_desc);
    weather_desc = desc->weather_desc;
    weather_desc.climate_desc.domain_id = desc->domain_id;
    weather_desc.climate_desc.world_seed = desc->world_seed;
    weather_desc.climate_desc.meters_per_unit = desc->meters_per_unit;
    weather_desc.climate_desc.shape = desc->shape;

    structure_desc = desc->structure_desc;
    structure_desc.domain_id = desc->domain_id;
    structure_desc.world_seed = desc->world_seed;
    structure_desc.meters_per_unit = desc->meters_per_unit;
    structure_desc.shape = desc->shape;
    structure_desc.terrain_desc = terrain_desc;
    structure_desc.geology_desc.domain_id = desc->domain_id;
    structure_desc.geology_desc.world_seed = desc->world_seed;
    structure_desc.geology_desc.meters_per_unit = desc->meters_per_unit;
    structure_desc.geology_desc.shape = desc->shape;
    if (desc->structure_cache_capacity > 0u) {
        structure_desc.cache_capacity = desc->structure_cache_capacity;
    }

    memset(domain, 0, sizeof(*domain));
    domain->surface = normalized;
    terrain_cache = desc->terrain_cache_capacity ? desc->terrain_cache_capacity : desc->cache_capacity;
    weather_cache = desc->weather_cache_capacity ? desc->weather_cache_capacity : desc->cache_capacity;
    dom_terrain_domain_init(&domain->terrain_domain, &terrain_desc, terrain_cache);
    dom_weather_domain_init(&domain->weather_domain, &weather_desc, weather_cache);
    dom_structure_domain_init(&domain->structure_domain, &structure_desc);
    dom_domain_policy_init(&domain->policy);
    domain->existence_state = DOM_DOMAIN_EXISTENCE_REALIZED;
    domain->archival_state = DOM_DOMAIN_ARCHIVAL_LIVE;
    domain->authoring_version = 1u;
    dom_travel_path_cache_init(&domain->path_cache);
    if (desc->cache_capacity > 0u) {
        dom_travel_path_cache_reserve(&domain->path_cache, desc->cache_capacity);
    }
    domain->capsule_count = 0u;
}

void dom_travel_domain_free(dom_travel_domain* domain)
{
    if (!domain) {
        return;
    }
    dom_terrain_domain_free(&domain->terrain_domain);
    dom_weather_domain_free(&domain->weather_domain);
    dom_structure_domain_free(&domain->structure_domain);
    dom_travel_path_cache_free(&domain->path_cache);
}

void dom_travel_domain_set_state(dom_travel_domain* domain,
                                 u32 existence_state,
                                 u32 archival_state)
{
    if (!domain) {
        return;
    }
    domain->existence_state = existence_state;
    domain->archival_state = archival_state;
    dom_terrain_domain_set_state(&domain->terrain_domain, existence_state, archival_state);
    dom_weather_domain_set_state(&domain->weather_domain, existence_state, archival_state);
    dom_structure_domain_set_state(&domain->structure_domain, existence_state, archival_state);
}

void dom_travel_domain_set_policy(dom_travel_domain* domain,
                                  const dom_domain_policy* policy)
{
    if (!domain || !policy) {
        return;
    }
    domain->policy = *policy;
    dom_terrain_domain_set_policy(&domain->terrain_domain, policy);
    dom_weather_domain_set_policy(&domain->weather_domain, policy);
    dom_structure_domain_set_policy(&domain->structure_domain, policy);
}

int dom_travel_sample_query(const dom_travel_domain* domain,
                            const dom_domain_point* point,
                            u64 tick,
                            u32 mode_id,
                            dom_domain_budget* budget,
                            dom_travel_sample* out_sample)
{
    dom_terrain_sample terrain;
    dom_weather_sample weather;
    dom_structure_sample structure;
    const dom_travel_mode_desc* mode;
    u32 mode_index = 0u;
    u32 flags = 0u;
    q16_16 base_cost = DOM_TRAVEL_UNKNOWN_Q16;
    q16_16 weather_mod = DOM_TRAVEL_UNKNOWN_Q16;
    q16_16 mode_mod = DOM_TRAVEL_UNKNOWN_Q16;
    q16_16 total_cost = DOM_TRAVEL_UNKNOWN_Q16;
    u32 budget_before = 0u;
    d_bool collapsed = D_FALSE;
    const dom_travel_macro_capsule* capsule = 0;
    if (!domain || !point || !out_sample) {
        return -1;
    }
    dom_travel_sample_init(out_sample);

    if (!dom_travel_domain_is_active(domain)) {
        out_sample->flags |= DOM_TRAVEL_SAMPLE_FIELDS_UNKNOWN;
        dom_travel_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_DOMAIN_INACTIVE, budget);
        return 0;
    }

    if (domain->capsule_count > 0u) {
        for (u32 i = 0u; i < domain->capsule_count; ++i) {
            if (dom_domain_aabb_contains(&domain->capsules[i].bounds, point)) {
                collapsed = D_TRUE;
                capsule = &domain->capsules[i];
                break;
            }
        }
    }
    if (collapsed) {
        out_sample->flags |= DOM_TRAVEL_SAMPLE_FIELDS_UNKNOWN | DOM_TRAVEL_SAMPLE_COLLAPSED;
        if (capsule) {
            out_sample->travel_cost = capsule->travel_cost_avg;
        }
        dom_travel_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                                 DOM_DOMAIN_CONFIDENCE_UNKNOWN, 0u, budget);
        return 0;
    }

    if (budget) {
        budget_before = budget->used_units;
    }
    if (!dom_domain_budget_consume(budget, domain->policy.cost_analytic)) {
        out_sample->flags |= DOM_TRAVEL_SAMPLE_FIELDS_UNKNOWN;
        dom_travel_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_BUDGET, budget);
        return 0;
    }

    if (dom_terrain_sample_query(&domain->terrain_domain, point, budget, &terrain) != 0) {
        flags |= DOM_TRAVEL_SAMPLE_FIELDS_UNKNOWN;
    }
    if (dom_weather_sample_query(&domain->weather_domain, point, tick, budget, &weather) != 0) {
        flags |= DOM_TRAVEL_SAMPLE_FIELDS_UNKNOWN;
    }
    if (dom_structure_sample_query(&domain->structure_domain, point, tick, budget, &structure) != 0) {
        flags |= DOM_TRAVEL_SAMPLE_FIELDS_UNKNOWN;
    }

    mode = dom_travel_mode_lookup(&domain->surface, mode_id, &mode_index);
    if (!mode) {
        flags |= DOM_TRAVEL_SAMPLE_MODE_UNKNOWN;
    }

    out_sample->mode_id = mode ? mode->mode_id : 0u;
    out_sample->structure_id = (structure.flags & DOM_STRUCTURE_SAMPLE_INSTANCE_PRESENT)
                               ? structure.structure_id : 0u;
    out_sample->slope = terrain.slope;
    out_sample->roughness = terrain.roughness;
    out_sample->material_primary = terrain.material_primary;

    if (terrain.flags & DOM_TERRAIN_SAMPLE_FIELDS_UNKNOWN) {
        flags |= DOM_TRAVEL_SAMPLE_FIELDS_UNKNOWN;
    }
    if (weather.flags & DOM_WEATHER_SAMPLE_FIELDS_UNKNOWN) {
        flags |= DOM_TRAVEL_SAMPLE_FIELDS_UNKNOWN;
    }
    if (structure.flags & DOM_STRUCTURE_SAMPLE_FIELDS_UNKNOWN) {
        flags |= DOM_TRAVEL_SAMPLE_FIELDS_UNKNOWN;
    }

    base_cost = terrain.travel_cost;
    base_cost = dom_travel_apply_structure_cost(&domain->surface,
                                                out_sample->structure_id,
                                                &flags,
                                                base_cost);
    weather_mod = dom_travel_weather_modifier(&domain->surface, &weather, &flags);
    mode_mod = dom_travel_mode_modifier(mode, base_cost, &flags);

    out_sample->travel_cost = base_cost;
    out_sample->weather_modifier = weather_mod;
    out_sample->mode_modifier = mode_mod;
    if (base_cost != DOM_TRAVEL_UNKNOWN_Q16 &&
        weather_mod != DOM_TRAVEL_UNKNOWN_Q16 &&
        mode_mod != DOM_TRAVEL_UNKNOWN_Q16) {
        total_cost = d_q16_16_add(base_cost, d_q16_16_add(weather_mod, mode_mod));
    }
    out_sample->total_cost = total_cost;

    out_sample->obstacle = dom_travel_obstacle_value(&domain->surface, &terrain, &structure,
                                                     mode ? mode : &domain->surface.modes[0],
                                                     &flags);
    if (out_sample->obstacle > 0) {
        flags |= DOM_TRAVEL_SAMPLE_OBSTACLE;
    }

    out_sample->flags |= flags;
    if (budget) {
        u32 cost_units = budget->used_units - budget_before;
        dom_travel_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                                 (flags & DOM_TRAVEL_SAMPLE_FIELDS_UNKNOWN)
                                 ? DOM_DOMAIN_CONFIDENCE_UNKNOWN
                                 : DOM_DOMAIN_CONFIDENCE_EXACT,
                                 cost_units, budget);
    } else {
        dom_travel_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                                 (flags & DOM_TRAVEL_SAMPLE_FIELDS_UNKNOWN)
                                 ? DOM_DOMAIN_CONFIDENCE_UNKNOWN
                                 : DOM_DOMAIN_CONFIDENCE_EXACT,
                                 0u, budget);
    }
    return 0;
}

int dom_travel_pathfind(dom_travel_domain* domain,
                        const dom_domain_point* origin,
                        const dom_domain_point* target,
                        u64 tick,
                        u32 mode_id,
                        dom_domain_budget* budget,
                        dom_travel_path* out_path)
{
    const dom_travel_path* cached;
    dom_travel_path coarse_path;
    dom_travel_path fine_path;
    q16_16 step;
    q16_16 coarse_step;
    q16_16 max_distance;
    u32 max_nodes;
    u32 max_points;
    if (!domain || !origin || !target || !out_path) {
        return -1;
    }
    dom_travel_path_init(out_path);
    if (!dom_travel_domain_is_active(domain)) {
        dom_travel_query_meta_refused(&out_path->meta, DOM_DOMAIN_REFUSE_DOMAIN_INACTIVE, budget);
        return -2;
    }

    cached = dom_travel_path_cache_get(&domain->path_cache, origin, target, mode_id, tick);
    if (cached) {
        *out_path = *cached;
        return 0;
    }

    step = domain->surface.path_step;
    coarse_step = domain->surface.path_coarse_step;
    max_distance = domain->surface.path_max_distance;
    max_nodes = domain->surface.path_max_nodes;
    max_points = domain->surface.path_max_points;

    if (coarse_step > step) {
        if (dom_travel_pathfind_internal(domain, origin, target, tick, mode_id, budget,
                                         coarse_step, max_distance, max_nodes, max_points,
                                         &coarse_path) == 0 &&
            (coarse_path.flags & DOM_TRAVEL_PATH_FOUND)) {
            dom_domain_point current = *origin;
            dom_travel_path_init(out_path);
            for (u32 i = 1u; i < coarse_path.point_count; ++i) {
                dom_domain_point next = coarse_path.points[i];
                if (dom_travel_pathfind_internal(domain, &current, &next, tick, mode_id, budget,
                                                 step, max_distance, max_nodes, max_points,
                                                 &fine_path) != 0 ||
                    (fine_path.flags & DOM_TRAVEL_PATH_FOUND) == 0u) {
                    break;
                }
                if (out_path->point_count == 0u) {
                    for (u32 p = 0u; p < fine_path.point_count; ++p) {
                        if (out_path->point_count < max_points) {
                            out_path->points[out_path->point_count++] = fine_path.points[p];
                        }
                    }
                } else {
                    for (u32 p = 1u; p < fine_path.point_count; ++p) {
                        if (out_path->point_count < max_points) {
                            out_path->points[out_path->point_count++] = fine_path.points[p];
                        }
                    }
                }
                out_path->total_cost = d_q16_16_add(out_path->total_cost, fine_path.total_cost);
                out_path->visited_nodes += fine_path.visited_nodes;
                current = next;
            }
            if (out_path->point_count > 0u) {
                out_path->flags |= DOM_TRAVEL_PATH_FOUND;
                dom_travel_query_meta_ok(&out_path->meta, DOM_DOMAIN_RES_ANALYTIC,
                                         DOM_DOMAIN_CONFIDENCE_EXACT, 0u, budget);
                dom_travel_path_cache_put(&domain->path_cache, origin, target, mode_id, tick, out_path);
                return 0;
            }
        }
    }

    if (dom_travel_pathfind_internal(domain, origin, target, tick, mode_id, budget,
                                     step, max_distance, max_nodes, max_points,
                                     out_path) == 0 &&
        (out_path->flags & DOM_TRAVEL_PATH_FOUND)) {
        dom_travel_path_cache_put(&domain->path_cache, origin, target, mode_id, tick, out_path);
        return 0;
    }

    out_path->flags |= DOM_TRAVEL_PATH_BLOCKED;
    dom_travel_query_meta_refused(&out_path->meta, DOM_DOMAIN_REFUSE_POLICY, budget);
    return -3;
}

int dom_travel_domain_collapse_tile(dom_travel_domain* domain,
                                    const dom_domain_tile_desc* desc,
                                    u64 tick)
{
    if (!domain || !desc) {
        return -1;
    }
    return dom_travel_capsule_store(domain, desc, tick);
}

int dom_travel_domain_expand_tile(dom_travel_domain* domain, u64 tile_id)
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

u32 dom_travel_domain_capsule_count(const dom_travel_domain* domain)
{
    return domain ? domain->capsule_count : 0u;
}

const dom_travel_macro_capsule* dom_travel_domain_capsule_at(const dom_travel_domain* domain,
                                                             u32 index)
{
    if (!domain || index >= domain->capsule_count) {
        return (const dom_travel_macro_capsule*)0;
    }
    return &domain->capsules[index];
}
