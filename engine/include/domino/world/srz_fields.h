/*
FILE: include/domino/world/srz_fields.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / world/srz_fields
RESPONSIBILITY: Deterministic simulation responsibility zone (SRZ) field sampling.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 headers as needed.
FORBIDDEN DEPENDENCIES: Engine private headers outside `include/domino/**`.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: Fixed-point only; deterministic ordering and math.
VERSIONING / ABI / DATA FORMAT NOTES: Versioned by SRZ0 specs.
EXTENSION POINTS: Extend via public headers and relevant `docs/architecture/**`.
*/
#ifndef DOMINO_WORLD_SRZ_FIELDS_H
#define DOMINO_WORLD_SRZ_FIELDS_H

#include "domino/core/types.h"
#include "domino/core/fixed.h"
#include "domino/world/domain_query.h"

#ifdef __cplusplus
extern "C" {
#endif

#define DOM_SRZ_MAX_ZONES 128u
#define DOM_SRZ_MAX_ASSIGNMENTS 128u
#define DOM_SRZ_MAX_POLICIES 64u
#define DOM_SRZ_MAX_LOGS 256u
#define DOM_SRZ_MAX_HASH_LINKS 512u
#define DOM_SRZ_MAX_DELTAS 128u
#define DOM_SRZ_MAX_DOMAIN_REFS 8u
#define DOM_SRZ_MAX_THRESHOLDS 8u
#define DOM_SRZ_MAX_REGIONS 16u
#define DOM_SRZ_MAX_CAPSULES 64u
#define DOM_SRZ_HIST_BINS 4u

#define DOM_SRZ_RATIO_ONE_Q16 ((q16_16)0x00010000)

enum dom_srz_mode {
    DOM_SRZ_MODE_UNSET = 0u,
    DOM_SRZ_MODE_SERVER = 1u,
    DOM_SRZ_MODE_DELEGATED = 2u,
    DOM_SRZ_MODE_DORMANT = 3u
};

enum dom_srz_verification_policy {
    DOM_SRZ_VERIFY_UNSET = 0u,
    DOM_SRZ_VERIFY_STRICT = 1u,
    DOM_SRZ_VERIFY_SPOT = 2u,
    DOM_SRZ_VERIFY_INVARIANT_ONLY = 3u
};

enum dom_srz_threshold_metric {
    DOM_SRZ_METRIC_UNSET = 0u,
    DOM_SRZ_METRIC_FAIL_RATE = 1u
};

enum dom_srz_zone_flags {
    DOM_SRZ_ZONE_UNRESOLVED = 1u << 0u,
    DOM_SRZ_ZONE_COLLAPSED = 1u << 1u,
    DOM_SRZ_ZONE_ESCALATED = 1u << 2u,
    DOM_SRZ_ZONE_DEESCALATED = 1u << 3u
};

enum dom_srz_assignment_flags {
    DOM_SRZ_ASSIGNMENT_UNRESOLVED = 1u << 0u,
    DOM_SRZ_ASSIGNMENT_COLLAPSED = 1u << 1u,
    DOM_SRZ_ASSIGNMENT_EXPIRED = 1u << 2u
};

enum dom_srz_policy_flags {
    DOM_SRZ_POLICY_UNRESOLVED = 1u << 0u
};

enum dom_srz_log_flags {
    DOM_SRZ_LOG_UNRESOLVED = 1u << 0u,
    DOM_SRZ_LOG_VERIFIED = 1u << 1u,
    DOM_SRZ_LOG_FAILED = 1u << 2u,
    DOM_SRZ_LOG_EPISTEMIC_MISMATCH = 1u << 3u
};

enum dom_srz_hash_flags {
    DOM_SRZ_HASH_UNRESOLVED = 1u << 0u,
    DOM_SRZ_HASH_BROKEN = 1u << 1u
};

enum dom_srz_delta_flags {
    DOM_SRZ_DELTA_UNRESOLVED = 1u << 0u,
    DOM_SRZ_DELTA_INVARIANTS_OK = 1u << 1u,
    DOM_SRZ_DELTA_INVARIANTS_FAIL = 1u << 2u
};

enum dom_srz_resolve_flags {
    DOM_SRZ_RESOLVE_PARTIAL = 1u << 0u,
    DOM_SRZ_RESOLVE_VERIFIED = 1u << 1u,
    DOM_SRZ_RESOLVE_VERIFICATION_FAILED = 1u << 2u,
    DOM_SRZ_RESOLVE_EPISTEMIC_REFUSED = 1u << 3u,
    DOM_SRZ_RESOLVE_ESCALATED = 1u << 4u,
    DOM_SRZ_RESOLVE_DEESCALATED = 1u << 5u,
    DOM_SRZ_RESOLVE_STRICT_APPLIED = 1u << 6u,
    DOM_SRZ_RESOLVE_SPOT_APPLIED = 1u << 7u,
    DOM_SRZ_RESOLVE_INVARIANT_ONLY_APPLIED = 1u << 8u
};

enum dom_srz_refusal_reason {
    DOM_SRZ_REFUSE_NONE = 0u,
    DOM_SRZ_REFUSE_BUDGET = 1u,
    DOM_SRZ_REFUSE_DOMAIN_INACTIVE = 2u,
    DOM_SRZ_REFUSE_ZONE_MISSING = 3u,
    DOM_SRZ_REFUSE_ASSIGNMENT_MISSING = 4u,
    DOM_SRZ_REFUSE_POLICY_MISSING = 5u,
    DOM_SRZ_REFUSE_LOG_MISSING = 6u,
    DOM_SRZ_REFUSE_HASH_MISSING = 7u,
    DOM_SRZ_REFUSE_DELTA_MISSING = 8u,
    DOM_SRZ_REFUSE_EPISTEMIC = 9u,
    DOM_SRZ_REFUSE_PROOF_INVALID = 10u,
    DOM_SRZ_REFUSE_POLICY = 11u,
    DOM_SRZ_REFUSE_INTERNAL = 12u
};

typedef struct dom_srz_threshold_desc {
    u32 metric_id;
    q16_16 value;
} dom_srz_threshold_desc;

typedef struct dom_srz_zone_desc {
    u32 srz_id;
    u32 domain_count;
    u32 domain_ids[DOM_SRZ_MAX_DOMAIN_REFS];
    u32 mode; /* dom_srz_mode */
    u32 verification_policy; /* dom_srz_verification_policy */
    u32 escalation_count;
    dom_srz_threshold_desc escalation[DOM_SRZ_MAX_THRESHOLDS];
    u32 deescalation_count;
    dom_srz_threshold_desc deescalation[DOM_SRZ_MAX_THRESHOLDS];
    u32 epistemic_scope_id;
    u32 policy_id;
    u32 provenance_id;
    u32 region_id;
    u32 flags; /* dom_srz_zone_flags */
} dom_srz_zone_desc;

typedef struct dom_srz_assignment_desc {
    u32 assignment_id;
    u32 srz_id;
    u32 executor_id;
    u32 authority_token_id;
    u32 capability_baseline_id;
    u64 start_tick;
    u64 expiry_tick;
    u32 provenance_id;
    u32 region_id;
    u32 flags; /* dom_srz_assignment_flags */
} dom_srz_assignment_desc;

typedef struct dom_srz_policy_desc {
    u32 policy_id;
    u32 verification_policy; /* dom_srz_verification_policy */
    q16_16 spot_check_rate;
    u64 strict_replay_interval;
    u64 max_segment_ticks;
    u32 provenance_id;
    u32 region_id;
    u32 flags; /* dom_srz_policy_flags */
} dom_srz_policy_desc;

typedef struct dom_srz_log_desc {
    u32 log_id;
    u32 srz_id;
    u32 assignment_id;
    u32 policy_id;
    u32 chain_id;
    u32 delta_id;
    u64 start_tick;
    u64 end_tick;
    u32 process_count;
    u32 rng_stream_count;
    u32 epistemic_scope_id;
    u32 provenance_id;
    u32 region_id;
    u32 flags; /* dom_srz_log_flags */
} dom_srz_log_desc;

typedef struct dom_srz_hash_link_desc {
    u32 link_id;
    u32 chain_id;
    u32 segment_index;
    u64 prev_hash;
    u64 hash;
    u64 start_tick;
    u64 end_tick;
    u32 process_count;
    u32 rng_stream_count;
    u32 provenance_id;
    u32 region_id;
    u32 flags; /* dom_srz_hash_flags */
} dom_srz_hash_link_desc;

typedef struct dom_srz_state_delta_desc {
    u32 delta_id;
    u32 srz_id;
    u32 log_id;
    u32 process_count;
    u32 rng_stream_count;
    u32 provenance_id;
    u32 region_id;
    u32 flags; /* dom_srz_delta_flags */
} dom_srz_state_delta_desc;

typedef struct dom_srz_zone {
    u32 srz_id;
    u32 domain_count;
    u32 domain_ids[DOM_SRZ_MAX_DOMAIN_REFS];
    u32 mode;
    u32 verification_policy;
    u32 escalation_count;
    dom_srz_threshold_desc escalation[DOM_SRZ_MAX_THRESHOLDS];
    u32 deescalation_count;
    dom_srz_threshold_desc deescalation[DOM_SRZ_MAX_THRESHOLDS];
    u32 epistemic_scope_id;
    u32 policy_id;
    u32 provenance_id;
    u32 region_id;
    u32 flags;
} dom_srz_zone;

typedef struct dom_srz_assignment {
    u32 assignment_id;
    u32 srz_id;
    u32 executor_id;
    u32 authority_token_id;
    u32 capability_baseline_id;
    u64 start_tick;
    u64 expiry_tick;
    u32 provenance_id;
    u32 region_id;
    u32 flags;
} dom_srz_assignment;

typedef struct dom_srz_policy {
    u32 policy_id;
    u32 verification_policy;
    q16_16 spot_check_rate;
    u64 strict_replay_interval;
    u64 max_segment_ticks;
    u32 provenance_id;
    u32 region_id;
    u32 flags;
} dom_srz_policy;

typedef struct dom_srz_log {
    u32 log_id;
    u32 srz_id;
    u32 assignment_id;
    u32 policy_id;
    u32 chain_id;
    u32 delta_id;
    u64 start_tick;
    u64 end_tick;
    u32 process_count;
    u32 rng_stream_count;
    u32 epistemic_scope_id;
    u32 provenance_id;
    u32 region_id;
    u32 flags;
} dom_srz_log;

typedef struct dom_srz_hash_link {
    u32 link_id;
    u32 chain_id;
    u32 segment_index;
    u64 prev_hash;
    u64 hash;
    u64 start_tick;
    u64 end_tick;
    u32 process_count;
    u32 rng_stream_count;
    u32 provenance_id;
    u32 region_id;
    u32 flags;
} dom_srz_hash_link;

typedef struct dom_srz_state_delta {
    u32 delta_id;
    u32 srz_id;
    u32 log_id;
    u32 process_count;
    u32 rng_stream_count;
    u32 provenance_id;
    u32 region_id;
    u32 flags;
} dom_srz_state_delta;

typedef struct dom_srz_surface_desc {
    dom_domain_id domain_id;
    u64 world_seed;
    q16_16 meters_per_unit;
    u32 zone_count;
    dom_srz_zone_desc zones[DOM_SRZ_MAX_ZONES];
    u32 assignment_count;
    dom_srz_assignment_desc assignments[DOM_SRZ_MAX_ASSIGNMENTS];
    u32 policy_count;
    dom_srz_policy_desc policies[DOM_SRZ_MAX_POLICIES];
    u32 log_count;
    dom_srz_log_desc logs[DOM_SRZ_MAX_LOGS];
    u32 hash_link_count;
    dom_srz_hash_link_desc hash_links[DOM_SRZ_MAX_HASH_LINKS];
    u32 delta_count;
    dom_srz_state_delta_desc deltas[DOM_SRZ_MAX_DELTAS];
} dom_srz_surface_desc;

typedef struct dom_srz_zone_sample {
    u32 srz_id;
    u32 domain_count;
    u32 mode;
    u32 verification_policy;
    u32 escalation_count;
    u32 deescalation_count;
    u32 epistemic_scope_id;
    u32 policy_id;
    u32 provenance_id;
    u32 region_id;
    u32 flags;
    dom_domain_query_meta meta;
} dom_srz_zone_sample;

typedef struct dom_srz_assignment_sample {
    u32 assignment_id;
    u32 srz_id;
    u32 executor_id;
    u32 authority_token_id;
    u32 capability_baseline_id;
    u64 start_tick;
    u64 expiry_tick;
    u32 provenance_id;
    u32 region_id;
    u32 flags;
    dom_domain_query_meta meta;
} dom_srz_assignment_sample;

typedef struct dom_srz_policy_sample {
    u32 policy_id;
    u32 verification_policy;
    q16_16 spot_check_rate;
    u64 strict_replay_interval;
    u64 max_segment_ticks;
    u32 provenance_id;
    u32 region_id;
    u32 flags;
    dom_domain_query_meta meta;
} dom_srz_policy_sample;

typedef struct dom_srz_log_sample {
    u32 log_id;
    u32 srz_id;
    u32 assignment_id;
    u32 policy_id;
    u32 chain_id;
    u32 delta_id;
    u64 start_tick;
    u64 end_tick;
    u32 process_count;
    u32 rng_stream_count;
    u32 epistemic_scope_id;
    u32 provenance_id;
    u32 region_id;
    u32 flags;
    dom_domain_query_meta meta;
} dom_srz_log_sample;

typedef struct dom_srz_hash_link_sample {
    u32 link_id;
    u32 chain_id;
    u32 segment_index;
    u64 prev_hash;
    u64 hash;
    u64 start_tick;
    u64 end_tick;
    u32 process_count;
    u32 rng_stream_count;
    u32 provenance_id;
    u32 region_id;
    u32 flags;
    dom_domain_query_meta meta;
} dom_srz_hash_link_sample;

typedef struct dom_srz_state_delta_sample {
    u32 delta_id;
    u32 srz_id;
    u32 log_id;
    u32 process_count;
    u32 rng_stream_count;
    u32 provenance_id;
    u32 region_id;
    u32 flags;
    dom_domain_query_meta meta;
} dom_srz_state_delta_sample;

typedef struct dom_srz_region_sample {
    u32 region_id;
    u32 zone_count;
    u32 assignment_count;
    u32 policy_count;
    u32 log_count;
    u32 hash_link_count;
    u32 delta_count;
    u32 server_mode_count;
    u32 delegated_mode_count;
    u32 dormant_mode_count;
    u32 verification_ok_count;
    u32 verification_fail_count;
    q16_16 failure_rate;
    u32 flags;
    dom_domain_query_meta meta;
} dom_srz_region_sample;

typedef struct dom_srz_resolve_result {
    u32 ok;
    u32 refusal_reason; /* dom_srz_refusal_reason */
    u32 flags; /* dom_srz_resolve_flags */
    u32 zone_count;
    u32 assignment_count;
    u32 policy_count;
    u32 log_count;
    u32 hash_link_count;
    u32 delta_count;
    u32 server_mode_count;
    u32 delegated_mode_count;
    u32 dormant_mode_count;
    u32 verification_ok_count;
    u32 verification_fail_count;
    q16_16 failure_rate;
} dom_srz_resolve_result;

typedef struct dom_srz_macro_capsule {
    u64 capsule_id;
    u32 region_id;
    u32 zone_count;
    u32 assignment_count;
    u32 policy_count;
    u32 log_count;
    u32 hash_link_count;
    u32 delta_count;
    u32 verification_ok_count;
    u32 verification_fail_count;
    q16_16 failure_hist[DOM_SRZ_HIST_BINS];
    u32 rng_cursor[DOM_SRZ_HIST_BINS];
} dom_srz_macro_capsule;

typedef struct dom_srz_domain {
    dom_domain_policy policy;
    u32 existence_state;
    u32 archival_state;
    u32 authoring_version;
    dom_srz_surface_desc surface;
    dom_srz_zone zones[DOM_SRZ_MAX_ZONES];
    u32 zone_count;
    dom_srz_assignment assignments[DOM_SRZ_MAX_ASSIGNMENTS];
    u32 assignment_count;
    dom_srz_policy policies[DOM_SRZ_MAX_POLICIES];
    u32 policy_count;
    dom_srz_log logs[DOM_SRZ_MAX_LOGS];
    u32 log_count;
    dom_srz_hash_link hash_links[DOM_SRZ_MAX_HASH_LINKS];
    u32 hash_link_count;
    dom_srz_state_delta deltas[DOM_SRZ_MAX_DELTAS];
    u32 delta_count;
    dom_srz_macro_capsule capsules[DOM_SRZ_MAX_CAPSULES];
    u32 capsule_count;
} dom_srz_domain;

void dom_srz_surface_desc_init(dom_srz_surface_desc* desc);

void dom_srz_domain_init(dom_srz_domain* domain,
                         const dom_srz_surface_desc* desc);
void dom_srz_domain_free(dom_srz_domain* domain);
void dom_srz_domain_set_state(dom_srz_domain* domain,
                              u32 existence_state,
                              u32 archival_state);
void dom_srz_domain_set_policy(dom_srz_domain* domain,
                               const dom_domain_policy* policy);

int dom_srz_zone_query(const dom_srz_domain* domain,
                       u32 srz_id,
                       dom_domain_budget* budget,
                       dom_srz_zone_sample* out_sample);

int dom_srz_assignment_query(const dom_srz_domain* domain,
                             u32 assignment_id,
                             dom_domain_budget* budget,
                             dom_srz_assignment_sample* out_sample);

int dom_srz_policy_query(const dom_srz_domain* domain,
                         u32 policy_id,
                         dom_domain_budget* budget,
                         dom_srz_policy_sample* out_sample);

int dom_srz_log_query(const dom_srz_domain* domain,
                      u32 log_id,
                      dom_domain_budget* budget,
                      dom_srz_log_sample* out_sample);

int dom_srz_hash_link_query(const dom_srz_domain* domain,
                            u32 link_id,
                            dom_domain_budget* budget,
                            dom_srz_hash_link_sample* out_sample);

int dom_srz_state_delta_query(const dom_srz_domain* domain,
                              u32 delta_id,
                              dom_domain_budget* budget,
                              dom_srz_state_delta_sample* out_sample);

int dom_srz_region_query(const dom_srz_domain* domain,
                         u32 region_id,
                         dom_domain_budget* budget,
                         dom_srz_region_sample* out_sample);

int dom_srz_resolve(dom_srz_domain* domain,
                    u32 region_id,
                    u64 tick,
                    u64 tick_delta,
                    dom_domain_budget* budget,
                    dom_srz_resolve_result* out_result);

int dom_srz_domain_collapse_region(dom_srz_domain* domain, u32 region_id);
int dom_srz_domain_expand_region(dom_srz_domain* domain, u32 region_id);

u32 dom_srz_domain_capsule_count(const dom_srz_domain* domain);
const dom_srz_macro_capsule* dom_srz_domain_capsule_at(const dom_srz_domain* domain,
                                                       u32 index);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINO_WORLD_SRZ_FIELDS_H */
