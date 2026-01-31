/*
FILE: include/domino/world/trust_fields.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / world/trust_fields
RESPONSIBILITY: Deterministic trust, reputation, and legitimacy field sampling.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 headers as needed.
FORBIDDEN DEPENDENCIES: Engine private headers outside `include/domino/**`.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: Fixed-point only; deterministic ordering and math.
VERSIONING / ABI / DATA FORMAT NOTES: Versioned by TRUST0 specs.
EXTENSION POINTS: Extend via public headers and relevant `docs/architecture/**`.
*/
#ifndef DOMINO_WORLD_TRUST_FIELDS_H
#define DOMINO_WORLD_TRUST_FIELDS_H

#include "domino/core/types.h"
#include "domino/core/fixed.h"
#include "domino/world/domain_query.h"

#ifdef __cplusplus
extern "C" {
#endif

#define DOM_TRUST_MAX_FIELDS 128u
#define DOM_TRUST_MAX_EVENTS 128u
#define DOM_TRUST_MAX_PROFILES 64u
#define DOM_TRUST_MAX_LEGITIMACY 64u
#define DOM_TRUST_MAX_REGIONS 16u
#define DOM_TRUST_MAX_CAPSULES 64u
#define DOM_TRUST_HIST_BINS 4u

#define DOM_TRUST_RATIO_ONE_Q16 ((q16_16)0x00010000)

enum dom_trust_process_type {
    DOM_TRUST_PROCESS_UNSET = 0u,
    DOM_TRUST_PROCESS_INCREASE = 1u,
    DOM_TRUST_PROCESS_DECREASE = 2u,
    DOM_TRUST_PROCESS_DECAY = 3u,
    DOM_TRUST_PROCESS_TRANSFER = 4u
};

enum dom_trust_field_flags {
    DOM_TRUST_FIELD_UNRESOLVED = 1u << 0u,
    DOM_TRUST_FIELD_COLLAPSED = 1u << 1u,
    DOM_TRUST_FIELD_DECAYING = 1u << 2u
};

enum dom_trust_event_flags {
    DOM_TRUST_EVENT_UNRESOLVED = 1u << 0u,
    DOM_TRUST_EVENT_APPLIED = 1u << 1u,
    DOM_TRUST_EVENT_INCIDENT = 1u << 2u,
    DOM_TRUST_EVENT_DISPUTE = 1u << 3u,
    DOM_TRUST_EVENT_COLLAPSED = 1u << 4u
};

enum dom_reputation_profile_flags {
    DOM_REPUTATION_PROFILE_UNRESOLVED = 1u << 0u,
    DOM_REPUTATION_PROFILE_COLLAPSED = 1u << 1u
};

enum dom_legitimacy_field_flags {
    DOM_LEGITIMACY_FIELD_UNRESOLVED = 1u << 0u,
    DOM_LEGITIMACY_FIELD_COLLAPSED = 1u << 1u
};

enum dom_trust_resolve_flags {
    DOM_TRUST_RESOLVE_PARTIAL = 1u << 0u,
    DOM_TRUST_RESOLVE_DECAYED = 1u << 1u,
    DOM_TRUST_RESOLVE_INCIDENT = 1u << 2u,
    DOM_TRUST_RESOLVE_DISPUTE = 1u << 3u
};

enum dom_trust_refusal_reason {
    DOM_TRUST_REFUSE_NONE = 0u,
    DOM_TRUST_REFUSE_BUDGET = 1u,
    DOM_TRUST_REFUSE_DOMAIN_INACTIVE = 2u,
    DOM_TRUST_REFUSE_FIELD_MISSING = 3u,
    DOM_TRUST_REFUSE_EVENT_MISSING = 4u,
    DOM_TRUST_REFUSE_PROFILE_MISSING = 5u,
    DOM_TRUST_REFUSE_LEGITIMACY_MISSING = 6u,
    DOM_TRUST_REFUSE_POLICY = 7u,
    DOM_TRUST_REFUSE_INTERNAL = 8u
};

typedef struct dom_trust_field_desc {
    u32 trust_id;
    u32 subject_ref_id;
    u32 context_id;
    q16_16 trust_level;
    q16_16 uncertainty;
    q16_16 decay_rate;
    u32 provenance_id;
    u32 region_id;
} dom_trust_field_desc;

typedef struct dom_trust_event_desc {
    u32 event_id;
    u32 process_type;
    u32 subject_ref_id;
    u32 source_ref_id;
    u32 context_id;
    q16_16 delta_level;
    q16_16 uncertainty;
    u64 event_tick;
    u32 region_id;
    u32 provenance_id;
    u32 flags; /* dom_trust_event_flags */
} dom_trust_event_desc;

typedef struct dom_reputation_profile_desc {
    u32 profile_id;
    u32 subject_ref_id;
    u32 region_id;
    q16_16 historical_performance;
    q16_16 audit_results;
    q16_16 incident_history;
    q16_16 endorsements;
    q16_16 disputes;
    q16_16 uncertainty;
} dom_reputation_profile_desc;

typedef struct dom_legitimacy_field_desc {
    u32 legitimacy_id;
    u32 institution_ref_id;
    u32 authority_scope_id;
    u32 region_id;
    q16_16 compliance_rate;
    q16_16 challenge_rate;
    q16_16 symbolic_support;
    q16_16 uncertainty;
    u32 provenance_id;
} dom_legitimacy_field_desc;

typedef struct dom_trust_field {
    u32 trust_id;
    u32 subject_ref_id;
    u32 context_id;
    q16_16 trust_level;
    q16_16 uncertainty;
    q16_16 decay_rate;
    u32 provenance_id;
    u32 region_id;
    u32 flags; /* dom_trust_field_flags */
} dom_trust_field;

typedef struct dom_trust_event {
    u32 event_id;
    u32 process_type;
    u32 subject_ref_id;
    u32 source_ref_id;
    u32 context_id;
    q16_16 delta_level;
    q16_16 uncertainty;
    u64 event_tick;
    u32 region_id;
    u32 provenance_id;
    u32 flags; /* dom_trust_event_flags */
} dom_trust_event;

typedef struct dom_reputation_profile {
    u32 profile_id;
    u32 subject_ref_id;
    u32 region_id;
    q16_16 historical_performance;
    q16_16 audit_results;
    q16_16 incident_history;
    q16_16 endorsements;
    q16_16 disputes;
    q16_16 uncertainty;
    u32 flags; /* dom_reputation_profile_flags */
} dom_reputation_profile;

typedef struct dom_legitimacy_field {
    u32 legitimacy_id;
    u32 institution_ref_id;
    u32 authority_scope_id;
    u32 region_id;
    q16_16 compliance_rate;
    q16_16 challenge_rate;
    q16_16 symbolic_support;
    q16_16 uncertainty;
    u32 provenance_id;
    u32 flags; /* dom_legitimacy_field_flags */
} dom_legitimacy_field;

typedef struct dom_trust_surface_desc {
    dom_domain_id domain_id;
    u64 world_seed;
    q16_16 meters_per_unit;
    u32 field_count;
    dom_trust_field_desc fields[DOM_TRUST_MAX_FIELDS];
    u32 event_count;
    dom_trust_event_desc events[DOM_TRUST_MAX_EVENTS];
    u32 profile_count;
    dom_reputation_profile_desc profiles[DOM_TRUST_MAX_PROFILES];
    u32 legitimacy_count;
    dom_legitimacy_field_desc legitimacy[DOM_TRUST_MAX_LEGITIMACY];
} dom_trust_surface_desc;

typedef struct dom_trust_field_sample {
    u32 trust_id;
    u32 subject_ref_id;
    u32 context_id;
    q16_16 trust_level;
    q16_16 uncertainty;
    q16_16 decay_rate;
    u32 provenance_id;
    u32 region_id;
    u32 flags; /* dom_trust_field_flags */
    dom_domain_query_meta meta;
} dom_trust_field_sample;

typedef struct dom_trust_event_sample {
    u32 event_id;
    u32 process_type;
    u32 subject_ref_id;
    u32 source_ref_id;
    u32 context_id;
    q16_16 delta_level;
    q16_16 uncertainty;
    u64 event_tick;
    u32 region_id;
    u32 provenance_id;
    u32 flags; /* dom_trust_event_flags */
    dom_domain_query_meta meta;
} dom_trust_event_sample;

typedef struct dom_reputation_profile_sample {
    u32 profile_id;
    u32 subject_ref_id;
    u32 region_id;
    q16_16 historical_performance;
    q16_16 audit_results;
    q16_16 incident_history;
    q16_16 endorsements;
    q16_16 disputes;
    q16_16 uncertainty;
    u32 flags; /* dom_reputation_profile_flags */
    dom_domain_query_meta meta;
} dom_reputation_profile_sample;

typedef struct dom_legitimacy_field_sample {
    u32 legitimacy_id;
    u32 institution_ref_id;
    u32 authority_scope_id;
    u32 region_id;
    q16_16 compliance_rate;
    q16_16 challenge_rate;
    q16_16 symbolic_support;
    q16_16 uncertainty;
    u32 provenance_id;
    u32 flags; /* dom_legitimacy_field_flags */
    dom_domain_query_meta meta;
} dom_legitimacy_field_sample;

typedef struct dom_trust_region_sample {
    u32 region_id;
    u32 field_count;
    u32 event_count;
    u32 profile_count;
    u32 legitimacy_count;
    q16_16 trust_avg;
    q16_16 dispute_rate_avg;
    q16_16 compliance_rate_avg;
    u32 flags; /* dom_trust_resolve_flags */
    dom_domain_query_meta meta;
} dom_trust_region_sample;

typedef struct dom_trust_resolve_result {
    u32 ok;
    u32 refusal_reason; /* dom_trust_refusal_reason */
    u32 flags; /* dom_trust_resolve_flags */
    u32 field_count;
    u32 event_count;
    u32 event_applied_count;
    u32 profile_count;
    u32 legitimacy_count;
    q16_16 trust_avg;
    q16_16 dispute_rate_avg;
    q16_16 compliance_rate_avg;
} dom_trust_resolve_result;

typedef struct dom_trust_macro_capsule {
    u64 capsule_id;
    u32 region_id;
    u32 field_count;
    u32 event_count;
    u32 profile_count;
    u32 legitimacy_count;
    q16_16 trust_avg;
    q16_16 dispute_rate_avg;
    q16_16 compliance_rate_avg;
    q16_16 trust_hist[DOM_TRUST_HIST_BINS];
    u32 rng_cursor[DOM_TRUST_HIST_BINS];
} dom_trust_macro_capsule;

typedef struct dom_trust_domain {
    dom_domain_policy policy;
    u32 existence_state;
    u32 archival_state;
    u32 authoring_version;
    dom_trust_surface_desc surface;
    dom_trust_field fields[DOM_TRUST_MAX_FIELDS];
    u32 field_count;
    dom_trust_event events[DOM_TRUST_MAX_EVENTS];
    u32 event_count;
    dom_reputation_profile profiles[DOM_TRUST_MAX_PROFILES];
    u32 profile_count;
    dom_legitimacy_field legitimacy[DOM_TRUST_MAX_LEGITIMACY];
    u32 legitimacy_count;
    dom_trust_macro_capsule capsules[DOM_TRUST_MAX_CAPSULES];
    u32 capsule_count;
} dom_trust_domain;

void dom_trust_surface_desc_init(dom_trust_surface_desc* desc);

void dom_trust_domain_init(dom_trust_domain* domain,
                           const dom_trust_surface_desc* desc);
void dom_trust_domain_free(dom_trust_domain* domain);
void dom_trust_domain_set_state(dom_trust_domain* domain,
                                u32 existence_state,
                                u32 archival_state);
void dom_trust_domain_set_policy(dom_trust_domain* domain,
                                 const dom_domain_policy* policy);

int dom_trust_field_query(const dom_trust_domain* domain,
                          u32 trust_id,
                          dom_domain_budget* budget,
                          dom_trust_field_sample* out_sample);

int dom_trust_event_query(const dom_trust_domain* domain,
                          u32 event_id,
                          dom_domain_budget* budget,
                          dom_trust_event_sample* out_sample);

int dom_reputation_profile_query(const dom_trust_domain* domain,
                                 u32 profile_id,
                                 dom_domain_budget* budget,
                                 dom_reputation_profile_sample* out_sample);

int dom_legitimacy_field_query(const dom_trust_domain* domain,
                               u32 legitimacy_id,
                               dom_domain_budget* budget,
                               dom_legitimacy_field_sample* out_sample);

int dom_trust_region_query(const dom_trust_domain* domain,
                           u32 region_id,
                           dom_domain_budget* budget,
                           dom_trust_region_sample* out_sample);

int dom_trust_resolve(dom_trust_domain* domain,
                      u32 region_id,
                      u64 tick,
                      u64 tick_delta,
                      dom_domain_budget* budget,
                      dom_trust_resolve_result* out_result);

int dom_trust_domain_collapse_region(dom_trust_domain* domain, u32 region_id);
int dom_trust_domain_expand_region(dom_trust_domain* domain, u32 region_id);

u32 dom_trust_domain_capsule_count(const dom_trust_domain* domain);
const dom_trust_macro_capsule* dom_trust_domain_capsule_at(const dom_trust_domain* domain,
                                                           u32 index);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINO_WORLD_TRUST_FIELDS_H */
