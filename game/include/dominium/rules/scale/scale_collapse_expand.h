/*
FILE: include/dominium/rules/scale/scale_collapse_expand.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / scale
RESPONSIBILITY: Deterministic collapse and expansion entry points for scale domains.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C89 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Collapse/expand ordering and results are deterministic and replayable.
*/
#ifndef DOMINIUM_RULES_SCALE_COLLAPSE_EXPAND_H
#define DOMINIUM_RULES_SCALE_COLLAPSE_EXPAND_H

#include "domino/core/dom_time_core.h"
#include "domino/core/types.h"
#include "domino/execution/task_node.h"
#include "domino/scale/macro_capsule_store.h"
#include "dominium/interest_set.h"

#ifdef __cplusplus
extern "C" {
#endif

#define DOM_SCALE_MACRO_CAPSULE_SCHEMA "dominium.schema.macro_capsule@1.0.0"
#define DOM_SCALE_MACRO_CAPSULE_VERSION 1u

typedef enum dom_scale_domain_kind {
    DOM_SCALE_DOMAIN_RESOURCES = 1,
    DOM_SCALE_DOMAIN_NETWORK = 2,
    DOM_SCALE_DOMAIN_AGENTS = 3
} dom_scale_domain_kind;

typedef enum dom_scale_event_kind {
    DOM_SCALE_EVENT_COLLAPSE = 1,
    DOM_SCALE_EVENT_EXPAND = 2,
    DOM_SCALE_EVENT_REFUSAL = 3,
    DOM_SCALE_EVENT_DEFER = 4
} dom_scale_event_kind;

typedef enum dom_scale_refusal_code {
    DOM_SCALE_REFUSE_NONE = 0,
    DOM_SCALE_REFUSE_INVALID_INTENT = 1,
    DOM_SCALE_REFUSE_CAPABILITY_MISSING = 3,
    DOM_SCALE_REFUSE_DOMAIN_FORBIDDEN = 4,
    DOM_SCALE_REFUSE_BUDGET_EXCEEDED = 7
} dom_scale_refusal_code;

typedef enum dom_scale_defer_code {
    DOM_SCALE_DEFER_NONE = 0,
    DOM_SCALE_DEFER_COLLAPSE = 1,
    DOM_SCALE_DEFER_EXPAND = 2
} dom_scale_defer_code;

typedef struct dom_scale_commit_token {
    dom_act_time_t commit_tick;
    u64 commit_nonce;
} dom_scale_commit_token;

typedef struct dom_scale_budget_policy {
    u32 max_tier2_domains;
    u32 max_tier1_domains;
    u32 refinement_budget_per_tick;
    u32 planning_budget_per_tick;
    u32 collapse_budget_per_tick;
    u32 expand_budget_per_tick;
    u32 collapse_cost_units;
    u32 expand_cost_units;
    dom_act_time_t min_dwell_ticks;
} dom_scale_budget_policy;

typedef struct dom_scale_budget_state {
    u32 active_tier2_domains;
    u32 active_tier1_domains;
    u32 refinement_used;
    u32 planning_used;
    u32 collapse_used;
    u32 expand_used;
} dom_scale_budget_state;

typedef struct dom_scale_event {
    u32 kind; /* dom_scale_event_kind */
    u64 domain_id;
    u32 domain_kind; /* dom_scale_domain_kind */
    u64 capsule_id;
    u32 reason_code;
    u32 refusal_code; /* dom_scale_refusal_code */
    u32 defer_code; /* dom_scale_defer_code */
    u32 detail_code;
    u32 seed_value;
    dom_act_time_t tick;
} dom_scale_event;

typedef struct dom_scale_event_log {
    dom_scale_event* events;
    u32 count;
    u32 capacity;
    u32 overflow;
} dom_scale_event_log;

typedef struct dom_scale_resource_entry {
    u64 resource_id;
    u64 quantity;
} dom_scale_resource_entry;

typedef struct dom_scale_resource_state {
    dom_scale_resource_entry* entries;
    u32 count;
    u32 capacity;
} dom_scale_resource_state;

typedef struct dom_scale_network_node {
    u64 node_id;
    u32 node_kind;
} dom_scale_network_node;

typedef struct dom_scale_network_edge {
    u64 edge_id;
    u64 from_node_id;
    u64 to_node_id;
    u64 capacity_units;
    u64 buffer_units;
    u32 wear_bucket0;
    u32 wear_bucket1;
    u32 wear_bucket2;
    u32 wear_bucket3;
} dom_scale_network_edge;

typedef struct dom_scale_network_state {
    dom_scale_network_node* nodes;
    u32 node_count;
    u32 node_capacity;
    dom_scale_network_edge* edges;
    u32 edge_count;
    u32 edge_capacity;
} dom_scale_network_state;

typedef struct dom_scale_agent_entry {
    u64 agent_id;
    u32 role_id;
    u32 trait_mask;
    u32 planning_bucket;
} dom_scale_agent_entry;

typedef struct dom_scale_agent_state {
    dom_scale_agent_entry* entries;
    u32 count;
    u32 capacity;
} dom_scale_agent_state;

typedef struct dom_scale_domain_slot {
    u64 domain_id;
    u32 domain_kind; /* dom_scale_domain_kind */
    dom_fidelity_tier tier;
    dom_act_time_t last_transition_tick;
    u64 capsule_id;
    dom_scale_resource_state resources;
    dom_scale_network_state network;
    dom_scale_agent_state agents;
} dom_scale_domain_slot;

typedef struct dom_scale_capsule_summary {
    u64 capsule_id;
    u64 domain_id;
    u32 domain_kind;
    dom_act_time_t source_tick;
    u32 collapse_reason;
    u32 seed_base;
    u64 invariant_hash;
    u64 statistic_hash;
    u32 invariant_count;
    u32 statistic_count;
} dom_scale_capsule_summary;

typedef struct dom_scale_operation_result {
    u64 domain_id;
    u32 domain_kind; /* dom_scale_domain_kind */
    dom_act_time_t tick;
    u64 capsule_id;
    dom_fidelity_tier from_tier;
    dom_fidelity_tier to_tier;
    u32 reason_code;
    u32 refusal_code; /* dom_scale_refusal_code */
    u32 defer_code; /* dom_scale_defer_code */
    u64 domain_hash_before;
    u64 domain_hash_after;
    u64 capsule_hash;
} dom_scale_operation_result;

typedef struct dom_scale_context {
    d_world* world;
    dom_scale_domain_slot* domains;
    u32 domain_count;
    u32 domain_capacity;
    dom_interest_state* interest_states;
    u32 interest_capacity;
    dom_interest_policy interest_policy;
    dom_scale_budget_policy budget_policy;
    dom_scale_budget_state budget_state;
    dom_scale_event_log* event_log;
    dom_act_time_t now_tick;
    u32 worker_count;
} dom_scale_context;

void dom_scale_event_log_init(dom_scale_event_log* log,
                              dom_scale_event* storage,
                              u32 capacity);
void dom_scale_event_log_clear(dom_scale_event_log* log);

void dom_scale_budget_policy_default(dom_scale_budget_policy* policy);
void dom_scale_interest_policy_default(dom_interest_policy* policy);

void dom_scale_context_init(dom_scale_context* ctx,
                            d_world* world,
                            dom_scale_domain_slot* domain_storage,
                            u32 domain_capacity,
                            dom_interest_state* interest_storage,
                            u32 interest_capacity,
                            dom_scale_event_log* event_log,
                            dom_act_time_t now_tick,
                            u32 worker_count);
int dom_scale_register_domain(dom_scale_context* ctx,
                              const dom_scale_domain_slot* slot);
dom_scale_domain_slot* dom_scale_find_domain(dom_scale_context* ctx,
                                             u64 domain_id);

void dom_scale_commit_token_make(dom_scale_commit_token* token,
                                 dom_act_time_t commit_tick,
                                 u32 sequence);
int dom_scale_commit_token_validate(const dom_scale_commit_token* token,
                                    dom_act_time_t expected_tick);

u64 dom_scale_domain_hash(const dom_scale_domain_slot* slot,
                          dom_act_time_t now_tick,
                          u32 worker_count);
int dom_scale_capsule_summarize(const unsigned char* bytes,
                                u32 byte_count,
                                dom_scale_capsule_summary* out_summary);

int dom_scale_collapse_domain(dom_scale_context* ctx,
                              const dom_scale_commit_token* token,
                              u64 domain_id,
                              u32 collapse_reason,
                              dom_scale_operation_result* out_result);
int dom_scale_expand_domain(dom_scale_context* ctx,
                            const dom_scale_commit_token* token,
                            u64 capsule_id,
                            dom_fidelity_tier target_tier,
                            u32 expand_reason,
                            dom_scale_operation_result* out_result);

u32 dom_scale_apply_interest(dom_scale_context* ctx,
                             const dom_scale_commit_token* token,
                             const dom_interest_set* interest,
                             dom_scale_operation_result* out_results,
                             u32 result_capacity);

const char* dom_scale_refusal_to_string(u32 refusal_code);
const char* dom_scale_defer_to_string(u32 defer_code);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_RULES_SCALE_COLLAPSE_EXPAND_H */

