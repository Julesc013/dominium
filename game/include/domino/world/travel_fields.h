/*
FILE: include/domino/world/travel_fields.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / world/travel_fields
RESPONSIBILITY: Deterministic travel cost and pathfinding over terrain, weather, and structures.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 headers as needed.
FORBIDDEN DEPENDENCIES: Engine private headers outside `include/domino/**`.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: Fixed-point only; deterministic ordering and math.
VERSIONING / ABI / DATA FORMAT NOTES: Versioned by TRAVEL0 specs.
EXTENSION POINTS: Extend via public headers and relevant `docs/architecture/**`.
*/
#ifndef DOMINO_WORLD_TRAVEL_FIELDS_H
#define DOMINO_WORLD_TRAVEL_FIELDS_H

#include "domino/core/types.h"
#include "domino/core/fixed.h"
#include "domino/world/domain_query.h"
#include "domino/world/terrain_surface.h"
#include "domino/world/weather_fields.h"
#include "domino/world/structure_fields.h"

#ifdef __cplusplus
extern "C" {
#endif

#define DOM_TRAVEL_MAX_MODES 8u
#define DOM_TRAVEL_MAX_ROADS 16u
#define DOM_TRAVEL_MAX_BRIDGES 16u
#define DOM_TRAVEL_MAX_OBSTACLES 16u
#define DOM_TRAVEL_MAX_CAPSULES 128u
#define DOM_TRAVEL_HIST_BINS 4u
#define DOM_TRAVEL_MAX_PATH_POINTS 64u
#define DOM_TRAVEL_MAX_PATH_CACHE 8u
#define DOM_TRAVEL_MAX_NODES 512u

#define DOM_TRAVEL_UNKNOWN_Q16 ((q16_16)0x80000000)

enum dom_travel_mode_kind {
    DOM_TRAVEL_MODE_WALK = 0u,
    DOM_TRAVEL_MODE_SWIM = 1u,
    DOM_TRAVEL_MODE_VEHICLE = 2u
};

enum dom_travel_sample_flags {
    DOM_TRAVEL_SAMPLE_FIELDS_UNKNOWN = 1u << 0u,
    DOM_TRAVEL_SAMPLE_OBSTACLE = 1u << 1u,
    DOM_TRAVEL_SAMPLE_ON_ROAD = 1u << 2u,
    DOM_TRAVEL_SAMPLE_ON_BRIDGE = 1u << 3u,
    DOM_TRAVEL_SAMPLE_COLLAPSED = 1u << 4u,
    DOM_TRAVEL_SAMPLE_MODE_UNKNOWN = 1u << 5u,
    DOM_TRAVEL_SAMPLE_VEHICLE_MISSING = 1u << 6u
};

enum dom_travel_path_flags {
    DOM_TRAVEL_PATH_FOUND = 1u << 0u,
    DOM_TRAVEL_PATH_BUDGET_EXHAUSTED = 1u << 1u,
    DOM_TRAVEL_PATH_BLOCKED = 1u << 2u,
    DOM_TRAVEL_PATH_INVALID_MODE = 1u << 3u
};

typedef struct dom_travel_mode_desc {
    u32 mode_id;
    u32 mode_kind; /* dom_travel_mode_kind */
    q16_16 slope_max;
    q16_16 cost_scale;
    q16_16 cost_add;
    q16_16 mass;
    q16_16 inertia;
    q16_16 damage_threshold;
    u32 vehicle_structure_id;
    u32 maturity_tag;
} dom_travel_mode_desc;

typedef struct dom_travel_surface_desc {
    dom_domain_id domain_id;
    u64 world_seed;
    q16_16 meters_per_unit;
    dom_terrain_shape_desc shape;
    dom_terrain_surface_desc terrain_desc;
    dom_weather_surface_desc weather_desc;
    dom_structure_surface_desc structure_desc;
    u32 mode_count;
    dom_travel_mode_desc modes[DOM_TRAVEL_MAX_MODES];
    u32 road_count;
    u32 road_structure_ids[DOM_TRAVEL_MAX_ROADS];
    u32 bridge_count;
    u32 bridge_structure_ids[DOM_TRAVEL_MAX_BRIDGES];
    u32 obstacle_count;
    u32 obstacle_structure_ids[DOM_TRAVEL_MAX_OBSTACLES];
    q16_16 road_cost_scale;
    q16_16 bridge_cost_scale;
    q16_16 weather_precip_scale;
    q16_16 weather_wetness_scale;
    q16_16 weather_temp_scale;
    q16_16 comfort_temp_min;
    q16_16 comfort_temp_max;
    q16_16 weather_wind_scale;
    q16_16 path_step;
    q16_16 path_coarse_step;
    q16_16 path_max_distance;
    u32 path_max_nodes;
    u32 path_max_points;
    u32 terrain_cache_capacity;
    u32 weather_cache_capacity;
    u32 structure_cache_capacity;
    u32 cache_capacity;
} dom_travel_surface_desc;

typedef struct dom_travel_sample {
    q16_16 travel_cost;
    q16_16 weather_modifier;
    q16_16 mode_modifier;
    q16_16 total_cost;
    q16_16 obstacle;
    q16_16 slope;
    q16_16 roughness;
    u32 material_primary;
    u32 structure_id;
    u32 mode_id;
    u32 flags; /* dom_travel_sample_flags */
    dom_domain_query_meta meta;
} dom_travel_sample;

typedef struct dom_travel_path {
    u32 point_count;
    dom_domain_point points[DOM_TRAVEL_MAX_PATH_POINTS];
    q16_16 total_cost;
    u32 visited_nodes;
    u32 flags; /* dom_travel_path_flags */
    dom_domain_query_meta meta;
} dom_travel_path;

typedef struct dom_travel_path_cache_entry {
    d_bool valid;
    dom_domain_point origin;
    dom_domain_point target;
    u32 mode_id;
    u64 tick;
    dom_travel_path path;
    u64 last_used;
    u64 insert_order;
} dom_travel_path_cache_entry;

typedef struct dom_travel_path_cache {
    dom_travel_path_cache_entry* entries;
    u32 capacity;
    u32 count;
    u64 use_counter;
    u64 next_insert_order;
} dom_travel_path_cache;

typedef struct dom_travel_macro_capsule {
    u64 capsule_id;
    u64 tile_id;
    u64 tick;
    dom_domain_aabb bounds;
    q16_16 road_length;
    q16_16 travel_cost_avg;
    q16_16 travel_cost_hist[DOM_TRAVEL_HIST_BINS];
} dom_travel_macro_capsule;

typedef struct dom_travel_domain {
    dom_terrain_domain terrain_domain;
    dom_weather_domain weather_domain;
    dom_structure_domain structure_domain;
    dom_domain_policy policy;
    u32 existence_state;
    u32 archival_state;
    u32 authoring_version;
    dom_travel_surface_desc surface;
    dom_travel_path_cache path_cache;
    dom_travel_macro_capsule capsules[DOM_TRAVEL_MAX_CAPSULES];
    u32 capsule_count;
} dom_travel_domain;

void dom_travel_surface_desc_init(dom_travel_surface_desc* desc);
void dom_travel_domain_init(dom_travel_domain* domain,
                            const dom_travel_surface_desc* desc);
void dom_travel_domain_free(dom_travel_domain* domain);
void dom_travel_domain_set_state(dom_travel_domain* domain,
                                 u32 existence_state,
                                 u32 archival_state);
void dom_travel_domain_set_policy(dom_travel_domain* domain,
                                  const dom_domain_policy* policy);

int dom_travel_sample_query(const dom_travel_domain* domain,
                            const dom_domain_point* point,
                            u64 tick,
                            u32 mode_id,
                            dom_domain_budget* budget,
                            dom_travel_sample* out_sample);

int dom_travel_pathfind(dom_travel_domain* domain,
                        const dom_domain_point* origin,
                        const dom_domain_point* target,
                        u64 tick,
                        u32 mode_id,
                        dom_domain_budget* budget,
                        dom_travel_path* out_path);

int dom_travel_domain_collapse_tile(dom_travel_domain* domain,
                                    const dom_domain_tile_desc* desc,
                                    u64 tick);
int dom_travel_domain_expand_tile(dom_travel_domain* domain, u64 tile_id);

u32 dom_travel_domain_capsule_count(const dom_travel_domain* domain);
const dom_travel_macro_capsule* dom_travel_domain_capsule_at(const dom_travel_domain* domain,
                                                             u32 index);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINO_WORLD_TRAVEL_FIELDS_H */
