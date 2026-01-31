/*
FILE: include/domino/world/autonomy_fields.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / world/autonomy_fields
RESPONSIBILITY: Deterministic AI autonomy, delegation, and planning field sampling.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 headers as needed.
FORBIDDEN DEPENDENCIES: Engine private headers outside `include/domino/**`.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: Fixed-point only; deterministic ordering and math.
VERSIONING / ABI / DATA FORMAT NOTES: Versioned by AIA0 specs.
EXTENSION POINTS: Extend via public headers and relevant `docs/architecture/**`.
*/
#ifndef DOMINO_WORLD_AUTONOMY_FIELDS_H
#define DOMINO_WORLD_AUTONOMY_FIELDS_H

#include "domino/core/types.h"
#include "domino/core/fixed.h"
#include "domino/world/domain_query.h"

#ifdef __cplusplus
extern "C" {
#endif

#define DOM_AUTONOMY_MAX_GOALS 128u
#define DOM_AUTONOMY_MAX_DELEGATIONS 128u
#define DOM_AUTONOMY_MAX_BUDGETS 128u
#define DOM_AUTONOMY_MAX_PLANS 128u
#define DOM_AUTONOMY_MAX_EVENTS 128u
#define DOM_AUTONOMY_MAX_REGIONS 16u
#define DOM_AUTONOMY_MAX_CAPSULES 64u
#define DOM_AUTONOMY_MAX_PROCESS_REFS 8u
#define DOM_AUTONOMY_MAX_PLAN_STEPS 16u
#define DOM_AUTONOMY_HIST_BINS 4u
#define DOM_AUTONOMY_EVENT_BINS 7u

#define DOM_AUTONOMY_RATIO_ONE_Q16 ((q16_16)0x00010000)

enum dom_autonomy_process_type {
    DOM_AUTONOMY_PROCESS_UNSET = 0u,
    DOM_AUTONOMY_PROCESS_PLAN = 1u,
    DOM_AUTONOMY_PROCESS_EXECUTE = 2u,
    DOM_AUTONOMY_PROCESS_REVISE = 3u,
    DOM_AUTONOMY_PROCESS_REVOKE = 4u,
    DOM_AUTONOMY_PROCESS_EXPIRE = 5u,
    DOM_AUTONOMY_PROCESS_FAIL = 6u,
    DOM_AUTONOMY_PROCESS_COMPLETE = 7u
};

enum dom_autonomy_plan_status {
    DOM_AUTONOMY_PLAN_UNSET = 0u,
    DOM_AUTONOMY_PLAN_PROPOSED = 1u,
    DOM_AUTONOMY_PLAN_ACTIVE = 2u,
    DOM_AUTONOMY_PLAN_FAILED = 3u,
    DOM_AUTONOMY_PLAN_COMPLETED = 4u,
    DOM_AUTONOMY_PLAN_REVOKED = 5u
};

enum dom_autonomy_goal_flags {
    DOM_AUTONOMY_GOAL_UNRESOLVED = 1u << 0u,
    DOM_AUTONOMY_GOAL_COLLAPSED = 1u << 1u,
    DOM_AUTONOMY_GOAL_EXPIRED = 1u << 2u
};

enum dom_autonomy_delegation_flags {
    DOM_AUTONOMY_DELEGATION_UNRESOLVED = 1u << 0u,
    DOM_AUTONOMY_DELEGATION_COLLAPSED = 1u << 1u,
    DOM_AUTONOMY_DELEGATION_REVOKED = 1u << 2u
};

enum dom_autonomy_budget_flags {
    DOM_AUTONOMY_BUDGET_UNRESOLVED = 1u << 0u,
    DOM_AUTONOMY_BUDGET_COLLAPSED = 1u << 1u,
    DOM_AUTONOMY_BUDGET_EXHAUSTED = 1u << 2u
};

enum dom_autonomy_plan_flags {
    DOM_AUTONOMY_PLAN_UNRESOLVED = 1u << 0u,
    DOM_AUTONOMY_PLAN_COLLAPSED = 1u << 1u,
    DOM_AUTONOMY_PLAN_FAILED_FLAG = 1u << 2u,
    DOM_AUTONOMY_PLAN_COMPLETED_FLAG = 1u << 3u,
    DOM_AUTONOMY_PLAN_REVOKED_FLAG = 1u << 4u
};

enum dom_autonomy_event_flags {
    DOM_AUTONOMY_EVENT_UNRESOLVED = 1u << 0u,
    DOM_AUTONOMY_EVENT_APPLIED = 1u << 1u,
    DOM_AUTONOMY_EVENT_FAILED = 1u << 2u
};

enum dom_autonomy_resolve_flags {
    DOM_AUTONOMY_RESOLVE_PARTIAL = 1u << 0u,
    DOM_AUTONOMY_RESOLVE_EVENTS_APPLIED = 1u << 1u,
    DOM_AUTONOMY_RESOLVE_PLAN_FAILED = 1u << 2u,
    DOM_AUTONOMY_RESOLVE_PLAN_COMPLETED = 1u << 3u,
    DOM_AUTONOMY_RESOLVE_DELEGATION_REVOKED = 1u << 4u,
    DOM_AUTONOMY_RESOLVE_GOAL_EXPIRED = 1u << 5u,
    DOM_AUTONOMY_RESOLVE_BUDGET_EXHAUSTED = 1u << 6u
};

enum dom_autonomy_refusal_reason {
    DOM_AUTONOMY_REFUSE_NONE = 0u,
    DOM_AUTONOMY_REFUSE_BUDGET = 1u,
    DOM_AUTONOMY_REFUSE_DOMAIN_INACTIVE = 2u,
    DOM_AUTONOMY_REFUSE_GOAL_MISSING = 3u,
    DOM_AUTONOMY_REFUSE_DELEGATION_MISSING = 4u,
    DOM_AUTONOMY_REFUSE_BUDGET_MISSING = 5u,
    DOM_AUTONOMY_REFUSE_PLAN_MISSING = 6u,
    DOM_AUTONOMY_REFUSE_EVENT_MISSING = 7u,
    DOM_AUTONOMY_REFUSE_POLICY = 8u,
    DOM_AUTONOMY_REFUSE_INTERNAL = 9u
};

typedef struct dom_autonomy_goal_desc {
    u32 goal_id;
    u32 objective_id;
    u32 success_condition_id;
    u32 constraint_id;
    q16_16 priority;
    u64 expiry_tick;
    u32 delegator_id;
    u32 provenance_id;
    u32 region_id;
    u32 flags; /* dom_autonomy_goal_flags */
} dom_autonomy_goal_desc;

typedef struct dom_autonomy_delegation_desc {
    u32 delegation_id;
    u32 delegator_id;
    u32 delegate_agent_id;
    u32 allowed_process_count;
    u32 allowed_process_ids[DOM_AUTONOMY_MAX_PROCESS_REFS];
    u64 time_budget_ticks;
    q48_16 energy_budget;
    q16_16 risk_budget;
    u32 oversight_policy_id;
    u32 revocation_policy_id;
    u32 provenance_id;
    u32 region_id;
    u32 flags; /* dom_autonomy_delegation_flags */
} dom_autonomy_delegation_desc;

typedef struct dom_autonomy_budget_desc {
    u32 budget_id;
    u32 delegation_id;
    u64 time_budget_ticks;
    u64 time_used_ticks;
    q48_16 energy_budget;
    q48_16 energy_used;
    q16_16 risk_budget;
    q16_16 risk_used;
    u32 planning_budget;
    u32 planning_used;
    u32 provenance_id;
    u32 region_id;
    u32 flags; /* dom_autonomy_budget_flags */
} dom_autonomy_budget_desc;

typedef struct dom_autonomy_plan_desc {
    u32 plan_id;
    u32 goal_id;
    u32 delegation_id;
    u32 step_count;
    u32 step_process_ids[DOM_AUTONOMY_MAX_PLAN_STEPS];
    q16_16 success_score;
    q48_16 estimated_cost;
    u64 created_tick;
    u64 last_update_tick;
    u32 status; /* dom_autonomy_plan_status */
    u32 provenance_id;
    u32 region_id;
    u32 flags; /* dom_autonomy_plan_flags */
} dom_autonomy_plan_desc;

typedef struct dom_autonomy_event_desc {
    u32 event_id;
    u32 process_type;
    u32 goal_id;
    u32 delegation_id;
    u32 plan_id;
    u32 budget_id;
    q16_16 delta_priority;
    q48_16 delta_energy_used;
    q16_16 delta_risk_used;
    u64 delta_time_used;
    u32 delta_planning_used;
    u64 event_tick;
    u32 provenance_id;
    u32 region_id;
    u32 flags; /* dom_autonomy_event_flags */
} dom_autonomy_event_desc;

typedef struct dom_autonomy_goal {
    u32 goal_id;
    u32 objective_id;
    u32 success_condition_id;
    u32 constraint_id;
    q16_16 priority;
    u64 expiry_tick;
    u32 delegator_id;
    u32 provenance_id;
    u32 region_id;
    u32 flags; /* dom_autonomy_goal_flags */
} dom_autonomy_goal;

typedef struct dom_autonomy_delegation {
    u32 delegation_id;
    u32 delegator_id;
    u32 delegate_agent_id;
    u32 allowed_process_count;
    u32 allowed_process_ids[DOM_AUTONOMY_MAX_PROCESS_REFS];
    u64 time_budget_ticks;
    q48_16 energy_budget;
    q16_16 risk_budget;
    u32 oversight_policy_id;
    u32 revocation_policy_id;
    u32 provenance_id;
    u32 region_id;
    u32 flags; /* dom_autonomy_delegation_flags */
} dom_autonomy_delegation;

typedef struct dom_autonomy_budget {
    u32 budget_id;
    u32 delegation_id;
    u64 time_budget_ticks;
    u64 time_used_ticks;
    q48_16 energy_budget;
    q48_16 energy_used;
    q16_16 risk_budget;
    q16_16 risk_used;
    u32 planning_budget;
    u32 planning_used;
    u32 provenance_id;
    u32 region_id;
    u32 flags; /* dom_autonomy_budget_flags */
} dom_autonomy_budget;

typedef struct dom_autonomy_plan {
    u32 plan_id;
    u32 goal_id;
    u32 delegation_id;
    u32 step_count;
    u32 step_process_ids[DOM_AUTONOMY_MAX_PLAN_STEPS];
    q16_16 success_score;
    q48_16 estimated_cost;
    u64 created_tick;
    u64 last_update_tick;
    u32 status; /* dom_autonomy_plan_status */
    u32 provenance_id;
    u32 region_id;
    u32 flags; /* dom_autonomy_plan_flags */
} dom_autonomy_plan;

typedef struct dom_autonomy_event {
    u32 event_id;
    u32 process_type;
    u32 goal_id;
    u32 delegation_id;
    u32 plan_id;
    u32 budget_id;
    q16_16 delta_priority;
    q48_16 delta_energy_used;
    q16_16 delta_risk_used;
    u64 delta_time_used;
    u32 delta_planning_used;
    u64 event_tick;
    u32 provenance_id;
    u32 region_id;
    u32 flags; /* dom_autonomy_event_flags */
} dom_autonomy_event;

typedef struct dom_autonomy_surface_desc {
    dom_domain_id domain_id;
    u64 world_seed;
    q16_16 meters_per_unit;
    u32 goal_count;
    dom_autonomy_goal_desc goals[DOM_AUTONOMY_MAX_GOALS];
    u32 delegation_count;
    dom_autonomy_delegation_desc delegations[DOM_AUTONOMY_MAX_DELEGATIONS];
    u32 budget_count;
    dom_autonomy_budget_desc budgets[DOM_AUTONOMY_MAX_BUDGETS];
    u32 plan_count;
    dom_autonomy_plan_desc plans[DOM_AUTONOMY_MAX_PLANS];
    u32 event_count;
    dom_autonomy_event_desc events[DOM_AUTONOMY_MAX_EVENTS];
} dom_autonomy_surface_desc;

typedef struct dom_autonomy_goal_sample {
    u32 goal_id;
    u32 objective_id;
    u32 success_condition_id;
    u32 constraint_id;
    q16_16 priority;
    u64 expiry_tick;
    u32 delegator_id;
    u32 provenance_id;
    u32 region_id;
    u32 flags; /* dom_autonomy_goal_flags */
    dom_domain_query_meta meta;
} dom_autonomy_goal_sample;

typedef struct dom_autonomy_delegation_sample {
    u32 delegation_id;
    u32 delegator_id;
    u32 delegate_agent_id;
    u32 allowed_process_count;
    u32 time_budget_ticks;
    q48_16 energy_budget;
    q16_16 risk_budget;
    u32 oversight_policy_id;
    u32 revocation_policy_id;
    u32 provenance_id;
    u32 region_id;
    u32 flags; /* dom_autonomy_delegation_flags */
    dom_domain_query_meta meta;
} dom_autonomy_delegation_sample;

typedef struct dom_autonomy_budget_sample {
    u32 budget_id;
    u32 delegation_id;
    u64 time_budget_ticks;
    u64 time_used_ticks;
    q48_16 energy_budget;
    q48_16 energy_used;
    q16_16 risk_budget;
    q16_16 risk_used;
    u32 planning_budget;
    u32 planning_used;
    u32 provenance_id;
    u32 region_id;
    u32 flags; /* dom_autonomy_budget_flags */
    dom_domain_query_meta meta;
} dom_autonomy_budget_sample;

typedef struct dom_autonomy_plan_sample {
    u32 plan_id;
    u32 goal_id;
    u32 delegation_id;
    u32 step_count;
    q16_16 success_score;
    q48_16 estimated_cost;
    u64 created_tick;
    u64 last_update_tick;
    u32 status; /* dom_autonomy_plan_status */
    u32 provenance_id;
    u32 region_id;
    u32 flags; /* dom_autonomy_plan_flags */
    dom_domain_query_meta meta;
} dom_autonomy_plan_sample;

typedef struct dom_autonomy_event_sample {
    u32 event_id;
    u32 process_type;
    u32 goal_id;
    u32 delegation_id;
    u32 plan_id;
    u32 budget_id;
    q16_16 delta_priority;
    q48_16 delta_energy_used;
    q16_16 delta_risk_used;
    u64 delta_time_used;
    u32 delta_planning_used;
    u64 event_tick;
    u32 provenance_id;
    u32 region_id;
    u32 flags; /* dom_autonomy_event_flags */
    dom_domain_query_meta meta;
} dom_autonomy_event_sample;

typedef struct dom_autonomy_region_sample {
    u32 region_id;
    u32 goal_count;
    u32 delegation_count;
    u32 budget_count;
    u32 plan_count;
    u32 event_count;
    q16_16 priority_avg;
    q16_16 success_avg;
    q16_16 budget_utilization_avg;
    u32 event_type_counts[DOM_AUTONOMY_EVENT_BINS];
    u32 flags; /* dom_autonomy_resolve_flags */
    dom_domain_query_meta meta;
} dom_autonomy_region_sample;

typedef struct dom_autonomy_resolve_result {
    u32 ok;
    u32 refusal_reason; /* dom_autonomy_refusal_reason */
    u32 flags; /* dom_autonomy_resolve_flags */
    u32 goal_count;
    u32 delegation_count;
    u32 budget_count;
    u32 plan_count;
    u32 event_count;
    u32 event_applied_count;
    q16_16 priority_avg;
    q16_16 success_avg;
    q16_16 budget_utilization_avg;
    u32 event_type_counts[DOM_AUTONOMY_EVENT_BINS];
} dom_autonomy_resolve_result;

typedef struct dom_autonomy_macro_capsule {
    u64 capsule_id;
    u32 region_id;
    u32 goal_count;
    u32 delegation_count;
    u32 budget_count;
    u32 plan_count;
    q16_16 priority_avg;
    q16_16 success_avg;
    q16_16 budget_utilization_avg;
    q16_16 priority_hist[DOM_AUTONOMY_HIST_BINS];
    q16_16 success_hist[DOM_AUTONOMY_HIST_BINS];
    u32 event_type_counts[DOM_AUTONOMY_EVENT_BINS];
    u32 rng_cursor[DOM_AUTONOMY_HIST_BINS];
} dom_autonomy_macro_capsule;

typedef struct dom_autonomy_domain {
    dom_domain_policy policy;
    u32 existence_state;
    u32 archival_state;
    u32 authoring_version;
    dom_autonomy_surface_desc surface;
    dom_autonomy_goal goals[DOM_AUTONOMY_MAX_GOALS];
    u32 goal_count;
    dom_autonomy_delegation delegations[DOM_AUTONOMY_MAX_DELEGATIONS];
    u32 delegation_count;
    dom_autonomy_budget budgets[DOM_AUTONOMY_MAX_BUDGETS];
    u32 budget_count;
    dom_autonomy_plan plans[DOM_AUTONOMY_MAX_PLANS];
    u32 plan_count;
    dom_autonomy_event events[DOM_AUTONOMY_MAX_EVENTS];
    u32 event_count;
    dom_autonomy_macro_capsule capsules[DOM_AUTONOMY_MAX_CAPSULES];
    u32 capsule_count;
} dom_autonomy_domain;

void dom_autonomy_surface_desc_init(dom_autonomy_surface_desc* desc);

void dom_autonomy_domain_init(dom_autonomy_domain* domain,
                              const dom_autonomy_surface_desc* desc);
void dom_autonomy_domain_free(dom_autonomy_domain* domain);
void dom_autonomy_domain_set_state(dom_autonomy_domain* domain,
                                   u32 existence_state,
                                   u32 archival_state);
void dom_autonomy_domain_set_policy(dom_autonomy_domain* domain,
                                    const dom_domain_policy* policy);

int dom_autonomy_goal_query(const dom_autonomy_domain* domain,
                            u32 goal_id,
                            dom_domain_budget* budget,
                            dom_autonomy_goal_sample* out_sample);

int dom_autonomy_delegation_query(const dom_autonomy_domain* domain,
                                  u32 delegation_id,
                                  dom_domain_budget* budget,
                                  dom_autonomy_delegation_sample* out_sample);

int dom_autonomy_budget_query(const dom_autonomy_domain* domain,
                              u32 budget_id,
                              dom_domain_budget* budget,
                              dom_autonomy_budget_sample* out_sample);

int dom_autonomy_plan_query(const dom_autonomy_domain* domain,
                            u32 plan_id,
                            dom_domain_budget* budget,
                            dom_autonomy_plan_sample* out_sample);

int dom_autonomy_event_query(const dom_autonomy_domain* domain,
                             u32 event_id,
                             dom_domain_budget* budget,
                             dom_autonomy_event_sample* out_sample);

int dom_autonomy_region_query(const dom_autonomy_domain* domain,
                              u32 region_id,
                              dom_domain_budget* budget,
                              dom_autonomy_region_sample* out_sample);

int dom_autonomy_resolve(dom_autonomy_domain* domain,
                         u32 region_id,
                         u64 tick,
                         u64 tick_delta,
                         dom_domain_budget* budget,
                         dom_autonomy_resolve_result* out_result);

int dom_autonomy_domain_collapse_region(dom_autonomy_domain* domain, u32 region_id);
int dom_autonomy_domain_expand_region(dom_autonomy_domain* domain, u32 region_id);

u32 dom_autonomy_domain_capsule_count(const dom_autonomy_domain* domain);
const dom_autonomy_macro_capsule* dom_autonomy_domain_capsule_at(const dom_autonomy_domain* domain,
                                                                 u32 index);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINO_WORLD_AUTONOMY_FIELDS_H */
