/*
FILE: include/domino/world/terrain_surface.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / world/terrain_surface
RESPONSIBILITY: Deterministic terrain surface provider, sampling, and coordinate helpers.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 headers as needed.
FORBIDDEN DEPENDENCIES: Engine private headers outside `include/domino/**`.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: Fixed-point only; deterministic ordering and math.
VERSIONING / ABI / DATA FORMAT NOTES: Versioned by TERRAIN0/TERRAIN1 specs.
EXTENSION POINTS: Extend via public headers and relevant `docs/architecture/**`.
*/
#ifndef DOMINO_WORLD_TERRAIN_SURFACE_H
#define DOMINO_WORLD_TERRAIN_SURFACE_H

#include "domino/core/types.h"
#include "domino/core/fixed.h"
#include "domino/world/domain_query.h"
#include "domino/world/domain_cache.h"

#ifdef __cplusplus
extern "C" {
#endif

enum dom_terrain_shape_kind {
    DOM_TERRAIN_SHAPE_SPHERE = 0,
    DOM_TERRAIN_SHAPE_OBLATE = 1,
    DOM_TERRAIN_SHAPE_SLAB = 2
};

typedef struct dom_terrain_shape_desc {
    u32   kind;               /* dom_terrain_shape_kind */
    q16_16 radius_equatorial; /* sphere/oblate */
    q16_16 radius_polar;      /* oblate; defaults to radius_equatorial */
    q16_16 slab_half_extent;  /* slab half-extent in X/Y */
    q16_16 slab_half_thickness; /* slab half-thickness in Z */
} dom_terrain_shape_desc;

typedef struct dom_terrain_noise_desc {
    u64   seed;
    q16_16 amplitude;     /* displacement magnitude */
    q16_16 cell_size;     /* local units per noise cell (>=1) */
} dom_terrain_noise_desc;

typedef struct dom_terrain_surface_desc {
    dom_domain_id domain_id;
    u64   world_seed;
    q16_16 meters_per_unit; /* global meters per local unit */
    dom_terrain_shape_desc shape;
    dom_terrain_noise_desc noise;
    u32   material_primary;
    q16_16 roughness_base;
    q16_16 travel_cost_base;
    q16_16 travel_cost_slope_scale;
    q16_16 travel_cost_roughness_scale;
    q16_16 walkable_max_slope;
} dom_terrain_surface_desc;

typedef struct dom_terrain_surface {
    dom_domain_id domain_id;
    u64   world_seed;
    q16_16 meters_per_unit;
    dom_terrain_shape_desc shape;
    dom_terrain_noise_desc noise;
    u32   material_primary;
    q16_16 roughness_base;
    q16_16 travel_cost_base;
    q16_16 travel_cost_slope_scale;
    q16_16 travel_cost_roughness_scale;
    q16_16 walkable_max_slope;
    dom_domain_sdf_source sdf_source;
} dom_terrain_surface;

#define DOM_TERRAIN_UNKNOWN_Q16 ((q16_16)0x80000000)

enum dom_terrain_sample_flags {
    DOM_TERRAIN_SAMPLE_PHI_UNKNOWN = 1u << 0u,
    DOM_TERRAIN_SAMPLE_FIELDS_UNKNOWN = 1u << 1u,
    DOM_TERRAIN_SAMPLE_COLLISION_UNKNOWN = 1u << 2u
};

typedef struct dom_terrain_sample {
    q16_16 phi;
    u32 material_primary;
    q16_16 roughness;
    q16_16 slope;
    q16_16 travel_cost;
    u32 flags; /* dom_terrain_sample_flags */
    dom_domain_query_meta meta;
} dom_terrain_sample;

typedef struct dom_terrain_chunk_coord {
    i32 tx;
    i32 ty;
    i32 tz;
    dom_domain_point origin;
} dom_terrain_chunk_coord;

typedef struct dom_terrain_global_point {
    q48_16 x;
    q48_16 y;
    q48_16 z;
} dom_terrain_global_point;

typedef struct dom_terrain_latlon {
    q16_16 latitude;  /* turns */
    q16_16 longitude; /* turns */
    q16_16 altitude;  /* local units (Q16.16) */
    u32 valid;
} dom_terrain_latlon;

typedef struct dom_terrain_macro_capsule {
    u64 capsule_id;
    u64 tile_id;
    dom_domain_aabb bounds;
    q16_16 phi_min;
    q16_16 phi_max;
    q16_16 roughness_min;
    q16_16 roughness_max;
    u32 material_primary;
} dom_terrain_macro_capsule;

#define DOM_TERRAIN_MAX_CAPSULES 128u

typedef struct dom_terrain_domain {
    dom_terrain_surface surface;
    dom_domain_volume volume;
    dom_domain_cache cache;
    dom_terrain_macro_capsule capsules[DOM_TERRAIN_MAX_CAPSULES];
    u32 capsule_count;
} dom_terrain_domain;

void dom_terrain_surface_desc_init(dom_terrain_surface_desc* desc);
void dom_terrain_surface_init(dom_terrain_surface* surface, const dom_terrain_surface_desc* desc);
const dom_domain_sdf_source* dom_terrain_surface_sdf(const dom_terrain_surface* surface);

void dom_terrain_domain_init(dom_terrain_domain* domain,
                             const dom_terrain_surface_desc* desc,
                             u32 cache_capacity);
void dom_terrain_domain_free(dom_terrain_domain* domain);
void dom_terrain_domain_set_state(dom_terrain_domain* domain,
                                  u32 existence_state,
                                  u32 archival_state);
void dom_terrain_domain_set_policy(dom_terrain_domain* domain,
                                   const dom_domain_policy* policy);

int dom_terrain_sample_query(const dom_terrain_domain* domain,
                             const dom_domain_point* point,
                             dom_domain_budget* budget,
                             dom_terrain_sample* out_sample);

d_bool dom_terrain_collision(const dom_terrain_domain* domain,
                             const dom_domain_point* point,
                             dom_domain_budget* budget,
                             dom_domain_query_meta* out_meta);

d_bool dom_terrain_walkable(const dom_terrain_domain* domain,
                            const dom_domain_point* point,
                            dom_domain_budget* budget,
                            dom_domain_query_meta* out_meta);

int dom_terrain_gradient(const dom_terrain_surface* surface,
                         const dom_domain_point* point,
                         dom_domain_point* out_grad);

void dom_terrain_chunk_coord_from_point(q16_16 tile_size,
                                        const dom_domain_point* point,
                                        dom_terrain_chunk_coord* out_coord);
void dom_terrain_point_to_chunk_local(const dom_terrain_chunk_coord* coord,
                                      const dom_domain_point* point,
                                      dom_domain_point* out_local);
void dom_terrain_point_to_player_local(const dom_domain_point* point,
                                       const dom_domain_point* player_origin,
                                       dom_domain_point* out_local);
void dom_terrain_global_to_local(const dom_terrain_surface* surface,
                                 const dom_terrain_global_point* global_point,
                                 dom_domain_point* out_local);
void dom_terrain_local_to_global(const dom_terrain_surface* surface,
                                 const dom_domain_point* local_point,
                                 dom_terrain_global_point* out_global);

dom_domain_point dom_terrain_latlon_to_local(const dom_terrain_shape_desc* shape,
                                             q16_16 latitude_turns,
                                             q16_16 longitude_turns,
                                             q16_16 altitude);
dom_terrain_latlon dom_terrain_local_to_latlon(const dom_terrain_shape_desc* shape,
                                               const dom_domain_point* point);

int dom_terrain_domain_collapse_tile(dom_terrain_domain* domain,
                                     const dom_domain_tile_desc* desc);
int dom_terrain_domain_expand_tile(dom_terrain_domain* domain, u64 tile_id);
u32 dom_terrain_domain_capsule_count(const dom_terrain_domain* domain);
const dom_terrain_macro_capsule* dom_terrain_domain_capsule_at(const dom_terrain_domain* domain,
                                                               u32 index);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINO_WORLD_TERRAIN_SURFACE_H */
