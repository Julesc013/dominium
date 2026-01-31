/*
FILE: include/domino/world/heat_fields.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / world/heat_fields
RESPONSIBILITY: Deterministic heat stores, flows, and thermal stress resolution.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 headers as needed.
FORBIDDEN DEPENDENCIES: Engine private headers outside `include/domino/**`.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: Fixed-point only; deterministic ordering and math.
VERSIONING / ABI / DATA FORMAT NOTES: Versioned by THERMAL0 specs.
EXTENSION POINTS: Extend via public headers and relevant `docs/architecture/**`.
*/
#ifndef DOMINO_WORLD_HEAT_FIELDS_H
#define DOMINO_WORLD_HEAT_FIELDS_H

#include "domino/core/types.h"
#include "domino/core/fixed.h"
#include "domino/world/domain_query.h"

#ifdef __cplusplus
extern "C" {
#endif

#define DOM_HEAT_MAX_STORES 64u
#define DOM_HEAT_MAX_FLOWS 128u
#define DOM_HEAT_MAX_STRESSES 64u
#define DOM_HEAT_MAX_NETWORKS 16u
#define DOM_HEAT_MAX_CAPSULES 64u
#define DOM_HEAT_HIST_BINS 4u

#define DOM_HEAT_RATIO_ONE_Q16 ((q16_16)0x00010000)

enum dom_heat_failure_mode {
    DOM_HEAT_FAILURE_OVERLOAD = 1u << 0u,
    DOM_HEAT_FAILURE_BLOCKED = 1u << 1u,
    DOM_HEAT_FAILURE_LEAKAGE = 1u << 2u,
    DOM_HEAT_FAILURE_CASCADE = 1u << 3u
};

enum dom_heat_store_flags {
    DOM_HEAT_STORE_UNKNOWN = 1u << 0u,
    DOM_HEAT_STORE_COLLAPSED = 1u << 1u
};

enum dom_heat_flow_flags {
    DOM_HEAT_FLOW_UNKNOWN = 1u << 0u,
    DOM_HEAT_FLOW_COLLAPSED = 1u << 1u,
    DOM_HEAT_FLOW_OVERLOAD = 1u << 2u,
    DOM_HEAT_FLOW_BLOCKED = 1u << 3u,
    DOM_HEAT_FLOW_LEAKAGE = 1u << 4u,
    DOM_HEAT_FLOW_CASCADE = 1u << 5u
};

enum dom_heat_stress_flags {
    DOM_THERMAL_STRESS_UNKNOWN = 1u << 0u,
    DOM_THERMAL_STRESS_OVERHEAT = 1u << 1u,
    DOM_THERMAL_STRESS_UNDERCOOL = 1u << 2u,
    DOM_THERMAL_STRESS_DAMAGE = 1u << 3u,
    DOM_THERMAL_STRESS_EFFICIENCY_LOSS = 1u << 4u,
    DOM_THERMAL_STRESS_SHUTDOWN = 1u << 5u
};

enum dom_heat_resolve_flags {
    DOM_HEAT_RESOLVE_PARTIAL = 1u << 0u,
    DOM_HEAT_RESOLVE_OVERHEAT = 1u << 1u,
    DOM_HEAT_RESOLVE_UNDERCOOL = 1u << 2u,
    DOM_HEAT_RESOLVE_DAMAGE = 1u << 3u,
    DOM_HEAT_RESOLVE_LEAKAGE = 1u << 4u,
    DOM_HEAT_RESOLVE_CASCADE = 1u << 5u,
    DOM_HEAT_RESOLVE_OVERLOAD = 1u << 6u,
    DOM_HEAT_RESOLVE_BLOCKED = 1u << 7u
};

enum dom_heat_refusal_reason {
    DOM_HEAT_REFUSE_NONE = 0u,
    DOM_HEAT_REFUSE_BUDGET = 1u,
    DOM_HEAT_REFUSE_DOMAIN_INACTIVE = 2u,
    DOM_HEAT_REFUSE_STORE_MISSING = 3u,
    DOM_HEAT_REFUSE_FLOW_MISSING = 4u,
    DOM_HEAT_REFUSE_STRESS_MISSING = 5u,
    DOM_HEAT_REFUSE_CAPACITY = 6u,
    DOM_HEAT_REFUSE_INSUFFICIENT = 7u,
    DOM_HEAT_REFUSE_POLICY = 8u,
    DOM_HEAT_REFUSE_INTERNAL = 9u
};

typedef struct dom_heat_store_desc {
    u32 store_id;
    q48_16 amount;
    q48_16 capacity;
    q16_16 ambient_exchange_rate;
    u32 network_id;
    dom_domain_point location;
} dom_heat_store_desc;

typedef struct dom_heat_flow_desc {
    u32 flow_id;
    u32 network_id;
    u32 source_store_id;
    u32 sink_store_id;
    q48_16 max_transfer_rate;
    q16_16 efficiency;
    u64 latency_ticks;
    u32 failure_mode_mask;
    q16_16 failure_chance;
} dom_heat_flow_desc;

typedef struct dom_thermal_stress_desc {
    u32 stress_id;
    u32 store_id;
    q48_16 safe_min;
    q48_16 safe_max;
    q16_16 damage_rate;
    q16_16 efficiency_modifier;
} dom_thermal_stress_desc;

typedef struct dom_heat_store {
    u32 store_id;
    q48_16 amount;
    q48_16 capacity;
    q16_16 ambient_exchange_rate;
    u32 network_id;
    dom_domain_point location;
    u32 flags; /* dom_heat_store_flags */
} dom_heat_store;

typedef struct dom_heat_flow {
    u32 flow_id;
    u32 network_id;
    u32 source_store_id;
    u32 sink_store_id;
    q48_16 max_transfer_rate;
    q16_16 efficiency;
    u64 latency_ticks;
    u32 failure_mode_mask;
    q16_16 failure_chance;
    u32 flags; /* dom_heat_flow_flags */
} dom_heat_flow;

typedef struct dom_thermal_stress {
    u32 stress_id;
    u32 store_id;
    q48_16 safe_min;
    q48_16 safe_max;
    q16_16 damage_rate;
    q16_16 efficiency_modifier;
    u32 flags; /* dom_heat_stress_flags */
} dom_thermal_stress;

typedef struct dom_heat_surface_desc {
    dom_domain_id domain_id;
    u64 world_seed;
    q16_16 meters_per_unit;
    q48_16 temperature_scale;
    u32 store_count;
    dom_heat_store_desc stores[DOM_HEAT_MAX_STORES];
    u32 flow_count;
    dom_heat_flow_desc flows[DOM_HEAT_MAX_FLOWS];
    u32 stress_count;
    dom_thermal_stress_desc stresses[DOM_HEAT_MAX_STRESSES];
} dom_heat_surface_desc;

typedef struct dom_heat_store_sample {
    u32 store_id;
    q48_16 amount;
    q48_16 capacity;
    q16_16 ambient_exchange_rate;
    u32 network_id;
    u32 flags; /* dom_heat_store_flags */
    dom_domain_query_meta meta;
} dom_heat_store_sample;

typedef struct dom_heat_flow_sample {
    u32 flow_id;
    u32 network_id;
    u32 source_store_id;
    u32 sink_store_id;
    q48_16 max_transfer_rate;
    q16_16 efficiency;
    u64 latency_ticks;
    u32 failure_mode_mask;
    q16_16 failure_chance;
    u32 flags; /* dom_heat_flow_flags */
    dom_domain_query_meta meta;
} dom_heat_flow_sample;

typedef struct dom_thermal_stress_sample {
    u32 stress_id;
    u32 store_id;
    q48_16 operating_temperature;
    q48_16 safe_min;
    q48_16 safe_max;
    q16_16 damage_rate;
    q16_16 efficiency_modifier;
    u32 flags; /* dom_heat_stress_flags */
    dom_domain_query_meta meta;
} dom_thermal_stress_sample;

typedef struct dom_heat_network_sample {
    u32 network_id;
    u32 store_count;
    u32 flow_count;
    q48_16 heat_total;
    q48_16 capacity_total;
    q48_16 dissipated_total;
    u32 flags; /* dom_heat_resolve_flags */
    dom_domain_query_meta meta;
} dom_heat_network_sample;

typedef struct dom_heat_resolve_result {
    u32 ok;
    u32 refusal_reason; /* dom_heat_refusal_reason */
    u32 flags; /* dom_heat_resolve_flags */
    u32 flow_count;
    u32 store_count;
    u32 stress_count;
    u32 stress_overheat_count;
    u32 stress_undercool_count;
    u32 stress_damage_count;
    q48_16 heat_transferred;
    q48_16 heat_dissipated;
    q48_16 heat_remaining;
} dom_heat_resolve_result;

typedef struct dom_heat_macro_capsule {
    u64 capsule_id;
    u32 network_id;
    u32 store_count;
    u32 flow_count;
    q48_16 heat_total;
    q48_16 capacity_total;
    q16_16 temperature_ratio_hist[DOM_HEAT_HIST_BINS];
    q48_16 transfer_rate_total;
    q48_16 dissipation_rate_total;
} dom_heat_macro_capsule;

typedef struct dom_heat_domain {
    dom_domain_policy policy;
    u32 existence_state;
    u32 archival_state;
    u32 authoring_version;
    dom_heat_surface_desc surface;
    dom_heat_store stores[DOM_HEAT_MAX_STORES];
    u32 store_count;
    dom_heat_flow flows[DOM_HEAT_MAX_FLOWS];
    u32 flow_count;
    dom_thermal_stress stresses[DOM_HEAT_MAX_STRESSES];
    u32 stress_count;
    dom_heat_macro_capsule capsules[DOM_HEAT_MAX_CAPSULES];
    u32 capsule_count;
} dom_heat_domain;

void dom_heat_surface_desc_init(dom_heat_surface_desc* desc);

void dom_heat_domain_init(dom_heat_domain* domain,
                          const dom_heat_surface_desc* desc);
void dom_heat_domain_free(dom_heat_domain* domain);
void dom_heat_domain_set_state(dom_heat_domain* domain,
                               u32 existence_state,
                               u32 archival_state);
void dom_heat_domain_set_policy(dom_heat_domain* domain,
                                const dom_domain_policy* policy);

int dom_heat_store_query(const dom_heat_domain* domain,
                         u32 store_id,
                         dom_domain_budget* budget,
                         dom_heat_store_sample* out_sample);

int dom_heat_flow_query(const dom_heat_domain* domain,
                        u32 flow_id,
                        dom_domain_budget* budget,
                        dom_heat_flow_sample* out_sample);

int dom_heat_stress_query(const dom_heat_domain* domain,
                          u32 stress_id,
                          dom_domain_budget* budget,
                          dom_thermal_stress_sample* out_sample);

int dom_heat_network_query(const dom_heat_domain* domain,
                           u32 network_id,
                           dom_domain_budget* budget,
                           dom_heat_network_sample* out_sample);

int dom_heat_resolve(dom_heat_domain* domain,
                     u32 network_id,
                     u64 tick,
                     u64 tick_delta,
                     dom_domain_budget* budget,
                     dom_heat_resolve_result* out_result);

int dom_heat_domain_collapse_network(dom_heat_domain* domain, u32 network_id);
int dom_heat_domain_expand_network(dom_heat_domain* domain, u32 network_id);

u32 dom_heat_domain_capsule_count(const dom_heat_domain* domain);
const dom_heat_macro_capsule* dom_heat_domain_capsule_at(const dom_heat_domain* domain,
                                                         u32 index);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINO_WORLD_HEAT_FIELDS_H */
