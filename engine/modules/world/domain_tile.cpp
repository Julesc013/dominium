/*
FILE: source/domino/world/domain_tile.cpp
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / world/domain_tile
RESPONSIBILITY: Implements deterministic SDF tile generation and sampling.
ALLOWED DEPENDENCIES: `include/domino/**` and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: Engine private headers outside world.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: Fixed-point math only; deterministic hashing and loops.
*/
#include "domino/world/domain_tile.h"

#include <stdlib.h>
#include <string.h>

static q16_16 dom_domain_abs_q16_16(q16_16 v)
{
    return (v < 0) ? (q16_16)-v : v;
}

static q16_16 dom_domain_clamp_q16_16(q16_16 v, q16_16 lo, q16_16 hi)
{
    if (v < lo) {
        return lo;
    }
    if (v > hi) {
        return hi;
    }
    return v;
}

static u64 dom_domain_hash_u8(u64 h, u8 v)
{
    h ^= (u64)v;
    h *= 1099511628211ULL;
    return h;
}

static u64 dom_domain_hash_u32(u64 h, u32 v)
{
    h = dom_domain_hash_u8(h, (u8)(v & 0xFFu));
    h = dom_domain_hash_u8(h, (u8)((v >> 8u) & 0xFFu));
    h = dom_domain_hash_u8(h, (u8)((v >> 16u) & 0xFFu));
    h = dom_domain_hash_u8(h, (u8)((v >> 24u) & 0xFFu));
    return h;
}

void dom_domain_tile_desc_init(dom_domain_tile_desc* desc)
{
    if (!desc) {
        return;
    }
    memset(desc, 0, sizeof(*desc));
}

void dom_domain_tile_init(dom_domain_tile* tile)
{
    if (!tile) {
        return;
    }
    memset(tile, 0, sizeof(*tile));
}

void dom_domain_tile_free(dom_domain_tile* tile)
{
    if (!tile) {
        return;
    }
    if (tile->samples) {
        free(tile->samples);
        tile->samples = (q16_16 *)0;
    }
    tile->sample_count = 0u;
    tile->sample_dim = 0u;
    tile->tile_id = 0u;
    tile->resolution = DOM_DOMAIN_RES_REFUSED;
    memset(&tile->bounds, 0, sizeof(tile->bounds));
    tile->authoring_version = 0u;
}

u64 dom_domain_tile_id_from_coord(i32 tx, i32 ty, i32 tz, u32 resolution)
{
    u64 h = 14695981039346656037ULL;
    h = dom_domain_hash_u32(h, (u32)tx);
    h = dom_domain_hash_u32(h, (u32)ty);
    h = dom_domain_hash_u32(h, (u32)tz);
    h = dom_domain_hash_u32(h, resolution);
    return h;
}

static q16_16 dom_domain_step_from_extent(q16_16 extent, u32 sample_dim)
{
    if (sample_dim <= 1u) {
        return 0;
    }
    return (q16_16)((i64)extent / (i64)(sample_dim - 1u));
}

int dom_domain_tile_build(dom_domain_tile* tile,
                          const dom_domain_tile_desc* desc,
                          const dom_domain_sdf_source* source)
{
    u32 i;
    u32 j;
    u32 k;
    u32 dim;
    q16_16 step_x;
    q16_16 step_y;
    q16_16 step_z;
    if (!tile || !desc || !source || !source->eval) {
        return -1;
    }

    dim = desc->sample_dim;
    if (dim == 0u) {
        return -1;
    }

    dom_domain_tile_free(tile);
    dom_domain_tile_init(tile);

    tile->tile_id = desc->tile_id;
    tile->resolution = desc->resolution;
    tile->sample_dim = dim;
    tile->bounds = desc->bounds;
    tile->authoring_version = desc->authoring_version;

    tile->sample_count = dim * dim * dim;
    tile->samples = (q16_16 *)malloc(sizeof(q16_16) * tile->sample_count);
    if (!tile->samples) {
        dom_domain_tile_free(tile);
        return -1;
    }

    step_x = dom_domain_step_from_extent((q16_16)(tile->bounds.max.x - tile->bounds.min.x), dim);
    step_y = dom_domain_step_from_extent((q16_16)(tile->bounds.max.y - tile->bounds.min.y), dim);
    step_z = dom_domain_step_from_extent((q16_16)(tile->bounds.max.z - tile->bounds.min.z), dim);

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
                u32 idx = (k * dim * dim) + (j * dim) + i;
                p.x = px;
                p.y = py;
                p.z = pz;
                tile->samples[idx] = source->eval(source->ctx, &p);
            }
        }
    }

    return 0;
}

static u32 dom_domain_sample_index_from_coord(q16_16 coord,
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

q16_16 dom_domain_tile_sample_nearest(const dom_domain_tile* tile,
                                      const dom_domain_point* point,
                                      dom_domain_point* out_sample_point)
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
    q16_16 sx;
    q16_16 sy;
    q16_16 sz;
    if (!tile || !tile->samples || !point || tile->sample_dim == 0u) {
        if (out_sample_point) {
            memset(out_sample_point, 0, sizeof(*out_sample_point));
        }
        return 0;
    }

    px = dom_domain_clamp_q16_16(point->x, tile->bounds.min.x, tile->bounds.max.x);
    py = dom_domain_clamp_q16_16(point->y, tile->bounds.min.y, tile->bounds.max.y);
    pz = dom_domain_clamp_q16_16(point->z, tile->bounds.min.z, tile->bounds.max.z);

    step_x = dom_domain_step_from_extent((q16_16)(tile->bounds.max.x - tile->bounds.min.x), tile->sample_dim);
    step_y = dom_domain_step_from_extent((q16_16)(tile->bounds.max.y - tile->bounds.min.y), tile->sample_dim);
    step_z = dom_domain_step_from_extent((q16_16)(tile->bounds.max.z - tile->bounds.min.z), tile->sample_dim);

    ix = dom_domain_sample_index_from_coord(px, tile->bounds.min.x, tile->bounds.max.x, step_x, tile->sample_dim);
    iy = dom_domain_sample_index_from_coord(py, tile->bounds.min.y, tile->bounds.max.y, step_y, tile->sample_dim);
    iz = dom_domain_sample_index_from_coord(pz, tile->bounds.min.z, tile->bounds.max.z, step_z, tile->sample_dim);

    sx = (ix == tile->sample_dim - 1u)
        ? tile->bounds.max.x
        : (q16_16)(tile->bounds.min.x + (q16_16)((i64)step_x * (i64)ix));
    sy = (iy == tile->sample_dim - 1u)
        ? tile->bounds.max.y
        : (q16_16)(tile->bounds.min.y + (q16_16)((i64)step_y * (i64)iy));
    sz = (iz == tile->sample_dim - 1u)
        ? tile->bounds.max.z
        : (q16_16)(tile->bounds.min.z + (q16_16)((i64)step_z * (i64)iz));

    if (out_sample_point) {
        out_sample_point->x = sx;
        out_sample_point->y = sy;
        out_sample_point->z = sz;
    }

    return tile->samples[(iz * tile->sample_dim * tile->sample_dim) + (iy * tile->sample_dim) + ix];
}

d_bool dom_domain_aabb_contains(const dom_domain_aabb* aabb, const dom_domain_point* point)
{
    if (!aabb || !point) {
        return D_FALSE;
    }
    if (point->x < aabb->min.x || point->x > aabb->max.x) {
        return D_FALSE;
    }
    if (point->y < aabb->min.y || point->y > aabb->max.y) {
        return D_FALSE;
    }
    if (point->z < aabb->min.z || point->z > aabb->max.z) {
        return D_FALSE;
    }
    return D_TRUE;
}

q16_16 dom_domain_aabb_distance_l1(const dom_domain_aabb* aabb, const dom_domain_point* point)
{
    q16_16 dx;
    q16_16 dy;
    q16_16 dz;
    i64 sum;
    if (!aabb || !point) {
        return 0;
    }

    dx = 0;
    if (point->x < aabb->min.x) {
        dx = (q16_16)(aabb->min.x - point->x);
    } else if (point->x > aabb->max.x) {
        dx = (q16_16)(point->x - aabb->max.x);
    }

    dy = 0;
    if (point->y < aabb->min.y) {
        dy = (q16_16)(aabb->min.y - point->y);
    } else if (point->y > aabb->max.y) {
        dy = (q16_16)(point->y - aabb->max.y);
    }

    dz = 0;
    if (point->z < aabb->min.z) {
        dz = (q16_16)(aabb->min.z - point->z);
    } else if (point->z > aabb->max.z) {
        dz = (q16_16)(point->z - aabb->max.z);
    }

    sum = (i64)dom_domain_abs_q16_16(dx) + (i64)dom_domain_abs_q16_16(dy) + (i64)dom_domain_abs_q16_16(dz);
    if (sum > 2147483647LL) {
        return (q16_16)2147483647;
    }
    return (q16_16)sum;
}
