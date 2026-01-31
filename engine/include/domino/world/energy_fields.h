/*
FILE: include/domino/world/energy_fields.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / world/energy_fields
RESPONSIBILITY: Deterministic energy stores, flows, and event-driven resolution.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 headers as needed.
FORBIDDEN DEPENDENCIES: Engine private headers outside `include/domino/**`.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: Fixed-point only; deterministic ordering and math.
VERSIONING / ABI / DATA FORMAT NOTES: Versioned by ENERGY0 specs.
EXTENSION POINTS: Extend via public headers and relevant `docs/architecture/**`.
*/
#ifndef DOMINO_WORLD_ENERGY_FIELDS_H
#define DOMINO_WORLD_ENERGY_FIELDS_H

#include "domino/core/types.h"
#include "domino/core/fixed.h"
#include "domino/world/domain_query.h"

#ifdef __cplusplus
extern "C" {
#endif

#define DOM_ENERGY_MAX_STORES 64u
#define DOM_ENERGY_MAX_FLOWS 128u
#define DOM_ENERGY_MAX_NETWORKS 16u
#define DOM_ENERGY_MAX_CAPSULES 64u
#define DOM_ENERGY_HIST_BINS 4u

#define DOM_ENERGY_RATIO_ONE_Q16 ((q16_16)0x00010000)

enum dom_energy_type {
    DOM_ENERGY_TYPE_UNSET = 0u,
    DOM_ENERGY_TYPE_ELECTRICAL = 1u,
    DOM_ENERGY_TYPE_CHEMICAL = 2u,
    DOM_ENERGY_TYPE_MECHANICAL = 3u,
    DOM_ENERGY_TYPE_THERMAL = 4u,
    DOM_ENERGY_TYPE_ABSTRACT = 5u
};

enum dom_energy_failure_mode {
    DOM_ENERGY_FAILURE_OVERLOAD = 1u << 0u,
    DOM_ENERGY_FAILURE_BROWNOUT = 1u << 1u,
    DOM_ENERGY_FAILURE_BLACKOUT = 1u << 2u,
    DOM_ENERGY_FAILURE_CASCADE = 1u << 3u,
    DOM_ENERGY_FAILURE_LEAKAGE = 1u << 4u
};

enum dom_energy_store_flags {
    DOM_ENERGY_STORE_UNKNOWN = 1u << 0u,
    DOM_ENERGY_STORE_COLLAPSED = 1u << 1u
};

enum dom_energy_flow_flags {
    DOM_ENERGY_FLOW_UNKNOWN = 1u << 0u,
    DOM_ENERGY_FLOW_COLLAPSED = 1u << 1u,
    DOM_ENERGY_FLOW_OVERLOAD = 1u << 2u,
    DOM_ENERGY_FLOW_BROWNOUT = 1u << 3u,
    DOM_ENERGY_FLOW_BLACKOUT = 1u << 4u,
    DOM_ENERGY_FLOW_CASCADE = 1u << 5u,
    DOM_ENERGY_FLOW_LEAKAGE = 1u << 6u
};

enum dom_energy_resolve_flags {
    DOM_ENERGY_RESOLVE_PARTIAL = 1u << 0u,
    DOM_ENERGY_RESOLVE_OVERLOAD = 1u << 1u,
    DOM_ENERGY_RESOLVE_BROWNOUT = 1u << 2u,
    DOM_ENERGY_RESOLVE_BLACKOUT = 1u << 3u,
    DOM_ENERGY_RESOLVE_CASCADE = 1u << 4u,
    DOM_ENERGY_RESOLVE_LEAKAGE = 1u << 5u
};

enum dom_energy_refusal_reason {
    DOM_ENERGY_REFUSE_NONE = 0u,
    DOM_ENERGY_REFUSE_BUDGET = 1u,
    DOM_ENERGY_REFUSE_DOMAIN_INACTIVE = 2u,
    DOM_ENERGY_REFUSE_STORE_MISSING = 3u,
    DOM_ENERGY_REFUSE_FLOW_MISSING = 4u,
    DOM_ENERGY_REFUSE_CAPACITY = 5u,
    DOM_ENERGY_REFUSE_INSUFFICIENT = 6u,
    DOM_ENERGY_REFUSE_POLICY = 7u,
    DOM_ENERGY_REFUSE_INTERNAL = 8u
};

typedef struct dom_energy_store_desc {
    u32 store_id;
    u32 energy_type;
    q48_16 amount;
    q48_16 capacity;
    q16_16 leakage_rate;
    u32 network_id;
    dom_domain_point location;
} dom_energy_store_desc;

typedef struct dom_energy_flow_desc {
    u32 flow_id;
    u32 network_id;
    u32 source_store_id;
    u32 sink_store_id;
    q48_16 max_transfer_rate;
    q16_16 efficiency;
    u64 latency_ticks;
    u32 failure_mode_mask;
    q16_16 failure_chance;
} dom_energy_flow_desc;

typedef struct dom_energy_loss_desc {
    q16_16 dissipation_fraction;
    u32 destination_type;
} dom_energy_loss_desc;

typedef struct dom_energy_store {
    u32 store_id;
    u32 energy_type;
    q48_16 amount;
    q48_16 capacity;
    q16_16 leakage_rate;
    u32 network_id;
    dom_domain_point location;
    u32 flags; /* dom_energy_store_flags */
} dom_energy_store;

typedef struct dom_energy_flow {
    u32 flow_id;
    u32 network_id;
    u32 source_store_id;
    u32 sink_store_id;
    q48_16 max_transfer_rate;
    q16_16 efficiency;
    u64 latency_ticks;
    u32 failure_mode_mask;
    q16_16 failure_chance;
    u32 flags; /* dom_energy_flow_flags */
} dom_energy_flow;

typedef struct dom_energy_surface_desc {
    dom_domain_id domain_id;
    u64 world_seed;
    q16_16 meters_per_unit;
    u32 store_count;
    dom_energy_store_desc stores[DOM_ENERGY_MAX_STORES];
    u32 flow_count;
    dom_energy_flow_desc flows[DOM_ENERGY_MAX_FLOWS];
    dom_energy_loss_desc loss;
} dom_energy_surface_desc;

typedef struct dom_energy_store_sample {
    u32 store_id;
    u32 energy_type;
    q48_16 amount;
    q48_16 capacity;
    q16_16 leakage_rate;
    u32 network_id;
    u32 flags; /* dom_energy_store_flags */
    dom_domain_query_meta meta;
} dom_energy_store_sample;

typedef struct dom_energy_flow_sample {
    u32 flow_id;
    u32 network_id;
    u32 source_store_id;
    u32 sink_store_id;
    q48_16 max_transfer_rate;
    q16_16 efficiency;
    u64 latency_ticks;
    u32 failure_mode_mask;
    q16_16 failure_chance;
    u32 flags; /* dom_energy_flow_flags */
    dom_domain_query_meta meta;
} dom_energy_flow_sample;

typedef struct dom_energy_network_sample {
    u32 network_id;
    u32 store_count;
    u32 flow_count;
    q48_16 energy_total;
    q48_16 capacity_total;
    q48_16 loss_total;
    u32 flags; /* dom_energy_resolve_flags */
    dom_domain_query_meta meta;
} dom_energy_network_sample;

typedef struct dom_energy_resolve_result {
    u32 ok;
    u32 refusal_reason; /* dom_energy_refusal_reason */
    u32 flags; /* dom_energy_resolve_flags */
    u32 flow_count;
    u32 store_count;
    q48_16 energy_transferred;
    q48_16 energy_lost;
    q48_16 energy_remaining;
} dom_energy_resolve_result;

typedef struct dom_energy_macro_capsule {
    u64 capsule_id;
    u32 network_id;
    u32 store_count;
    u32 flow_count;
    q48_16 energy_total;
    q48_16 capacity_total;
    q16_16 energy_ratio_hist[DOM_ENERGY_HIST_BINS];
    q48_16 transfer_rate_total;
    q48_16 loss_rate_total;
} dom_energy_macro_capsule;

typedef struct dom_energy_domain {
    dom_domain_policy policy;
    u32 existence_state;
    u32 archival_state;
    u32 authoring_version;
    dom_energy_surface_desc surface;
    dom_energy_store stores[DOM_ENERGY_MAX_STORES];
    u32 store_count;
    dom_energy_flow flows[DOM_ENERGY_MAX_FLOWS];
    u32 flow_count;
    dom_energy_macro_capsule capsules[DOM_ENERGY_MAX_CAPSULES];
    u32 capsule_count;
} dom_energy_domain;

void dom_energy_surface_desc_init(dom_energy_surface_desc* desc);

void dom_energy_domain_init(dom_energy_domain* domain,
                            const dom_energy_surface_desc* desc);
void dom_energy_domain_free(dom_energy_domain* domain);
void dom_energy_domain_set_state(dom_energy_domain* domain,
                                 u32 existence_state,
                                 u32 archival_state);
void dom_energy_domain_set_policy(dom_energy_domain* domain,
                                  const dom_domain_policy* policy);

int dom_energy_store_query(const dom_energy_domain* domain,
                           u32 store_id,
                           dom_domain_budget* budget,
                           dom_energy_store_sample* out_sample);

int dom_energy_flow_query(const dom_energy_domain* domain,
                          u32 flow_id,
                          dom_domain_budget* budget,
                          dom_energy_flow_sample* out_sample);

int dom_energy_network_query(const dom_energy_domain* domain,
                             u32 network_id,
                             dom_domain_budget* budget,
                             dom_energy_network_sample* out_sample);

int dom_energy_resolve(dom_energy_domain* domain,
                       u32 network_id,
                       u64 tick,
                       u64 tick_delta,
                       dom_domain_budget* budget,
                       dom_energy_resolve_result* out_result);

int dom_energy_domain_collapse_network(dom_energy_domain* domain, u32 network_id);
int dom_energy_domain_expand_network(dom_energy_domain* domain, u32 network_id);

u32 dom_energy_domain_capsule_count(const dom_energy_domain* domain);
const dom_energy_macro_capsule* dom_energy_domain_capsule_at(const dom_energy_domain* domain,
                                                             u32 index);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINO_WORLD_ENERGY_FIELDS_H */
