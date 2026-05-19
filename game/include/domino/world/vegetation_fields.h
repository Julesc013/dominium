/*
FILE: include/domino/world/vegetation_fields.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / world/vegetation_fields
RESPONSIBILITY: Deterministic vegetation placement and event-driven growth sampling.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 headers as needed.
FORBIDDEN DEPENDENCIES: Engine private headers outside `include/domino/**`.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: Fixed-point only; deterministic ordering and math.
VERSIONING / ABI / DATA FORMAT NOTES: Versioned by VEGETATION0 specs.
EXTENSION POINTS: Extend via public headers and relevant `docs/architecture/**`.
*/
#ifndef DOMINO_WORLD_VEGETATION_FIELDS_H
#define DOMINO_WORLD_VEGETATION_FIELDS_H

#include "domino/core/types.h"
#include "domino/core/fixed.h"
#include "domino/world/domain_query.h"
#include "domino/world/terrain_surface.h"
#include "domino/world/climate_fields.h"
#include "domino/world/weather_fields.h"
#include "domino/world/geology_fields.h"

#ifdef __cplusplus
extern "C" {
#endif

#define DOM_VEG_MAX_SPECIES 16u
#define DOM_VEG_MAX_BIOMES 8u
#define DOM_VEG_MAX_CAPSULES 128u
#define DOM_VEG_HIST_BINS 4u

#define DOM_VEG_UNKNOWN_Q16 ((q16_16)0x80000000)

enum dom_vegetation_mode {
    DOM_VEG_MODE_STATIC = 0u,
    DOM_VEG_MODE_REGENERATIVE = 1u
};

typedef struct dom_vegetation_climate_tolerance {
    q16_16 temperature_min;
    q16_16 temperature_max;
    q16_16 moisture_min;
    q16_16 moisture_max;
} dom_vegetation_climate_tolerance;

typedef struct dom_vegetation_species_desc {
    u32 species_id;
    u32 preferred_biome_count;
    u32 preferred_biomes[DOM_VEG_MAX_BIOMES];
    dom_vegetation_climate_tolerance climate_tolerance;
    q16_16 growth_rate;
    q16_16 max_size;
    u64 lifespan_ticks;
    u32 material_traits;
    q16_16 slope_max;
    u32 material_mask;
    q16_16 hardness_min;
    q16_16 hardness_max;
    u64 grow_period_ticks;
    u64 die_period_ticks;
    u64 regen_period_ticks;
    q16_16 regen_chance;
    q16_16 death_rate;
    u32 maturity_tag;
} dom_vegetation_species_desc;

typedef struct dom_vegetation_surface_desc {
    dom_domain_id domain_id;
    u64 world_seed;
    q16_16 meters_per_unit;
    dom_terrain_shape_desc shape;
    dom_terrain_surface_desc terrain_desc;
    dom_climate_surface_desc climate_desc;
    dom_climate_biome_catalog biome_catalog;
    dom_weather_schedule_desc weather_schedule;
    dom_geology_surface_desc geology_desc;
    u32 species_count;
    dom_vegetation_species_desc species[DOM_VEG_MAX_SPECIES];
    q16_16 placement_cell_size;
    q16_16 density_base;
    u64 weather_window_ticks;
    u32 cache_capacity;
    u32 mode; /* dom_vegetation_mode */
} dom_vegetation_surface_desc;

typedef struct dom_vegetation_instance {
    u32 species_id;
    dom_domain_point location;
    q16_16 size;
    q16_16 health;
    u64 age_ticks;
    u32 flags;
} dom_vegetation_instance;

enum dom_vegetation_sample_flags {
    DOM_VEG_SAMPLE_FIELDS_UNKNOWN = 1u << 0u,
    DOM_VEG_SAMPLE_INSTANCE_PRESENT = 1u << 1u,
    DOM_VEG_SAMPLE_COLLAPSED = 1u << 2u
};

typedef struct dom_vegetation_sample {
    q16_16 coverage;
    u32 biome_id;
    q16_16 suitability;
    dom_vegetation_instance instance;
    u32 flags; /* dom_vegetation_sample_flags */
    dom_domain_query_meta meta;
} dom_vegetation_sample;

typedef struct dom_vegetation_tile {
    u64 tile_id;
    u32 resolution;
    u32 sample_dim;
    dom_domain_aabb bounds;
    u32 authoring_version;
    u64 window_start;
    u64 window_ticks;
    u32 sample_count;
    q16_16* data_q16;
    q16_16* coverage;
    q16_16* suitability;
    q16_16* size;
    q16_16* health;
    u64* age_ticks;
    u32* data_u32;
    u32* biome_id;
    u32* species_id;
    u32* flags;
} dom_vegetation_tile;

typedef struct dom_vegetation_cache_entry {
    dom_domain_id domain_id;
    u64 tile_id;
    u32 resolution;
    u32 authoring_version;
    u64 window_start;
    u64 window_ticks;
    u64 last_used;
    u64 insert_order;
    d_bool valid;
    dom_vegetation_tile tile;
} dom_vegetation_cache_entry;

typedef struct dom_vegetation_cache {
    dom_vegetation_cache_entry* entries;
    u32 capacity;
    u32 count;
    u64 use_counter;
    u64 next_insert_order;
} dom_vegetation_cache;

typedef struct dom_vegetation_macro_capsule {
    u64 capsule_id;
    u64 tile_id;
    u64 tick;
    dom_domain_aabb bounds;
    q16_16 coverage_avg;
    u32 species_count;
    u32 species_ids[DOM_VEG_MAX_SPECIES];
    q16_16 size_hist[DOM_VEG_MAX_SPECIES][DOM_VEG_HIST_BINS];
    q16_16 age_hist[DOM_VEG_MAX_SPECIES][DOM_VEG_HIST_BINS];
    u32 rng_cursor[DOM_VEG_MAX_SPECIES];
} dom_vegetation_macro_capsule;

typedef struct dom_vegetation_domain {
    dom_terrain_domain terrain_domain;
    dom_climate_domain climate_domain;
    dom_weather_domain weather_domain;
    dom_geology_domain geology_domain;
    dom_domain_policy policy;
    u32 existence_state;
    u32 archival_state;
    u32 authoring_version;
    dom_vegetation_surface_desc surface;
    dom_vegetation_cache cache;
    dom_vegetation_macro_capsule capsules[DOM_VEG_MAX_CAPSULES];
    u32 capsule_count;
} dom_vegetation_domain;

void dom_vegetation_surface_desc_init(dom_vegetation_surface_desc* desc);
void dom_vegetation_domain_init(dom_vegetation_domain* domain,
                                const dom_vegetation_surface_desc* desc);
void dom_vegetation_domain_free(dom_vegetation_domain* domain);
void dom_vegetation_domain_set_state(dom_vegetation_domain* domain,
                                     u32 existence_state,
                                     u32 archival_state);
void dom_vegetation_domain_set_policy(dom_vegetation_domain* domain,
                                      const dom_domain_policy* policy);

int dom_vegetation_sample_query(const dom_vegetation_domain* domain,
                                const dom_domain_point* point,
                                u64 tick,
                                dom_domain_budget* budget,
                                dom_vegetation_sample* out_sample);

int dom_vegetation_domain_collapse_tile(dom_vegetation_domain* domain,
                                        const dom_domain_tile_desc* desc,
                                        u64 tick);
int dom_vegetation_domain_expand_tile(dom_vegetation_domain* domain, u64 tile_id);

u32 dom_vegetation_domain_capsule_count(const dom_vegetation_domain* domain);
const dom_vegetation_macro_capsule* dom_vegetation_domain_capsule_at(const dom_vegetation_domain* domain,
                                                                     u32 index);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINO_WORLD_VEGETATION_FIELDS_H */
