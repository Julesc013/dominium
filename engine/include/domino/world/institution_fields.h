/*
FILE: include/domino/world/institution_fields.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / world/institution_fields
RESPONSIBILITY: Deterministic institution, law, and governance field sampling.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 headers as needed.
FORBIDDEN DEPENDENCIES: Engine private headers outside `include/domino/**`.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: Fixed-point only; deterministic ordering and math.
VERSIONING / ABI / DATA FORMAT NOTES: Versioned by GOV0 specs.
EXTENSION POINTS: Extend via public headers and relevant `docs/architecture/**`.
*/
#ifndef DOMINO_WORLD_INSTITUTION_FIELDS_H
#define DOMINO_WORLD_INSTITUTION_FIELDS_H

#include "domino/core/types.h"
#include "domino/core/fixed.h"
#include "domino/world/domain_query.h"

#ifdef __cplusplus
extern "C" {
#endif

#define DOM_INSTITUTION_MAX_ENTITIES 128u
#define DOM_INSTITUTION_MAX_SCOPES 64u
#define DOM_INSTITUTION_MAX_CAPABILITIES 128u
#define DOM_INSTITUTION_MAX_RULES 128u
#define DOM_INSTITUTION_MAX_ENFORCEMENTS 128u
#define DOM_INSTITUTION_MAX_REGIONS 16u
#define DOM_INSTITUTION_MAX_CAPSULES 64u
#define DOM_INSTITUTION_MAX_AUTHORITY_TYPES 8u
#define DOM_INSTITUTION_MAX_SUBJECT_DOMAINS 8u
#define DOM_INSTITUTION_MAX_RULE_TARGETS 8u
#define DOM_INSTITUTION_HIST_BINS 4u
#define DOM_INSTITUTION_ACTION_BINS 4u

#define DOM_INSTITUTION_RATIO_ONE_Q16 ((q16_16)0x00010000)

enum dom_institution_rule_action {
    DOM_INSTITUTION_RULE_UNSET = 0u,
    DOM_INSTITUTION_RULE_ALLOW = 1u,
    DOM_INSTITUTION_RULE_FORBID = 2u,
    DOM_INSTITUTION_RULE_CONDITIONAL = 3u,
    DOM_INSTITUTION_RULE_LICENSE = 4u
};

enum dom_institution_enforcement_action {
    DOM_INSTITUTION_ENFORCE_UNSET = 0u,
    DOM_INSTITUTION_ENFORCE_PERMIT = 1u,
    DOM_INSTITUTION_ENFORCE_DENY = 2u,
    DOM_INSTITUTION_ENFORCE_PENALIZE = 3u,
    DOM_INSTITUTION_ENFORCE_LICENSE = 4u
};

enum dom_institution_entity_flags {
    DOM_INSTITUTION_ENTITY_UNRESOLVED = 1u << 0u,
    DOM_INSTITUTION_ENTITY_COLLAPSED = 1u << 1u
};

enum dom_institution_scope_flags {
    DOM_INSTITUTION_SCOPE_UNRESOLVED = 1u << 0u,
    DOM_INSTITUTION_SCOPE_COLLAPSED = 1u << 1u
};

enum dom_institution_capability_flags {
    DOM_INSTITUTION_CAPABILITY_UNRESOLVED = 1u << 0u,
    DOM_INSTITUTION_CAPABILITY_COLLAPSED = 1u << 1u,
    DOM_INSTITUTION_CAPABILITY_LICENSE_REQUIRED = 1u << 2u
};

enum dom_institution_rule_flags {
    DOM_INSTITUTION_RULE_UNRESOLVED = 1u << 0u,
    DOM_INSTITUTION_RULE_COLLAPSED = 1u << 1u,
    DOM_INSTITUTION_RULE_FLAG_CONDITIONAL = 1u << 2u,
    DOM_INSTITUTION_RULE_FLAG_LICENSE_REQUIRED = 1u << 3u
};

enum dom_institution_enforcement_flags {
    DOM_INSTITUTION_ENFORCEMENT_UNRESOLVED = 1u << 0u,
    DOM_INSTITUTION_ENFORCEMENT_APPLIED = 1u << 1u,
    DOM_INSTITUTION_ENFORCEMENT_FAILED = 1u << 2u
};

enum dom_institution_resolve_flags {
    DOM_INSTITUTION_RESOLVE_PARTIAL = 1u << 0u,
    DOM_INSTITUTION_RESOLVE_EVENTS_APPLIED = 1u << 1u
};

enum dom_institution_refusal_reason {
    DOM_INSTITUTION_REFUSE_NONE = 0u,
    DOM_INSTITUTION_REFUSE_BUDGET = 1u,
    DOM_INSTITUTION_REFUSE_DOMAIN_INACTIVE = 2u,
    DOM_INSTITUTION_REFUSE_ENTITY_MISSING = 3u,
    DOM_INSTITUTION_REFUSE_SCOPE_MISSING = 4u,
    DOM_INSTITUTION_REFUSE_CAPABILITY_MISSING = 5u,
    DOM_INSTITUTION_REFUSE_RULE_MISSING = 6u,
    DOM_INSTITUTION_REFUSE_ENFORCEMENT_MISSING = 7u,
    DOM_INSTITUTION_REFUSE_POLICY = 8u,
    DOM_INSTITUTION_REFUSE_INTERNAL = 9u
};

typedef struct dom_institution_entity_desc {
    u32 institution_id;
    u32 scope_id;
    u32 authority_count;
    u32 authority_types[DOM_INSTITUTION_MAX_AUTHORITY_TYPES];
    q48_16 enforcement_capacity;
    q48_16 resource_budget;
    q16_16 legitimacy_level;
    u32 legitimacy_ref_id;
    u32 knowledge_base_id;
    u32 provenance_id;
    u32 region_id;
} dom_institution_entity_desc;

typedef struct dom_institution_scope_desc {
    u32 scope_id;
    u32 spatial_domain_id;
    u32 subject_domain_count;
    u32 subject_domain_ids[DOM_INSTITUTION_MAX_SUBJECT_DOMAINS];
    u32 overlap_policy_id;
    u32 provenance_id;
    u32 region_id;
} dom_institution_scope_desc;

typedef struct dom_institution_capability_desc {
    u32 capability_id;
    u32 institution_id;
    u32 scope_id;
    u32 authority_type_id;
    u32 process_family_id;
    q48_16 capacity_limit;
    u32 license_required_id;
    u32 provenance_id;
    u32 region_id;
    u32 flags; /* dom_institution_capability_flags */
} dom_institution_capability_desc;

typedef struct dom_institution_rule_desc {
    u32 rule_id;
    u32 institution_id;
    u32 scope_id;
    u32 process_family_id;
    u32 subject_domain_id;
    u32 authority_type_id;
    u32 action; /* dom_institution_rule_action */
    u32 license_required_id;
    u32 provenance_id;
    u32 region_id;
    u32 flags; /* dom_institution_rule_flags */
} dom_institution_rule_desc;

typedef struct dom_institution_enforcement_desc {
    u32 enforcement_id;
    u32 institution_id;
    u32 rule_id;
    u32 process_family_id;
    u32 agent_id;
    u32 action; /* dom_institution_enforcement_action */
    u64 event_tick;
    u32 provenance_id;
    u32 region_id;
    u32 flags; /* dom_institution_enforcement_flags */
} dom_institution_enforcement_desc;

typedef struct dom_institution_entity {
    u32 institution_id;
    u32 scope_id;
    u32 authority_count;
    u32 authority_types[DOM_INSTITUTION_MAX_AUTHORITY_TYPES];
    q48_16 enforcement_capacity;
    q48_16 resource_budget;
    q16_16 legitimacy_level;
    u32 legitimacy_ref_id;
    u32 knowledge_base_id;
    u32 provenance_id;
    u32 region_id;
    u32 flags; /* dom_institution_entity_flags */
} dom_institution_entity;

typedef struct dom_institution_scope {
    u32 scope_id;
    u32 spatial_domain_id;
    u32 subject_domain_count;
    u32 subject_domain_ids[DOM_INSTITUTION_MAX_SUBJECT_DOMAINS];
    u32 overlap_policy_id;
    u32 provenance_id;
    u32 region_id;
    u32 flags; /* dom_institution_scope_flags */
} dom_institution_scope;

typedef struct dom_institution_capability {
    u32 capability_id;
    u32 institution_id;
    u32 scope_id;
    u32 authority_type_id;
    u32 process_family_id;
    q48_16 capacity_limit;
    u32 license_required_id;
    u32 provenance_id;
    u32 region_id;
    u32 flags; /* dom_institution_capability_flags */
} dom_institution_capability;

typedef struct dom_institution_rule {
    u32 rule_id;
    u32 institution_id;
    u32 scope_id;
    u32 process_family_id;
    u32 subject_domain_id;
    u32 authority_type_id;
    u32 action; /* dom_institution_rule_action */
    u32 license_required_id;
    u32 provenance_id;
    u32 region_id;
    u32 flags; /* dom_institution_rule_flags */
} dom_institution_rule;

typedef struct dom_institution_enforcement {
    u32 enforcement_id;
    u32 institution_id;
    u32 rule_id;
    u32 process_family_id;
    u32 agent_id;
    u32 action; /* dom_institution_enforcement_action */
    u64 event_tick;
    u32 provenance_id;
    u32 region_id;
    u32 flags; /* dom_institution_enforcement_flags */
} dom_institution_enforcement;

typedef struct dom_institution_surface_desc {
    dom_domain_id domain_id;
    u64 world_seed;
    q16_16 meters_per_unit;
    u32 entity_count;
    dom_institution_entity_desc entities[DOM_INSTITUTION_MAX_ENTITIES];
    u32 scope_count;
    dom_institution_scope_desc scopes[DOM_INSTITUTION_MAX_SCOPES];
    u32 capability_count;
    dom_institution_capability_desc capabilities[DOM_INSTITUTION_MAX_CAPABILITIES];
    u32 rule_count;
    dom_institution_rule_desc rules[DOM_INSTITUTION_MAX_RULES];
    u32 enforcement_count;
    dom_institution_enforcement_desc enforcement[DOM_INSTITUTION_MAX_ENFORCEMENTS];
} dom_institution_surface_desc;

typedef struct dom_institution_entity_sample {
    u32 institution_id;
    u32 scope_id;
    u32 authority_count;
    u32 authority_types[DOM_INSTITUTION_MAX_AUTHORITY_TYPES];
    q48_16 enforcement_capacity;
    q48_16 resource_budget;
    q16_16 legitimacy_level;
    u32 legitimacy_ref_id;
    u32 knowledge_base_id;
    u32 provenance_id;
    u32 region_id;
    u32 flags; /* dom_institution_entity_flags */
    dom_domain_query_meta meta;
} dom_institution_entity_sample;

typedef struct dom_institution_scope_sample {
    u32 scope_id;
    u32 spatial_domain_id;
    u32 subject_domain_count;
    u32 subject_domain_ids[DOM_INSTITUTION_MAX_SUBJECT_DOMAINS];
    u32 overlap_policy_id;
    u32 provenance_id;
    u32 region_id;
    u32 flags; /* dom_institution_scope_flags */
    dom_domain_query_meta meta;
} dom_institution_scope_sample;

typedef struct dom_institution_capability_sample {
    u32 capability_id;
    u32 institution_id;
    u32 scope_id;
    u32 authority_type_id;
    u32 process_family_id;
    q48_16 capacity_limit;
    u32 license_required_id;
    u32 provenance_id;
    u32 region_id;
    u32 flags; /* dom_institution_capability_flags */
    dom_domain_query_meta meta;
} dom_institution_capability_sample;

typedef struct dom_institution_rule_sample {
    u32 rule_id;
    u32 institution_id;
    u32 scope_id;
    u32 process_family_id;
    u32 subject_domain_id;
    u32 authority_type_id;
    u32 action; /* dom_institution_rule_action */
    u32 license_required_id;
    u32 provenance_id;
    u32 region_id;
    u32 flags; /* dom_institution_rule_flags */
    dom_domain_query_meta meta;
} dom_institution_rule_sample;

typedef struct dom_institution_enforcement_sample {
    u32 enforcement_id;
    u32 institution_id;
    u32 rule_id;
    u32 process_family_id;
    u32 agent_id;
    u32 action; /* dom_institution_enforcement_action */
    u64 event_tick;
    u32 provenance_id;
    u32 region_id;
    u32 flags; /* dom_institution_enforcement_flags */
    dom_domain_query_meta meta;
} dom_institution_enforcement_sample;

typedef struct dom_institution_region_sample {
    u32 region_id;
    u32 entity_count;
    u32 scope_count;
    u32 capability_count;
    u32 rule_count;
    u32 enforcement_count;
    q48_16 enforcement_capacity_avg;
    q48_16 resource_budget_avg;
    q16_16 legitimacy_avg;
    u32 enforcement_action_counts[DOM_INSTITUTION_ACTION_BINS];
    u32 flags; /* dom_institution_resolve_flags */
    dom_domain_query_meta meta;
} dom_institution_region_sample;

typedef struct dom_institution_resolve_result {
    u32 ok;
    u32 refusal_reason; /* dom_institution_refusal_reason */
    u32 flags; /* dom_institution_resolve_flags */
    u32 entity_count;
    u32 scope_count;
    u32 capability_count;
    u32 rule_count;
    u32 enforcement_count;
    u32 enforcement_applied_count;
    q48_16 enforcement_capacity_avg;
    q48_16 resource_budget_avg;
    q16_16 legitimacy_avg;
    u32 enforcement_action_counts[DOM_INSTITUTION_ACTION_BINS];
} dom_institution_resolve_result;

typedef struct dom_institution_macro_capsule {
    u64 capsule_id;
    u32 region_id;
    u32 entity_count;
    u32 scope_count;
    u32 capability_count;
    u32 rule_count;
    u32 enforcement_count;
    q48_16 enforcement_capacity_avg;
    q48_16 resource_budget_avg;
    q16_16 legitimacy_avg;
    q16_16 legitimacy_hist[DOM_INSTITUTION_HIST_BINS];
    u32 enforcement_action_counts[DOM_INSTITUTION_ACTION_BINS];
    u32 rng_cursor[DOM_INSTITUTION_HIST_BINS];
} dom_institution_macro_capsule;

typedef struct dom_institution_domain {
    dom_domain_policy policy;
    u32 existence_state;
    u32 archival_state;
    u32 authoring_version;
    dom_institution_surface_desc surface;
    dom_institution_entity entities[DOM_INSTITUTION_MAX_ENTITIES];
    u32 entity_count;
    dom_institution_scope scopes[DOM_INSTITUTION_MAX_SCOPES];
    u32 scope_count;
    dom_institution_capability capabilities[DOM_INSTITUTION_MAX_CAPABILITIES];
    u32 capability_count;
    dom_institution_rule rules[DOM_INSTITUTION_MAX_RULES];
    u32 rule_count;
    dom_institution_enforcement enforcement[DOM_INSTITUTION_MAX_ENFORCEMENTS];
    u32 enforcement_count;
    dom_institution_macro_capsule capsules[DOM_INSTITUTION_MAX_CAPSULES];
    u32 capsule_count;
} dom_institution_domain;

void dom_institution_surface_desc_init(dom_institution_surface_desc* desc);

void dom_institution_domain_init(dom_institution_domain* domain,
                                 const dom_institution_surface_desc* desc);
void dom_institution_domain_free(dom_institution_domain* domain);
void dom_institution_domain_set_state(dom_institution_domain* domain,
                                      u32 existence_state,
                                      u32 archival_state);
void dom_institution_domain_set_policy(dom_institution_domain* domain,
                                       const dom_domain_policy* policy);

int dom_institution_entity_query(const dom_institution_domain* domain,
                                 u32 institution_id,
                                 dom_domain_budget* budget,
                                 dom_institution_entity_sample* out_sample);

int dom_institution_scope_query(const dom_institution_domain* domain,
                                u32 scope_id,
                                dom_domain_budget* budget,
                                dom_institution_scope_sample* out_sample);

int dom_institution_capability_query(const dom_institution_domain* domain,
                                     u32 capability_id,
                                     dom_domain_budget* budget,
                                     dom_institution_capability_sample* out_sample);

int dom_institution_rule_query(const dom_institution_domain* domain,
                               u32 rule_id,
                               dom_domain_budget* budget,
                               dom_institution_rule_sample* out_sample);

int dom_institution_enforcement_query(const dom_institution_domain* domain,
                                      u32 enforcement_id,
                                      dom_domain_budget* budget,
                                      dom_institution_enforcement_sample* out_sample);

int dom_institution_region_query(const dom_institution_domain* domain,
                                 u32 region_id,
                                 dom_domain_budget* budget,
                                 dom_institution_region_sample* out_sample);

int dom_institution_resolve(dom_institution_domain* domain,
                            u32 region_id,
                            u64 tick,
                            u64 tick_delta,
                            dom_domain_budget* budget,
                            dom_institution_resolve_result* out_result);

int dom_institution_domain_collapse_region(dom_institution_domain* domain, u32 region_id);
int dom_institution_domain_expand_region(dom_institution_domain* domain, u32 region_id);

u32 dom_institution_domain_capsule_count(const dom_institution_domain* domain);
const dom_institution_macro_capsule* dom_institution_domain_capsule_at(
    const dom_institution_domain* domain,
    u32 index);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINO_WORLD_INSTITUTION_FIELDS_H */
