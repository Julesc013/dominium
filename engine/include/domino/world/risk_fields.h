/*
FILE: include/domino/world/risk_fields.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / world/risk_fields
RESPONSIBILITY: Deterministic risk fields, liability, and insurance resolution.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 headers as needed.
FORBIDDEN DEPENDENCIES: Engine private headers outside `include/domino/**`.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: Fixed-point only; deterministic ordering and math.
VERSIONING / ABI / DATA FORMAT NOTES: Versioned by RISK0 specs.
EXTENSION POINTS: Extend via public headers and relevant `docs/architecture/**`.
*/
#ifndef DOMINO_WORLD_RISK_FIELDS_H
#define DOMINO_WORLD_RISK_FIELDS_H

#include "domino/core/types.h"
#include "domino/core/fixed.h"
#include "domino/world/domain_query.h"

#ifdef __cplusplus
extern "C" {
#endif

#define DOM_RISK_MAX_TYPES 32u
#define DOM_RISK_MAX_FIELDS 128u
#define DOM_RISK_MAX_EXPOSURES 128u
#define DOM_RISK_MAX_PROFILES 64u
#define DOM_RISK_MAX_EVENTS 64u
#define DOM_RISK_MAX_ATTRIBUTIONS 128u
#define DOM_RISK_MAX_POLICIES 64u
#define DOM_RISK_MAX_CLAIMS 128u
#define DOM_RISK_MAX_REGIONS 16u
#define DOM_RISK_MAX_CAPSULES 64u
#define DOM_RISK_HIST_BINS 4u
#define DOM_RISK_CLASS_COUNT 6u

#define DOM_RISK_RATIO_ONE_Q16 ((q16_16)0x00010000)

enum dom_risk_class {
    DOM_RISK_CLASS_UNSET = 0u,
    DOM_RISK_CLASS_FIRE = 1u,
    DOM_RISK_CLASS_FLOOD = 2u,
    DOM_RISK_CLASS_TOXIC = 3u,
    DOM_RISK_CLASS_THERMAL = 4u,
    DOM_RISK_CLASS_FINANCIAL = 5u,
    DOM_RISK_CLASS_INFO = 6u
};

enum dom_risk_field_flags {
    DOM_RISK_FIELD_UNRESOLVED = 1u << 0u,
    DOM_RISK_FIELD_COLLAPSED = 1u << 1u,
    DOM_RISK_FIELD_DECAYING = 1u << 2u
};

enum dom_risk_type_flags {
    DOM_RISK_TYPE_UNRESOLVED = 1u << 0u
};

enum dom_risk_exposure_flags {
    DOM_RISK_EXPOSURE_UNRESOLVED = 1u << 0u,
    DOM_RISK_EXPOSURE_COLLAPSED = 1u << 1u,
    DOM_RISK_EXPOSURE_OVER_LIMIT = 1u << 2u
};

enum dom_risk_profile_flags {
    DOM_RISK_PROFILE_UNRESOLVED = 1u << 0u,
    DOM_RISK_PROFILE_COLLAPSED = 1u << 1u
};

enum dom_risk_event_flags {
    DOM_RISK_EVENT_UNRESOLVED = 1u << 0u
};

enum dom_risk_attr_flags {
    DOM_RISK_ATTR_UNRESOLVED = 1u << 0u
};

enum dom_risk_policy_flags {
    DOM_RISK_POLICY_UNRESOLVED = 1u << 0u,
    DOM_RISK_POLICY_INACTIVE = 1u << 1u
};

enum dom_risk_claim_flags {
    DOM_RISK_CLAIM_UNRESOLVED = 1u << 0u,
    DOM_RISK_CLAIM_APPROVED = 1u << 1u,
    DOM_RISK_CLAIM_DENIED = 1u << 2u
};

enum dom_risk_resolve_flags {
    DOM_RISK_RESOLVE_PARTIAL = 1u << 0u,
    DOM_RISK_RESOLVE_DECAYED = 1u << 1u,
    DOM_RISK_RESOLVE_OVER_LIMIT = 1u << 2u,
    DOM_RISK_RESOLVE_CLAIM_APPROVED = 1u << 3u,
    DOM_RISK_RESOLVE_CLAIM_DENIED = 1u << 4u
};

enum dom_risk_refusal_reason {
    DOM_RISK_REFUSE_NONE = 0u,
    DOM_RISK_REFUSE_BUDGET = 1u,
    DOM_RISK_REFUSE_DOMAIN_INACTIVE = 2u,
    DOM_RISK_REFUSE_FIELD_MISSING = 3u,
    DOM_RISK_REFUSE_EXPOSURE_MISSING = 4u,
    DOM_RISK_REFUSE_PROFILE_MISSING = 5u,
    DOM_RISK_REFUSE_EVENT_MISSING = 6u,
    DOM_RISK_REFUSE_POLICY_MISSING = 7u,
    DOM_RISK_REFUSE_CLAIM_MISSING = 8u,
    DOM_RISK_REFUSE_POLICY = 9u,
    DOM_RISK_REFUSE_INTERNAL = 10u
};

typedef struct dom_risk_type_desc {
    u32 type_id;
    u32 risk_class;
    q16_16 default_exposure_rate;
    q48_16 default_impact_mean;
    q16_16 default_impact_spread;
    q16_16 default_uncertainty;
} dom_risk_type_desc;

typedef struct dom_risk_field_desc {
    u32 risk_id;
    u32 risk_type_id;
    q16_16 exposure_rate;
    q48_16 impact_mean;
    q16_16 impact_spread;
    q16_16 uncertainty;
    u32 hazard_ref_id;
    u32 provenance_id;
    u32 region_id;
    q16_16 radius;
    dom_domain_point center;
} dom_risk_field_desc;

typedef struct dom_risk_exposure_desc {
    u32 exposure_id;
    u32 risk_type_id;
    q16_16 exposure_rate;
    q48_16 exposure_limit;
    q48_16 exposure_accumulated;
    q16_16 sensitivity;
    q16_16 uncertainty;
    u32 subject_ref_id;
    u32 region_id;
    dom_domain_point location;
    u32 provenance_id;
} dom_risk_exposure_desc;

typedef struct dom_risk_profile_desc {
    u32 profile_id;
    u32 subject_ref_id;
    u32 region_id;
    q48_16 exposure_total;
    q48_16 impact_mean;
    q16_16 impact_spread;
    q16_16 uncertainty;
} dom_risk_profile_desc;

typedef struct dom_liability_event_desc {
    u32 event_id;
    u32 risk_type_id;
    u32 hazard_ref_id;
    u32 exposure_ref_id;
    q48_16 loss_amount;
    u64 event_tick;
    u32 subject_ref_id;
    u32 region_id;
    u32 provenance_id;
} dom_liability_event_desc;

typedef struct dom_liability_attribution_desc {
    u32 attribution_id;
    u32 event_id;
    u32 responsible_ref_id;
    u32 role_tag;
    u32 compliance_tag;
    q16_16 negligence_score;
    q16_16 share_ratio;
    q16_16 uncertainty;
    u32 provenance_id;
} dom_liability_attribution_desc;

typedef struct dom_insurance_policy_desc {
    u32 policy_id;
    u32 holder_ref_id;
    u32 risk_type_id;
    q16_16 coverage_ratio;
    q48_16 premium;
    q48_16 payout_limit;
    q48_16 deductible;
    u32 audit_tag;
    q16_16 audit_score;
    u64 start_tick;
    u64 end_tick;
    u32 region_id;
} dom_insurance_policy_desc;

typedef struct dom_insurance_claim_desc {
    u32 claim_id;
    u32 policy_id;
    u32 event_id;
    q48_16 claim_amount;
    q48_16 approved_amount;
    u32 status_tag;
    u64 filed_tick;
    u64 resolved_tick;
    u32 audit_ref_id;
} dom_insurance_claim_desc;

typedef struct dom_risk_type {
    u32 type_id;
    u32 risk_class;
    q16_16 default_exposure_rate;
    q48_16 default_impact_mean;
    q16_16 default_impact_spread;
    q16_16 default_uncertainty;
    u32 flags; /* dom_risk_type_flags */
} dom_risk_type;

typedef struct dom_risk_field {
    u32 risk_id;
    u32 risk_type_id;
    q16_16 exposure_rate;
    q48_16 impact_mean;
    q16_16 impact_spread;
    q16_16 uncertainty;
    u32 hazard_ref_id;
    u32 provenance_id;
    u32 region_id;
    q16_16 radius;
    dom_domain_point center;
    u32 flags;
} dom_risk_field;

typedef struct dom_risk_exposure {
    u32 exposure_id;
    u32 risk_type_id;
    q16_16 exposure_rate;
    q48_16 exposure_limit;
    q48_16 exposure_accumulated;
    q16_16 sensitivity;
    q16_16 uncertainty;
    u32 subject_ref_id;
    u32 region_id;
    dom_domain_point location;
    u32 provenance_id;
    u32 flags;
} dom_risk_exposure;

typedef struct dom_risk_profile {
    u32 profile_id;
    u32 subject_ref_id;
    u32 region_id;
    q48_16 exposure_total;
    q48_16 impact_mean;
    q16_16 impact_spread;
    q16_16 uncertainty;
    u32 flags;
} dom_risk_profile;

typedef struct dom_liability_event {
    u32 event_id;
    u32 risk_type_id;
    u32 hazard_ref_id;
    u32 exposure_ref_id;
    q48_16 loss_amount;
    u64 event_tick;
    u32 subject_ref_id;
    u32 region_id;
    u32 provenance_id;
    u32 flags;
} dom_liability_event;

typedef struct dom_liability_attribution {
    u32 attribution_id;
    u32 event_id;
    u32 responsible_ref_id;
    u32 role_tag;
    u32 compliance_tag;
    q16_16 negligence_score;
    q16_16 share_ratio;
    q16_16 uncertainty;
    u32 provenance_id;
    u32 flags;
} dom_liability_attribution;

typedef struct dom_insurance_policy {
    u32 policy_id;
    u32 holder_ref_id;
    u32 risk_type_id;
    q16_16 coverage_ratio;
    q48_16 premium;
    q48_16 payout_limit;
    q48_16 deductible;
    u32 audit_tag;
    q16_16 audit_score;
    u64 start_tick;
    u64 end_tick;
    u32 region_id;
    u32 flags;
} dom_insurance_policy;

typedef struct dom_insurance_claim {
    u32 claim_id;
    u32 policy_id;
    u32 event_id;
    q48_16 claim_amount;
    q48_16 approved_amount;
    u32 status_tag;
    u64 filed_tick;
    u64 resolved_tick;
    u32 audit_ref_id;
    u32 flags;
} dom_insurance_claim;

typedef struct dom_risk_surface_desc {
    dom_domain_id domain_id;
    u64 world_seed;
    q16_16 meters_per_unit;
    u32 type_count;
    dom_risk_type_desc types[DOM_RISK_MAX_TYPES];
    u32 field_count;
    dom_risk_field_desc fields[DOM_RISK_MAX_FIELDS];
    u32 exposure_count;
    dom_risk_exposure_desc exposures[DOM_RISK_MAX_EXPOSURES];
    u32 profile_count;
    dom_risk_profile_desc profiles[DOM_RISK_MAX_PROFILES];
    u32 event_count;
    dom_liability_event_desc events[DOM_RISK_MAX_EVENTS];
    u32 attribution_count;
    dom_liability_attribution_desc attributions[DOM_RISK_MAX_ATTRIBUTIONS];
    u32 policy_count;
    dom_insurance_policy_desc policies[DOM_RISK_MAX_POLICIES];
    u32 claim_count;
    dom_insurance_claim_desc claims[DOM_RISK_MAX_CLAIMS];
} dom_risk_surface_desc;

typedef struct dom_risk_type_sample {
    u32 type_id;
    u32 risk_class;
    q16_16 default_exposure_rate;
    q48_16 default_impact_mean;
    q16_16 default_impact_spread;
    q16_16 default_uncertainty;
    u32 flags; /* dom_risk_type_flags */
    dom_domain_query_meta meta;
} dom_risk_type_sample;

typedef struct dom_risk_field_sample {
    u32 risk_id;
    u32 risk_type_id;
    q16_16 exposure_rate;
    q48_16 impact_mean;
    q16_16 impact_spread;
    q16_16 uncertainty;
    u32 hazard_ref_id;
    u32 provenance_id;
    u32 region_id;
    q16_16 radius;
    u32 flags;
    dom_domain_query_meta meta;
} dom_risk_field_sample;

typedef struct dom_risk_exposure_sample {
    u32 exposure_id;
    u32 risk_type_id;
    q16_16 exposure_rate;
    q48_16 exposure_limit;
    q48_16 exposure_accumulated;
    q16_16 sensitivity;
    q16_16 uncertainty;
    u32 subject_ref_id;
    u32 region_id;
    u32 provenance_id;
    u32 flags;
    dom_domain_query_meta meta;
} dom_risk_exposure_sample;

typedef struct dom_risk_profile_sample {
    u32 profile_id;
    u32 subject_ref_id;
    u32 region_id;
    q48_16 exposure_total;
    q48_16 impact_mean;
    q16_16 impact_spread;
    q16_16 uncertainty;
    u32 flags;
    dom_domain_query_meta meta;
} dom_risk_profile_sample;

typedef struct dom_liability_event_sample {
    u32 event_id;
    u32 risk_type_id;
    u32 hazard_ref_id;
    u32 exposure_ref_id;
    q48_16 loss_amount;
    u64 event_tick;
    u32 subject_ref_id;
    u32 region_id;
    u32 provenance_id;
    u32 flags;
    dom_domain_query_meta meta;
} dom_liability_event_sample;

typedef struct dom_liability_attribution_sample {
    u32 attribution_id;
    u32 event_id;
    u32 responsible_ref_id;
    u32 role_tag;
    u32 compliance_tag;
    q16_16 negligence_score;
    q16_16 share_ratio;
    q16_16 uncertainty;
    u32 provenance_id;
    u32 flags;
    dom_domain_query_meta meta;
} dom_liability_attribution_sample;

typedef struct dom_insurance_policy_sample {
    u32 policy_id;
    u32 holder_ref_id;
    u32 risk_type_id;
    q16_16 coverage_ratio;
    q48_16 premium;
    q48_16 payout_limit;
    q48_16 deductible;
    u32 audit_tag;
    q16_16 audit_score;
    u64 start_tick;
    u64 end_tick;
    u32 region_id;
    u32 flags;
    dom_domain_query_meta meta;
} dom_insurance_policy_sample;

typedef struct dom_insurance_claim_sample {
    u32 claim_id;
    u32 policy_id;
    u32 event_id;
    q48_16 claim_amount;
    q48_16 approved_amount;
    u32 status_tag;
    u64 filed_tick;
    u64 resolved_tick;
    u32 audit_ref_id;
    u32 flags;
    dom_domain_query_meta meta;
} dom_insurance_claim_sample;

typedef struct dom_risk_region_sample {
    u32 region_id;
    u32 field_count;
    u32 exposure_count;
    u32 profile_count;
    q48_16 exposure_total;
    q48_16 impact_mean_total;
    q16_16 impact_spread_avg;
    u32 flags; /* dom_risk_resolve_flags */
    dom_domain_query_meta meta;
} dom_risk_region_sample;

typedef struct dom_risk_resolve_result {
    u32 ok;
    u32 refusal_reason; /* dom_risk_refusal_reason */
    u32 flags; /* dom_risk_resolve_flags */
    u32 field_count;
    u32 exposure_count;
    u32 exposure_over_limit_count;
    u32 profile_count;
    u32 claim_count;
    u32 claim_approved_count;
    u32 claim_denied_count;
    q48_16 exposure_total;
    q48_16 impact_mean_total;
    q48_16 claim_paid_total;
} dom_risk_resolve_result;

typedef struct dom_risk_macro_capsule {
    u64 capsule_id;
    u32 region_id;
    u32 field_count;
    u32 exposure_count;
    u32 profile_count;
    q48_16 exposure_total;
    u32 risk_type_counts[DOM_RISK_CLASS_COUNT];
    q16_16 exposure_hist[DOM_RISK_HIST_BINS];
    u32 rng_cursor[DOM_RISK_CLASS_COUNT];
} dom_risk_macro_capsule;

typedef struct dom_risk_domain {
    dom_domain_policy policy;
    u32 existence_state;
    u32 archival_state;
    u32 authoring_version;
    dom_risk_surface_desc surface;
    dom_risk_type types[DOM_RISK_MAX_TYPES];
    u32 type_count;
    dom_risk_field fields[DOM_RISK_MAX_FIELDS];
    u32 field_count;
    dom_risk_exposure exposures[DOM_RISK_MAX_EXPOSURES];
    u32 exposure_count;
    dom_risk_profile profiles[DOM_RISK_MAX_PROFILES];
    u32 profile_count;
    dom_liability_event events[DOM_RISK_MAX_EVENTS];
    u32 event_count;
    dom_liability_attribution attributions[DOM_RISK_MAX_ATTRIBUTIONS];
    u32 attribution_count;
    dom_insurance_policy policies[DOM_RISK_MAX_POLICIES];
    u32 policy_count;
    dom_insurance_claim claims[DOM_RISK_MAX_CLAIMS];
    u32 claim_count;
    dom_risk_macro_capsule capsules[DOM_RISK_MAX_CAPSULES];
    u32 capsule_count;
} dom_risk_domain;

void dom_risk_surface_desc_init(dom_risk_surface_desc* desc);

void dom_risk_domain_init(dom_risk_domain* domain,
                          const dom_risk_surface_desc* desc);
void dom_risk_domain_free(dom_risk_domain* domain);
void dom_risk_domain_set_state(dom_risk_domain* domain,
                               u32 existence_state,
                               u32 archival_state);
void dom_risk_domain_set_policy(dom_risk_domain* domain,
                                const dom_domain_policy* policy);

int dom_risk_type_query(const dom_risk_domain* domain,
                        u32 type_id,
                        dom_domain_budget* budget,
                        dom_risk_type_sample* out_sample);

int dom_risk_field_query(const dom_risk_domain* domain,
                         u32 field_id,
                         dom_domain_budget* budget,
                         dom_risk_field_sample* out_sample);

int dom_risk_exposure_query(const dom_risk_domain* domain,
                            u32 exposure_id,
                            dom_domain_budget* budget,
                            dom_risk_exposure_sample* out_sample);

int dom_risk_profile_query(const dom_risk_domain* domain,
                           u32 profile_id,
                           dom_domain_budget* budget,
                           dom_risk_profile_sample* out_sample);

int dom_liability_event_query(const dom_risk_domain* domain,
                              u32 event_id,
                              dom_domain_budget* budget,
                              dom_liability_event_sample* out_sample);

int dom_liability_attribution_query(const dom_risk_domain* domain,
                                    u32 attribution_id,
                                    dom_domain_budget* budget,
                                    dom_liability_attribution_sample* out_sample);

int dom_insurance_policy_query(const dom_risk_domain* domain,
                               u32 policy_id,
                               dom_domain_budget* budget,
                               dom_insurance_policy_sample* out_sample);

int dom_insurance_claim_query(const dom_risk_domain* domain,
                              u32 claim_id,
                              dom_domain_budget* budget,
                              dom_insurance_claim_sample* out_sample);

int dom_risk_region_query(const dom_risk_domain* domain,
                          u32 region_id,
                          dom_domain_budget* budget,
                          dom_risk_region_sample* out_sample);

int dom_risk_resolve(dom_risk_domain* domain,
                     u32 region_id,
                     u64 tick,
                     u64 tick_delta,
                     dom_domain_budget* budget,
                     dom_risk_resolve_result* out_result);

int dom_risk_domain_collapse_region(dom_risk_domain* domain, u32 region_id);
int dom_risk_domain_expand_region(dom_risk_domain* domain, u32 region_id);

u32 dom_risk_domain_capsule_count(const dom_risk_domain* domain);
const dom_risk_macro_capsule* dom_risk_domain_capsule_at(const dom_risk_domain* domain,
                                                         u32 index);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINO_WORLD_RISK_FIELDS_H */
