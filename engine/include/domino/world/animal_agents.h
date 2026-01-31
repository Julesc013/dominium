/*
FILE: include/domino/world/animal_agents.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / world/animal_agents
RESPONSIBILITY: Deterministic animal agents with coarse, event-driven lifecycle sampling.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 headers as needed.
FORBIDDEN DEPENDENCIES: Engine private headers outside `include/domino/**`.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: Fixed-point only; deterministic ordering and math.
VERSIONING / ABI / DATA FORMAT NOTES: Versioned by ANIMAL0 specs.
EXTENSION POINTS: Extend via public headers and relevant `docs/architecture/**`.
*/
#ifndef DOMINO_WORLD_ANIMAL_AGENTS_H
#define DOMINO_WORLD_ANIMAL_AGENTS_H

#include "domino/core/types.h"
#include "domino/core/fixed.h"
#include "domino/world/domain_query.h"
#include "domino/world/terrain_surface.h"
#include "domino/world/climate_fields.h"
#include "domino/world/weather_fields.h"
#include "domino/world/vegetation_fields.h"

#ifdef __cplusplus
extern "C" {
#endif

#define DOM_ANIMAL_MAX_SPECIES 16u
#define DOM_ANIMAL_MAX_BIOMES 8u
#define DOM_ANIMAL_MAX_DIET 8u
#define DOM_ANIMAL_MAX_CAPSULES 128u
#define DOM_ANIMAL_HIST_BINS 4u

#define DOM_ANIMAL_UNKNOWN_Q16 ((q16_16)0x80000000)

enum dom_animal_movement_mode {
    DOM_ANIMAL_MOVE_LAND = 0u,
    DOM_ANIMAL_MOVE_WATER = 1u,
    DOM_ANIMAL_MOVE_AIR = 2u
};

enum dom_animal_need {
    DOM_ANIMAL_NEED_EAT = 0u,
    DOM_ANIMAL_NEED_REST = 1u,
    DOM_ANIMAL_NEED_REPRODUCE = 2u,
    DOM_ANIMAL_NEED_WANDER = 3u,
    DOM_ANIMAL_NEED_UNKNOWN = 4u
};

enum dom_animal_death_reason {
    DOM_ANIMAL_DEATH_NONE = 0u,
    DOM_ANIMAL_DEATH_AGE = 1u,
    DOM_ANIMAL_DEATH_STARVATION = 2u,
    DOM_ANIMAL_DEATH_STRESS = 3u
};

typedef struct dom_animal_climate_tolerance {
    q16_16 temperature_min;
    q16_16 temperature_max;
    q16_16 moisture_min;
    q16_16 moisture_max;
} dom_animal_climate_tolerance;

typedef struct dom_animal_metabolism_desc {
    q16_16 energy_consumption_rate;
    q16_16 rest_requirement;
} dom_animal_metabolism_desc;

typedef struct dom_animal_reproduction_desc {
    u64 maturity_age_ticks;
    u64 gestation_ticks;
    u32 offspring_min;
    u32 offspring_max;
    q16_16 reproduction_chance;
} dom_animal_reproduction_desc;

typedef struct dom_animal_species_desc {
    u32 species_id;
    u32 preferred_biome_count;
    u32 preferred_biomes[DOM_ANIMAL_MAX_BIOMES];
    dom_animal_climate_tolerance climate_tolerance;
    u32 movement_mode; /* dom_animal_movement_mode */
    u32 diet_count;
    u32 diet_species[DOM_ANIMAL_MAX_DIET];
    dom_animal_metabolism_desc metabolism;
    dom_animal_reproduction_desc reproduction;
    u64 lifespan_ticks;
    u32 size_class;
    q16_16 movement_speed;
    q16_16 slope_max;
    q16_16 death_rate;
    u32 maturity_tag;
} dom_animal_species_desc;

typedef struct dom_animal_surface_desc {
    dom_domain_id domain_id;
    u64 world_seed;
    q16_16 meters_per_unit;
    dom_terrain_shape_desc shape;
    dom_vegetation_surface_desc vegetation_desc;
    u32 species_count;
    dom_animal_species_desc species[DOM_ANIMAL_MAX_SPECIES];
    q16_16 placement_cell_size;
    q16_16 density_base;
    u64 decision_period_ticks;
    u32 cache_capacity;
} dom_animal_surface_desc;

typedef struct dom_animal_agent {
    u32 species_id;
    dom_domain_point location;
    q16_16 energy;
    q16_16 health;
    u64 age_ticks;
    u32 current_need; /* dom_animal_need */
    u32 movement_mode; /* dom_animal_movement_mode */
    u32 flags;
} dom_animal_agent;

enum dom_animal_sample_flags {
    DOM_ANIMAL_SAMPLE_FIELDS_UNKNOWN = 1u << 0u,
    DOM_ANIMAL_SAMPLE_AGENT_PRESENT = 1u << 1u,
    DOM_ANIMAL_SAMPLE_COLLAPSED = 1u << 2u,
    DOM_ANIMAL_SAMPLE_DEAD = 1u << 3u
};

typedef struct dom_animal_sample {
    q16_16 suitability;
    u32 biome_id;
    q16_16 vegetation_coverage;
    q16_16 vegetation_consumed;
    dom_animal_agent agent;
    u32 death_reason; /* dom_animal_death_reason */
    u32 flags; /* dom_animal_sample_flags */
    dom_domain_query_meta meta;
} dom_animal_sample;

typedef struct dom_animal_tile {
    u64 tile_id;
    u32 resolution;
    u32 sample_dim;
    dom_domain_aabb bounds;
    u32 authoring_version;
    u64 window_start;
    u64 window_ticks;
    u32 sample_count;
    q16_16* data_q16;
    q16_16* suitability;
    q16_16* vegetation_coverage;
    q16_16* vegetation_consumed;
    q16_16* energy;
    q16_16* health;
    u64* age_ticks;
    u32* data_u32;
    u32* biome_id;
    u32* species_id;
    u32* need;
    u32* movement_mode;
    u32* death_reason;
    u32* flags;
} dom_animal_tile;

typedef struct dom_animal_cache_entry {
    dom_domain_id domain_id;
    u64 tile_id;
    u32 resolution;
    u32 authoring_version;
    u64 window_start;
    u64 window_ticks;
    u64 last_used;
    u64 insert_order;
    d_bool valid;
    dom_animal_tile tile;
} dom_animal_cache_entry;

typedef struct dom_animal_cache {
    dom_animal_cache_entry* entries;
    u32 capacity;
    u32 count;
    u64 use_counter;
    u64 next_insert_order;
} dom_animal_cache;

typedef struct dom_animal_macro_capsule {
    u64 capsule_id;
    u64 tile_id;
    u64 tick;
    dom_domain_aabb bounds;
    u32 species_count;
    u32 species_ids[DOM_ANIMAL_MAX_SPECIES];
    u32 population_counts[DOM_ANIMAL_MAX_SPECIES];
    q16_16 energy_hist[DOM_ANIMAL_MAX_SPECIES][DOM_ANIMAL_HIST_BINS];
    q16_16 age_hist[DOM_ANIMAL_MAX_SPECIES][DOM_ANIMAL_HIST_BINS];
    u32 rng_cursor[DOM_ANIMAL_MAX_SPECIES];
} dom_animal_macro_capsule;

typedef struct dom_animal_domain {
    dom_vegetation_domain vegetation_domain;
    dom_domain_policy policy;
    u32 existence_state;
    u32 archival_state;
    u32 authoring_version;
    dom_animal_surface_desc surface;
    dom_animal_cache cache;
    dom_animal_macro_capsule capsules[DOM_ANIMAL_MAX_CAPSULES];
    u32 capsule_count;
} dom_animal_domain;

void dom_animal_surface_desc_init(dom_animal_surface_desc* desc);
void dom_animal_domain_init(dom_animal_domain* domain,
                            const dom_animal_surface_desc* desc);
void dom_animal_domain_free(dom_animal_domain* domain);
void dom_animal_domain_set_state(dom_animal_domain* domain,
                                 u32 existence_state,
                                 u32 archival_state);
void dom_animal_domain_set_policy(dom_animal_domain* domain,
                                  const dom_domain_policy* policy);

int dom_animal_sample_query(const dom_animal_domain* domain,
                            const dom_domain_point* point,
                            u64 tick,
                            dom_domain_budget* budget,
                            dom_animal_sample* out_sample);

int dom_animal_domain_collapse_tile(dom_animal_domain* domain,
                                    const dom_domain_tile_desc* desc,
                                    u64 tick);
int dom_animal_domain_expand_tile(dom_animal_domain* domain, u64 tile_id);

u32 dom_animal_domain_capsule_count(const dom_animal_domain* domain);
const dom_animal_macro_capsule* dom_animal_domain_capsule_at(const dom_animal_domain* domain,
                                                             u32 index);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINO_WORLD_ANIMAL_AGENTS_H */
