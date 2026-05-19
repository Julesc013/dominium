/*
FILE: include/domino/world/knowledge_fields.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / world/knowledge_fields
RESPONSIBILITY: Deterministic knowledge, skill, and education field sampling.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 headers as needed.
FORBIDDEN DEPENDENCIES: Engine private headers outside `include/domino/**`.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: Fixed-point only; deterministic ordering and math.
VERSIONING / ABI / DATA FORMAT NOTES: Versioned by KNS0 specs.
EXTENSION POINTS: Extend via public headers and relevant `docs/architecture/**`.
*/
#ifndef DOMINO_WORLD_KNOWLEDGE_FIELDS_H
#define DOMINO_WORLD_KNOWLEDGE_FIELDS_H

#include "domino/core/types.h"
#include "domino/core/fixed.h"
#include "domino/world/domain_query.h"

#ifdef __cplusplus
extern "C" {
#endif

#define DOM_KNOWLEDGE_MAX_ARTIFACTS 128u
#define DOM_KNOWLEDGE_MAX_SKILLS 128u
#define DOM_KNOWLEDGE_MAX_PROGRAMS 64u
#define DOM_KNOWLEDGE_MAX_EVENTS 128u
#define DOM_KNOWLEDGE_MAX_REGIONS 16u
#define DOM_KNOWLEDGE_MAX_CAPSULES 64u
#define DOM_KNOWLEDGE_MAX_PROCESS_REFS 8u
#define DOM_KNOWLEDGE_MAX_INSTRUCTOR_REFS 8u
#define DOM_KNOWLEDGE_HIST_BINS 4u

#define DOM_KNOWLEDGE_RATIO_ONE_Q16 ((q16_16)0x00010000)

enum dom_knowledge_process_type {
    DOM_KNOWLEDGE_PROCESS_UNSET = 0u,
    DOM_KNOWLEDGE_PROCESS_PRACTICE = 1u,
    DOM_KNOWLEDGE_PROCESS_STUDY = 2u,
    DOM_KNOWLEDGE_PROCESS_TRAIN = 3u,
    DOM_KNOWLEDGE_PROCESS_CERTIFY = 4u
};

enum dom_knowledge_artifact_flags {
    DOM_KNOWLEDGE_ARTIFACT_UNRESOLVED = 1u << 0u,
    DOM_KNOWLEDGE_ARTIFACT_COLLAPSED = 1u << 1u,
    DOM_KNOWLEDGE_ARTIFACT_DECAYING = 1u << 2u
};

enum dom_skill_profile_flags {
    DOM_SKILL_PROFILE_UNRESOLVED = 1u << 0u,
    DOM_SKILL_PROFILE_COLLAPSED = 1u << 1u,
    DOM_SKILL_PROFILE_DECAYING = 1u << 2u
};

enum dom_education_program_flags {
    DOM_EDU_PROGRAM_UNRESOLVED = 1u << 0u,
    DOM_EDU_PROGRAM_COLLAPSED = 1u << 1u
};

enum dom_knowledge_event_flags {
    DOM_KNOWLEDGE_EVENT_UNRESOLVED = 1u << 0u,
    DOM_KNOWLEDGE_EVENT_APPLIED = 1u << 1u
};

enum dom_knowledge_resolve_flags {
    DOM_KNOWLEDGE_RESOLVE_PARTIAL = 1u << 0u,
    DOM_KNOWLEDGE_RESOLVE_DECAYED = 1u << 1u,
    DOM_KNOWLEDGE_RESOLVE_EVENT_APPLIED = 1u << 2u
};

enum dom_knowledge_refusal_reason {
    DOM_KNOWLEDGE_REFUSE_NONE = 0u,
    DOM_KNOWLEDGE_REFUSE_BUDGET = 1u,
    DOM_KNOWLEDGE_REFUSE_DOMAIN_INACTIVE = 2u,
    DOM_KNOWLEDGE_REFUSE_ARTIFACT_MISSING = 3u,
    DOM_KNOWLEDGE_REFUSE_SKILL_MISSING = 4u,
    DOM_KNOWLEDGE_REFUSE_PROGRAM_MISSING = 5u,
    DOM_KNOWLEDGE_REFUSE_EVENT_MISSING = 6u,
    DOM_KNOWLEDGE_REFUSE_POLICY = 7u,
    DOM_KNOWLEDGE_REFUSE_INTERNAL = 8u
};

typedef struct dom_knowledge_artifact_desc {
    u32 artifact_id;
    u32 subject_domain_id;
    u32 claim_count;
    u32 evidence_count;
    q16_16 confidence;
    q16_16 uncertainty;
    q16_16 decay_rate;
    u32 provenance_id;
    u32 region_id;
} dom_knowledge_artifact_desc;

typedef struct dom_skill_profile_desc {
    u32 profile_id;
    u32 subject_ref_id;
    u32 skill_domain_id;
    q16_16 variance_reduction;
    q16_16 failure_bias_reduction;
    q16_16 decay_rate;
    u32 process_ref_count;
    u32 process_refs[DOM_KNOWLEDGE_MAX_PROCESS_REFS];
    u32 provenance_id;
    u32 region_id;
} dom_skill_profile_desc;

typedef struct dom_education_program_desc {
    u32 program_id;
    u32 curriculum_id;
    u64 duration_ticks;
    q48_16 energy_cost;
    q48_16 resource_cost;
    u32 instructor_count;
    u32 instructor_refs[DOM_KNOWLEDGE_MAX_INSTRUCTOR_REFS];
    u32 output_skill_id;
    u32 accreditation_id;
    u32 provenance_id;
    u32 region_id;
} dom_education_program_desc;

typedef struct dom_knowledge_event_desc {
    u32 event_id;
    u32 process_type;
    u32 subject_ref_id;
    u32 artifact_id;
    u32 skill_id;
    u32 program_id;
    q16_16 delta_confidence;
    q16_16 delta_uncertainty;
    q16_16 delta_variance;
    q16_16 delta_failure_bias;
    u64 event_tick;
    u32 region_id;
    u32 provenance_id;
    u32 flags; /* dom_knowledge_event_flags */
} dom_knowledge_event_desc;

typedef struct dom_knowledge_artifact {
    u32 artifact_id;
    u32 subject_domain_id;
    u32 claim_count;
    u32 evidence_count;
    q16_16 confidence;
    q16_16 uncertainty;
    q16_16 decay_rate;
    u32 provenance_id;
    u32 region_id;
    u32 flags; /* dom_knowledge_artifact_flags */
} dom_knowledge_artifact;

typedef struct dom_skill_profile {
    u32 profile_id;
    u32 subject_ref_id;
    u32 skill_domain_id;
    q16_16 variance_reduction;
    q16_16 failure_bias_reduction;
    q16_16 decay_rate;
    u32 process_ref_count;
    u32 process_refs[DOM_KNOWLEDGE_MAX_PROCESS_REFS];
    u32 provenance_id;
    u32 region_id;
    u32 flags; /* dom_skill_profile_flags */
} dom_skill_profile;

typedef struct dom_education_program {
    u32 program_id;
    u32 curriculum_id;
    u64 duration_ticks;
    q48_16 energy_cost;
    q48_16 resource_cost;
    u32 instructor_count;
    u32 instructor_refs[DOM_KNOWLEDGE_MAX_INSTRUCTOR_REFS];
    u32 output_skill_id;
    u32 accreditation_id;
    u32 provenance_id;
    u32 region_id;
    u32 flags; /* dom_education_program_flags */
} dom_education_program;

typedef struct dom_knowledge_event {
    u32 event_id;
    u32 process_type;
    u32 subject_ref_id;
    u32 artifact_id;
    u32 skill_id;
    u32 program_id;
    q16_16 delta_confidence;
    q16_16 delta_uncertainty;
    q16_16 delta_variance;
    q16_16 delta_failure_bias;
    u64 event_tick;
    u32 region_id;
    u32 provenance_id;
    u32 flags; /* dom_knowledge_event_flags */
} dom_knowledge_event;

typedef struct dom_knowledge_surface_desc {
    dom_domain_id domain_id;
    u64 world_seed;
    q16_16 meters_per_unit;
    u32 artifact_count;
    dom_knowledge_artifact_desc artifacts[DOM_KNOWLEDGE_MAX_ARTIFACTS];
    u32 skill_count;
    dom_skill_profile_desc skills[DOM_KNOWLEDGE_MAX_SKILLS];
    u32 program_count;
    dom_education_program_desc programs[DOM_KNOWLEDGE_MAX_PROGRAMS];
    u32 event_count;
    dom_knowledge_event_desc events[DOM_KNOWLEDGE_MAX_EVENTS];
} dom_knowledge_surface_desc;

typedef struct dom_knowledge_artifact_sample {
    u32 artifact_id;
    u32 subject_domain_id;
    u32 claim_count;
    u32 evidence_count;
    q16_16 confidence;
    q16_16 uncertainty;
    q16_16 decay_rate;
    u32 provenance_id;
    u32 region_id;
    u32 flags; /* dom_knowledge_artifact_flags */
    dom_domain_query_meta meta;
} dom_knowledge_artifact_sample;

typedef struct dom_skill_profile_sample {
    u32 profile_id;
    u32 subject_ref_id;
    u32 skill_domain_id;
    q16_16 variance_reduction;
    q16_16 failure_bias_reduction;
    q16_16 decay_rate;
    u32 process_ref_count;
    u32 process_refs[DOM_KNOWLEDGE_MAX_PROCESS_REFS];
    u32 provenance_id;
    u32 region_id;
    u32 flags; /* dom_skill_profile_flags */
    dom_domain_query_meta meta;
} dom_skill_profile_sample;

typedef struct dom_education_program_sample {
    u32 program_id;
    u32 curriculum_id;
    u64 duration_ticks;
    q48_16 energy_cost;
    q48_16 resource_cost;
    u32 instructor_count;
    u32 instructor_refs[DOM_KNOWLEDGE_MAX_INSTRUCTOR_REFS];
    u32 output_skill_id;
    u32 accreditation_id;
    u32 provenance_id;
    u32 region_id;
    u32 flags; /* dom_education_program_flags */
    dom_domain_query_meta meta;
} dom_education_program_sample;

typedef struct dom_knowledge_event_sample {
    u32 event_id;
    u32 process_type;
    u32 subject_ref_id;
    u32 artifact_id;
    u32 skill_id;
    u32 program_id;
    q16_16 delta_confidence;
    q16_16 delta_uncertainty;
    q16_16 delta_variance;
    q16_16 delta_failure_bias;
    u64 event_tick;
    u32 region_id;
    u32 provenance_id;
    u32 flags; /* dom_knowledge_event_flags */
    dom_domain_query_meta meta;
} dom_knowledge_event_sample;

typedef struct dom_knowledge_region_sample {
    u32 region_id;
    u32 artifact_count;
    u32 skill_count;
    u32 program_count;
    u32 event_count;
    q16_16 confidence_avg;
    q16_16 uncertainty_avg;
    q16_16 variance_reduction_avg;
    q16_16 failure_bias_reduction_avg;
    u32 flags; /* dom_knowledge_resolve_flags */
    dom_domain_query_meta meta;
} dom_knowledge_region_sample;

typedef struct dom_knowledge_resolve_result {
    u32 ok;
    u32 refusal_reason; /* dom_knowledge_refusal_reason */
    u32 flags; /* dom_knowledge_resolve_flags */
    u32 artifact_count;
    u32 skill_count;
    u32 program_count;
    u32 event_count;
    u32 event_applied_count;
    q16_16 confidence_avg;
    q16_16 uncertainty_avg;
    q16_16 variance_reduction_avg;
    q16_16 failure_bias_reduction_avg;
} dom_knowledge_resolve_result;

typedef struct dom_knowledge_macro_capsule {
    u64 capsule_id;
    u32 region_id;
    u32 artifact_count;
    u32 skill_count;
    u32 program_count;
    q16_16 confidence_avg;
    q16_16 variance_reduction_avg;
    q16_16 confidence_hist[DOM_KNOWLEDGE_HIST_BINS];
    q16_16 variance_hist[DOM_KNOWLEDGE_HIST_BINS];
    u32 rng_cursor[DOM_KNOWLEDGE_HIST_BINS];
} dom_knowledge_macro_capsule;

typedef struct dom_knowledge_domain {
    dom_domain_policy policy;
    u32 existence_state;
    u32 archival_state;
    u32 authoring_version;
    dom_knowledge_surface_desc surface;
    dom_knowledge_artifact artifacts[DOM_KNOWLEDGE_MAX_ARTIFACTS];
    u32 artifact_count;
    dom_skill_profile skills[DOM_KNOWLEDGE_MAX_SKILLS];
    u32 skill_count;
    dom_education_program programs[DOM_KNOWLEDGE_MAX_PROGRAMS];
    u32 program_count;
    dom_knowledge_event events[DOM_KNOWLEDGE_MAX_EVENTS];
    u32 event_count;
    dom_knowledge_macro_capsule capsules[DOM_KNOWLEDGE_MAX_CAPSULES];
    u32 capsule_count;
} dom_knowledge_domain;

void dom_knowledge_surface_desc_init(dom_knowledge_surface_desc* desc);

void dom_knowledge_domain_init(dom_knowledge_domain* domain,
                               const dom_knowledge_surface_desc* desc);
void dom_knowledge_domain_free(dom_knowledge_domain* domain);
void dom_knowledge_domain_set_state(dom_knowledge_domain* domain,
                                    u32 existence_state,
                                    u32 archival_state);
void dom_knowledge_domain_set_policy(dom_knowledge_domain* domain,
                                     const dom_domain_policy* policy);

int dom_knowledge_artifact_query(const dom_knowledge_domain* domain,
                                 u32 artifact_id,
                                 dom_domain_budget* budget,
                                 dom_knowledge_artifact_sample* out_sample);

int dom_skill_profile_query(const dom_knowledge_domain* domain,
                            u32 profile_id,
                            dom_domain_budget* budget,
                            dom_skill_profile_sample* out_sample);

int dom_education_program_query(const dom_knowledge_domain* domain,
                                u32 program_id,
                                dom_domain_budget* budget,
                                dom_education_program_sample* out_sample);

int dom_knowledge_event_query(const dom_knowledge_domain* domain,
                              u32 event_id,
                              dom_domain_budget* budget,
                              dom_knowledge_event_sample* out_sample);

int dom_knowledge_region_query(const dom_knowledge_domain* domain,
                               u32 region_id,
                               dom_domain_budget* budget,
                               dom_knowledge_region_sample* out_sample);

int dom_knowledge_resolve(dom_knowledge_domain* domain,
                          u32 region_id,
                          u64 tick,
                          u64 tick_delta,
                          dom_domain_budget* budget,
                          dom_knowledge_resolve_result* out_result);

int dom_knowledge_domain_collapse_region(dom_knowledge_domain* domain, u32 region_id);
int dom_knowledge_domain_expand_region(dom_knowledge_domain* domain, u32 region_id);

u32 dom_knowledge_domain_capsule_count(const dom_knowledge_domain* domain);
const dom_knowledge_macro_capsule* dom_knowledge_domain_capsule_at(const dom_knowledge_domain* domain,
                                                                   u32 index);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINO_WORLD_KNOWLEDGE_FIELDS_H */
