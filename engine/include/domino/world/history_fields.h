/*
FILE: include/domino/world/history_fields.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / world/history_fields
RESPONSIBILITY: Deterministic history and civilization graph sampling.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 headers as needed.
FORBIDDEN DEPENDENCIES: Engine private headers outside `include/domino/**`.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: Fixed-point only; deterministic ordering and math.
VERSIONING / ABI / DATA FORMAT NOTES: Versioned by HIST0 specs.
EXTENSION POINTS: Extend via public headers and relevant `docs/architecture/**`.
*/
#ifndef DOMINO_WORLD_HISTORY_FIELDS_H
#define DOMINO_WORLD_HISTORY_FIELDS_H

#include "domino/core/types.h"
#include "domino/core/fixed.h"
#include "domino/world/domain_query.h"

#ifdef __cplusplus
extern "C" {
#endif

#define DOM_HISTORY_MAX_SOURCES 128u
#define DOM_HISTORY_MAX_EVENTS 256u
#define DOM_HISTORY_MAX_EPOCHS 64u
#define DOM_HISTORY_MAX_GRAPHS 32u
#define DOM_HISTORY_MAX_NODES 128u
#define DOM_HISTORY_MAX_EDGES 256u
#define DOM_HISTORY_MAX_REGIONS 16u
#define DOM_HISTORY_MAX_CAPSULES 64u
#define DOM_HISTORY_MAX_SOURCE_REFS 8u
#define DOM_HISTORY_MAX_NODE_REFS 16u
#define DOM_HISTORY_MAX_EDGE_REFS 32u
#define DOM_HISTORY_HIST_BINS 4u
#define DOM_HISTORY_EVENT_CLASS_COUNT 5u

#define DOM_HISTORY_RATIO_ONE_Q16 ((q16_16)0x00010000)

enum dom_history_event_role {
    DOM_HISTORY_ROLE_UNSET = 0u,
    DOM_HISTORY_ROLE_DERIVED = 1u,
    DOM_HISTORY_ROLE_PROCESS = 2u
};

enum dom_history_event_category {
    DOM_HISTORY_EVENT_UNSET = 0u,
    DOM_HISTORY_EVENT_WAR = 1u,
    DOM_HISTORY_EVENT_DISASTER = 2u,
    DOM_HISTORY_EVENT_REFORM = 3u,
    DOM_HISTORY_EVENT_DISCOVERY = 4u
};

enum dom_history_process_type {
    DOM_HISTORY_PROCESS_UNSET = 0u,
    DOM_HISTORY_PROCESS_RECORD = 1u,
    DOM_HISTORY_PROCESS_FORGET = 2u,
    DOM_HISTORY_PROCESS_REVISE = 3u,
    DOM_HISTORY_PROCESS_MYTHOLOGIZE = 4u
};

enum dom_history_source_type {
    DOM_HISTORY_SOURCE_UNSET = 0u,
    DOM_HISTORY_SOURCE_REPLAY = 1u,
    DOM_HISTORY_SOURCE_ARCHIVE = 2u,
    DOM_HISTORY_SOURCE_ORAL = 3u,
    DOM_HISTORY_SOURCE_ARTIFACT = 4u,
    DOM_HISTORY_SOURCE_INFERENCE = 5u
};

enum dom_history_epoch_type {
    DOM_HISTORY_EPOCH_UNSET = 0u,
    DOM_HISTORY_EPOCH_CONFLICT = 1u,
    DOM_HISTORY_EPOCH_TECH = 2u,
    DOM_HISTORY_EPOCH_INSTITUTION = 3u,
    DOM_HISTORY_EPOCH_ENVIRONMENT = 4u
};

enum dom_civilization_edge_type {
    DOM_CIV_EDGE_UNSET = 0u,
    DOM_CIV_EDGE_COOPERATION = 1u,
    DOM_CIV_EDGE_DEPENDENCY = 2u,
    DOM_CIV_EDGE_CONFLICT = 3u,
    DOM_CIV_EDGE_CULTURAL = 4u
};

enum dom_history_event_flags {
    DOM_HISTORY_EVENT_UNRESOLVED = 1u << 0u,
    DOM_HISTORY_EVENT_FORGOTTEN = 1u << 1u,
    DOM_HISTORY_EVENT_REVISED = 1u << 2u,
    DOM_HISTORY_EVENT_MYTH = 1u << 3u,
    DOM_HISTORY_EVENT_RECORDED = 1u << 4u,
    DOM_HISTORY_EVENT_APPLIED = 1u << 5u,
    DOM_HISTORY_EVENT_COLLAPSED = 1u << 6u
};

enum dom_history_source_flags {
    DOM_HISTORY_SOURCE_UNRESOLVED = 1u << 0u,
    DOM_HISTORY_SOURCE_ARCHAEOLOGY = 1u << 1u,
    DOM_HISTORY_SOURCE_COLLAPSED = 1u << 2u
};

enum dom_history_epoch_flags {
    DOM_HISTORY_EPOCH_UNRESOLVED = 1u << 0u,
    DOM_HISTORY_EPOCH_CONTESTED = 1u << 1u,
    DOM_HISTORY_EPOCH_COLLAPSED = 1u << 2u
};

enum dom_civilization_graph_flags {
    DOM_CIV_GRAPH_UNRESOLVED = 1u << 0u,
    DOM_CIV_GRAPH_COLLAPSED = 1u << 1u
};

enum dom_civilization_node_flags {
    DOM_CIV_NODE_UNRESOLVED = 1u << 0u,
    DOM_CIV_NODE_COLLAPSED = 1u << 1u
};

enum dom_civilization_edge_flags {
    DOM_CIV_EDGE_UNRESOLVED = 1u << 0u,
    DOM_CIV_EDGE_COLLAPSED = 1u << 1u
};

enum dom_history_resolve_flags {
    DOM_HISTORY_RESOLVE_PARTIAL = 1u << 0u,
    DOM_HISTORY_RESOLVE_DECAYED = 1u << 1u,
    DOM_HISTORY_RESOLVE_FORGOTTEN = 1u << 2u,
    DOM_HISTORY_RESOLVE_REVISED = 1u << 3u,
    DOM_HISTORY_RESOLVE_MYTH = 1u << 4u,
    DOM_HISTORY_RESOLVE_ARCHAEOLOGY = 1u << 5u
};

enum dom_history_refusal_reason {
    DOM_HISTORY_REFUSE_NONE = 0u,
    DOM_HISTORY_REFUSE_BUDGET = 1u,
    DOM_HISTORY_REFUSE_DOMAIN_INACTIVE = 2u,
    DOM_HISTORY_REFUSE_SOURCE_MISSING = 3u,
    DOM_HISTORY_REFUSE_EVENT_MISSING = 4u,
    DOM_HISTORY_REFUSE_EPOCH_MISSING = 5u,
    DOM_HISTORY_REFUSE_GRAPH_MISSING = 6u,
    DOM_HISTORY_REFUSE_NODE_MISSING = 7u,
    DOM_HISTORY_REFUSE_EDGE_MISSING = 8u,
    DOM_HISTORY_REFUSE_POLICY = 9u,
    DOM_HISTORY_REFUSE_INTERNAL = 10u
};

typedef struct dom_history_source_desc {
    u32 source_id;
    u32 source_type;
    u32 source_event_id;
    u32 perspective_ref_id;
    q16_16 confidence;
    q16_16 bias;
    u64 recorded_tick;
    u32 region_id;
    u32 provenance_id;
    u32 flags; /* dom_history_source_flags */
} dom_history_source_desc;

typedef struct dom_history_event_desc {
    u32 event_id;
    u32 event_role;
    u32 category;
    u32 process_type;
    u32 target_event_id;
    u64 start_tick;
    u64 end_tick;
    u32 source_count;
    u32 source_refs[DOM_HISTORY_MAX_SOURCE_REFS];
    u32 perspective_ref_id;
    q16_16 confidence;
    q16_16 uncertainty;
    q16_16 bias;
    q16_16 decay_rate;
    q16_16 delta_confidence;
    q16_16 delta_uncertainty;
    q16_16 delta_bias;
    q16_16 myth_weight;
    u32 epoch_ref_id;
    u32 region_id;
    u32 provenance_id;
    u32 flags; /* dom_history_event_flags */
} dom_history_event_desc;

typedef struct dom_history_epoch_desc {
    u32 epoch_id;
    u32 epoch_type;
    u64 start_tick;
    u64 end_tick;
    q16_16 confidence;
    q16_16 uncertainty;
    q16_16 bias;
    u32 perspective_ref_id;
    u32 region_id;
    u32 provenance_id;
    u32 flags; /* dom_history_epoch_flags */
} dom_history_epoch_desc;

typedef struct dom_civilization_node_desc {
    u32 node_id;
    u32 institution_ref_id;
    u32 region_id;
    u32 flags; /* dom_civilization_node_flags */
} dom_civilization_node_desc;

typedef struct dom_civilization_edge_desc {
    u32 edge_id;
    u32 from_node_id;
    u32 to_node_id;
    u32 edge_type;
    q16_16 trust_weight;
    q48_16 trade_volume;
    q16_16 standard_weight;
    u32 region_id;
    u32 flags; /* dom_civilization_edge_flags */
} dom_civilization_edge_desc;

typedef struct dom_civilization_graph_desc {
    u32 graph_id;
    u32 epoch_ref_id;
    u32 node_count;
    u32 node_refs[DOM_HISTORY_MAX_NODE_REFS];
    u32 edge_count;
    u32 edge_refs[DOM_HISTORY_MAX_EDGE_REFS];
    u32 region_id;
    u32 provenance_id;
    u32 flags; /* dom_civilization_graph_flags */
} dom_civilization_graph_desc;

typedef struct dom_history_source {
    u32 source_id;
    u32 source_type;
    u32 source_event_id;
    u32 perspective_ref_id;
    q16_16 confidence;
    q16_16 bias;
    u64 recorded_tick;
    u32 region_id;
    u32 provenance_id;
    u32 flags; /* dom_history_source_flags */
} dom_history_source;

typedef struct dom_history_event {
    u32 event_id;
    u32 event_role;
    u32 category;
    u32 process_type;
    u32 target_event_id;
    u64 start_tick;
    u64 end_tick;
    u32 source_count;
    u32 source_refs[DOM_HISTORY_MAX_SOURCE_REFS];
    u32 perspective_ref_id;
    q16_16 confidence;
    q16_16 uncertainty;
    q16_16 bias;
    q16_16 decay_rate;
    q16_16 delta_confidence;
    q16_16 delta_uncertainty;
    q16_16 delta_bias;
    q16_16 myth_weight;
    u32 epoch_ref_id;
    u32 region_id;
    u32 provenance_id;
    u32 flags; /* dom_history_event_flags */
} dom_history_event;

typedef struct dom_history_epoch {
    u32 epoch_id;
    u32 epoch_type;
    u64 start_tick;
    u64 end_tick;
    q16_16 confidence;
    q16_16 uncertainty;
    q16_16 bias;
    u32 perspective_ref_id;
    u32 region_id;
    u32 provenance_id;
    u32 flags; /* dom_history_epoch_flags */
} dom_history_epoch;

typedef struct dom_civilization_node {
    u32 node_id;
    u32 institution_ref_id;
    u32 region_id;
    u32 flags; /* dom_civilization_node_flags */
} dom_civilization_node;

typedef struct dom_civilization_edge {
    u32 edge_id;
    u32 from_node_id;
    u32 to_node_id;
    u32 edge_type;
    q16_16 trust_weight;
    q48_16 trade_volume;
    q16_16 standard_weight;
    u32 region_id;
    u32 flags; /* dom_civilization_edge_flags */
} dom_civilization_edge;

typedef struct dom_civilization_graph {
    u32 graph_id;
    u32 epoch_ref_id;
    u32 node_count;
    u32 node_refs[DOM_HISTORY_MAX_NODE_REFS];
    u32 edge_count;
    u32 edge_refs[DOM_HISTORY_MAX_EDGE_REFS];
    q16_16 trust_weight_avg;
    q48_16 trade_volume_total;
    q16_16 standard_weight_avg;
    u32 region_id;
    u32 provenance_id;
    u32 flags; /* dom_civilization_graph_flags */
} dom_civilization_graph;

typedef struct dom_history_surface_desc {
    dom_domain_id domain_id;
    u64 world_seed;
    q16_16 meters_per_unit;
    u32 source_count;
    dom_history_source_desc sources[DOM_HISTORY_MAX_SOURCES];
    u32 event_count;
    dom_history_event_desc events[DOM_HISTORY_MAX_EVENTS];
    u32 epoch_count;
    dom_history_epoch_desc epochs[DOM_HISTORY_MAX_EPOCHS];
    u32 graph_count;
    dom_civilization_graph_desc graphs[DOM_HISTORY_MAX_GRAPHS];
    u32 node_count;
    dom_civilization_node_desc nodes[DOM_HISTORY_MAX_NODES];
    u32 edge_count;
    dom_civilization_edge_desc edges[DOM_HISTORY_MAX_EDGES];
} dom_history_surface_desc;

typedef struct dom_history_source_sample {
    u32 source_id;
    u32 source_type;
    u32 source_event_id;
    u32 perspective_ref_id;
    q16_16 confidence;
    q16_16 bias;
    u64 recorded_tick;
    u32 region_id;
    u32 provenance_id;
    u32 flags; /* dom_history_source_flags */
    dom_domain_query_meta meta;
} dom_history_source_sample;

typedef struct dom_history_event_sample {
    u32 event_id;
    u32 event_role;
    u32 category;
    u32 process_type;
    u32 target_event_id;
    u64 start_tick;
    u64 end_tick;
    u32 source_count;
    u32 perspective_ref_id;
    q16_16 confidence;
    q16_16 uncertainty;
    q16_16 bias;
    q16_16 decay_rate;
    q16_16 delta_confidence;
    q16_16 delta_uncertainty;
    q16_16 delta_bias;
    q16_16 myth_weight;
    u32 epoch_ref_id;
    u32 region_id;
    u32 provenance_id;
    u32 flags; /* dom_history_event_flags */
    dom_domain_query_meta meta;
} dom_history_event_sample;

typedef struct dom_history_epoch_sample {
    u32 epoch_id;
    u32 epoch_type;
    u64 start_tick;
    u64 end_tick;
    q16_16 confidence;
    q16_16 uncertainty;
    q16_16 bias;
    u32 perspective_ref_id;
    u32 region_id;
    u32 provenance_id;
    u32 flags; /* dom_history_epoch_flags */
    dom_domain_query_meta meta;
} dom_history_epoch_sample;

typedef struct dom_civilization_node_sample {
    u32 node_id;
    u32 institution_ref_id;
    u32 region_id;
    u32 flags; /* dom_civilization_node_flags */
    dom_domain_query_meta meta;
} dom_civilization_node_sample;

typedef struct dom_civilization_edge_sample {
    u32 edge_id;
    u32 from_node_id;
    u32 to_node_id;
    u32 edge_type;
    q16_16 trust_weight;
    q48_16 trade_volume;
    q16_16 standard_weight;
    u32 region_id;
    u32 flags; /* dom_civilization_edge_flags */
    dom_domain_query_meta meta;
} dom_civilization_edge_sample;

typedef struct dom_civilization_graph_sample {
    u32 graph_id;
    u32 epoch_ref_id;
    u32 node_count;
    u32 edge_count;
    q16_16 trust_weight_avg;
    q48_16 trade_volume_total;
    q16_16 standard_weight_avg;
    u32 region_id;
    u32 provenance_id;
    u32 flags; /* dom_civilization_graph_flags */
    dom_domain_query_meta meta;
} dom_civilization_graph_sample;

typedef struct dom_history_region_sample {
    u32 region_id;
    u32 source_count;
    u32 event_count;
    u32 process_count;
    u32 epoch_count;
    u32 graph_count;
    u32 node_count;
    u32 edge_count;
    q16_16 confidence_avg;
    q16_16 uncertainty_avg;
    q16_16 bias_avg;
    q16_16 trust_weight_avg;
    q48_16 trade_volume_total;
    q16_16 standard_weight_avg;
    u32 flags; /* dom_history_resolve_flags */
    dom_domain_query_meta meta;
} dom_history_region_sample;

typedef struct dom_history_resolve_result {
    u32 ok;
    u32 refusal_reason; /* dom_history_refusal_reason */
    u32 flags; /* dom_history_resolve_flags */
    u32 source_count;
    u32 event_count;
    u32 process_count;
    u32 event_applied_count;
    u32 epoch_count;
    u32 graph_count;
    u32 node_count;
    u32 edge_count;
    q16_16 confidence_avg;
    q16_16 uncertainty_avg;
    q16_16 bias_avg;
    q16_16 trust_weight_avg;
    q48_16 trade_volume_total;
    q16_16 standard_weight_avg;
} dom_history_resolve_result;

typedef struct dom_history_macro_capsule {
    u64 capsule_id;
    u32 region_id;
    u32 source_count;
    u32 event_count;
    u32 epoch_count;
    u32 graph_count;
    u32 node_count;
    u32 edge_count;
    u32 event_category_counts[DOM_HISTORY_EVENT_CLASS_COUNT];
    q16_16 bias_hist[DOM_HISTORY_HIST_BINS];
    q16_16 confidence_hist[DOM_HISTORY_HIST_BINS];
    u32 rng_cursor[DOM_HISTORY_HIST_BINS];
} dom_history_macro_capsule;

typedef struct dom_history_domain {
    dom_domain_policy policy;
    u32 existence_state;
    u32 archival_state;
    u32 authoring_version;
    dom_history_surface_desc surface;
    dom_history_source sources[DOM_HISTORY_MAX_SOURCES];
    u32 source_count;
    dom_history_event events[DOM_HISTORY_MAX_EVENTS];
    u32 event_count;
    dom_history_epoch epochs[DOM_HISTORY_MAX_EPOCHS];
    u32 epoch_count;
    dom_civilization_graph graphs[DOM_HISTORY_MAX_GRAPHS];
    u32 graph_count;
    dom_civilization_node nodes[DOM_HISTORY_MAX_NODES];
    u32 node_count;
    dom_civilization_edge edges[DOM_HISTORY_MAX_EDGES];
    u32 edge_count;
    dom_history_macro_capsule capsules[DOM_HISTORY_MAX_CAPSULES];
    u32 capsule_count;
} dom_history_domain;

void dom_history_surface_desc_init(dom_history_surface_desc* desc);

void dom_history_domain_init(dom_history_domain* domain,
                             const dom_history_surface_desc* desc);
void dom_history_domain_free(dom_history_domain* domain);
void dom_history_domain_set_state(dom_history_domain* domain,
                                  u32 existence_state,
                                  u32 archival_state);
void dom_history_domain_set_policy(dom_history_domain* domain,
                                   const dom_domain_policy* policy);

int dom_history_source_query(const dom_history_domain* domain,
                             u32 source_id,
                             dom_domain_budget* budget,
                             dom_history_source_sample* out_sample);

int dom_history_event_query(const dom_history_domain* domain,
                            u32 event_id,
                            dom_domain_budget* budget,
                            dom_history_event_sample* out_sample);

int dom_history_epoch_query(const dom_history_domain* domain,
                            u32 epoch_id,
                            dom_domain_budget* budget,
                            dom_history_epoch_sample* out_sample);

int dom_civilization_graph_query(const dom_history_domain* domain,
                                 u32 graph_id,
                                 dom_domain_budget* budget,
                                 dom_civilization_graph_sample* out_sample);

int dom_civilization_node_query(const dom_history_domain* domain,
                                u32 node_id,
                                dom_domain_budget* budget,
                                dom_civilization_node_sample* out_sample);

int dom_civilization_edge_query(const dom_history_domain* domain,
                                u32 edge_id,
                                dom_domain_budget* budget,
                                dom_civilization_edge_sample* out_sample);

int dom_history_region_query(const dom_history_domain* domain,
                             u32 region_id,
                             dom_domain_budget* budget,
                             dom_history_region_sample* out_sample);

int dom_history_resolve(dom_history_domain* domain,
                        u32 region_id,
                        u64 tick,
                        u64 tick_delta,
                        dom_domain_budget* budget,
                        dom_history_resolve_result* out_result);

int dom_history_domain_collapse_region(dom_history_domain* domain, u32 region_id);
int dom_history_domain_expand_region(dom_history_domain* domain, u32 region_id);

u32 dom_history_domain_capsule_count(const dom_history_domain* domain);
const dom_history_macro_capsule* dom_history_domain_capsule_at(const dom_history_domain* domain,
                                                               u32 index);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINO_WORLD_HISTORY_FIELDS_H */
