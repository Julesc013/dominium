/*
FILE: include/domino/world/structure_fields.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / world/structure_fields
RESPONSIBILITY: Deterministic structure placement, stress sampling, and process-driven collapse hooks.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 headers as needed.
FORBIDDEN DEPENDENCIES: Engine private headers outside `include/domino/**`.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: Fixed-point only; deterministic ordering and math.
VERSIONING / ABI / DATA FORMAT NOTES: Versioned by STRUCTURE0 specs.
EXTENSION POINTS: Extend via public headers and relevant `docs/architecture/**`.
*/
#ifndef DOMINO_WORLD_STRUCTURE_FIELDS_H
#define DOMINO_WORLD_STRUCTURE_FIELDS_H

#include "domino/core/types.h"
#include "domino/core/fixed.h"
#include "domino/world/domain_query.h"
#include "domino/world/terrain_surface.h"
#include "domino/world/geology_fields.h"

#ifdef __cplusplus
extern "C" {
#endif

#define DOM_STRUCTURE_MAX_SPECS 16u
#define DOM_STRUCTURE_MAX_ANCHORS 8u
#define DOM_STRUCTURE_MAX_INSTANCES 256u
#define DOM_STRUCTURE_MAX_CAPSULES 128u
#define DOM_STRUCTURE_HIST_BINS 4u

#define DOM_STRUCTURE_UNKNOWN_Q16 ((q16_16)0x80000000)

enum dom_structure_anchor_kind {
    DOM_STRUCTURE_ANCHOR_TERRAIN = 0u,
    DOM_STRUCTURE_ANCHOR_STRUCTURE = 1u
};

enum dom_structure_overlay_kind {
    DOM_STRUCTURE_OVERLAY_NONE = 0u,
    DOM_STRUCTURE_OVERLAY_DELTA_PHI = 1u,
    DOM_STRUCTURE_OVERLAY_DELTA_MATERIAL = 2u,
    DOM_STRUCTURE_OVERLAY_DELTA_FIELD = 3u
};

enum dom_structure_instance_flags {
    DOM_STRUCTURE_INSTANCE_COLLAPSED = 1u << 0u,
    DOM_STRUCTURE_INSTANCE_UNSTABLE = 1u << 1u,
    DOM_STRUCTURE_INSTANCE_REINFORCED = 1u << 2u
};

enum dom_structure_sample_flags {
    DOM_STRUCTURE_SAMPLE_FIELDS_UNKNOWN = 1u << 0u,
    DOM_STRUCTURE_SAMPLE_INSTANCE_PRESENT = 1u << 1u,
    DOM_STRUCTURE_SAMPLE_COLLAPSED = 1u << 2u,
    DOM_STRUCTURE_SAMPLE_ANCHOR_UNKNOWN = 1u << 3u,
    DOM_STRUCTURE_SAMPLE_UNSTABLE = 1u << 4u
};

typedef struct dom_structure_anchor_desc {
    dom_domain_point offset;
    u32 kind; /* dom_structure_anchor_kind */
    u32 target_id;
    q16_16 support_scale;
} dom_structure_anchor_desc;

typedef struct dom_structure_material_traits {
    q16_16 stiffness;
    q16_16 density;
    q16_16 brittleness;
} dom_structure_material_traits;

typedef struct dom_structure_spec_desc {
    u32 structure_id;
    u32 geometry_id;
    dom_structure_material_traits traits;
    q16_16 load_capacity;
    u32 anchor_count;
    dom_structure_anchor_desc anchors[DOM_STRUCTURE_MAX_ANCHORS];
    q16_16 gravity_scale;
    q16_16 slope_max;
    u32 maturity_tag;
} dom_structure_spec_desc;

typedef struct dom_structure_instance {
    u32 structure_id;
    dom_domain_point location;
    q16_16 integrity;
    q16_16 reinforcement;
    u32 flags; /* dom_structure_instance_flags */
    i32 cell_x;
    i32 cell_y;
    i32 cell_z;
} dom_structure_instance;

typedef struct dom_structure_sample {
    q16_16 support_capacity;
    q16_16 applied_stress;
    q16_16 stress_ratio;
    q16_16 integrity;
    u32 structure_id;
    u32 anchor_required_mask;
    u32 anchor_supported_mask;
    u32 flags; /* dom_structure_sample_flags */
    dom_domain_query_meta meta;
} dom_structure_sample;

typedef struct dom_structure_tile {
    u64 tile_id;
    u32 resolution;
    u32 sample_dim;
    dom_domain_aabb bounds;
    u32 authoring_version;
    u32 sample_count;
    q16_16* data_q16;
    q16_16* support_capacity;
    q16_16* applied_stress;
    q16_16* stress_ratio;
    q16_16* integrity;
    u32* data_u32;
    u32* structure_id;
    u32* anchor_supported_mask;
    u32* flags;
} dom_structure_tile;

typedef struct dom_structure_cache_entry {
    dom_domain_id domain_id;
    u64 tile_id;
    u32 resolution;
    u32 authoring_version;
    u64 last_used;
    u64 insert_order;
    d_bool valid;
    dom_structure_tile tile;
} dom_structure_cache_entry;

typedef struct dom_structure_cache {
    dom_structure_cache_entry* entries;
    u32 capacity;
    u32 count;
    u64 use_counter;
    u64 next_insert_order;
} dom_structure_cache;

typedef struct dom_structure_process_result {
    u32 ok;
    u32 refusal_reason; /* dom_domain_refusal_reason */
    u32 flags;
    q16_16 support_capacity;
    q16_16 applied_stress;
    q16_16 stress_ratio;
} dom_structure_process_result;

typedef struct dom_structure_collapse_result {
    u32 ok;
    u32 refusal_reason; /* dom_domain_refusal_reason */
    u32 overlay_kind; /* dom_structure_overlay_kind */
    q16_16 delta_phi;
    q16_16 debris_fill;
} dom_structure_collapse_result;

typedef struct dom_structure_surface_desc {
    dom_domain_id domain_id;
    u64 world_seed;
    q16_16 meters_per_unit;
    dom_terrain_shape_desc shape;
    dom_terrain_surface_desc terrain_desc;
    dom_geology_surface_desc geology_desc;
    u32 structure_count;
    dom_structure_spec_desc structures[DOM_STRUCTURE_MAX_SPECS];
    u32 instance_count;
    dom_structure_instance instances[DOM_STRUCTURE_MAX_INSTANCES];
    q16_16 placement_cell_size;
    q16_16 density_base;
    u64 stress_check_period_ticks;
    u64 repair_period_ticks;
    u64 reinforce_period_ticks;
    u32 cache_capacity;
} dom_structure_surface_desc;

typedef struct dom_structure_macro_capsule {
    u64 capsule_id;
    u64 tile_id;
    u64 tick;
    dom_domain_aabb bounds;
    u32 structure_count;
    u32 structure_ids[DOM_STRUCTURE_MAX_SPECS];
    u32 instance_counts[DOM_STRUCTURE_MAX_SPECS];
    q16_16 integrity_hist[DOM_STRUCTURE_MAX_SPECS][DOM_STRUCTURE_HIST_BINS];
    q16_16 stress_hist[DOM_STRUCTURE_MAX_SPECS][DOM_STRUCTURE_HIST_BINS];
    q16_16 mass_total;
    u32 rng_cursor[DOM_STRUCTURE_MAX_SPECS];
} dom_structure_macro_capsule;

typedef struct dom_structure_domain {
    dom_terrain_domain terrain_domain;
    dom_geology_domain geology_domain;
    dom_domain_policy policy;
    u32 existence_state;
    u32 archival_state;
    u32 authoring_version;
    dom_structure_surface_desc surface;
    dom_structure_cache cache;
    dom_structure_macro_capsule capsules[DOM_STRUCTURE_MAX_CAPSULES];
    u32 capsule_count;
    dom_structure_instance instances[DOM_STRUCTURE_MAX_INSTANCES];
    u32 instance_count;
} dom_structure_domain;

void dom_structure_surface_desc_init(dom_structure_surface_desc* desc);
void dom_structure_domain_init(dom_structure_domain* domain,
                               const dom_structure_surface_desc* desc);
void dom_structure_domain_free(dom_structure_domain* domain);
void dom_structure_domain_set_state(dom_structure_domain* domain,
                                    u32 existence_state,
                                    u32 archival_state);
void dom_structure_domain_set_policy(dom_structure_domain* domain,
                                     const dom_domain_policy* policy);

int dom_structure_sample_query(const dom_structure_domain* domain,
                               const dom_domain_point* point,
                               u64 tick,
                               dom_domain_budget* budget,
                               dom_structure_sample* out_sample);

int dom_structure_place(dom_structure_domain* domain,
                        const dom_structure_instance* instance,
                        u64 tick,
                        dom_structure_process_result* out_result);
int dom_structure_remove(dom_structure_domain* domain,
                         u32 instance_index,
                         u64 tick,
                         dom_structure_process_result* out_result);
int dom_structure_repair(dom_structure_domain* domain,
                         u32 instance_index,
                         q16_16 amount,
                         u64 tick,
                         dom_structure_process_result* out_result);
int dom_structure_reinforce(dom_structure_domain* domain,
                            u32 instance_index,
                            q16_16 amount,
                            u64 tick,
                            dom_structure_process_result* out_result);
int dom_structure_collapse(dom_structure_domain* domain,
                           u32 instance_index,
                           u64 tick,
                           dom_structure_collapse_result* out_result);

int dom_structure_domain_collapse_tile(dom_structure_domain* domain,
                                       const dom_domain_tile_desc* desc,
                                       u64 tick);
int dom_structure_domain_expand_tile(dom_structure_domain* domain, u64 tile_id);

u32 dom_structure_domain_capsule_count(const dom_structure_domain* domain);
const dom_structure_macro_capsule* dom_structure_domain_capsule_at(const dom_structure_domain* domain,
                                                                   u32 index);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINO_WORLD_STRUCTURE_FIELDS_H */
