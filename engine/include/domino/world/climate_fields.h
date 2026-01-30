/*
FILE: include/domino/world/climate_fields.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / world/climate_fields
RESPONSIBILITY: Deterministic climate envelope sampling and biome classification.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 headers as needed.
FORBIDDEN DEPENDENCIES: Engine private headers outside `include/domino/**`.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: Fixed-point only; deterministic ordering and math.
VERSIONING / ABI / DATA FORMAT NOTES: Versioned by CLIMATE0 specs.
EXTENSION POINTS: Extend via public headers and relevant `docs/architecture/**`.
*/
#ifndef DOMINO_WORLD_CLIMATE_FIELDS_H
#define DOMINO_WORLD_CLIMATE_FIELDS_H

#include "domino/core/types.h"
#include "domino/core/fixed.h"
#include "domino/world/domain_query.h"
#include "domino/world/terrain_surface.h"
#include "domino/world/geology_fields.h"

#ifdef __cplusplus
extern "C" {
#endif

#define DOM_CLIMATE_HIST_BINS 4u
#define DOM_CLIMATE_MAX_CAPSULES 128u
#define DOM_CLIMATE_MAX_BIOMES 16u

#define DOM_CLIMATE_UNKNOWN_Q16 ((q16_16)0x80000000)

enum dom_climate_wind_dir {
    DOM_CLIMATE_WIND_UNKNOWN = 0u,
    DOM_CLIMATE_WIND_NORTH = 1u,
    DOM_CLIMATE_WIND_NORTHEAST = 2u,
    DOM_CLIMATE_WIND_EAST = 3u,
    DOM_CLIMATE_WIND_SOUTHEAST = 4u,
    DOM_CLIMATE_WIND_SOUTH = 5u,
    DOM_CLIMATE_WIND_SOUTHWEST = 6u,
    DOM_CLIMATE_WIND_WEST = 7u,
    DOM_CLIMATE_WIND_NORTHWEST = 8u
};

typedef struct dom_climate_noise_desc {
    u64   seed;
    q16_16 amplitude;
    q16_16 cell_size;
} dom_climate_noise_desc;

enum dom_climate_anchor_mask {
    DOM_CLIMATE_ANCHOR_TEMPERATURE_MEAN  = 1u << 0u,
    DOM_CLIMATE_ANCHOR_TEMPERATURE_RANGE = 1u << 1u,
    DOM_CLIMATE_ANCHOR_PRECIP_MEAN       = 1u << 2u,
    DOM_CLIMATE_ANCHOR_PRECIP_RANGE      = 1u << 3u,
    DOM_CLIMATE_ANCHOR_SEASONALITY       = 1u << 4u,
    DOM_CLIMATE_ANCHOR_WIND_PREVAILING   = 1u << 5u
};

typedef struct dom_climate_anchor_desc {
    u32 mask;
    q16_16 temperature_mean;
    q16_16 temperature_range;
    q16_16 precipitation_mean;
    q16_16 precipitation_range;
    q16_16 seasonality;
    u32 wind_prevailing;
} dom_climate_anchor_desc;

typedef struct dom_climate_surface_desc {
    dom_domain_id domain_id;
    u64 world_seed;
    q16_16 meters_per_unit;
    dom_terrain_shape_desc shape;
    dom_climate_noise_desc noise;
    q16_16 temp_equator;
    q16_16 temp_pole;
    q16_16 temp_altitude_scale;
    q16_16 temp_range_base;
    q16_16 temp_range_lat_scale;
    q16_16 precip_equator;
    q16_16 precip_pole;
    q16_16 precip_altitude_scale;
    q16_16 precip_range_base;
    q16_16 precip_range_lat_scale;
    q16_16 seasonality_base;
    q16_16 seasonality_lat_scale;
    q16_16 noise_temp_scale;
    q16_16 noise_precip_scale;
    q16_16 noise_season_scale;
    u32 wind_band_count;
    dom_climate_anchor_desc anchor;
} dom_climate_surface_desc;

typedef struct dom_climate_surface {
    dom_domain_id domain_id;
    u64 world_seed;
    q16_16 meters_per_unit;
    dom_terrain_shape_desc shape;
    dom_climate_noise_desc noise;
    q16_16 temp_equator;
    q16_16 temp_pole;
    q16_16 temp_altitude_scale;
    q16_16 temp_range_base;
    q16_16 temp_range_lat_scale;
    q16_16 precip_equator;
    q16_16 precip_pole;
    q16_16 precip_altitude_scale;
    q16_16 precip_range_base;
    q16_16 precip_range_lat_scale;
    q16_16 seasonality_base;
    q16_16 seasonality_lat_scale;
    q16_16 noise_temp_scale;
    q16_16 noise_precip_scale;
    q16_16 noise_season_scale;
    u32 wind_band_count;
    dom_climate_anchor_desc anchor;
    u64 noise_seed_temp;
    u64 noise_seed_precip;
    u64 noise_seed_season;
    u64 noise_seed_wind;
    dom_terrain_surface terrain_surface;
} dom_climate_surface;

enum dom_climate_sample_flags {
    DOM_CLIMATE_SAMPLE_FIELDS_UNKNOWN = 1u << 0u,
    DOM_CLIMATE_SAMPLE_WIND_UNKNOWN = 1u << 1u,
    DOM_CLIMATE_SAMPLE_COLLAPSED = 1u << 2u
};

typedef struct dom_climate_sample {
    q16_16 temperature_mean;
    q16_16 temperature_range;
    q16_16 precipitation_mean;
    q16_16 precipitation_range;
    q16_16 seasonality;
    u32 wind_prevailing;
    u32 flags; /* dom_climate_sample_flags */
    dom_domain_query_meta meta;
} dom_climate_sample;

typedef struct dom_climate_tile {
    u64 tile_id;
    u32 resolution;
    u32 sample_dim;
    dom_domain_aabb bounds;
    u32 authoring_version;
    u32 sample_count;
    q16_16 *data;
    q16_16 *temperature_mean;
    q16_16 *temperature_range;
    q16_16 *precipitation_mean;
    q16_16 *precipitation_range;
    q16_16 *seasonality;
    u32 *wind_prevailing;
} dom_climate_tile;

typedef struct dom_climate_cache_entry {
    dom_domain_id domain_id;
    u64 tile_id;
    u32 resolution;
    u32 authoring_version;
    u64 last_used;
    u64 insert_order;
    d_bool valid;
    dom_climate_tile tile;
} dom_climate_cache_entry;

typedef struct dom_climate_cache {
    dom_climate_cache_entry *entries;
    u32 capacity;
    u32 count;
    u64 use_counter;
    u64 next_insert_order;
} dom_climate_cache;

typedef struct dom_climate_macro_capsule {
    u64 capsule_id;
    u64 tile_id;
    dom_domain_aabb bounds;
    u32 sample_count;
    q16_16 temperature_mean_avg;
    q16_16 precipitation_mean_avg;
    q16_16 temperature_hist[DOM_CLIMATE_HIST_BINS];
    q16_16 precipitation_hist[DOM_CLIMATE_HIST_BINS];
    q16_16 seasonality_hist[DOM_CLIMATE_HIST_BINS];
} dom_climate_macro_capsule;

typedef struct dom_climate_domain {
    dom_climate_surface surface;
    dom_domain_policy policy;
    u32 existence_state;
    u32 archival_state;
    u32 authoring_version;
    dom_climate_cache cache;
    dom_climate_macro_capsule capsules[DOM_CLIMATE_MAX_CAPSULES];
    u32 capsule_count;
} dom_climate_domain;

enum dom_climate_biome_rule_mask {
    DOM_CLIMATE_BIOME_RULE_TEMP      = 1u << 0u,
    DOM_CLIMATE_BIOME_RULE_PRECIP    = 1u << 1u,
    DOM_CLIMATE_BIOME_RULE_SEASON    = 1u << 2u,
    DOM_CLIMATE_BIOME_RULE_ELEVATION = 1u << 3u,
    DOM_CLIMATE_BIOME_RULE_MOISTURE  = 1u << 4u,
    DOM_CLIMATE_BIOME_RULE_HARDNESS  = 1u << 5u,
    DOM_CLIMATE_BIOME_RULE_STRATA    = 1u << 6u
};

typedef struct dom_climate_biome_rule {
    u32 biome_id;
    u32 mask;
    q16_16 temp_min;
    q16_16 temp_max;
    q16_16 precip_min;
    q16_16 precip_max;
    q16_16 season_min;
    q16_16 season_max;
    q16_16 elevation_min;
    q16_16 elevation_max;
    q16_16 moisture_min;
    q16_16 moisture_max;
    q16_16 hardness_min;
    q16_16 hardness_max;
    u32 required_strata_id;
} dom_climate_biome_rule;

typedef struct dom_climate_biome_catalog {
    u32 biome_count;
    dom_climate_biome_rule rules[DOM_CLIMATE_MAX_BIOMES];
} dom_climate_biome_catalog;

enum dom_climate_biome_input_flags {
    DOM_CLIMATE_BIOME_INPUT_ELEVATION_UNKNOWN = 1u << 0u,
    DOM_CLIMATE_BIOME_INPUT_MOISTURE_UNKNOWN = 1u << 1u
};

enum dom_climate_biome_result_flags {
    DOM_CLIMATE_BIOME_RESULT_UNKNOWN = 1u << 0u
};

typedef struct dom_climate_biome_inputs {
    const dom_climate_sample* climate;
    const dom_terrain_sample* terrain;
    const dom_geology_sample* geology;
    q16_16 elevation;
    q16_16 moisture_proxy;
    u32 flags; /* dom_climate_biome_input_flags */
} dom_climate_biome_inputs;

typedef struct dom_climate_biome_result {
    u32 biome_id;
    q16_16 confidence;
    u32 flags; /* dom_climate_biome_result_flags */
} dom_climate_biome_result;

void dom_climate_surface_desc_init(dom_climate_surface_desc* desc);
void dom_climate_surface_init(dom_climate_surface* surface, const dom_climate_surface_desc* desc);

void dom_climate_domain_init(dom_climate_domain* domain,
                             const dom_climate_surface_desc* desc,
                             u32 cache_capacity);
void dom_climate_domain_free(dom_climate_domain* domain);
void dom_climate_domain_set_state(dom_climate_domain* domain,
                                  u32 existence_state,
                                  u32 archival_state);
void dom_climate_domain_set_policy(dom_climate_domain* domain,
                                   const dom_domain_policy* policy);

int dom_climate_sample_query(const dom_climate_domain* domain,
                             const dom_domain_point* point,
                             dom_domain_budget* budget,
                             dom_climate_sample* out_sample);

int dom_climate_domain_collapse_tile(dom_climate_domain* domain,
                                     const dom_domain_tile_desc* desc);
int dom_climate_domain_expand_tile(dom_climate_domain* domain, u64 tile_id);

u32 dom_climate_domain_capsule_count(const dom_climate_domain* domain);
const dom_climate_macro_capsule* dom_climate_domain_capsule_at(const dom_climate_domain* domain,
                                                               u32 index);

int dom_climate_biome_resolve(const dom_climate_biome_catalog* catalog,
                              const dom_climate_biome_inputs* inputs,
                              dom_climate_biome_result* out_result);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINO_WORLD_CLIMATE_FIELDS_H */
