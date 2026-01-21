/*
FILE: include/domino/world/domain_tile.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / world/domain_tile
RESPONSIBILITY: Defines domain SDF tile structures and sampling contracts.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: Fixed-point only; deterministic ordering and hashing.
VERSIONING / ABI / DATA FORMAT NOTES: Versioned by DOMAIN0/DOMAIN1 specs.
EXTENSION POINTS: Extend via public headers and relevant `docs/arch/**`.
*/
#ifndef DOMINO_WORLD_DOMAIN_TILE_H
#define DOMINO_WORLD_DOMAIN_TILE_H

#include "domino/core/types.h"
#include "domino/core/fixed.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef u64 dom_domain_id;

typedef struct dom_domain_point {
    q16_16 x;
    q16_16 y;
    q16_16 z;
} dom_domain_point;

typedef struct dom_domain_aabb {
    dom_domain_point min;
    dom_domain_point max;
} dom_domain_aabb;

typedef enum dom_domain_resolution {
    DOM_DOMAIN_RES_FULL = 0,
    DOM_DOMAIN_RES_MEDIUM = 1,
    DOM_DOMAIN_RES_COARSE = 2,
    DOM_DOMAIN_RES_ANALYTIC = 3,
    DOM_DOMAIN_RES_REFUSED = 4
} dom_domain_resolution;

typedef q16_16 (*dom_domain_sdf_eval_fn)(const void* ctx, const dom_domain_point* point);

typedef struct dom_domain_sdf_source {
    dom_domain_sdf_eval_fn eval;
    dom_domain_sdf_eval_fn analytic_eval;
    const void* ctx;
    dom_domain_aabb bounds;
    u32 has_analytic;
} dom_domain_sdf_source;

typedef struct dom_domain_tile_desc {
    u64             tile_id;
    u32             resolution; /* dom_domain_resolution */
    u32             sample_dim;
    dom_domain_aabb bounds;
    u32             authoring_version;
} dom_domain_tile_desc;

typedef struct dom_domain_tile {
    u64             tile_id;
    u32             resolution; /* dom_domain_resolution */
    u32             sample_dim;
    dom_domain_aabb bounds;
    q16_16         *samples;
    u32             sample_count;
    u32             authoring_version;
} dom_domain_tile;

void  dom_domain_tile_desc_init(dom_domain_tile_desc* desc);
void  dom_domain_tile_init(dom_domain_tile* tile);
void  dom_domain_tile_free(dom_domain_tile* tile);
u64   dom_domain_tile_id_from_coord(i32 tx, i32 ty, i32 tz, u32 resolution);
int   dom_domain_tile_build(dom_domain_tile* tile,
                            const dom_domain_tile_desc* desc,
                            const dom_domain_sdf_source* source);
q16_16 dom_domain_tile_sample_nearest(const dom_domain_tile* tile,
                                      const dom_domain_point* point,
                                      dom_domain_point* out_sample_point);

d_bool dom_domain_aabb_contains(const dom_domain_aabb* aabb, const dom_domain_point* point);
q16_16 dom_domain_aabb_distance_l1(const dom_domain_aabb* aabb, const dom_domain_point* point);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINO_WORLD_DOMAIN_TILE_H */
