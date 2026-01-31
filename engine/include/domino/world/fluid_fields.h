/*
FILE: include/domino/world/fluid_fields.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / world/fluid_fields
RESPONSIBILITY: Deterministic fluid stores, flows, pressure, and containment resolution.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 headers as needed.
FORBIDDEN DEPENDENCIES: Engine private headers outside `include/domino/**`.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: Fixed-point only; deterministic ordering and math.
VERSIONING / ABI / DATA FORMAT NOTES: Versioned by FLUIDS0 specs.
EXTENSION POINTS: Extend via public headers and relevant `docs/architecture/**`.
*/
#ifndef DOMINO_WORLD_FLUID_FIELDS_H
#define DOMINO_WORLD_FLUID_FIELDS_H

#include "domino/core/types.h"
#include "domino/core/fixed.h"
#include "domino/world/domain_query.h"

#ifdef __cplusplus
extern "C" {
#endif

#define DOM_FLUID_MAX_STORES 64u
#define DOM_FLUID_MAX_FLOWS 128u
#define DOM_FLUID_MAX_PRESSURES 64u
#define DOM_FLUID_MAX_PROPERTIES 32u
#define DOM_FLUID_MAX_NETWORKS 16u
#define DOM_FLUID_MAX_CAPSULES 64u
#define DOM_FLUID_HIST_BINS 4u

#define DOM_FLUID_RATIO_ONE_Q16 ((q16_16)0x00010000)

enum dom_fluid_type {
    DOM_FLUID_TYPE_UNSET = 0u,
    DOM_FLUID_TYPE_WATER = 1u,
    DOM_FLUID_TYPE_OIL = 2u,
    DOM_FLUID_TYPE_GAS = 3u,
    DOM_FLUID_TYPE_LAVA = 4u,
    DOM_FLUID_TYPE_ABSTRACT = 5u
};

enum dom_fluid_failure_mode {
    DOM_FLUID_FAILURE_OVERLOAD = 1u << 0u,
    DOM_FLUID_FAILURE_BLOCKED = 1u << 1u,
    DOM_FLUID_FAILURE_LEAKAGE = 1u << 2u,
    DOM_FLUID_FAILURE_CASCADE = 1u << 3u
};

enum dom_fluid_store_flags {
    DOM_FLUID_STORE_UNRESOLVED = 1u << 0u,
    DOM_FLUID_STORE_COLLAPSED = 1u << 1u,
    DOM_FLUID_STORE_RUPTURED = 1u << 2u
};

enum dom_fluid_flow_flags {
    DOM_FLUID_FLOW_UNRESOLVED = 1u << 0u,
    DOM_FLUID_FLOW_COLLAPSED = 1u << 1u,
    DOM_FLUID_FLOW_OVERLOAD = 1u << 2u,
    DOM_FLUID_FLOW_BLOCKED = 1u << 3u,
    DOM_FLUID_FLOW_LEAKAGE = 1u << 4u,
    DOM_FLUID_FLOW_CASCADE = 1u << 5u,
    DOM_FLUID_FLOW_RUPTURE = 1u << 6u
};

enum dom_fluid_pressure_flags {
    DOM_FLUID_PRESSURE_UNRESOLVED = 1u << 0u,
    DOM_FLUID_PRESSURE_OVER_LIMIT = 1u << 1u,
    DOM_FLUID_PRESSURE_RUPTURED = 1u << 2u
};

enum dom_fluid_property_flags {
    DOM_FLUID_PROPERTY_UNRESOLVED = 1u << 0u
};

enum dom_fluid_resolve_flags {
    DOM_FLUID_RESOLVE_PARTIAL = 1u << 0u,
    DOM_FLUID_RESOLVE_OVERLOAD = 1u << 1u,
    DOM_FLUID_RESOLVE_BLOCKED = 1u << 2u,
    DOM_FLUID_RESOLVE_LEAKAGE = 1u << 3u,
    DOM_FLUID_RESOLVE_CASCADE = 1u << 4u,
    DOM_FLUID_RESOLVE_RUPTURE = 1u << 5u,
    DOM_FLUID_RESOLVE_PRESSURE_OVER = 1u << 6u
};

enum dom_fluid_refusal_reason {
    DOM_FLUID_REFUSE_NONE = 0u,
    DOM_FLUID_REFUSE_BUDGET = 1u,
    DOM_FLUID_REFUSE_DOMAIN_INACTIVE = 2u,
    DOM_FLUID_REFUSE_STORE_MISSING = 3u,
    DOM_FLUID_REFUSE_FLOW_MISSING = 4u,
    DOM_FLUID_REFUSE_PRESSURE_MISSING = 5u,
    DOM_FLUID_REFUSE_PROPERTY_MISSING = 6u,
    DOM_FLUID_REFUSE_CAPACITY = 7u,
    DOM_FLUID_REFUSE_INSUFFICIENT = 8u,
    DOM_FLUID_REFUSE_POLICY = 9u,
    DOM_FLUID_REFUSE_INTERNAL = 10u
};

typedef struct dom_fluid_store_desc {
    u32 store_id;
    u32 fluid_type;
    q48_16 volume;
    q48_16 max_volume;
    q48_16 temperature;
    q16_16 contamination;
    q16_16 leakage_rate;
    u32 network_id;
    dom_domain_point location;
} dom_fluid_store_desc;

typedef struct dom_fluid_flow_desc {
    u32 flow_id;
    u32 network_id;
    u32 source_store_id;
    u32 sink_store_id;
    q48_16 max_transfer_rate;
    q16_16 efficiency;
    u64 latency_ticks;
    u32 failure_mode_mask;
    q16_16 failure_chance;
    q48_16 energy_per_volume;
} dom_fluid_flow_desc;

typedef struct dom_fluid_pressure_desc {
    u32 pressure_id;
    u32 store_id;
    q48_16 pressure_limit;
    q48_16 rupture_threshold;
    q16_16 release_ratio;
} dom_fluid_pressure_desc;

typedef struct dom_fluid_property_desc {
    u32 property_id;
    u32 fluid_type;
    q48_16 density;
    u32 viscosity_class;
    u32 compressibility_class;
    u32 hazard_profile;
} dom_fluid_property_desc;

typedef struct dom_fluid_store {
    u32 store_id;
    u32 fluid_type;
    q48_16 volume;
    q48_16 max_volume;
    q48_16 temperature;
    q16_16 contamination;
    q16_16 leakage_rate;
    u32 network_id;
    dom_domain_point location;
    u32 flags; /* dom_fluid_store_flags */
} dom_fluid_store;

typedef struct dom_fluid_flow {
    u32 flow_id;
    u32 network_id;
    u32 source_store_id;
    u32 sink_store_id;
    q48_16 max_transfer_rate;
    q16_16 efficiency;
    u64 latency_ticks;
    u32 failure_mode_mask;
    q16_16 failure_chance;
    q48_16 energy_per_volume;
    u32 flags; /* dom_fluid_flow_flags */
} dom_fluid_flow;

typedef struct dom_fluid_pressure {
    u32 pressure_id;
    u32 store_id;
    q48_16 amount;
    q48_16 pressure_limit;
    q48_16 rupture_threshold;
    q16_16 release_ratio;
    u32 flags; /* dom_fluid_pressure_flags */
} dom_fluid_pressure;

typedef struct dom_fluid_property {
    u32 property_id;
    u32 fluid_type;
    q48_16 density;
    u32 viscosity_class;
    u32 compressibility_class;
    u32 hazard_profile;
    u32 flags; /* dom_fluid_property_flags */
} dom_fluid_property;

typedef struct dom_fluid_surface_desc {
    dom_domain_id domain_id;
    u64 world_seed;
    q16_16 meters_per_unit;
    q48_16 pressure_scale;
    u32 store_count;
    dom_fluid_store_desc stores[DOM_FLUID_MAX_STORES];
    u32 flow_count;
    dom_fluid_flow_desc flows[DOM_FLUID_MAX_FLOWS];
    u32 pressure_count;
    dom_fluid_pressure_desc pressures[DOM_FLUID_MAX_PRESSURES];
    u32 property_count;
    dom_fluid_property_desc properties[DOM_FLUID_MAX_PROPERTIES];
} dom_fluid_surface_desc;

typedef struct dom_fluid_store_sample {
    u32 store_id;
    u32 fluid_type;
    q48_16 volume;
    q48_16 max_volume;
    q48_16 temperature;
    q16_16 contamination;
    q16_16 leakage_rate;
    u32 network_id;
    u32 flags; /* dom_fluid_store_flags */
    dom_domain_query_meta meta;
} dom_fluid_store_sample;

typedef struct dom_fluid_flow_sample {
    u32 flow_id;
    u32 network_id;
    u32 source_store_id;
    u32 sink_store_id;
    q48_16 max_transfer_rate;
    q16_16 efficiency;
    u64 latency_ticks;
    u32 failure_mode_mask;
    q16_16 failure_chance;
    q48_16 energy_per_volume;
    u32 flags; /* dom_fluid_flow_flags */
    dom_domain_query_meta meta;
} dom_fluid_flow_sample;

typedef struct dom_fluid_pressure_sample {
    u32 pressure_id;
    u32 store_id;
    q48_16 amount;
    q48_16 pressure_limit;
    q48_16 rupture_threshold;
    q16_16 release_ratio;
    u32 flags; /* dom_fluid_pressure_flags */
    dom_domain_query_meta meta;
} dom_fluid_pressure_sample;

typedef struct dom_fluid_property_sample {
    u32 property_id;
    u32 fluid_type;
    q48_16 density;
    u32 viscosity_class;
    u32 compressibility_class;
    u32 hazard_profile;
    u32 flags; /* dom_fluid_property_flags */
    dom_domain_query_meta meta;
} dom_fluid_property_sample;

typedef struct dom_fluid_network_sample {
    u32 network_id;
    u32 store_count;
    u32 flow_count;
    q48_16 volume_total;
    q48_16 capacity_total;
    q48_16 pressure_total;
    q16_16 contamination_avg;
    u32 flags; /* dom_fluid_resolve_flags */
    dom_domain_query_meta meta;
} dom_fluid_network_sample;

typedef struct dom_fluid_resolve_result {
    u32 ok;
    u32 refusal_reason; /* dom_fluid_refusal_reason */
    u32 flags; /* dom_fluid_resolve_flags */
    u32 flow_count;
    u32 store_count;
    u32 pressure_count;
    u32 pressure_over_limit_count;
    u32 pressure_rupture_count;
    q48_16 volume_transferred;
    q48_16 volume_leaked;
    q48_16 volume_remaining;
    q48_16 energy_required;
} dom_fluid_resolve_result;

typedef struct dom_fluid_macro_capsule {
    u64 capsule_id;
    u32 network_id;
    u32 store_count;
    u32 flow_count;
    q48_16 volume_total;
    q48_16 capacity_total;
    q16_16 pressure_ratio_hist[DOM_FLUID_HIST_BINS];
    q16_16 contamination_ratio_hist[DOM_FLUID_HIST_BINS];
    q48_16 transfer_rate_total;
    q48_16 leakage_rate_total;
} dom_fluid_macro_capsule;

typedef struct dom_fluid_domain {
    dom_domain_policy policy;
    u32 existence_state;
    u32 archival_state;
    u32 authoring_version;
    dom_fluid_surface_desc surface;
    dom_fluid_store stores[DOM_FLUID_MAX_STORES];
    u32 store_count;
    dom_fluid_flow flows[DOM_FLUID_MAX_FLOWS];
    u32 flow_count;
    dom_fluid_pressure pressures[DOM_FLUID_MAX_PRESSURES];
    u32 pressure_count;
    dom_fluid_property properties[DOM_FLUID_MAX_PROPERTIES];
    u32 property_count;
    dom_fluid_macro_capsule capsules[DOM_FLUID_MAX_CAPSULES];
    u32 capsule_count;
} dom_fluid_domain;

void dom_fluid_surface_desc_init(dom_fluid_surface_desc* desc);

void dom_fluid_domain_init(dom_fluid_domain* domain,
                           const dom_fluid_surface_desc* desc);
void dom_fluid_domain_free(dom_fluid_domain* domain);
void dom_fluid_domain_set_state(dom_fluid_domain* domain,
                                u32 existence_state,
                                u32 archival_state);
void dom_fluid_domain_set_policy(dom_fluid_domain* domain,
                                 const dom_domain_policy* policy);

int dom_fluid_store_query(const dom_fluid_domain* domain,
                          u32 store_id,
                          dom_domain_budget* budget,
                          dom_fluid_store_sample* out_sample);

int dom_fluid_flow_query(const dom_fluid_domain* domain,
                         u32 flow_id,
                         dom_domain_budget* budget,
                         dom_fluid_flow_sample* out_sample);

int dom_fluid_pressure_query(const dom_fluid_domain* domain,
                             u32 pressure_id,
                             dom_domain_budget* budget,
                             dom_fluid_pressure_sample* out_sample);

int dom_fluid_property_query(const dom_fluid_domain* domain,
                             u32 property_id,
                             dom_domain_budget* budget,
                             dom_fluid_property_sample* out_sample);

int dom_fluid_network_query(const dom_fluid_domain* domain,
                            u32 network_id,
                            dom_domain_budget* budget,
                            dom_fluid_network_sample* out_sample);

int dom_fluid_resolve(dom_fluid_domain* domain,
                      u32 network_id,
                      u64 tick,
                      u64 tick_delta,
                      dom_domain_budget* budget,
                      dom_fluid_resolve_result* out_result);

int dom_fluid_domain_collapse_network(dom_fluid_domain* domain, u32 network_id);
int dom_fluid_domain_expand_network(dom_fluid_domain* domain, u32 network_id);

u32 dom_fluid_domain_capsule_count(const dom_fluid_domain* domain);
const dom_fluid_macro_capsule* dom_fluid_domain_capsule_at(const dom_fluid_domain* domain,
                                                           u32 index);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINO_WORLD_FLUID_FIELDS_H */
