/*
FILE: include/domino/world/hazard_fields.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / world/hazard_fields
RESPONSIBILITY: Deterministic hazard field sampling, exposure tracking, and propagation hooks.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 headers as needed.
FORBIDDEN DEPENDENCIES: Engine private headers outside `include/domino/**`.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: Fixed-point only; deterministic ordering and math.
VERSIONING / ABI / DATA FORMAT NOTES: Versioned by HAZARD0 specs.
EXTENSION POINTS: Extend via public headers and relevant `docs/architecture/**`.
*/
#ifndef DOMINO_WORLD_HAZARD_FIELDS_H
#define DOMINO_WORLD_HAZARD_FIELDS_H

#include "domino/core/types.h"
#include "domino/core/fixed.h"
#include "domino/world/domain_query.h"

#ifdef __cplusplus
extern "C" {
#endif

#define DOM_HAZARD_MAX_FIELDS 128u
#define DOM_HAZARD_MAX_EXPOSURES 128u
#define DOM_HAZARD_MAX_TYPES 32u
#define DOM_HAZARD_MAX_REGIONS 16u
#define DOM_HAZARD_MAX_CAPSULES 64u
#define DOM_HAZARD_HIST_BINS 4u
#define DOM_HAZARD_CLASS_COUNT 7u

#define DOM_HAZARD_RATIO_ONE_Q16 ((q16_16)0x00010000)

enum dom_hazard_class {
    DOM_HAZARD_CLASS_UNSET = 0u,
    DOM_HAZARD_CLASS_FIRE = 1u,
    DOM_HAZARD_CLASS_TOXIC = 2u,
    DOM_HAZARD_CLASS_RADIATION = 3u,
    DOM_HAZARD_CLASS_PRESSURE = 4u,
    DOM_HAZARD_CLASS_THERMAL = 5u,
    DOM_HAZARD_CLASS_BIOLOGICAL = 6u,
    DOM_HAZARD_CLASS_INFORMATION = 7u
};

enum dom_hazard_field_flags {
    DOM_HAZARD_FIELD_UNRESOLVED = 1u << 0u,
    DOM_HAZARD_FIELD_COLLAPSED = 1u << 1u,
    DOM_HAZARD_FIELD_DECAYING = 1u << 2u
};

enum dom_hazard_exposure_flags {
    DOM_HAZARD_EXPOSURE_UNRESOLVED = 1u << 0u,
    DOM_HAZARD_EXPOSURE_COLLAPSED = 1u << 1u,
    DOM_HAZARD_EXPOSURE_OVER_LIMIT = 1u << 2u
};

enum dom_hazard_type_flags {
    DOM_HAZARD_TYPE_UNRESOLVED = 1u << 0u
};

enum dom_hazard_resolve_flags {
    DOM_HAZARD_RESOLVE_PARTIAL = 1u << 0u,
    DOM_HAZARD_RESOLVE_DECAYED = 1u << 1u,
    DOM_HAZARD_RESOLVE_OVER_LIMIT = 1u << 2u
};

enum dom_hazard_refusal_reason {
    DOM_HAZARD_REFUSE_NONE = 0u,
    DOM_HAZARD_REFUSE_BUDGET = 1u,
    DOM_HAZARD_REFUSE_DOMAIN_INACTIVE = 2u,
    DOM_HAZARD_REFUSE_FIELD_MISSING = 3u,
    DOM_HAZARD_REFUSE_EXPOSURE_MISSING = 4u,
    DOM_HAZARD_REFUSE_TYPE_MISSING = 5u,
    DOM_HAZARD_REFUSE_POLICY = 6u,
    DOM_HAZARD_REFUSE_INTERNAL = 7u
};

typedef struct dom_hazard_type_desc {
    u32 type_id;
    u32 hazard_class;
    q16_16 default_intensity;
    q16_16 default_exposure_rate;
    q16_16 default_decay_rate;
    q16_16 default_uncertainty;
} dom_hazard_type_desc;

typedef struct dom_hazard_field_desc {
    u32 hazard_id;
    u32 hazard_type_id;
    q16_16 intensity;
    q16_16 exposure_rate;
    q16_16 decay_rate;
    q16_16 uncertainty;
    u32 provenance_id;
    u32 region_id;
    q16_16 radius;
    dom_domain_point center;
} dom_hazard_field_desc;

typedef struct dom_hazard_exposure_desc {
    u32 exposure_id;
    u32 hazard_type_id;
    q48_16 exposure_limit;
    q16_16 sensitivity;
    q16_16 uncertainty;
    u32 provenance_id;
    u32 region_id;
    dom_domain_point location;
    q48_16 exposure_accumulated;
} dom_hazard_exposure_desc;

typedef struct dom_hazard_type {
    u32 type_id;
    u32 hazard_class;
    q16_16 default_intensity;
    q16_16 default_exposure_rate;
    q16_16 default_decay_rate;
    q16_16 default_uncertainty;
    u32 flags; /* dom_hazard_type_flags */
} dom_hazard_type;

typedef struct dom_hazard_field {
    u32 hazard_id;
    u32 hazard_type_id;
    q16_16 intensity;
    q16_16 exposure_rate;
    q16_16 decay_rate;
    q16_16 uncertainty;
    u32 provenance_id;
    u32 region_id;
    q16_16 radius;
    dom_domain_point center;
    u32 flags; /* dom_hazard_field_flags */
} dom_hazard_field;

typedef struct dom_hazard_exposure {
    u32 exposure_id;
    u32 hazard_type_id;
    q48_16 exposure_limit;
    q16_16 sensitivity;
    q16_16 uncertainty;
    u32 provenance_id;
    u32 region_id;
    dom_domain_point location;
    q48_16 exposure_accumulated;
    u32 flags; /* dom_hazard_exposure_flags */
} dom_hazard_exposure;

typedef struct dom_hazard_surface_desc {
    dom_domain_id domain_id;
    u64 world_seed;
    q16_16 meters_per_unit;
    u32 type_count;
    dom_hazard_type_desc types[DOM_HAZARD_MAX_TYPES];
    u32 field_count;
    dom_hazard_field_desc fields[DOM_HAZARD_MAX_FIELDS];
    u32 exposure_count;
    dom_hazard_exposure_desc exposures[DOM_HAZARD_MAX_EXPOSURES];
} dom_hazard_surface_desc;

typedef struct dom_hazard_type_sample {
    u32 type_id;
    u32 hazard_class;
    q16_16 default_intensity;
    q16_16 default_exposure_rate;
    q16_16 default_decay_rate;
    q16_16 default_uncertainty;
    u32 flags; /* dom_hazard_type_flags */
    dom_domain_query_meta meta;
} dom_hazard_type_sample;

typedef struct dom_hazard_field_sample {
    u32 hazard_id;
    u32 hazard_type_id;
    q16_16 intensity;
    q16_16 exposure_rate;
    q16_16 decay_rate;
    q16_16 uncertainty;
    u32 provenance_id;
    u32 region_id;
    q16_16 radius;
    u32 flags; /* dom_hazard_field_flags */
    dom_domain_query_meta meta;
} dom_hazard_field_sample;

typedef struct dom_hazard_exposure_sample {
    u32 exposure_id;
    u32 hazard_type_id;
    q48_16 exposure_limit;
    q16_16 sensitivity;
    q16_16 uncertainty;
    u32 provenance_id;
    u32 region_id;
    q48_16 exposure_accumulated;
    u32 flags; /* dom_hazard_exposure_flags */
    dom_domain_query_meta meta;
} dom_hazard_exposure_sample;

typedef struct dom_hazard_region_sample {
    u32 region_id;
    u32 field_count;
    u32 exposure_count;
    q48_16 hazard_energy_total;
    q48_16 exposure_total;
    u32 flags; /* dom_hazard_resolve_flags */
    dom_domain_query_meta meta;
} dom_hazard_region_sample;

typedef struct dom_hazard_resolve_result {
    u32 ok;
    u32 refusal_reason; /* dom_hazard_refusal_reason */
    u32 flags; /* dom_hazard_resolve_flags */
    u32 field_count;
    u32 exposure_count;
    u32 exposure_over_limit_count;
    q48_16 hazard_energy_total;
    q48_16 exposure_total;
} dom_hazard_resolve_result;

typedef struct dom_hazard_macro_capsule {
    u64 capsule_id;
    u32 region_id;
    u32 field_count;
    u32 exposure_count;
    q48_16 hazard_energy_total;
    u32 hazard_type_counts[DOM_HAZARD_CLASS_COUNT];
    q16_16 exposure_hist[DOM_HAZARD_HIST_BINS];
    u32 rng_cursor[DOM_HAZARD_CLASS_COUNT];
} dom_hazard_macro_capsule;

typedef struct dom_hazard_domain {
    dom_domain_policy policy;
    u32 existence_state;
    u32 archival_state;
    u32 authoring_version;
    dom_hazard_surface_desc surface;
    dom_hazard_type types[DOM_HAZARD_MAX_TYPES];
    u32 type_count;
    dom_hazard_field fields[DOM_HAZARD_MAX_FIELDS];
    u32 field_count;
    dom_hazard_exposure exposures[DOM_HAZARD_MAX_EXPOSURES];
    u32 exposure_count;
    dom_hazard_macro_capsule capsules[DOM_HAZARD_MAX_CAPSULES];
    u32 capsule_count;
} dom_hazard_domain;

void dom_hazard_surface_desc_init(dom_hazard_surface_desc* desc);

void dom_hazard_domain_init(dom_hazard_domain* domain,
                            const dom_hazard_surface_desc* desc);
void dom_hazard_domain_free(dom_hazard_domain* domain);
void dom_hazard_domain_set_state(dom_hazard_domain* domain,
                                 u32 existence_state,
                                 u32 archival_state);
void dom_hazard_domain_set_policy(dom_hazard_domain* domain,
                                  const dom_domain_policy* policy);

int dom_hazard_type_query(const dom_hazard_domain* domain,
                          u32 type_id,
                          dom_domain_budget* budget,
                          dom_hazard_type_sample* out_sample);

int dom_hazard_field_query(const dom_hazard_domain* domain,
                           u32 field_id,
                           dom_domain_budget* budget,
                           dom_hazard_field_sample* out_sample);

int dom_hazard_exposure_query(const dom_hazard_domain* domain,
                              u32 exposure_id,
                              dom_domain_budget* budget,
                              dom_hazard_exposure_sample* out_sample);

int dom_hazard_region_query(const dom_hazard_domain* domain,
                            u32 region_id,
                            dom_domain_budget* budget,
                            dom_hazard_region_sample* out_sample);

int dom_hazard_resolve(dom_hazard_domain* domain,
                       u32 region_id,
                       u64 tick,
                       u64 tick_delta,
                       dom_domain_budget* budget,
                       dom_hazard_resolve_result* out_result);

int dom_hazard_domain_collapse_region(dom_hazard_domain* domain, u32 region_id);
int dom_hazard_domain_expand_region(dom_hazard_domain* domain, u32 region_id);

u32 dom_hazard_domain_capsule_count(const dom_hazard_domain* domain);
const dom_hazard_macro_capsule* dom_hazard_domain_capsule_at(const dom_hazard_domain* domain,
                                                             u32 index);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINO_WORLD_HAZARD_FIELDS_H */
