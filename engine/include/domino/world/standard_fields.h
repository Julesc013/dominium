/*
FILE: include/domino/world/standard_fields.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / world/standard_fields
RESPONSIBILITY: Deterministic standards, toolchains, and meta-tool field sampling.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 headers as needed.
FORBIDDEN DEPENDENCIES: Engine private headers outside `include/domino/**`.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: Fixed-point only; deterministic ordering and math.
VERSIONING / ABI / DATA FORMAT NOTES: Versioned by STD0 specs.
EXTENSION POINTS: Extend via public headers and relevant `docs/architecture/**`.
*/
#ifndef DOMINO_WORLD_STANDARD_FIELDS_H
#define DOMINO_WORLD_STANDARD_FIELDS_H

#include "domino/core/types.h"
#include "domino/core/fixed.h"
#include "domino/world/domain_query.h"

#ifdef __cplusplus
extern "C" {
#endif

#define DOM_STANDARD_MAX_DEFINITIONS 128u
#define DOM_STANDARD_MAX_VERSIONS 128u
#define DOM_STANDARD_MAX_SCOPES 128u
#define DOM_STANDARD_MAX_EVENTS 128u
#define DOM_STANDARD_MAX_TOOLS 128u
#define DOM_STANDARD_MAX_EDGES 128u
#define DOM_STANDARD_MAX_GRAPHS 64u
#define DOM_STANDARD_MAX_GRAPH_NODES 16u
#define DOM_STANDARD_MAX_GRAPH_EDGES 32u
#define DOM_STANDARD_MAX_ADOPTION_REQS 8u
#define DOM_STANDARD_MAX_ENFORCEMENTS 8u
#define DOM_STANDARD_MAX_REGIONS 16u
#define DOM_STANDARD_MAX_CAPSULES 64u
#define DOM_STANDARD_HIST_BINS 4u
#define DOM_STANDARD_EVENT_BINS 5u

#define DOM_STANDARD_RATIO_ONE_Q16 ((q16_16)0x00010000)

enum dom_standard_process_type {
    DOM_STANDARD_PROCESS_UNSET = 0u,
    DOM_STANDARD_PROCESS_PROPOSE = 1u,
    DOM_STANDARD_PROCESS_ADOPT = 2u,
    DOM_STANDARD_PROCESS_AUDIT = 3u,
    DOM_STANDARD_PROCESS_ENFORCE = 4u,
    DOM_STANDARD_PROCESS_REVOKE = 5u
};

enum dom_standard_version_status {
    DOM_STANDARD_STATUS_UNSET = 0u,
    DOM_STANDARD_STATUS_ACTIVE = 1u,
    DOM_STANDARD_STATUS_DEPRECATED = 2u,
    DOM_STANDARD_STATUS_REVOKED = 3u
};

enum dom_standard_definition_flags {
    DOM_STANDARD_DEF_UNRESOLVED = 1u << 0u,
    DOM_STANDARD_DEF_COLLAPSED = 1u << 1u
};

enum dom_standard_version_flags {
    DOM_STANDARD_VERSION_UNRESOLVED = 1u << 0u,
    DOM_STANDARD_VERSION_COLLAPSED = 1u << 1u,
    DOM_STANDARD_VERSION_REVOKED = 1u << 2u
};

enum dom_standard_scope_flags {
    DOM_STANDARD_SCOPE_UNRESOLVED = 1u << 0u,
    DOM_STANDARD_SCOPE_COLLAPSED = 1u << 1u,
    DOM_STANDARD_SCOPE_ADOPTED = 1u << 2u,
    DOM_STANDARD_SCOPE_NONCOMPLIANT = 1u << 3u,
    DOM_STANDARD_SCOPE_LOCKED_IN = 1u << 4u,
    DOM_STANDARD_SCOPE_REVOKED = 1u << 5u
};

enum dom_standard_event_flags {
    DOM_STANDARD_EVENT_UNRESOLVED = 1u << 0u,
    DOM_STANDARD_EVENT_APPLIED = 1u << 1u,
    DOM_STANDARD_EVENT_FAILED = 1u << 2u,
    DOM_STANDARD_EVENT_COLLAPSED = 1u << 3u
};

enum dom_meta_tool_flags {
    DOM_META_TOOL_UNRESOLVED = 1u << 0u,
    DOM_META_TOOL_COLLAPSED = 1u << 1u
};

enum dom_toolchain_edge_flags {
    DOM_TOOLCHAIN_EDGE_UNRESOLVED = 1u << 0u,
    DOM_TOOLCHAIN_EDGE_COLLAPSED = 1u << 1u,
    DOM_TOOLCHAIN_EDGE_BRIDGE = 1u << 2u
};

enum dom_toolchain_graph_flags {
    DOM_TOOLCHAIN_GRAPH_UNRESOLVED = 1u << 0u,
    DOM_TOOLCHAIN_GRAPH_COLLAPSED = 1u << 1u
};

enum dom_standard_resolve_flags {
    DOM_STANDARD_RESOLVE_PARTIAL = 1u << 0u,
    DOM_STANDARD_RESOLVE_EVENTS_APPLIED = 1u << 1u,
    DOM_STANDARD_RESOLVE_ADOPTION_SHIFT = 1u << 2u,
    DOM_STANDARD_RESOLVE_COMPLIANCE_SHIFT = 1u << 3u,
    DOM_STANDARD_RESOLVE_LOCKIN_SHIFT = 1u << 4u,
    DOM_STANDARD_RESOLVE_REVOCATION = 1u << 5u
};

enum dom_standard_refusal_reason {
    DOM_STANDARD_REFUSE_NONE = 0u,
    DOM_STANDARD_REFUSE_BUDGET = 1u,
    DOM_STANDARD_REFUSE_DOMAIN_INACTIVE = 2u,
    DOM_STANDARD_REFUSE_DEFINITION_MISSING = 3u,
    DOM_STANDARD_REFUSE_VERSION_MISSING = 4u,
    DOM_STANDARD_REFUSE_SCOPE_MISSING = 5u,
    DOM_STANDARD_REFUSE_EVENT_MISSING = 6u,
    DOM_STANDARD_REFUSE_TOOL_MISSING = 7u,
    DOM_STANDARD_REFUSE_EDGE_MISSING = 8u,
    DOM_STANDARD_REFUSE_GRAPH_MISSING = 9u,
    DOM_STANDARD_REFUSE_POLICY = 10u,
    DOM_STANDARD_REFUSE_INTERNAL = 11u
};

typedef struct dom_standard_definition_desc {
    u32 standard_id;
    u32 subject_domain_id;
    u32 specification_id;
    u32 current_version_id;
    u32 compatibility_policy_id;
    u32 issuing_institution_id;
    u32 adoption_req_count;
    u32 adoption_req_ids[DOM_STANDARD_MAX_ADOPTION_REQS];
    u32 enforcement_count;
    u32 enforcement_ids[DOM_STANDARD_MAX_ENFORCEMENTS];
    u32 provenance_id;
    u32 region_id;
    u32 flags; /* dom_standard_definition_flags */
} dom_standard_definition_desc;

typedef struct dom_standard_version_desc {
    u32 version_id;
    u32 standard_id;
    u32 version_tag_id;
    u32 compatibility_group_id;
    q16_16 compatibility_score;
    q16_16 adoption_threshold;
    u32 status; /* dom_standard_version_status */
    u64 release_tick;
    u32 provenance_id;
    u32 region_id;
    u32 flags; /* dom_standard_version_flags */
} dom_standard_version_desc;

typedef struct dom_standard_scope_desc {
    u32 scope_id;
    u32 standard_id;
    u32 version_id;
    u32 spatial_domain_id;
    u32 subject_domain_id;
    q16_16 adoption_rate;
    q16_16 compliance_rate;
    q16_16 lock_in_index;
    q16_16 enforcement_level;
    u32 provenance_id;
    u32 region_id;
    u32 flags; /* dom_standard_scope_flags */
} dom_standard_scope_desc;

typedef struct dom_standard_event_desc {
    u32 event_id;
    u32 process_type;
    u32 standard_id;
    u32 version_id;
    u32 scope_id;
    q16_16 delta_adoption;
    q16_16 delta_compliance;
    q16_16 delta_lock_in;
    u64 event_tick;
    u32 provenance_id;
    u32 region_id;
    u32 flags; /* dom_standard_event_flags */
} dom_standard_event_desc;

typedef struct dom_meta_tool_desc {
    u32 tool_id;
    u32 tool_type_id;
    u32 input_standard_id;
    u32 output_standard_id;
    q48_16 capacity;
    q48_16 energy_cost;
    q48_16 heat_output;
    q16_16 error_rate;
    q16_16 bias;
    u32 provenance_id;
    u32 region_id;
    u32 flags; /* dom_meta_tool_flags */
} dom_meta_tool_desc;

typedef struct dom_toolchain_edge_desc {
    u32 edge_id;
    u32 from_tool_id;
    u32 to_tool_id;
    u32 input_standard_id;
    u32 output_standard_id;
    q16_16 compatibility_score;
    u32 provenance_id;
    u32 region_id;
    u32 flags; /* dom_toolchain_edge_flags */
} dom_toolchain_edge_desc;

typedef struct dom_toolchain_graph_desc {
    u32 graph_id;
    u32 node_count;
    u32 node_tool_ids[DOM_STANDARD_MAX_GRAPH_NODES];
    u32 edge_count;
    u32 edge_ids[DOM_STANDARD_MAX_GRAPH_EDGES];
    u32 provenance_id;
    u32 region_id;
    u32 flags; /* dom_toolchain_graph_flags */
} dom_toolchain_graph_desc;

typedef struct dom_standard_definition {
    u32 standard_id;
    u32 subject_domain_id;
    u32 specification_id;
    u32 current_version_id;
    u32 compatibility_policy_id;
    u32 issuing_institution_id;
    u32 adoption_req_count;
    u32 adoption_req_ids[DOM_STANDARD_MAX_ADOPTION_REQS];
    u32 enforcement_count;
    u32 enforcement_ids[DOM_STANDARD_MAX_ENFORCEMENTS];
    u32 provenance_id;
    u32 region_id;
    u32 flags; /* dom_standard_definition_flags */
} dom_standard_definition;

typedef struct dom_standard_version {
    u32 version_id;
    u32 standard_id;
    u32 version_tag_id;
    u32 compatibility_group_id;
    q16_16 compatibility_score;
    q16_16 adoption_threshold;
    u32 status; /* dom_standard_version_status */
    u64 release_tick;
    u32 provenance_id;
    u32 region_id;
    u32 flags; /* dom_standard_version_flags */
} dom_standard_version;

typedef struct dom_standard_scope {
    u32 scope_id;
    u32 standard_id;
    u32 version_id;
    u32 spatial_domain_id;
    u32 subject_domain_id;
    q16_16 adoption_rate;
    q16_16 compliance_rate;
    q16_16 lock_in_index;
    q16_16 enforcement_level;
    u32 provenance_id;
    u32 region_id;
    u32 flags; /* dom_standard_scope_flags */
} dom_standard_scope;

typedef struct dom_standard_event {
    u32 event_id;
    u32 process_type;
    u32 standard_id;
    u32 version_id;
    u32 scope_id;
    q16_16 delta_adoption;
    q16_16 delta_compliance;
    q16_16 delta_lock_in;
    u64 event_tick;
    u32 provenance_id;
    u32 region_id;
    u32 flags; /* dom_standard_event_flags */
} dom_standard_event;

typedef struct dom_meta_tool {
    u32 tool_id;
    u32 tool_type_id;
    u32 input_standard_id;
    u32 output_standard_id;
    q48_16 capacity;
    q48_16 energy_cost;
    q48_16 heat_output;
    q16_16 error_rate;
    q16_16 bias;
    u32 provenance_id;
    u32 region_id;
    u32 flags; /* dom_meta_tool_flags */
} dom_meta_tool;

typedef struct dom_toolchain_edge {
    u32 edge_id;
    u32 from_tool_id;
    u32 to_tool_id;
    u32 input_standard_id;
    u32 output_standard_id;
    q16_16 compatibility_score;
    u32 provenance_id;
    u32 region_id;
    u32 flags; /* dom_toolchain_edge_flags */
} dom_toolchain_edge;

typedef struct dom_toolchain_graph {
    u32 graph_id;
    u32 node_count;
    u32 node_tool_ids[DOM_STANDARD_MAX_GRAPH_NODES];
    u32 edge_count;
    u32 edge_ids[DOM_STANDARD_MAX_GRAPH_EDGES];
    u32 provenance_id;
    u32 region_id;
    u32 flags; /* dom_toolchain_graph_flags */
} dom_toolchain_graph;

typedef struct dom_standard_surface_desc {
    dom_domain_id domain_id;
    u64 world_seed;
    q16_16 meters_per_unit;
    u32 definition_count;
    dom_standard_definition_desc definitions[DOM_STANDARD_MAX_DEFINITIONS];
    u32 version_count;
    dom_standard_version_desc versions[DOM_STANDARD_MAX_VERSIONS];
    u32 scope_count;
    dom_standard_scope_desc scopes[DOM_STANDARD_MAX_SCOPES];
    u32 event_count;
    dom_standard_event_desc events[DOM_STANDARD_MAX_EVENTS];
    u32 tool_count;
    dom_meta_tool_desc tools[DOM_STANDARD_MAX_TOOLS];
    u32 edge_count;
    dom_toolchain_edge_desc edges[DOM_STANDARD_MAX_EDGES];
    u32 graph_count;
    dom_toolchain_graph_desc graphs[DOM_STANDARD_MAX_GRAPHS];
} dom_standard_surface_desc;

typedef struct dom_standard_definition_sample {
    u32 standard_id;
    u32 subject_domain_id;
    u32 specification_id;
    u32 current_version_id;
    u32 compatibility_policy_id;
    u32 issuing_institution_id;
    u32 adoption_req_count;
    u32 enforcement_count;
    u32 provenance_id;
    u32 region_id;
    u32 flags; /* dom_standard_definition_flags */
    dom_domain_query_meta meta;
} dom_standard_definition_sample;

typedef struct dom_standard_version_sample {
    u32 version_id;
    u32 standard_id;
    u32 version_tag_id;
    u32 compatibility_group_id;
    q16_16 compatibility_score;
    q16_16 adoption_threshold;
    u32 status; /* dom_standard_version_status */
    u64 release_tick;
    u32 provenance_id;
    u32 region_id;
    u32 flags; /* dom_standard_version_flags */
    dom_domain_query_meta meta;
} dom_standard_version_sample;

typedef struct dom_standard_scope_sample {
    u32 scope_id;
    u32 standard_id;
    u32 version_id;
    u32 spatial_domain_id;
    u32 subject_domain_id;
    q16_16 adoption_rate;
    q16_16 compliance_rate;
    q16_16 lock_in_index;
    q16_16 enforcement_level;
    u32 provenance_id;
    u32 region_id;
    u32 flags; /* dom_standard_scope_flags */
    dom_domain_query_meta meta;
} dom_standard_scope_sample;

typedef struct dom_standard_event_sample {
    u32 event_id;
    u32 process_type;
    u32 standard_id;
    u32 version_id;
    u32 scope_id;
    q16_16 delta_adoption;
    q16_16 delta_compliance;
    q16_16 delta_lock_in;
    u64 event_tick;
    u32 provenance_id;
    u32 region_id;
    u32 flags; /* dom_standard_event_flags */
    dom_domain_query_meta meta;
} dom_standard_event_sample;

typedef struct dom_meta_tool_sample {
    u32 tool_id;
    u32 tool_type_id;
    u32 input_standard_id;
    u32 output_standard_id;
    q48_16 capacity;
    q48_16 energy_cost;
    q48_16 heat_output;
    q16_16 error_rate;
    q16_16 bias;
    u32 provenance_id;
    u32 region_id;
    u32 flags; /* dom_meta_tool_flags */
    dom_domain_query_meta meta;
} dom_meta_tool_sample;

typedef struct dom_toolchain_edge_sample {
    u32 edge_id;
    u32 from_tool_id;
    u32 to_tool_id;
    u32 input_standard_id;
    u32 output_standard_id;
    q16_16 compatibility_score;
    u32 provenance_id;
    u32 region_id;
    u32 flags; /* dom_toolchain_edge_flags */
    dom_domain_query_meta meta;
} dom_toolchain_edge_sample;

typedef struct dom_toolchain_graph_sample {
    u32 graph_id;
    u32 node_count;
    u32 edge_count;
    u32 provenance_id;
    u32 region_id;
    u32 flags; /* dom_toolchain_graph_flags */
    dom_domain_query_meta meta;
} dom_toolchain_graph_sample;

typedef struct dom_standard_region_sample {
    u32 region_id;
    u32 definition_count;
    u32 version_count;
    u32 scope_count;
    u32 event_count;
    u32 tool_count;
    u32 edge_count;
    u32 graph_count;
    q16_16 adoption_avg;
    q16_16 compliance_avg;
    q16_16 lock_in_avg;
    q16_16 compatibility_avg;
    u32 event_type_counts[DOM_STANDARD_EVENT_BINS];
    u32 flags; /* dom_standard_resolve_flags */
    dom_domain_query_meta meta;
} dom_standard_region_sample;

typedef struct dom_standard_resolve_result {
    u32 ok;
    u32 refusal_reason; /* dom_standard_refusal_reason */
    u32 flags; /* dom_standard_resolve_flags */
    u32 definition_count;
    u32 version_count;
    u32 scope_count;
    u32 event_count;
    u32 event_applied_count;
    u32 tool_count;
    u32 edge_count;
    u32 graph_count;
    q16_16 adoption_avg;
    q16_16 compliance_avg;
    q16_16 lock_in_avg;
    q16_16 compatibility_avg;
    u32 event_type_counts[DOM_STANDARD_EVENT_BINS];
} dom_standard_resolve_result;

typedef struct dom_standard_macro_capsule {
    u64 capsule_id;
    u32 region_id;
    u32 definition_count;
    u32 version_count;
    u32 scope_count;
    u32 event_count;
    u32 tool_count;
    u32 edge_count;
    u32 graph_count;
    q16_16 adoption_avg;
    q16_16 compliance_avg;
    q16_16 lock_in_avg;
    q16_16 compatibility_avg;
    q16_16 adoption_hist[DOM_STANDARD_HIST_BINS];
    q16_16 compliance_hist[DOM_STANDARD_HIST_BINS];
    q16_16 lock_in_hist[DOM_STANDARD_HIST_BINS];
    u32 event_type_counts[DOM_STANDARD_EVENT_BINS];
    u32 rng_cursor[DOM_STANDARD_HIST_BINS];
} dom_standard_macro_capsule;

typedef struct dom_standard_domain {
    dom_domain_policy policy;
    u32 existence_state;
    u32 archival_state;
    u32 authoring_version;
    dom_standard_surface_desc surface;
    dom_standard_definition definitions[DOM_STANDARD_MAX_DEFINITIONS];
    u32 definition_count;
    dom_standard_version versions[DOM_STANDARD_MAX_VERSIONS];
    u32 version_count;
    dom_standard_scope scopes[DOM_STANDARD_MAX_SCOPES];
    u32 scope_count;
    dom_standard_event events[DOM_STANDARD_MAX_EVENTS];
    u32 event_count;
    dom_meta_tool tools[DOM_STANDARD_MAX_TOOLS];
    u32 tool_count;
    dom_toolchain_edge edges[DOM_STANDARD_MAX_EDGES];
    u32 edge_count;
    dom_toolchain_graph graphs[DOM_STANDARD_MAX_GRAPHS];
    u32 graph_count;
    dom_standard_macro_capsule capsules[DOM_STANDARD_MAX_CAPSULES];
    u32 capsule_count;
} dom_standard_domain;

void dom_standard_surface_desc_init(dom_standard_surface_desc* desc);

void dom_standard_domain_init(dom_standard_domain* domain,
                              const dom_standard_surface_desc* desc);
void dom_standard_domain_free(dom_standard_domain* domain);
void dom_standard_domain_set_state(dom_standard_domain* domain,
                                   u32 existence_state,
                                   u32 archival_state);
void dom_standard_domain_set_policy(dom_standard_domain* domain,
                                    const dom_domain_policy* policy);

int dom_standard_definition_query(const dom_standard_domain* domain,
                                  u32 standard_id,
                                  dom_domain_budget* budget,
                                  dom_standard_definition_sample* out_sample);

int dom_standard_version_query(const dom_standard_domain* domain,
                               u32 version_id,
                               dom_domain_budget* budget,
                               dom_standard_version_sample* out_sample);

int dom_standard_scope_query(const dom_standard_domain* domain,
                             u32 scope_id,
                             dom_domain_budget* budget,
                             dom_standard_scope_sample* out_sample);

int dom_standard_event_query(const dom_standard_domain* domain,
                             u32 event_id,
                             dom_domain_budget* budget,
                             dom_standard_event_sample* out_sample);

int dom_meta_tool_query(const dom_standard_domain* domain,
                        u32 tool_id,
                        dom_domain_budget* budget,
                        dom_meta_tool_sample* out_sample);

int dom_toolchain_edge_query(const dom_standard_domain* domain,
                             u32 edge_id,
                             dom_domain_budget* budget,
                             dom_toolchain_edge_sample* out_sample);

int dom_toolchain_graph_query(const dom_standard_domain* domain,
                              u32 graph_id,
                              dom_domain_budget* budget,
                              dom_toolchain_graph_sample* out_sample);

int dom_standard_region_query(const dom_standard_domain* domain,
                              u32 region_id,
                              dom_domain_budget* budget,
                              dom_standard_region_sample* out_sample);

int dom_standard_resolve(dom_standard_domain* domain,
                         u32 region_id,
                         u64 tick,
                         u64 tick_delta,
                         dom_domain_budget* budget,
                         dom_standard_resolve_result* out_result);

int dom_standard_domain_collapse_region(dom_standard_domain* domain, u32 region_id);
int dom_standard_domain_expand_region(dom_standard_domain* domain, u32 region_id);

u32 dom_standard_domain_capsule_count(const dom_standard_domain* domain);
const dom_standard_macro_capsule* dom_standard_domain_capsule_at(const dom_standard_domain* domain,
                                                                 u32 index);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINO_WORLD_STANDARD_FIELDS_H */
