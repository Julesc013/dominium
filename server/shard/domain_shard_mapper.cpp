/*
FILE: server/shard/domain_shard_mapper.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Server / shard
RESPONSIBILITY: Deterministic domain-driven shard mapping and partitioning.
*/
#include "domain_shard_mapper.h"

#include <string.h>

#ifdef __cplusplus
extern "C" {
#endif

static u64 dom_domain_shard_hash_mix(u64 hash, u64 value)
{
    u32 i;
    for (i = 0u; i < 8u; ++i) {
        hash ^= (u64)((value >> (i * 8u)) & 0xFFu);
        hash *= 1099511628211ULL;
    }
    return hash;
}

static dom_shard_id dom_domain_shard_pick(u64 seed,
                                          dom_domain_id domain_id,
                                          u64 tile_id,
                                          u32 shard_count)
{
    u64 hash = 1469598103934665603ULL;
    if (shard_count == 0u) {
        return 0u;
    }
    hash = dom_domain_shard_hash_mix(hash, seed);
    hash = dom_domain_shard_hash_mix(hash, domain_id);
    hash = dom_domain_shard_hash_mix(hash, tile_id);
    return (dom_shard_id)((hash % (u64)shard_count) + 1u);
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

static q16_16 dom_domain_mid_q16_16(q16_16 a, q16_16 b)
{
    i64 diff = (i64)b - (i64)a;
    i64 half = diff / 2;
    i64 mid = (i64)a + half;
    if (mid > 2147483647LL) {
        return (q16_16)2147483647;
    }
    if (mid < -2147483647LL - 1LL) {
        return (q16_16)(-2147483647LL - 1LL);
    }
    return (q16_16)mid;
}

static int dom_domain_bounds_valid(const dom_domain_aabb* bounds)
{
    if (!bounds) {
        return 0;
    }
    if (bounds->min.x > bounds->max.x) return 0;
    if (bounds->min.y > bounds->max.y) return 0;
    if (bounds->min.z > bounds->max.z) return 0;
    return 1;
}

static d_bool dom_domain_state_allows_activity(const dom_domain_volume* volume)
{
    if (!volume) {
        return D_FALSE;
    }
    if (volume->existence_state == DOM_DOMAIN_EXISTENCE_NONEXISTENT ||
        volume->existence_state == DOM_DOMAIN_EXISTENCE_DECLARED ||
        volume->existence_state == DOM_DOMAIN_EXISTENCE_ARCHIVED) {
        return D_FALSE;
    }
    if (volume->archival_state != DOM_DOMAIN_ARCHIVAL_LIVE) {
        return D_FALSE;
    }
    return D_TRUE;
}

static d_bool dom_domain_state_has_spatial(const dom_domain_volume* volume)
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

void dom_domain_partition_params_init(dom_domain_partition_params* params)
{
    if (!params) {
        return;
    }
    memset(params, 0, sizeof(*params));
    params->shard_count = 1u;
    params->allow_split = 1u;
    params->resolution = DOM_DOMAIN_RES_COARSE;
    params->max_tiles_per_domain = 1024u;
    params->budget_units = 0u;
    params->global_seed = 0u;
}

d_bool dom_domain_shard_streaming_allowed(const dom_domain_shard_input* input)
{
    if (!input || !input->volume) {
        return D_FALSE;
    }
    if ((input->flags & DOM_DOMAIN_SHARD_FLAG_ALLOW_STREAMING) == 0u) {
        return D_FALSE;
    }
    return dom_domain_state_allows_activity(input->volume);
}

static d_bool dom_domain_shard_simulation_allowed(const dom_domain_shard_input* input)
{
    if (!input || !input->volume) {
        return D_FALSE;
    }
    if ((input->flags & DOM_DOMAIN_SHARD_FLAG_ALLOW_SIMULATION) == 0u) {
        return D_FALSE;
    }
    return dom_domain_state_allows_activity(input->volume);
}

int dom_domain_shard_map(const dom_domain_shard_input* inputs,
                         u32 input_count,
                         const dom_domain_partition_params* params,
                         dom_shard_domain_index* out_index)
{
    u32 i;
    if (!inputs || !params || !out_index) {
        return -1;
    }
    if (params->shard_count == 0u) {
        return -2;
    }

    dom_shard_domain_index_clear(out_index);

    for (i = 0u; i < input_count; ++i) {
        const dom_domain_shard_input* input = &inputs[i];
        const dom_domain_volume* volume = input->volume;
        const dom_domain_sdf_source* source;
        dom_domain_budget budget;
        dom_domain_budget* budget_ptr = (dom_domain_budget *)0;
        u32 allow_split;
        dom_shard_id domain_shard;
        dom_domain_aabb bounds;
        q16_16 tile_size;
        i32 tx_max;
        i32 ty_max;
        i32 tz_max;
        u32 resolution;
        u32 tile_count;
        d_bool stream_allowed;
        d_bool sim_allowed;
        int budget_exhausted;

        if (!volume) {
            out_index->uncertain = 1u;
            continue;
        }
        source = volume->source;
        if (!source || !dom_domain_bounds_valid(&source->bounds)) {
            out_index->uncertain = 1u;
            continue;
        }
        if (!dom_domain_state_has_spatial(volume)) {
            continue;
        }

        tile_size = volume->policy.tile_size;
        if (tile_size <= 0) {
            out_index->uncertain = 1u;
            continue;
        }

        bounds = source->bounds;
        tx_max = dom_domain_floor_div_q16_16((i64)bounds.max.x - (i64)bounds.min.x, tile_size);
        ty_max = dom_domain_floor_div_q16_16((i64)bounds.max.y - (i64)bounds.min.y, tile_size);
        tz_max = dom_domain_floor_div_q16_16((i64)bounds.max.z - (i64)bounds.min.z, tile_size);

        if (tx_max < 0 || ty_max < 0 || tz_max < 0) {
            out_index->uncertain = 1u;
            continue;
        }

        resolution = params->resolution;
        if (resolution >= DOM_DOMAIN_RES_REFUSED) {
            resolution = DOM_DOMAIN_RES_COARSE;
        }

        if (params->budget_units > 0u) {
            dom_domain_budget_init(&budget, params->budget_units);
            budget_ptr = &budget;
        }

        allow_split = (params->allow_split != 0u &&
                       (input->flags & DOM_DOMAIN_SHARD_FLAG_ALLOW_SPLIT) != 0u);
        domain_shard = dom_domain_shard_pick(params->global_seed, input->domain_id, 0u, params->shard_count);
        stream_allowed = dom_domain_shard_streaming_allowed(input);
        sim_allowed = dom_domain_shard_simulation_allowed(input);
        budget_exhausted = 0;

        tile_count = 0u;
        for (i32 tz = 0; tz <= tz_max && !budget_exhausted; ++tz) {
            for (i32 ty = 0; ty <= ty_max && !budget_exhausted; ++ty) {
                for (i32 tx = 0; tx <= tx_max; ++tx) {
                    dom_domain_aabb tile_bounds;
                    dom_domain_point center;
                    dom_domain_query_meta meta;
                    d_bool inside;
                    dom_shard_domain_assignment assignment;
                    u64 tile_id;
                    dom_shard_id shard_id;

                    if (params->max_tiles_per_domain > 0u &&
                        tile_count >= params->max_tiles_per_domain) {
                        out_index->uncertain = 1u;
                        budget_exhausted = 1;
                        break;
                    }
                    tile_count += 1u;

                    dom_domain_make_tile_bounds(&bounds, tile_size, tx, ty, tz, &tile_bounds);
                    center.x = dom_domain_mid_q16_16(tile_bounds.min.x, tile_bounds.max.x);
                    center.y = dom_domain_mid_q16_16(tile_bounds.min.y, tile_bounds.max.y);
                    center.z = dom_domain_mid_q16_16(tile_bounds.min.z, tile_bounds.max.z);

                    inside = dom_domain_contains(volume, &center, budget_ptr, &meta);
                    if (meta.status != DOM_DOMAIN_QUERY_OK) {
                        out_index->uncertain = 1u;
                        if (meta.refusal_reason == DOM_DOMAIN_REFUSE_BUDGET) {
                            budget_exhausted = 1;
                            break;
                        }
                        continue;
                    }
                    if (meta.confidence != DOM_DOMAIN_CONFIDENCE_EXACT) {
                        out_index->uncertain = 1u;
                        continue;
                    }
                    if (!inside) {
                        continue;
                    }

                    tile_id = dom_domain_tile_id_from_coord(tx, ty, tz, resolution);
                    shard_id = allow_split
                        ? dom_domain_shard_pick(params->global_seed, input->domain_id, tile_id, params->shard_count)
                        : domain_shard;

                    memset(&assignment, 0, sizeof(assignment));
                    assignment.domain_id = input->domain_id;
                    assignment.tile_id = tile_id;
                    assignment.resolution = resolution;
                    assignment.bounds = tile_bounds;
                    assignment.shard_id = shard_id;
                    assignment.flags = 0u;
                    if (stream_allowed) {
                        assignment.flags |= DOM_SHARD_DOMAIN_FLAG_STREAMING_ALLOWED;
                    }
                    if (sim_allowed) {
                        assignment.flags |= DOM_SHARD_DOMAIN_FLAG_SIMULATION_ALLOWED;
                    }
                    if (!allow_split) {
                        assignment.flags |= DOM_SHARD_DOMAIN_FLAG_WHOLE_DOMAIN;
                    }

                    if (dom_shard_domain_index_add(out_index, &assignment) != 0) {
                        out_index->overflow = 1u;
                        return -3;
                    }
                }
            }
        }
    }

    return 0;
}

#ifdef __cplusplus
} /* extern "C" */
#endif
