/*
FILE: include/domino/world/geology_fields.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / world/geology_fields
RESPONSIBILITY: Deterministic subsurface geology and resource field sampling.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 headers as needed.
FORBIDDEN DEPENDENCIES: Engine private headers outside `include/domino/**`.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: Fixed-point only; deterministic ordering and math.
VERSIONING / ABI / DATA FORMAT NOTES: Versioned by GEOLOGY0 specs.
EXTENSION POINTS: Extend via public headers and relevant `docs/architecture/**`.
*/
#ifndef DOMINO_WORLD_GEOLOGY_FIELDS_H
#define DOMINO_WORLD_GEOLOGY_FIELDS_H

#include "domino/core/types.h"
#include "domino/core/fixed.h"
#include "domino/world/domain_query.h"
#include "domino/world/terrain_surface.h"

#ifdef __cplusplus
extern "C" {
#endif

#define DOM_GEOLOGY_MAX_LAYERS 16u
#define DOM_GEOLOGY_MAX_RESOURCES 8u
#define DOM_GEOLOGY_MAX_CAPSULES 128u
#define DOM_GEOLOGY_HIST_BINS 4u

#define DOM_GEOLOGY_UNKNOWN_Q16 ((q16_16)0x80000000)

typedef struct dom_geology_layer_desc {
    u32 layer_id;
    q16_16 thickness;
    q16_16 hardness;
    q16_16 fracture_risk;
    u32 has_fracture;
} dom_geology_layer_desc;

typedef struct dom_geology_resource_desc {
    u32 resource_id;
    u64 seed;
    q16_16 base_density;
    q16_16 noise_amplitude;
    q16_16 noise_cell_size;
    q16_16 pocket_threshold;
    q16_16 pocket_boost;
    q16_16 pocket_cell_size;
} dom_geology_resource_desc;

typedef struct dom_geology_surface_desc {
    dom_domain_id domain_id;
    u64 world_seed;
    q16_16 meters_per_unit;
    dom_terrain_shape_desc shape;
    dom_terrain_noise_desc noise;
    u32 layer_count;
    dom_geology_layer_desc layers[DOM_GEOLOGY_MAX_LAYERS];
    u32 resource_count;
    dom_geology_resource_desc resources[DOM_GEOLOGY_MAX_RESOURCES];
    q16_16 default_hardness;
    q16_16 default_fracture_risk;
} dom_geology_surface_desc;

typedef struct dom_geology_surface {
    dom_domain_id domain_id;
    u64 world_seed;
    q16_16 meters_per_unit;
    dom_terrain_shape_desc shape;
    dom_terrain_noise_desc noise;
    u32 layer_count;
    dom_geology_layer_desc layers[DOM_GEOLOGY_MAX_LAYERS];
    u32 resource_count;
    dom_geology_resource_desc resources[DOM_GEOLOGY_MAX_RESOURCES];
    q16_16 default_hardness;
    q16_16 default_fracture_risk;
    dom_terrain_surface terrain_surface;
} dom_geology_surface;

enum dom_geology_sample_flags {
    DOM_GEOLOGY_SAMPLE_STRATA_UNKNOWN = 1u << 0u,
    DOM_GEOLOGY_SAMPLE_FIELDS_UNKNOWN = 1u << 1u,
    DOM_GEOLOGY_SAMPLE_RESOURCES_UNKNOWN = 1u << 2u,
    DOM_GEOLOGY_SAMPLE_COLLAPSED = 1u << 3u
};

typedef struct dom_geology_sample {
    u32 strata_layer_id;
    u32 strata_index;
    q16_16 hardness;
    q16_16 fracture_risk;
    u32 resource_count;
    q16_16 resource_density[DOM_GEOLOGY_MAX_RESOURCES];
    u32 flags; /* dom_geology_sample_flags */
    dom_domain_query_meta meta;
} dom_geology_sample;

typedef struct dom_geology_tile {
    u64 tile_id;
    u32 resolution;
    u32 sample_dim;
    dom_domain_aabb bounds;
    u32 authoring_version;
    u32 sample_count;
    u32 resource_count;
    q16_16 *data;
    q16_16 *hardness;
    q16_16 *fracture_risk;
    q16_16 *resource_density;
    u32 *strata_ids;
} dom_geology_tile;

typedef struct dom_geology_cache_entry {
    dom_domain_id domain_id;
    u64 tile_id;
    u32 resolution;
    u32 authoring_version;
    u64 last_used;
    u64 insert_order;
    d_bool valid;
    dom_geology_tile tile;
} dom_geology_cache_entry;

typedef struct dom_geology_cache {
    dom_geology_cache_entry *entries;
    u32 capacity;
    u32 count;
    u64 use_counter;
    u64 next_insert_order;
} dom_geology_cache;

typedef struct dom_geology_macro_capsule {
    u64 capsule_id;
    u64 tile_id;
    dom_domain_aabb bounds;
    u32 sample_count;
    u32 layer_count;
    u32 layer_ids[DOM_GEOLOGY_MAX_LAYERS];
    u32 layer_sample_counts[DOM_GEOLOGY_MAX_LAYERS];
    q16_16 hardness_hist[DOM_GEOLOGY_HIST_BINS];
    q16_16 resource_hist[DOM_GEOLOGY_MAX_RESOURCES][DOM_GEOLOGY_HIST_BINS];
    q16_16 resource_total[DOM_GEOLOGY_MAX_RESOURCES];
} dom_geology_macro_capsule;

typedef struct dom_geology_domain {
    dom_geology_surface surface;
    dom_domain_policy policy;
    u32 existence_state;
    u32 archival_state;
    u32 authoring_version;
    dom_geology_cache cache;
    dom_geology_macro_capsule capsules[DOM_GEOLOGY_MAX_CAPSULES];
    u32 capsule_count;
} dom_geology_domain;

void dom_geology_surface_desc_init(dom_geology_surface_desc* desc);
void dom_geology_surface_init(dom_geology_surface* surface, const dom_geology_surface_desc* desc);

void dom_geology_domain_init(dom_geology_domain* domain,
                             const dom_geology_surface_desc* desc,
                             u32 cache_capacity);
void dom_geology_domain_free(dom_geology_domain* domain);
void dom_geology_domain_set_state(dom_geology_domain* domain,
                                  u32 existence_state,
                                  u32 archival_state);
void dom_geology_domain_set_policy(dom_geology_domain* domain,
                                   const dom_domain_policy* policy);

int dom_geology_sample_query(const dom_geology_domain* domain,
                             const dom_domain_point* point,
                             dom_domain_budget* budget,
                             dom_geology_sample* out_sample);

int dom_geology_domain_collapse_tile(dom_geology_domain* domain,
                                     const dom_domain_tile_desc* desc);
int dom_geology_domain_expand_tile(dom_geology_domain* domain, u64 tile_id);

u32 dom_geology_domain_capsule_count(const dom_geology_domain* domain);
const dom_geology_macro_capsule* dom_geology_domain_capsule_at(const dom_geology_domain* domain,
                                                               u32 index);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINO_WORLD_GEOLOGY_FIELDS_H */
