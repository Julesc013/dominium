/*
FILE: source/domino/world/structure_fields.cpp
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / world/structure_fields
RESPONSIBILITY: Implements deterministic structure placement, stress sampling, and collapse hooks.
ALLOWED DEPENDENCIES: `include/domino/**` and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: Engine private headers outside world.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: Fixed-point only; deterministic ordering and math.
*/
#include "domino/world/structure_fields.h"

#include "domino/core/fixed_math.h"
#include "domino/core/rng_model.h"

#include <stdlib.h>
#include <string.h>
#include <stdio.h>

static q16_16 dom_struct_abs_q16_16(q16_16 v)
{
    return (v < 0) ? (q16_16)-v : v;
}

static q16_16 dom_struct_clamp_q16_16(q16_16 v, q16_16 lo, q16_16 hi)
{
    if (v < lo) {
        return lo;
    }
    if (v > hi) {
        return hi;
    }
    return v;
}

static i32 dom_struct_floor_div_q16(q16_16 value, q16_16 denom)
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

static u64 dom_struct_hash_u64(u64 h, u64 v)
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

static u64 dom_struct_cell_key(i32 cx, i32 cy, i32 cz)
{
    u64 h = 14695981039346656037ULL;
    h = dom_struct_hash_u64(h, (u64)(u32)cx);
    h = dom_struct_hash_u64(h, (u64)(u32)cy);
    h = dom_struct_hash_u64(h, (u64)(u32)cz);
    return h;
}

static q16_16 dom_struct_ratio_from_u32(u32 value)
{
    return (q16_16)(value >> 16);
}

static void dom_struct_stream_name(char* out_name, size_t cap,
                                   dom_domain_id domain_id,
                                   const char* purpose)
{
    if (!out_name || cap == 0u) {
        return;
    }
    if (!purpose || !purpose[0]) {
        purpose = "unknown";
    }
    sprintf(out_name, "noise.stream.%llu.structure.%s",
            (unsigned long long)domain_id,
            purpose);
    out_name[cap - 1u] = '\0';
}

static void dom_struct_rng_state_for_cell(d_rng_state* rng,
                                          const dom_structure_surface_desc* surface,
                                          const char* purpose,
                                          u64 cell_key,
                                          u32 structure_id,
                                          u64 event_index)
{
    char stream[96];
    u64 tick_index;
    if (!rng || !surface) {
        return;
    }
    dom_struct_stream_name(stream, sizeof(stream), surface->domain_id, purpose);
    D_DET_GUARD_RNG_STREAM_NAME(stream);
    tick_index = dom_struct_hash_u64(cell_key, event_index);
    d_rng_state_from_context(rng,
                             surface->world_seed,
                             surface->domain_id,
                             (u64)structure_id,
                             tick_index,
                             stream,
                             D_RNG_MIX_DOMAIN | D_RNG_MIX_PROCESS | D_RNG_MIX_TICK | D_RNG_MIX_STREAM);
}

static void dom_struct_cell_coord(q16_16 cell_size,
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
    *out_cx = dom_struct_floor_div_q16(point->x, cell_size);
    *out_cy = dom_struct_floor_div_q16(point->y, cell_size);
    *out_cz = dom_struct_floor_div_q16(point->z, cell_size);
}

static dom_domain_point dom_struct_cell_center(q16_16 cell_size, i32 cx, i32 cy, i32 cz)
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

static void dom_structure_cache_init(dom_structure_cache* cache)
{
    if (!cache) {
        return;
    }
    memset(cache, 0, sizeof(*cache));
}

static void dom_structure_tile_init(dom_structure_tile* tile)
{
    if (!tile) {
        return;
    }
    memset(tile, 0, sizeof(*tile));
}

static void dom_structure_tile_free(dom_structure_tile* tile)
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
    tile->support_capacity = (q16_16*)0;
    tile->applied_stress = (q16_16*)0;
    tile->stress_ratio = (q16_16*)0;
    tile->integrity = (q16_16*)0;
    tile->structure_id = (u32*)0;
    tile->anchor_supported_mask = (u32*)0;
    tile->flags = (u32*)0;
    tile->sample_count = 0u;
    tile->sample_dim = 0u;
    tile->tile_id = 0u;
    tile->resolution = DOM_DOMAIN_RES_REFUSED;
    memset(&tile->bounds, 0, sizeof(tile->bounds));
    tile->authoring_version = 0u;
}

static void dom_structure_cache_free(dom_structure_cache* cache)
{
    if (!cache) {
        return;
    }
    if (cache->entries) {
        for (u32 i = 0u; i < cache->capacity; ++i) {
            dom_structure_tile_free(&cache->entries[i].tile);
        }
        free(cache->entries);
        cache->entries = (dom_structure_cache_entry*)0;
    }
    cache->capacity = 0u;
    cache->count = 0u;
    cache->use_counter = 0u;
    cache->next_insert_order = 0u;
}

static int dom_structure_cache_reserve(dom_structure_cache* cache, u32 capacity)
{
    dom_structure_cache_entry* new_entries;
    u32 old_cap;
    if (!cache) {
        return -1;
    }
    if (capacity <= cache->capacity) {
        return 0;
    }
    new_entries = (dom_structure_cache_entry*)realloc(cache->entries,
                                                      capacity * sizeof(dom_structure_cache_entry));
    if (!new_entries) {
        return -1;
    }
    old_cap = cache->capacity;
    cache->entries = new_entries;
    cache->capacity = capacity;
    for (u32 i = old_cap; i < cache->capacity; ++i) {
        memset(&cache->entries[i], 0, sizeof(dom_structure_cache_entry));
        dom_structure_tile_init(&cache->entries[i].tile);
        cache->entries[i].valid = D_FALSE;
    }
    return 0;
}

static dom_structure_cache_entry* dom_structure_cache_find_entry(dom_structure_cache* cache,
                                                                 dom_domain_id domain_id,
                                                                 u64 tile_id,
                                                                 u32 resolution,
                                                                 u32 authoring_version)
{
    if (!cache || !cache->entries) {
        return (dom_structure_cache_entry*)0;
    }
    for (u32 i = 0u; i < cache->capacity; ++i) {
        dom_structure_cache_entry* entry = &cache->entries[i];
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
    return (dom_structure_cache_entry*)0;
}

static const dom_structure_tile* dom_structure_cache_peek(const dom_structure_cache* cache,
                                                          dom_domain_id domain_id,
                                                          u64 tile_id,
                                                          u32 resolution,
                                                          u32 authoring_version)
{
    if (!cache || !cache->entries) {
        return (const dom_structure_tile*)0;
    }
    for (u32 i = 0u; i < cache->capacity; ++i) {
        const dom_structure_cache_entry* entry = &cache->entries[i];
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
    return (const dom_structure_tile*)0;
}

static const dom_structure_tile* dom_structure_cache_get(dom_structure_cache* cache,
                                                         dom_domain_id domain_id,
                                                         u64 tile_id,
                                                         u32 resolution,
                                                         u32 authoring_version)
{
    dom_structure_cache_entry* entry;
    if (!cache) {
        return (const dom_structure_tile*)0;
    }
    entry = dom_structure_cache_find_entry(cache, domain_id, tile_id, resolution, authoring_version);
    if (!entry) {
        return (const dom_structure_tile*)0;
    }
    cache->use_counter += 1u;
    entry->last_used = cache->use_counter;
    return &entry->tile;
}

static dom_structure_cache_entry* dom_structure_cache_select_slot(dom_structure_cache* cache)
{
    dom_structure_cache_entry* best = (dom_structure_cache_entry*)0;
    if (!cache || !cache->entries || cache->capacity == 0u) {
        return (dom_structure_cache_entry*)0;
    }
    for (u32 i = 0u; i < cache->capacity; ++i) {
        dom_structure_cache_entry* entry = &cache->entries[i];
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

static dom_structure_tile* dom_structure_cache_put(dom_structure_cache* cache,
                                                   dom_domain_id domain_id,
                                                   dom_structure_tile* tile)
{
    dom_structure_cache_entry* entry;
    if (!cache || !tile) {
        return (dom_structure_tile*)0;
    }
    if (!cache->entries || cache->capacity == 0u) {
        return (dom_structure_tile*)0;
    }
    entry = dom_structure_cache_find_entry(cache, domain_id, tile->tile_id,
                                           tile->resolution, tile->authoring_version);
    if (!entry) {
        entry = dom_structure_cache_select_slot(cache);
    }
    if (!entry) {
        return (dom_structure_tile*)0;
    }
    if (entry->valid) {
        dom_structure_tile_free(&entry->tile);
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

    dom_structure_tile_init(tile);
    return &entry->tile;
}

static void dom_structure_cache_invalidate_domain(dom_structure_cache* cache, dom_domain_id domain_id)
{
    if (!cache || !cache->entries) {
        return;
    }
    for (u32 i = 0u; i < cache->capacity; ++i) {
        dom_structure_cache_entry* entry = &cache->entries[i];
        if (entry->valid && entry->domain_id == domain_id) {
            dom_structure_tile_free(&entry->tile);
            entry->valid = D_FALSE;
            if (cache->count > 0u) {
                cache->count -= 1u;
            }
        }
    }
}

static q16_16 dom_struct_step_from_extent(q16_16 extent, u32 sample_dim)
{
    if (sample_dim <= 1u) {
        return 0;
    }
    return (q16_16)((i64)extent / (i64)(sample_dim - 1u));
}

static u32 dom_struct_sample_index_from_coord(q16_16 coord,
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

static void dom_struct_query_meta_refused(dom_domain_query_meta* meta,
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

static void dom_struct_query_meta_ok(dom_domain_query_meta* meta,
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

static d_bool dom_struct_resolution_allowed(u32 max_resolution, u32 resolution)
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

static d_bool dom_struct_domain_is_active(const dom_structure_domain* domain)
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

static void dom_struct_sample_init(dom_structure_sample* sample)
{
    if (!sample) {
        return;
    }
    memset(sample, 0, sizeof(*sample));
    sample->support_capacity = DOM_STRUCTURE_UNKNOWN_Q16;
    sample->applied_stress = 0;
    sample->stress_ratio = DOM_STRUCTURE_UNKNOWN_Q16;
    sample->integrity = 0;
    sample->structure_id = 0u;
    sample->anchor_required_mask = 0u;
    sample->anchor_supported_mask = 0u;
    sample->flags = 0u;
}

static u32 dom_struct_spec_index(const dom_structure_surface_desc* surface, u32 structure_id)
{
    if (!surface) {
        return DOM_STRUCTURE_MAX_SPECS;
    }
    for (u32 i = 0u; i < surface->structure_count && i < DOM_STRUCTURE_MAX_SPECS; ++i) {
        if (surface->structures[i].structure_id == structure_id) {
            return i;
        }
    }
    return DOM_STRUCTURE_MAX_SPECS;
}

static u32 dom_struct_anchor_required_mask(const dom_structure_spec_desc* spec)
{
    u32 mask = 0u;
    if (!spec) {
        return 0u;
    }
    for (u32 i = 0u; i < spec->anchor_count && i < DOM_STRUCTURE_MAX_ANCHORS; ++i) {
        mask |= (1u << i);
    }
    return mask;
}

static d_bool dom_struct_anchor_has_unknown_kind(const dom_structure_spec_desc* spec)
{
    if (!spec) {
        return D_FALSE;
    }
    for (u32 i = 0u; i < spec->anchor_count && i < DOM_STRUCTURE_MAX_ANCHORS; ++i) {
        if (spec->anchors[i].kind != DOM_STRUCTURE_ANCHOR_TERRAIN) {
            return D_TRUE;
        }
    }
    return D_FALSE;
}

static q16_16 dom_struct_support_capacity(const dom_structure_domain* domain,
                                          const dom_domain_point* point,
                                          dom_domain_budget* budget,
                                          q16_16* out_slope,
                                          u32* out_flags)
{
    dom_terrain_sample terrain;
    dom_geology_sample geology;
    q16_16 support = DOM_STRUCTURE_UNKNOWN_Q16;
    u32 flags = 0u;
    if (out_slope) {
        *out_slope = 0;
    }
    if (!domain || !point) {
        if (out_flags) {
            *out_flags |= DOM_STRUCTURE_SAMPLE_FIELDS_UNKNOWN;
        }
        return DOM_STRUCTURE_UNKNOWN_Q16;
    }
    if (dom_terrain_sample_query(&domain->terrain_domain, point, budget, &terrain) != 0) {
        if (out_flags) {
            *out_flags |= DOM_STRUCTURE_SAMPLE_FIELDS_UNKNOWN;
        }
        return DOM_STRUCTURE_UNKNOWN_Q16;
    }
    if (out_slope) {
        *out_slope = terrain.slope;
    }
    if (terrain.flags & (DOM_TERRAIN_SAMPLE_FIELDS_UNKNOWN | DOM_TERRAIN_SAMPLE_PHI_UNKNOWN)) {
        flags |= DOM_STRUCTURE_SAMPLE_FIELDS_UNKNOWN;
    }
    if (dom_geology_sample_query(&domain->geology_domain, point, budget, &geology) != 0) {
        flags |= DOM_STRUCTURE_SAMPLE_FIELDS_UNKNOWN;
    }
    if (geology.flags & (DOM_GEOLOGY_SAMPLE_FIELDS_UNKNOWN | DOM_GEOLOGY_SAMPLE_STRATA_UNKNOWN)) {
        flags |= DOM_STRUCTURE_SAMPLE_FIELDS_UNKNOWN;
    }
    if (flags) {
        if (out_flags) {
            *out_flags |= flags;
        }
        return DOM_STRUCTURE_UNKNOWN_Q16;
    }
    if (terrain.phi > 0) {
        support = 0;
    } else {
        q16_16 hardness = dom_struct_clamp_q16_16(geology.hardness, 0, d_q16_16_from_int(1));
        q16_16 fracture = dom_struct_clamp_q16_16(geology.fracture_risk, 0, d_q16_16_from_int(1));
        q16_16 slope_factor = dom_struct_clamp_q16_16(d_q16_16_sub(d_q16_16_from_int(1), terrain.slope), 0, d_q16_16_from_int(1));
        support = d_q16_16_mul(hardness, d_q16_16_sub(d_q16_16_from_int(1), fracture));
        support = d_q16_16_mul(support, slope_factor);
    }
    if (out_flags) {
        *out_flags |= flags;
    }
    return support;
}

static const dom_structure_spec_desc* dom_struct_select_instance(const dom_structure_domain* domain,
                                                                 const dom_domain_point* point,
                                                                 dom_structure_instance* out_temp,
                                                                 const dom_structure_instance** out_instance,
                                                                 u32* out_flags)
{
    i32 cx = 0;
    i32 cy = 0;
    i32 cz = 0;
    const dom_structure_spec_desc* spec = (const dom_structure_spec_desc*)0;
    const dom_structure_instance* best = (const dom_structure_instance*)0;
    u32 best_id = 0xFFFFFFFFu;
    u32 best_index = 0xFFFFFFFFu;
    if (out_instance) {
        *out_instance = (const dom_structure_instance*)0;
    }
    if (!domain || !point) {
        if (out_flags) {
            *out_flags |= DOM_STRUCTURE_SAMPLE_FIELDS_UNKNOWN;
        }
        return (const dom_structure_spec_desc*)0;
    }
    dom_struct_cell_coord(domain->surface.placement_cell_size, point, &cx, &cy, &cz);
    for (u32 i = 0u; i < domain->instance_count && i < DOM_STRUCTURE_MAX_INSTANCES; ++i) {
        const dom_structure_instance* inst = &domain->instances[i];
        if (inst->structure_id == 0u) {
            continue;
        }
        if (inst->cell_x != cx || inst->cell_y != cy || inst->cell_z != cz) {
            continue;
        }
        if (!best || inst->structure_id < best_id ||
            (inst->structure_id == best_id && i < best_index)) {
            best = inst;
            best_id = inst->structure_id;
            best_index = i;
        }
    }
    if (best) {
        u32 spec_index = dom_struct_spec_index(&domain->surface, best->structure_id);
        if (spec_index >= DOM_STRUCTURE_MAX_SPECS) {
            if (out_flags) {
                *out_flags |= DOM_STRUCTURE_SAMPLE_FIELDS_UNKNOWN;
            }
            return (const dom_structure_spec_desc*)0;
        }
        if (out_instance) {
            *out_instance = best;
        }
        return &domain->surface.structures[spec_index];
    }

    if (domain->surface.structure_count == 0u || domain->surface.density_base <= 0) {
        return (const dom_structure_spec_desc*)0;
    }
    if (!out_temp) {
        return (const dom_structure_spec_desc*)0;
    }
    {
        d_rng_state rng;
        u64 cell_key = dom_struct_cell_key(cx, cy, cz);
        dom_struct_rng_state_for_cell(&rng, &domain->surface, "placement", cell_key, 0u, 0u);
        if (dom_struct_ratio_from_u32(d_rng_next_u32(&rng)) >= domain->surface.density_base) {
            return (const dom_structure_spec_desc*)0;
        }
        {
            u32 idx = 0u;
            if (domain->surface.structure_count > 0u) {
                idx = d_rng_next_u32(&rng) % domain->surface.structure_count;
                if (idx >= DOM_STRUCTURE_MAX_SPECS) {
                    idx = 0u;
                }
            }
            spec = &domain->surface.structures[idx];
            memset(out_temp, 0, sizeof(*out_temp));
            out_temp->structure_id = spec->structure_id;
            out_temp->location = dom_struct_cell_center(domain->surface.placement_cell_size, cx, cy, cz);
            out_temp->integrity = d_q16_16_from_int(1);
            out_temp->reinforcement = 0;
            out_temp->flags = 0u;
            out_temp->cell_x = cx;
            out_temp->cell_y = cy;
            out_temp->cell_z = cz;
            if (out_instance) {
                *out_instance = out_temp;
            }
            return spec;
        }
    }
}

static q16_16 dom_struct_applied_stress(const dom_structure_spec_desc* spec)
{
    q16_16 load;
    if (!spec) {
        return 0;
    }
    load = spec->traits.density;
    load = d_q16_16_add(load, d_q16_16_mul(load, spec->traits.stiffness));
    return d_q16_16_mul(load, spec->gravity_scale);
}

static q16_16 dom_struct_stress_ratio(q16_16 applied, q16_16 support, q16_16 capacity)
{
    q16_16 limit;
    if (support == DOM_STRUCTURE_UNKNOWN_Q16) {
        return DOM_STRUCTURE_UNKNOWN_Q16;
    }
    limit = d_q16_16_mul(support, capacity);
    if (limit <= 0) {
        return DOM_STRUCTURE_UNKNOWN_Q16;
    }
    return d_fixed_div_q16_16(applied, limit);
}

static void dom_struct_eval_fields(const dom_structure_domain* domain,
                                   const dom_domain_point* point,
                                   u64 tick,
                                   dom_domain_budget* budget,
                                   dom_structure_sample* out_sample)
{
    dom_structure_instance temp;
    const dom_structure_instance* inst = (const dom_structure_instance*)0;
    const dom_structure_spec_desc* spec = (const dom_structure_spec_desc*)0;
    q16_16 support = DOM_STRUCTURE_UNKNOWN_Q16;
    q16_16 applied = 0;
    q16_16 ratio = DOM_STRUCTURE_UNKNOWN_Q16;
    q16_16 integrity = 0;
    q16_16 slope = 0;
    u32 flags = 0u;
    u32 anchor_required = 0u;
    u32 anchor_supported = 0u;
    (void)tick;

    if (!out_sample) {
        return;
    }
    dom_struct_sample_init(out_sample);
    support = dom_struct_support_capacity(domain, point, budget, &slope, &flags);
    out_sample->support_capacity = support;
    if (flags) {
        out_sample->flags |= DOM_STRUCTURE_SAMPLE_FIELDS_UNKNOWN;
    }

    spec = dom_struct_select_instance(domain, point, &temp, &inst, &flags);
    if (flags) {
        out_sample->flags |= DOM_STRUCTURE_SAMPLE_FIELDS_UNKNOWN;
    }
    if (!spec) {
        out_sample->structure_id = 0u;
        out_sample->integrity = 0;
        out_sample->applied_stress = 0;
        out_sample->stress_ratio = DOM_STRUCTURE_UNKNOWN_Q16;
        return;
    }

    out_sample->flags |= DOM_STRUCTURE_SAMPLE_INSTANCE_PRESENT;
    out_sample->structure_id = spec->structure_id;

    anchor_required = dom_struct_anchor_required_mask(spec);
    if (dom_struct_anchor_has_unknown_kind(spec)) {
        out_sample->flags |= DOM_STRUCTURE_SAMPLE_ANCHOR_UNKNOWN;
    }

    if (support != DOM_STRUCTURE_UNKNOWN_Q16 && support > 0) {
        anchor_supported = anchor_required;
    } else {
        anchor_supported = 0u;
    }

    out_sample->anchor_required_mask = anchor_required;
    out_sample->anchor_supported_mask = anchor_supported;

    if (inst && (inst->flags & DOM_STRUCTURE_INSTANCE_COLLAPSED)) {
        out_sample->flags |= DOM_STRUCTURE_SAMPLE_COLLAPSED;
    }
    if (inst && (inst->flags & DOM_STRUCTURE_INSTANCE_UNSTABLE)) {
        out_sample->flags |= DOM_STRUCTURE_SAMPLE_UNSTABLE;
    }

    applied = dom_struct_applied_stress(spec);
    if (inst) {
        q16_16 reinforce = dom_struct_clamp_q16_16(inst->reinforcement, 0, d_q16_16_from_int(1));
        if (support != DOM_STRUCTURE_UNKNOWN_Q16) {
            support = d_q16_16_add(support, d_q16_16_mul(support, reinforce));
            out_sample->support_capacity = support;
        }
    }
    ratio = dom_struct_stress_ratio(applied, support, spec->load_capacity);

    if (inst) {
        integrity = inst->integrity;
    } else {
        integrity = d_q16_16_from_int(1);
    }

    if (ratio != DOM_STRUCTURE_UNKNOWN_Q16 && ratio > d_q16_16_from_int(1)) {
        q16_16 over = d_q16_16_sub(ratio, d_q16_16_from_int(1));
        q16_16 penalty = d_q16_16_mul(over, spec->traits.brittleness);
        if (integrity > penalty) {
            integrity = d_q16_16_sub(integrity, penalty);
        } else {
            integrity = 0;
        }
        out_sample->flags |= DOM_STRUCTURE_SAMPLE_UNSTABLE;
    }

    if (out_sample->flags & DOM_STRUCTURE_SAMPLE_COLLAPSED) {
        integrity = 0;
    }

    out_sample->applied_stress = applied;
    out_sample->stress_ratio = ratio;
    out_sample->integrity = integrity;

    if (spec->slope_max > 0 && slope > spec->slope_max) {
        out_sample->flags |= DOM_STRUCTURE_SAMPLE_UNSTABLE;
    }
}

static int dom_struct_tile_build(dom_structure_tile* tile,
                                 const dom_domain_tile_desc* desc,
                                 const dom_structure_domain* domain,
                                 u64 tick)
{
    u32 sample_dim;
    u32 sample_count;
    u32 q16_count;
    u32 u32_count;
    q16_16 extent_x;
    q16_16 extent_y;
    q16_16 extent_z;
    q16_16 step_x;
    q16_16 step_y;
    q16_16 step_z;
    if (!tile || !desc || !domain) {
        return -1;
    }
    sample_dim = desc->sample_dim;
    if (sample_dim == 0u) {
        return -1;
    }
    sample_count = sample_dim * sample_dim * sample_dim;
    q16_count = sample_count * 4u;
    u32_count = sample_count * 3u;
    tile->data_q16 = (q16_16*)calloc(q16_count, sizeof(q16_16));
    tile->data_u32 = (u32*)calloc(u32_count, sizeof(u32));
    if (!tile->data_q16 || !tile->data_u32) {
        dom_structure_tile_free(tile);
        return -1;
    }
    tile->support_capacity = tile->data_q16;
    tile->applied_stress = tile->support_capacity + sample_count;
    tile->stress_ratio = tile->applied_stress + sample_count;
    tile->integrity = tile->stress_ratio + sample_count;

    tile->structure_id = tile->data_u32;
    tile->anchor_supported_mask = tile->structure_id + sample_count;
    tile->flags = tile->anchor_supported_mask + sample_count;

    tile->tile_id = desc->tile_id;
    tile->resolution = desc->resolution;
    tile->sample_dim = sample_dim;
    tile->bounds = desc->bounds;
    tile->authoring_version = desc->authoring_version;
    tile->sample_count = sample_count;

    extent_x = d_q16_16_sub(desc->bounds.max.x, desc->bounds.min.x);
    extent_y = d_q16_16_sub(desc->bounds.max.y, desc->bounds.min.y);
    extent_z = d_q16_16_sub(desc->bounds.max.z, desc->bounds.min.z);
    step_x = dom_struct_step_from_extent(extent_x, sample_dim);
    step_y = dom_struct_step_from_extent(extent_y, sample_dim);
    step_z = dom_struct_step_from_extent(extent_z, sample_dim);

    for (u32 z = 0u; z < sample_dim; ++z) {
        q16_16 zpos = desc->bounds.min.z;
        if (sample_dim > 1u) {
            zpos = d_q16_16_add(desc->bounds.min.z, (q16_16)((i64)step_z * (i64)z));
        }
        for (u32 y = 0u; y < sample_dim; ++y) {
            q16_16 ypos = desc->bounds.min.y;
            if (sample_dim > 1u) {
                ypos = d_q16_16_add(desc->bounds.min.y, (q16_16)((i64)step_y * (i64)y));
            }
            for (u32 x = 0u; x < sample_dim; ++x) {
                q16_16 xpos = desc->bounds.min.x;
                u32 index = (z * sample_dim * sample_dim) + (y * sample_dim) + x;
                dom_domain_point point;
                dom_structure_sample sample;
                if (sample_dim > 1u) {
                    xpos = d_q16_16_add(desc->bounds.min.x, (q16_16)((i64)step_x * (i64)x));
                }
                point.x = xpos;
                point.y = ypos;
                point.z = zpos;
                dom_struct_eval_fields(domain, &point, tick, (dom_domain_budget*)0, &sample);
                tile->support_capacity[index] = sample.support_capacity;
                tile->applied_stress[index] = sample.applied_stress;
                tile->stress_ratio[index] = sample.stress_ratio;
                tile->integrity[index] = sample.integrity;
                tile->structure_id[index] = sample.structure_id;
                tile->anchor_supported_mask[index] = sample.anchor_supported_mask;
                tile->flags[index] = sample.flags;
            }
        }
    }

    return 0;
}

static void dom_struct_sample_from_tile(const dom_structure_domain* domain,
                                        const dom_structure_tile* tile,
                                        const dom_domain_point* point,
                                        dom_structure_sample* out_sample)
{
    u32 ix;
    u32 iy;
    u32 iz;
    u32 index;
    if (!domain || !tile || !point || !out_sample) {
        return;
    }
    dom_struct_sample_init(out_sample);

    ix = dom_struct_sample_index_from_coord(point->x,
                                            tile->bounds.min.x,
                                            tile->bounds.max.x,
                                            dom_struct_step_from_extent(d_q16_16_sub(tile->bounds.max.x, tile->bounds.min.x), tile->sample_dim),
                                            tile->sample_dim);
    iy = dom_struct_sample_index_from_coord(point->y,
                                            tile->bounds.min.y,
                                            tile->bounds.max.y,
                                            dom_struct_step_from_extent(d_q16_16_sub(tile->bounds.max.y, tile->bounds.min.y), tile->sample_dim),
                                            tile->sample_dim);
    iz = dom_struct_sample_index_from_coord(point->z,
                                            tile->bounds.min.z,
                                            tile->bounds.max.z,
                                            dom_struct_step_from_extent(d_q16_16_sub(tile->bounds.max.z, tile->bounds.min.z), tile->sample_dim),
                                            tile->sample_dim);
    index = (iz * tile->sample_dim * tile->sample_dim) + (iy * tile->sample_dim) + ix;
    if (index >= tile->sample_count) {
        index = tile->sample_count - 1u;
    }

    out_sample->support_capacity = tile->support_capacity[index];
    out_sample->applied_stress = tile->applied_stress[index];
    out_sample->stress_ratio = tile->stress_ratio[index];
    out_sample->integrity = tile->integrity[index];
    out_sample->structure_id = tile->structure_id[index];
    out_sample->anchor_supported_mask = tile->anchor_supported_mask[index];
    out_sample->flags = tile->flags[index];

    if (out_sample->structure_id != 0u) {
        u32 spec_index = dom_struct_spec_index(&domain->surface, out_sample->structure_id);
        if (spec_index < DOM_STRUCTURE_MAX_SPECS) {
            out_sample->anchor_required_mask = dom_struct_anchor_required_mask(&domain->surface.structures[spec_index]);
        }
    }
}

static int dom_struct_tile_cached(const dom_structure_domain* domain,
                                  const dom_domain_tile_desc* desc)
{
    if (!domain || !desc) {
        return 0;
    }
    return dom_structure_cache_peek(&domain->cache,
                                    domain->surface.domain_id,
                                    desc->tile_id,
                                    desc->resolution,
                                    desc->authoring_version) != 0;
}

static const dom_structure_tile* dom_struct_tile_get(dom_structure_domain* domain,
                                                     const dom_domain_tile_desc* desc,
                                                     u64 tick,
                                                     d_bool allow_build)
{
    const dom_structure_tile* cached;
    if (!domain || !desc) {
        return (const dom_structure_tile*)0;
    }
    cached = dom_structure_cache_get(&domain->cache,
                                     domain->surface.domain_id,
                                     desc->tile_id,
                                     desc->resolution,
                                     desc->authoring_version);
    if (cached) {
        return cached;
    }
    if (!allow_build) {
        return (const dom_structure_tile*)0;
    }
    {
        dom_structure_tile temp;
        dom_structure_tile_init(&temp);
        if (dom_struct_tile_build(&temp, desc, domain, tick) != 0) {
            dom_structure_tile_free(&temp);
            return (const dom_structure_tile*)0;
        }
        cached = dom_structure_cache_put(&domain->cache, domain->surface.domain_id, &temp);
        if (!cached) {
            dom_structure_tile_free(&temp);
            return (const dom_structure_tile*)0;
        }
        return cached;
    }
}

void dom_structure_surface_desc_init(dom_structure_surface_desc* desc)
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

    desc->structure_count = 0u;
    desc->instance_count = 0u;
    desc->placement_cell_size = d_q16_16_from_int(8);
    desc->density_base = d_q16_16_from_int(0);
    desc->stress_check_period_ticks = 240u;
    desc->repair_period_ticks = 600u;
    desc->reinforce_period_ticks = 1200u;
    desc->cache_capacity = 128u;

    for (u32 i = 0u; i < DOM_STRUCTURE_MAX_SPECS; ++i) {
        dom_structure_spec_desc* spec = &desc->structures[i];
        memset(spec, 0, sizeof(*spec));
        spec->traits.stiffness = d_q16_16_from_double(0.3);
        spec->traits.density = d_q16_16_from_double(0.4);
        spec->traits.brittleness = d_q16_16_from_double(0.2);
        spec->load_capacity = d_q16_16_from_int(1);
        spec->anchor_count = 1u;
        spec->anchors[0].kind = DOM_STRUCTURE_ANCHOR_TERRAIN;
        spec->anchors[0].support_scale = d_q16_16_from_int(1);
        spec->gravity_scale = d_q16_16_from_int(1);
        spec->slope_max = d_q16_16_from_int(1);
        spec->maturity_tag = 0u;
    }
    for (u32 i = 0u; i < DOM_STRUCTURE_MAX_INSTANCES; ++i) {
        dom_structure_instance* inst = &desc->instances[i];
        memset(inst, 0, sizeof(*inst));
        inst->integrity = d_q16_16_from_int(1);
        inst->reinforcement = 0;
    }
}

static void dom_struct_seed_instances(dom_structure_domain* domain)
{
    if (!domain) {
        return;
    }
    domain->instance_count = 0u;
    if (domain->surface.instance_count == 0u) {
        return;
    }
    for (u32 i = 0u; i < domain->surface.instance_count && i < DOM_STRUCTURE_MAX_INSTANCES; ++i) {
        dom_structure_instance inst = domain->surface.instances[i];
        if (inst.structure_id == 0u) {
            continue;
        }
        dom_struct_cell_coord(domain->surface.placement_cell_size, &inst.location,
                              &inst.cell_x, &inst.cell_y, &inst.cell_z);
        if (inst.integrity < 0) {
            inst.integrity = 0;
        }
        if (inst.integrity > d_q16_16_from_int(1)) {
            inst.integrity = d_q16_16_from_int(1);
        }
        if (inst.reinforcement < 0) {
            inst.reinforcement = 0;
        }
        if (inst.reinforcement > d_q16_16_from_int(1)) {
            inst.reinforcement = d_q16_16_from_int(1);
        }
        domain->instances[domain->instance_count++] = inst;
    }
}

void dom_structure_domain_init(dom_structure_domain* domain,
                               const dom_structure_surface_desc* desc)
{
    dom_structure_surface_desc normalized;
    dom_terrain_surface_desc terrain_desc;
    dom_geology_surface_desc geology_desc;
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
    dom_structure_cache_init(&domain->cache);
    if (cache_capacity > 0u) {
        dom_structure_cache_reserve(&domain->cache, cache_capacity);
    }
    domain->capsule_count = 0u;
    dom_struct_seed_instances(domain);
}

void dom_structure_domain_free(dom_structure_domain* domain)
{
    if (!domain) {
        return;
    }
    dom_structure_cache_free(&domain->cache);
    dom_terrain_domain_free(&domain->terrain_domain);
    dom_geology_domain_free(&domain->geology_domain);
    domain->capsule_count = 0u;
    domain->instance_count = 0u;
}

void dom_structure_domain_set_state(dom_structure_domain* domain,
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
        dom_structure_cache_invalidate_domain(&domain->cache, domain->surface.domain_id);
    }
}

void dom_structure_domain_set_policy(dom_structure_domain* domain,
                                     const dom_domain_policy* policy)
{
    if (!domain || !policy) {
        return;
    }
    domain->policy = *policy;
    dom_terrain_domain_set_policy(&domain->terrain_domain, policy);
    dom_geology_domain_set_policy(&domain->geology_domain, policy);
    dom_structure_cache_invalidate_domain(&domain->cache, domain->surface.domain_id);
}

static int dom_struct_build_tile_desc(const dom_structure_domain* domain,
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
        return 0;
    }
    source = dom_terrain_surface_sdf(&domain->terrain_domain.surface);
    if (!source) {
        return 0;
    }
    tile_size = domain->policy.tile_size;
    if (tile_size <= 0) {
        return 0;
    }
    if (resolution == DOM_DOMAIN_RES_FULL) {
        sample_dim = domain->policy.sample_dim_full;
    } else if (resolution == DOM_DOMAIN_RES_MEDIUM) {
        sample_dim = domain->policy.sample_dim_medium;
    } else {
        sample_dim = domain->policy.sample_dim_coarse;
    }
    if (sample_dim == 0u) {
        return 0;
    }
    tx = dom_struct_floor_div_q16((q16_16)(point->x - source->bounds.min.x), tile_size);
    ty = dom_struct_floor_div_q16((q16_16)(point->y - source->bounds.min.y), tile_size);
    tz = dom_struct_floor_div_q16((q16_16)(point->z - source->bounds.min.z), tile_size);
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
    return 1;
}

int dom_structure_sample_query(const dom_structure_domain* domain,
                               const dom_domain_point* point,
                               u64 tick,
                               dom_domain_budget* budget,
                               dom_structure_sample* out_sample)
{
    dom_domain_tile_desc desc;
    const dom_domain_sdf_source* source;
    u32 budget_before = 0u;
    u32 cost_units = 0u;
    d_bool collapsed = D_FALSE;
    if (!domain || !point || !out_sample) {
        return -1;
    }
    dom_struct_sample_init(out_sample);
    if (budget) {
        budget_before = budget->used_units;
    }
    if (!dom_struct_domain_is_active(domain)) {
        dom_struct_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_DOMAIN_INACTIVE, budget);
        out_sample->flags |= DOM_STRUCTURE_SAMPLE_FIELDS_UNKNOWN;
        return 0;
    }
    source = dom_terrain_surface_sdf(&domain->terrain_domain.surface);
    if (!source || !source->eval) {
        dom_struct_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_NO_SOURCE, budget);
        out_sample->flags |= DOM_STRUCTURE_SAMPLE_FIELDS_UNKNOWN;
        return 0;
    }
    if (!dom_domain_aabb_contains(&source->bounds, point)) {
        dom_struct_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_COARSE,
                                 DOM_DOMAIN_CONFIDENCE_LOWER_BOUND, 0u, budget);
        out_sample->flags |= DOM_STRUCTURE_SAMPLE_FIELDS_UNKNOWN;
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
        dom_struct_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                                 DOM_DOMAIN_CONFIDENCE_UNKNOWN, 0u, budget);
        out_sample->flags |= DOM_STRUCTURE_SAMPLE_FIELDS_UNKNOWN | DOM_STRUCTURE_SAMPLE_COLLAPSED;
        return 0;
    }

    if (dom_struct_resolution_allowed(domain->policy.max_resolution, DOM_DOMAIN_RES_FULL)) {
        if (dom_domain_budget_consume(budget, domain->policy.cost_full)) {
            dom_struct_eval_fields(domain, point, tick, budget, out_sample);
            if (budget) {
                cost_units = budget->used_units - budget_before;
            }
            dom_struct_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_FULL,
                                     DOM_DOMAIN_CONFIDENCE_EXACT, cost_units, budget);
            return 0;
        }
    }

    if (dom_struct_resolution_allowed(domain->policy.max_resolution, DOM_DOMAIN_RES_MEDIUM)) {
        u32 cost = domain->policy.cost_medium;
        if (dom_struct_build_tile_desc(domain, point, DOM_DOMAIN_RES_MEDIUM, &desc)) {
            if (!dom_struct_tile_cached(domain, &desc)) {
                cost += domain->policy.tile_build_cost_medium;
            }
            if (dom_domain_budget_consume(budget, cost)) {
                const dom_structure_tile* tile = dom_struct_tile_get((dom_structure_domain*)domain, &desc, tick, D_TRUE);
                if (!tile) {
                    dom_struct_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_INTERNAL, budget);
                    out_sample->flags |= DOM_STRUCTURE_SAMPLE_FIELDS_UNKNOWN;
                    return 0;
                }
                dom_struct_sample_from_tile(domain, tile, point, out_sample);
                if (budget) {
                    cost_units = budget->used_units - budget_before;
                }
                dom_struct_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_MEDIUM,
                                         DOM_DOMAIN_CONFIDENCE_LOWER_BOUND, cost_units, budget);
                return 0;
            }
        }
    }

    if (dom_struct_resolution_allowed(domain->policy.max_resolution, DOM_DOMAIN_RES_COARSE)) {
        u32 cost = domain->policy.cost_coarse;
        if (dom_struct_build_tile_desc(domain, point, DOM_DOMAIN_RES_COARSE, &desc)) {
            if (!dom_struct_tile_cached(domain, &desc)) {
                cost += domain->policy.tile_build_cost_coarse;
            }
            if (dom_domain_budget_consume(budget, cost)) {
                const dom_structure_tile* tile = dom_struct_tile_get((dom_structure_domain*)domain, &desc, tick, D_TRUE);
                if (!tile) {
                    dom_struct_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_INTERNAL, budget);
                    out_sample->flags |= DOM_STRUCTURE_SAMPLE_FIELDS_UNKNOWN;
                    return 0;
                }
                dom_struct_sample_from_tile(domain, tile, point, out_sample);
                if (budget) {
                    cost_units = budget->used_units - budget_before;
                }
                dom_struct_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_COARSE,
                                         DOM_DOMAIN_CONFIDENCE_LOWER_BOUND, cost_units, budget);
                return 0;
            }
        }
    }

    if (dom_struct_resolution_allowed(domain->policy.max_resolution, DOM_DOMAIN_RES_ANALYTIC)) {
        if (dom_domain_budget_consume(budget, domain->policy.cost_analytic)) {
            dom_struct_eval_fields(domain, point, tick, budget, out_sample);
            if (budget) {
                cost_units = budget->used_units - budget_before;
            }
            dom_struct_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                                     DOM_DOMAIN_CONFIDENCE_EXACT, cost_units, budget);
            return 0;
        }
    }

    dom_struct_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_BUDGET, budget);
    out_sample->flags |= DOM_STRUCTURE_SAMPLE_FIELDS_UNKNOWN;
    return 0;
}

static u32 dom_struct_hist_bin(q16_16 value)
{
    q16_16 clamped = dom_struct_clamp_q16_16(value, 0, d_q16_16_from_int(1));
    u32 scaled = (u32)(((i64)clamped * (DOM_STRUCTURE_HIST_BINS - 1u)) >> 16);
    if (scaled >= DOM_STRUCTURE_HIST_BINS) {
        scaled = DOM_STRUCTURE_HIST_BINS - 1u;
    }
    return scaled;
}

static q16_16 dom_struct_hist_bin_ratio(u32 count, u32 total)
{
    if (total == 0u) {
        return 0;
    }
    return (q16_16)(((u64)count << 16) / total);
}

static u32 dom_struct_rng_cursor(const dom_structure_surface_desc* surface,
                                 const dom_structure_spec_desc* spec,
                                 u64 tick)
{
    d_rng_state rng;
    u64 period = 1u;
    u64 event_index = 0u;
    if (!surface || !spec) {
        return 0u;
    }
    if (surface->stress_check_period_ticks > 0u) {
        period = surface->stress_check_period_ticks;
    }
    if (period > 0u) {
        event_index = tick / period;
    }
    dom_struct_rng_state_for_cell(&rng, surface, "stress", 0u, spec->structure_id, event_index);
    return rng.state;
}

static int dom_struct_capsule_store(dom_structure_domain* domain,
                                    const dom_domain_tile_desc* desc,
                                    u64 tick)
{
    dom_structure_macro_capsule capsule;
    dom_structure_tile tile;
    u32 integrity_bins[DOM_STRUCTURE_MAX_SPECS][DOM_STRUCTURE_HIST_BINS];
    u32 stress_bins[DOM_STRUCTURE_MAX_SPECS][DOM_STRUCTURE_HIST_BINS];
    q16_16 mass_total = 0;
    u32 sample_count;
    if (!domain || !desc) {
        return -1;
    }
    if (domain->capsule_count >= DOM_STRUCTURE_MAX_CAPSULES) {
        return -2;
    }
    memset(integrity_bins, 0, sizeof(integrity_bins));
    memset(stress_bins, 0, sizeof(stress_bins));
    dom_structure_tile_init(&tile);
    if (dom_struct_tile_build(&tile, desc, domain, tick) != 0) {
        dom_structure_tile_free(&tile);
        return -1;
    }
    sample_count = tile.sample_count;
    for (u32 i = 0u; i < sample_count; ++i) {
        if (tile.flags[i] & DOM_STRUCTURE_SAMPLE_INSTANCE_PRESENT) {
            u32 spec_index = dom_struct_spec_index(&domain->surface, tile.structure_id[i]);
            if (spec_index < DOM_STRUCTURE_MAX_SPECS) {
                const dom_structure_spec_desc* spec = &domain->surface.structures[spec_index];
                integrity_bins[spec_index][dom_struct_hist_bin(tile.integrity[i])] += 1u;
                stress_bins[spec_index][dom_struct_hist_bin(tile.stress_ratio[i])] += 1u;
                mass_total = d_q16_16_add(mass_total, spec->traits.density);
            }
        }
    }

    memset(&capsule, 0, sizeof(capsule));
    capsule.capsule_id = desc->tile_id;
    capsule.tile_id = desc->tile_id;
    capsule.tick = tick;
    capsule.bounds = desc->bounds;
    capsule.structure_count = domain->surface.structure_count;
    if (capsule.structure_count > DOM_STRUCTURE_MAX_SPECS) {
        capsule.structure_count = DOM_STRUCTURE_MAX_SPECS;
    }
    for (u32 s = 0u; s < capsule.structure_count; ++s) {
        capsule.structure_ids[s] = domain->surface.structures[s].structure_id;
        capsule.instance_counts[s] = 0u;
        for (u32 b = 0u; b < DOM_STRUCTURE_HIST_BINS; ++b) {
            capsule.integrity_hist[s][b] = dom_struct_hist_bin_ratio(integrity_bins[s][b], sample_count);
            capsule.stress_hist[s][b] = dom_struct_hist_bin_ratio(stress_bins[s][b], sample_count);
        }
        capsule.rng_cursor[s] = dom_struct_rng_cursor(&domain->surface, &domain->surface.structures[s], tick);
    }
    for (u32 i = 0u; i < sample_count; ++i) {
        if (tile.flags[i] & DOM_STRUCTURE_SAMPLE_INSTANCE_PRESENT) {
            u32 spec_index = dom_struct_spec_index(&domain->surface, tile.structure_id[i]);
            if (spec_index < DOM_STRUCTURE_MAX_SPECS) {
                capsule.instance_counts[spec_index] += 1u;
            }
        }
    }
    capsule.mass_total = mass_total;

    dom_structure_tile_free(&tile);
    domain->capsules[domain->capsule_count++] = capsule;
    return 0;
}

int dom_structure_domain_collapse_tile(dom_structure_domain* domain,
                                       const dom_domain_tile_desc* desc,
                                       u64 tick)
{
    if (!domain || !desc) {
        return -1;
    }
    if (domain->cache.entries) {
        for (u32 i = 0u; i < domain->cache.capacity; ++i) {
            dom_structure_cache_entry* entry = &domain->cache.entries[i];
            if (!entry->valid) {
                continue;
            }
            if (entry->domain_id == domain->surface.domain_id &&
                entry->tile_id == desc->tile_id) {
                dom_structure_tile_free(&entry->tile);
                entry->valid = D_FALSE;
                if (domain->cache.count > 0u) {
                    domain->cache.count -= 1u;
                }
            }
        }
    }
    return dom_struct_capsule_store(domain, desc, tick);
}

int dom_structure_domain_expand_tile(dom_structure_domain* domain, u64 tile_id)
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

u32 dom_structure_domain_capsule_count(const dom_structure_domain* domain)
{
    return domain ? domain->capsule_count : 0u;
}

const dom_structure_macro_capsule* dom_structure_domain_capsule_at(const dom_structure_domain* domain,
                                                                   u32 index)
{
    if (!domain || index >= domain->capsule_count) {
        return (const dom_structure_macro_capsule*)0;
    }
    return &domain->capsules[index];
}

static void dom_struct_process_result_init(dom_structure_process_result* result)
{
    if (!result) {
        return;
    }
    memset(result, 0, sizeof(*result));
    result->ok = 0u;
    result->refusal_reason = DOM_DOMAIN_REFUSE_NONE;
    result->flags = 0u;
    result->support_capacity = DOM_STRUCTURE_UNKNOWN_Q16;
    result->applied_stress = 0;
    result->stress_ratio = DOM_STRUCTURE_UNKNOWN_Q16;
}

static int dom_struct_place_common(dom_structure_domain* domain,
                                   dom_structure_instance* inst,
                                   u64 tick,
                                   dom_structure_process_result* out_result)
{
    dom_structure_sample sample;
    dom_struct_process_result_init(out_result);
    if (!domain || !inst) {
        if (out_result) {
            out_result->refusal_reason = DOM_DOMAIN_REFUSE_INTERNAL;
        }
        return -1;
    }
    if (!dom_struct_domain_is_active(domain)) {
        if (out_result) {
            out_result->refusal_reason = DOM_DOMAIN_REFUSE_DOMAIN_INACTIVE;
        }
        return -2;
    }
    if (domain->instance_count >= DOM_STRUCTURE_MAX_INSTANCES) {
        if (out_result) {
            out_result->refusal_reason = DOM_DOMAIN_REFUSE_INTERNAL;
        }
        return -3;
    }
    if (dom_struct_spec_index(&domain->surface, inst->structure_id) >= DOM_STRUCTURE_MAX_SPECS) {
        if (out_result) {
            out_result->refusal_reason = DOM_DOMAIN_REFUSE_NO_SOURCE;
        }
        return -4;
    }
    dom_struct_eval_fields(domain, &inst->location, tick, (dom_domain_budget*)0, &sample);
    if (sample.flags & DOM_STRUCTURE_SAMPLE_FIELDS_UNKNOWN) {
        if (out_result) {
            out_result->refusal_reason = DOM_DOMAIN_REFUSE_NO_ANALYTIC;
        }
        return -5;
    }
    if (sample.support_capacity <= 0) {
        if (out_result) {
            out_result->refusal_reason = DOM_DOMAIN_REFUSE_POLICY;
        }
        return -6;
    }
    if (out_result) {
        out_result->support_capacity = sample.support_capacity;
        out_result->applied_stress = sample.applied_stress;
        out_result->stress_ratio = sample.stress_ratio;
        out_result->ok = 1u;
    }
    return 0;
}

int dom_structure_place(dom_structure_domain* domain,
                        const dom_structure_instance* instance,
                        u64 tick,
                        dom_structure_process_result* out_result)
{
    dom_structure_instance inst;
    if (!domain || !instance) {
        if (out_result) {
            dom_struct_process_result_init(out_result);
            out_result->refusal_reason = DOM_DOMAIN_REFUSE_INTERNAL;
        }
        return -1;
    }
    inst = *instance;
    if (inst.integrity < 0) {
        inst.integrity = 0;
    }
    if (inst.integrity > d_q16_16_from_int(1)) {
        inst.integrity = d_q16_16_from_int(1);
    }
    if (inst.reinforcement < 0) {
        inst.reinforcement = 0;
    }
    if (inst.reinforcement > d_q16_16_from_int(1)) {
        inst.reinforcement = d_q16_16_from_int(1);
    }
    dom_struct_cell_coord(domain->surface.placement_cell_size, &inst.location,
                          &inst.cell_x, &inst.cell_y, &inst.cell_z);
    if (dom_struct_place_common(domain, &inst, tick, out_result) != 0) {
        return -2;
    }
    if (out_result && out_result->stress_ratio != DOM_STRUCTURE_UNKNOWN_Q16 &&
        out_result->stress_ratio > d_q16_16_from_int(1)) {
        inst.flags |= DOM_STRUCTURE_INSTANCE_UNSTABLE;
        if (out_result) {
            out_result->flags |= DOM_STRUCTURE_INSTANCE_UNSTABLE;
        }
    }
    domain->instances[domain->instance_count++] = inst;
    return 0;
}

int dom_structure_remove(dom_structure_domain* domain,
                         u32 instance_index,
                         u64 tick,
                         dom_structure_process_result* out_result)
{
    (void)tick;
    dom_struct_process_result_init(out_result);
    if (!domain || instance_index >= domain->instance_count) {
        if (out_result) {
            out_result->refusal_reason = DOM_DOMAIN_REFUSE_INTERNAL;
        }
        return -1;
    }
    if (!dom_struct_domain_is_active(domain)) {
        if (out_result) {
            out_result->refusal_reason = DOM_DOMAIN_REFUSE_DOMAIN_INACTIVE;
        }
        return -2;
    }
    domain->instances[instance_index] = domain->instances[domain->instance_count - 1u];
    domain->instance_count -= 1u;
    if (out_result) {
        out_result->ok = 1u;
    }
    return 0;
}

int dom_structure_repair(dom_structure_domain* domain,
                         u32 instance_index,
                         q16_16 amount,
                         u64 tick,
                         dom_structure_process_result* out_result)
{
    (void)tick;
    dom_struct_process_result_init(out_result);
    if (!domain || instance_index >= domain->instance_count) {
        if (out_result) {
            out_result->refusal_reason = DOM_DOMAIN_REFUSE_INTERNAL;
        }
        return -1;
    }
    if (!dom_struct_domain_is_active(domain)) {
        if (out_result) {
            out_result->refusal_reason = DOM_DOMAIN_REFUSE_DOMAIN_INACTIVE;
        }
        return -2;
    }
    {
        dom_structure_instance* inst = &domain->instances[instance_index];
        if (inst->flags & DOM_STRUCTURE_INSTANCE_COLLAPSED) {
            if (out_result) {
                out_result->refusal_reason = DOM_DOMAIN_REFUSE_POLICY;
            }
            return -3;
        }
        if (amount < 0) {
            amount = 0;
        }
        inst->integrity = d_q16_16_add(inst->integrity, amount);
        if (inst->integrity > d_q16_16_from_int(1)) {
            inst->integrity = d_q16_16_from_int(1);
        }
    }
    if (out_result) {
        out_result->ok = 1u;
    }
    return 0;
}

int dom_structure_reinforce(dom_structure_domain* domain,
                            u32 instance_index,
                            q16_16 amount,
                            u64 tick,
                            dom_structure_process_result* out_result)
{
    (void)tick;
    dom_struct_process_result_init(out_result);
    if (!domain || instance_index >= domain->instance_count) {
        if (out_result) {
            out_result->refusal_reason = DOM_DOMAIN_REFUSE_INTERNAL;
        }
        return -1;
    }
    if (!dom_struct_domain_is_active(domain)) {
        if (out_result) {
            out_result->refusal_reason = DOM_DOMAIN_REFUSE_DOMAIN_INACTIVE;
        }
        return -2;
    }
    {
        dom_structure_instance* inst = &domain->instances[instance_index];
        if (amount < 0) {
            amount = 0;
        }
        inst->reinforcement = d_q16_16_add(inst->reinforcement, amount);
        if (inst->reinforcement > d_q16_16_from_int(1)) {
            inst->reinforcement = d_q16_16_from_int(1);
        }
        inst->flags |= DOM_STRUCTURE_INSTANCE_REINFORCED;
    }
    if (out_result) {
        out_result->ok = 1u;
    }
    return 0;
}

int dom_structure_collapse(dom_structure_domain* domain,
                           u32 instance_index,
                           u64 tick,
                           dom_structure_collapse_result* out_result)
{
    dom_structure_sample sample;
    const dom_structure_spec_desc* spec;
    if (out_result) {
        memset(out_result, 0, sizeof(*out_result));
        out_result->ok = 0u;
        out_result->refusal_reason = DOM_DOMAIN_REFUSE_NONE;
        out_result->overlay_kind = DOM_STRUCTURE_OVERLAY_NONE;
        out_result->delta_phi = 0;
        out_result->debris_fill = 0;
    }
    if (!domain || instance_index >= domain->instance_count) {
        if (out_result) {
            out_result->refusal_reason = DOM_DOMAIN_REFUSE_INTERNAL;
        }
        return -1;
    }
    if (!dom_struct_domain_is_active(domain)) {
        if (out_result) {
            out_result->refusal_reason = DOM_DOMAIN_REFUSE_DOMAIN_INACTIVE;
        }
        return -2;
    }
    dom_struct_eval_fields(domain, &domain->instances[instance_index].location, tick, (dom_domain_budget*)0, &sample);
    if (sample.flags & DOM_STRUCTURE_SAMPLE_FIELDS_UNKNOWN) {
        if (out_result) {
            out_result->refusal_reason = DOM_DOMAIN_REFUSE_NO_ANALYTIC;
        }
        return -3;
    }
    if (sample.stress_ratio != DOM_STRUCTURE_UNKNOWN_Q16 &&
        sample.stress_ratio <= d_q16_16_from_int(1)) {
        if (out_result) {
            out_result->refusal_reason = DOM_DOMAIN_REFUSE_POLICY;
        }
        return -4;
    }

    domain->instances[instance_index].flags |= DOM_STRUCTURE_INSTANCE_COLLAPSED;
    domain->instances[instance_index].integrity = 0;

    if (out_result) {
        out_result->ok = 1u;
        out_result->overlay_kind = DOM_STRUCTURE_OVERLAY_DELTA_PHI;
        out_result->delta_phi = (q16_16)-d_q16_16_from_int(1);
        spec = (dom_struct_spec_index(&domain->surface, domain->instances[instance_index].structure_id) < DOM_STRUCTURE_MAX_SPECS)
               ? &domain->surface.structures[dom_struct_spec_index(&domain->surface, domain->instances[instance_index].structure_id)]
               : (const dom_structure_spec_desc*)0;
        if (spec) {
            out_result->debris_fill = spec->traits.density;
        } else {
            out_result->debris_fill = d_q16_16_from_int(1);
        }
    }
    return 0;
}
