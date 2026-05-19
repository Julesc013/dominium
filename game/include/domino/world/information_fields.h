/*
FILE: include/domino/world/information_fields.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / world/information_fields
RESPONSIBILITY: Deterministic information networks, data routing, and inspection.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 headers as needed.
FORBIDDEN DEPENDENCIES: Engine private headers outside `include/domino/**`.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: Fixed-point only; deterministic ordering and math.
VERSIONING / ABI / DATA FORMAT NOTES: Versioned by INFO0 specs.
EXTENSION POINTS: Extend via public headers and relevant `docs/architecture/**`.
*/
#ifndef DOMINO_WORLD_INFORMATION_FIELDS_H
#define DOMINO_WORLD_INFORMATION_FIELDS_H

#include "domino/core/types.h"
#include "domino/core/fixed.h"
#include "domino/world/domain_query.h"

#ifdef __cplusplus
extern "C" {
#endif

#define DOM_INFO_MAX_NODES 64u
#define DOM_INFO_MAX_LINKS 128u
#define DOM_INFO_MAX_DATA 256u
#define DOM_INFO_MAX_CAPACITY_PROFILES 64u
#define DOM_INFO_MAX_NETWORKS 16u
#define DOM_INFO_MAX_CAPSULES 64u
#define DOM_INFO_HIST_BINS 4u

#define DOM_INFO_RATIO_ONE_Q16 ((q16_16)0x00010000)

enum dom_info_node_type {
    DOM_INFO_NODE_UNSET = 0u,
    DOM_INFO_NODE_ROUTER = 1u,
    DOM_INFO_NODE_SWITCH = 2u,
    DOM_INFO_NODE_ANTENNA = 3u,
    DOM_INFO_NODE_SATELLITE = 4u,
    DOM_INFO_NODE_COMPUTE = 5u,
    DOM_INFO_NODE_STORAGE = 6u,
    DOM_INFO_NODE_ENDPOINT = 7u
};

enum dom_info_data_type {
    DOM_INFO_DATA_UNSET = 0u,
    DOM_INFO_DATA_CONTROL = 1u,
    DOM_INFO_DATA_TELEMETRY = 2u,
    DOM_INFO_DATA_MESSAGE = 3u,
    DOM_INFO_DATA_STORAGE = 4u
};

enum dom_info_latency_class {
    DOM_INFO_LATENCY_IMMEDIATE = 0u,
    DOM_INFO_LATENCY_LOCAL = 1u,
    DOM_INFO_LATENCY_REGIONAL = 2u,
    DOM_INFO_LATENCY_ORBITAL = 3u,
    DOM_INFO_LATENCY_INTERPLANETARY = 4u
};

enum dom_info_congestion_policy {
    DOM_INFO_CONGESTION_QUEUE = 0u,
    DOM_INFO_CONGESTION_DROP_NEWEST = 1u,
    DOM_INFO_CONGESTION_DROP_OLDEST = 2u,
    DOM_INFO_CONGESTION_DEGRADE = 3u
};

enum dom_info_link_direction {
    DOM_INFO_LINK_BIDIR = 0u,
    DOM_INFO_LINK_A_TO_B = 1u,
    DOM_INFO_LINK_B_TO_A = 2u
};

enum dom_info_node_flags {
    DOM_INFO_NODE_FLAG_COLLAPSED = 1u << 0u
};

enum dom_info_link_flags {
    DOM_INFO_LINK_FLAG_COLLAPSED = 1u << 0u,
    DOM_INFO_LINK_FLAG_CONGESTED = 1u << 1u,
    DOM_INFO_LINK_FLAG_OUTAGE = 1u << 2u,
    DOM_INFO_LINK_FLAG_CORRUPT = 1u << 3u
};

enum dom_info_data_flags {
    DOM_INFO_DATA_FLAG_PENDING = 1u << 0u,
    DOM_INFO_DATA_FLAG_DELIVERED = 1u << 1u,
    DOM_INFO_DATA_FLAG_DROPPED = 1u << 2u,
    DOM_INFO_DATA_FLAG_CORRUPT = 1u << 3u,
    DOM_INFO_DATA_FLAG_STORED = 1u << 4u,
    DOM_INFO_DATA_FLAG_QUEUED = 1u << 5u
};

enum dom_info_resolve_flags {
    DOM_INFO_RESOLVE_PARTIAL = 1u << 0u,
    DOM_INFO_RESOLVE_CONGESTED = 1u << 1u,
    DOM_INFO_RESOLVE_OUTAGE = 1u << 2u,
    DOM_INFO_RESOLVE_CORRUPT = 1u << 3u,
    DOM_INFO_RESOLVE_DROPPED = 1u << 4u
};

enum dom_info_refusal_reason {
    DOM_INFO_REFUSE_NONE = 0u,
    DOM_INFO_REFUSE_BUDGET = 1u,
    DOM_INFO_REFUSE_DOMAIN_INACTIVE = 2u,
    DOM_INFO_REFUSE_NODE_MISSING = 3u,
    DOM_INFO_REFUSE_LINK_MISSING = 4u,
    DOM_INFO_REFUSE_DATA_MISSING = 5u,
    DOM_INFO_REFUSE_CAPACITY_MISSING = 6u,
    DOM_INFO_REFUSE_POLICY = 7u,
    DOM_INFO_REFUSE_INTERNAL = 8u
};

typedef struct dom_info_capacity_desc {
    u32 capacity_id;
    q48_16 bandwidth_limit;
    u32 latency_class;
    q16_16 error_rate;
    u32 congestion_policy;
} dom_info_capacity_desc;

typedef struct dom_info_node_desc {
    u32 node_id;
    u32 node_type;
    q48_16 compute_capacity;
    q48_16 storage_capacity;
    q48_16 energy_per_unit;
    q48_16 heat_per_unit;
    u32 network_id;
    dom_domain_point location;
} dom_info_node_desc;

typedef struct dom_info_link_desc {
    u32 link_id;
    u32 network_id;
    u32 node_a_id;
    u32 node_b_id;
    u32 capacity_id;
    u32 direction;
} dom_info_link_desc;

typedef struct dom_info_data_desc {
    u32 data_id;
    u32 data_type;
    q48_16 data_size;
    q16_16 data_uncertainty;
    u32 source_node_id;
    u32 sink_node_id;
    u32 protocol_id;
    u32 network_id;
    u64 send_tick;
} dom_info_data_desc;

typedef struct dom_info_capacity {
    u32 capacity_id;
    q48_16 bandwidth_limit;
    u32 latency_class;
    q16_16 error_rate;
    u32 congestion_policy;
    u32 flags;
} dom_info_capacity;

typedef struct dom_info_node {
    u32 node_id;
    u32 node_type;
    q48_16 compute_capacity;
    q48_16 storage_capacity;
    q48_16 storage_used;
    q48_16 energy_per_unit;
    q48_16 heat_per_unit;
    u32 network_id;
    dom_domain_point location;
    u32 flags;
} dom_info_node;

typedef struct dom_info_link {
    u32 link_id;
    u32 network_id;
    u32 node_a_id;
    u32 node_b_id;
    u32 capacity_id;
    u32 direction;
    u32 flags;
} dom_info_link;

typedef struct dom_info_data {
    u32 data_id;
    u32 data_type;
    q48_16 data_size;
    q16_16 data_uncertainty;
    u32 source_node_id;
    u32 sink_node_id;
    u32 protocol_id;
    u32 network_id;
    u64 send_tick;
    u32 flags;
} dom_info_data;

typedef struct dom_info_surface_desc {
    dom_domain_id domain_id;
    u64 world_seed;
    q16_16 meters_per_unit;
    u32 capacity_count;
    dom_info_capacity_desc capacities[DOM_INFO_MAX_CAPACITY_PROFILES];
    u32 node_count;
    dom_info_node_desc nodes[DOM_INFO_MAX_NODES];
    u32 link_count;
    dom_info_link_desc links[DOM_INFO_MAX_LINKS];
    u32 data_count;
    dom_info_data_desc data[DOM_INFO_MAX_DATA];
} dom_info_surface_desc;

typedef struct dom_info_capacity_sample {
    u32 capacity_id;
    q48_16 bandwidth_limit;
    u32 latency_class;
    q16_16 error_rate;
    u32 congestion_policy;
    u32 flags;
    dom_domain_query_meta meta;
} dom_info_capacity_sample;

typedef struct dom_info_node_sample {
    u32 node_id;
    u32 node_type;
    q48_16 compute_capacity;
    q48_16 storage_capacity;
    q48_16 storage_used;
    q48_16 energy_per_unit;
    q48_16 heat_per_unit;
    u32 network_id;
    u32 flags;
    dom_domain_query_meta meta;
} dom_info_node_sample;

typedef struct dom_info_link_sample {
    u32 link_id;
    u32 network_id;
    u32 node_a_id;
    u32 node_b_id;
    u32 capacity_id;
    u32 direction;
    u32 flags;
    dom_domain_query_meta meta;
} dom_info_link_sample;

typedef struct dom_info_data_sample {
    u32 data_id;
    u32 data_type;
    q48_16 data_size;
    q16_16 data_uncertainty;
    u32 source_node_id;
    u32 sink_node_id;
    u32 protocol_id;
    u32 network_id;
    u64 send_tick;
    u32 flags;
    dom_domain_query_meta meta;
} dom_info_data_sample;

typedef struct dom_info_network_sample {
    u32 network_id;
    u32 node_count;
    u32 link_count;
    u32 data_count;
    q48_16 data_total;
    u32 queued_count;
    u32 dropped_count;
    q16_16 error_rate_avg;
    u32 flags; /* dom_info_resolve_flags */
    dom_domain_query_meta meta;
} dom_info_network_sample;

typedef struct dom_info_resolve_result {
    u32 ok;
    u32 refusal_reason; /* dom_info_refusal_reason */
    u32 flags;          /* dom_info_resolve_flags */
    u32 delivered_count;
    u32 dropped_count;
    u32 queued_count;
    q48_16 energy_cost_total;
    q48_16 heat_generated_total;
} dom_info_resolve_result;

typedef struct dom_info_macro_capsule {
    u64 capsule_id;
    u32 network_id;
    u32 node_count;
    u32 link_count;
    u32 data_count;
    q48_16 data_total;
    q16_16 error_rate_hist[DOM_INFO_HIST_BINS];
} dom_info_macro_capsule;

typedef struct dom_info_domain {
    dom_domain_policy policy;
    u32 existence_state;
    u32 archival_state;
    u32 authoring_version;
    dom_info_surface_desc surface;
    dom_info_capacity capacities[DOM_INFO_MAX_CAPACITY_PROFILES];
    u32 capacity_count;
    dom_info_node nodes[DOM_INFO_MAX_NODES];
    u32 node_count;
    dom_info_link links[DOM_INFO_MAX_LINKS];
    u32 link_count;
    dom_info_data data[DOM_INFO_MAX_DATA];
    u32 data_count;
    dom_info_macro_capsule capsules[DOM_INFO_MAX_CAPSULES];
    u32 capsule_count;
} dom_info_domain;

void dom_info_surface_desc_init(dom_info_surface_desc* desc);

void dom_info_domain_init(dom_info_domain* domain,
                          const dom_info_surface_desc* desc);
void dom_info_domain_free(dom_info_domain* domain);
void dom_info_domain_set_state(dom_info_domain* domain,
                               u32 existence_state,
                               u32 archival_state);
void dom_info_domain_set_policy(dom_info_domain* domain,
                                const dom_domain_policy* policy);

int dom_info_capacity_query(const dom_info_domain* domain,
                            u32 capacity_id,
                            dom_domain_budget* budget,
                            dom_info_capacity_sample* out_sample);

int dom_info_node_query(const dom_info_domain* domain,
                        u32 node_id,
                        dom_domain_budget* budget,
                        dom_info_node_sample* out_sample);

int dom_info_link_query(const dom_info_domain* domain,
                        u32 link_id,
                        dom_domain_budget* budget,
                        dom_info_link_sample* out_sample);

int dom_info_data_query(const dom_info_domain* domain,
                        u32 data_id,
                        dom_domain_budget* budget,
                        dom_info_data_sample* out_sample);

int dom_info_network_query(const dom_info_domain* domain,
                           u32 network_id,
                           dom_domain_budget* budget,
                           dom_info_network_sample* out_sample);

int dom_info_resolve(dom_info_domain* domain,
                     u32 network_id,
                     u64 tick,
                     u64 tick_delta,
                     dom_domain_budget* budget,
                     dom_info_resolve_result* out_result);

int dom_info_domain_collapse_network(dom_info_domain* domain, u32 network_id);
int dom_info_domain_expand_network(dom_info_domain* domain, u32 network_id);

u32 dom_info_domain_capsule_count(const dom_info_domain* domain);
const dom_info_macro_capsule* dom_info_domain_capsule_at(const dom_info_domain* domain,
                                                         u32 index);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINO_WORLD_INFORMATION_FIELDS_H */
