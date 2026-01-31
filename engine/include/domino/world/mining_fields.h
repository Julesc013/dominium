/*
FILE: include/domino/world/mining_fields.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / world/mining_fields
RESPONSIBILITY: Deterministic mining processes (cut/extract/support) and material chunk tracking.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 headers as needed.
FORBIDDEN DEPENDENCIES: Engine private headers outside `include/domino/**`.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: Fixed-point only; deterministic ordering and math.
VERSIONING / ABI / DATA FORMAT NOTES: Versioned by MINING0 specs.
EXTENSION POINTS: Extend via public headers and relevant `docs/architecture/**`.
*/
#ifndef DOMINO_WORLD_MINING_FIELDS_H
#define DOMINO_WORLD_MINING_FIELDS_H

#include "domino/core/types.h"
#include "domino/core/fixed.h"
#include "domino/world/domain_query.h"
#include "domino/world/terrain_surface.h"
#include "domino/world/geology_fields.h"

#ifdef __cplusplus
extern "C" {
#endif

#define DOM_MINING_MAX_RESOURCES DOM_GEOLOGY_MAX_RESOURCES
#define DOM_MINING_MAX_LAYERS DOM_GEOLOGY_MAX_LAYERS
#define DOM_MINING_MAX_OVERLAYS 256u
#define DOM_MINING_MAX_DEPLETIONS 256u
#define DOM_MINING_MAX_CHUNKS 256u

#define DOM_MINING_UNKNOWN_Q16 ((q16_16)0x80000000)

enum dom_mining_overlay_kind {
    DOM_MINING_OVERLAY_CUT = 0u,
    DOM_MINING_OVERLAY_FILL = 1u
};

enum dom_mining_overlay_flags {
    DOM_MINING_OVERLAY_COLLAPSE = 1u << 0u,
    DOM_MINING_OVERLAY_TOOL = 1u << 1u
};

enum dom_mining_chunk_flags {
    DOM_MINING_CHUNK_WASTE = 1u << 0u
};

enum dom_mining_sample_flags {
    DOM_MINING_SAMPLE_FIELDS_UNKNOWN = 1u << 0u,
    DOM_MINING_SAMPLE_COLLAPSED = 1u << 1u
};

enum dom_mining_result_flags {
    DOM_MINING_RESULT_LAW_BLOCK = 1u << 0u,
    DOM_MINING_RESULT_METALAW_BLOCK = 1u << 1u,
    DOM_MINING_RESULT_DEPLETED = 1u << 2u,
    DOM_MINING_RESULT_COLLAPSE_RISK = 1u << 3u
};

typedef struct dom_mining_overlay {
    u32 overlay_id;
    u32 overlay_kind; /* dom_mining_overlay_kind */
    dom_domain_point center;
    q16_16 radius;
    u64 tick;
    u32 process_id;
    u32 event_id;
    u32 flags; /* dom_mining_overlay_flags */
} dom_mining_overlay;

typedef struct dom_mining_depletion {
    u32 resource_id;
    dom_domain_point center;
    q16_16 radius;
    q16_16 depletion;
    u64 tick;
} dom_mining_depletion;

typedef struct dom_material_chunk {
    u32 chunk_id;
    u32 material_id;
    dom_domain_point location;
    q16_16 mass;
    q16_16 volume;
    q16_16 purity;
    u32 flags; /* dom_mining_chunk_flags */
    u32 process_id;
    u64 tick;
} dom_material_chunk;

typedef struct dom_mining_surface_desc {
    dom_domain_id domain_id;
    u64 world_seed;
    q16_16 meters_per_unit;
    dom_terrain_shape_desc shape;
    dom_terrain_surface_desc terrain_desc;
    dom_geology_surface_desc geology_desc;
    q16_16 cut_radius_max;
    q16_16 extract_radius_max;
    q16_16 support_radius_scale;
    q16_16 collapse_fill_scale;
    u32 cut_cost_base;
    u32 cut_cost_per_unit;
    u32 extract_cost_base;
    u32 extract_cost_per_unit;
    u32 support_cost_base;
    u32 overlay_capacity;
    u32 depletion_capacity;
    u32 chunk_capacity;
    u32 cache_capacity;
    u32 law_allow_mining;
    u32 metalaw_allow_mining;
    u32 tailings_material_id;
} dom_mining_surface_desc;

typedef struct dom_mining_sample {
    q16_16 phi;
    u32 material_primary;
    q16_16 support_capacity;
    q16_16 stress;
    q16_16 stress_ratio;
    u32 resource_count;
    q16_16 resource_density[DOM_MINING_MAX_RESOURCES];
    u32 flags; /* dom_mining_sample_flags */
    dom_domain_query_meta meta;
} dom_mining_sample;

typedef struct dom_mining_cut_result {
    u32 ok;
    u32 refusal_reason;
    u32 flags; /* dom_mining_result_flags */
    u32 overlay_id;
    q16_16 cut_radius;
    q16_16 cut_volume;
    u32 overlay_count;
} dom_mining_cut_result;

typedef struct dom_mining_extract_result {
    u32 ok;
    u32 refusal_reason;
    u32 flags; /* dom_mining_result_flags */
    q16_16 extract_radius;
    q16_16 extract_volume;
    q16_16 extracted_mass;
    q16_16 tailings_mass;
    u32 resource_chunks;
    u32 tailings_chunks;
    u32 chunk_count;
} dom_mining_extract_result;

typedef struct dom_mining_support_result {
    u32 ok;
    u32 refusal_reason;
    u32 flags; /* dom_mining_result_flags */
    q16_16 support_capacity;
    q16_16 stress;
    q16_16 stress_ratio;
    u32 collapse_risk;
    q16_16 collapse_radius;
} dom_mining_support_result;

typedef struct dom_mining_domain {
    dom_terrain_domain terrain_domain;
    dom_geology_domain geology_domain;
    dom_domain_policy policy;
    u32 existence_state;
    u32 archival_state;
    u32 authoring_version;
    dom_mining_surface_desc surface;
    dom_mining_overlay overlays[DOM_MINING_MAX_OVERLAYS];
    u32 overlay_count;
    dom_mining_depletion depletions[DOM_MINING_MAX_DEPLETIONS];
    u32 depletion_count;
    dom_material_chunk chunks[DOM_MINING_MAX_CHUNKS];
    u32 chunk_count;
} dom_mining_domain;

void dom_mining_surface_desc_init(dom_mining_surface_desc* desc);
void dom_mining_domain_init(dom_mining_domain* domain,
                            const dom_mining_surface_desc* desc);
void dom_mining_domain_free(dom_mining_domain* domain);
void dom_mining_domain_set_state(dom_mining_domain* domain,
                                 u32 existence_state,
                                 u32 archival_state);
void dom_mining_domain_set_policy(dom_mining_domain* domain,
                                  const dom_domain_policy* policy);

int dom_mining_sample_query(const dom_mining_domain* domain,
                            const dom_domain_point* point,
                            dom_domain_budget* budget,
                            dom_mining_sample* out_sample);

int dom_mining_cut(dom_mining_domain* domain,
                   const dom_domain_point* center,
                   q16_16 radius,
                   u64 tick,
                   dom_domain_budget* budget,
                   dom_mining_cut_result* out_result);

int dom_mining_extract(dom_mining_domain* domain,
                       const dom_domain_point* center,
                       q16_16 radius,
                       u64 tick,
                       dom_domain_budget* budget,
                       dom_mining_extract_result* out_result);

int dom_mining_support_check(dom_mining_domain* domain,
                             const dom_domain_point* center,
                             q16_16 radius,
                             u64 tick,
                             dom_mining_support_result* out_result);

u32 dom_mining_overlay_count(const dom_mining_domain* domain);
const dom_mining_overlay* dom_mining_overlay_at(const dom_mining_domain* domain, u32 index);
u32 dom_mining_chunk_count(const dom_mining_domain* domain);
const dom_material_chunk* dom_mining_chunk_at(const dom_mining_domain* domain, u32 index);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINO_WORLD_MINING_FIELDS_H */
