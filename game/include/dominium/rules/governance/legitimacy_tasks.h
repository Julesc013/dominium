/*
FILE: include/dominium/rules/governance/legitimacy_tasks.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / governance
RESPONSIBILITY: Governance task helpers for Work IR execution.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Governance ordering and updates are deterministic.
*/
#ifndef DOMINIUM_RULES_GOVERNANCE_LEGITIMACY_TASKS_H
#define DOMINIUM_RULES_GOVERNANCE_LEGITIMACY_TASKS_H

#include "domino/core/types.h"
#include "domino/core/dom_time_core.h"
#include "dominium/rules/governance/policy_model.h"
#include "dominium/rules/governance/jurisdiction_model.h"
#include "dominium/rules/governance/legitimacy_model.h"
#include "dominium/rules/governance/enforcement_capacity.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum dom_governance_audit_kind {
    DOM_GOV_AUDIT_POLICY_APPLY = 1,
    DOM_GOV_AUDIT_LEGITIMACY_UPDATE = 2,
    DOM_GOV_AUDIT_AUTHORITY_ENFORCE = 3,
    DOM_GOV_AUDIT_LAW_LIFECYCLE = 4
} dom_governance_audit_kind;

typedef struct dom_governance_audit_entry {
    u64 event_id;
    u32 kind;
    u64 primary_id;
    i64 amount;
} dom_governance_audit_entry;

typedef struct dom_governance_audit_log {
    dom_governance_audit_entry* entries;
    u32 count;
    u32 capacity;
    u64 next_event_id;
} dom_governance_audit_log;

void dom_governance_audit_init(dom_governance_audit_log* log,
                               dom_governance_audit_entry* storage,
                               u32 capacity,
                               u64 start_id);
int dom_governance_audit_record(dom_governance_audit_log* log,
                                u32 kind,
                                u64 primary_id,
                                i64 amount);

typedef struct dom_governance_legitimacy_event {
    u64 event_id;
    u64 legitimacy_id;
    i32 delta;
    dom_act_time_t trigger_act;
} dom_governance_legitimacy_event;

typedef struct dom_governance_authority_action {
    u64 action_id;
    u64 jurisdiction_id;
    u32 enforcer_cost;
    dom_act_time_t trigger_act;
} dom_governance_authority_action;

typedef struct dom_governance_law_lifecycle_event {
    u64 law_id;
    u32 next_state;
    dom_act_time_t trigger_act;
} dom_governance_law_lifecycle_event;

typedef struct dom_governance_law_state {
    u64 law_id;
    u32 state;
} dom_governance_law_state;

typedef struct dom_governance_law_registry {
    dom_governance_law_state* states;
    u32 count;
    u32 capacity;
} dom_governance_law_registry;

typedef struct dom_governance_runtime_state {
    u32 policy_cursor;
    u32 legitimacy_cursor;
    u32 authority_cursor;
    u32 lifecycle_cursor;
} dom_governance_runtime_state;

void dom_governance_runtime_reset(dom_governance_runtime_state* state);
void dom_governance_law_registry_init(dom_governance_law_registry* reg,
                                      dom_governance_law_state* storage,
                                      u32 capacity);

u32 dom_governance_policy_apply_slice(policy_registry* policies,
                                      jurisdiction_registry* jurisdictions,
                                      legitimacy_registry* legitimacies,
                                      enforcement_capacity_registry* enforcement,
                                      u32 start_index,
                                      u32 max_count,
                                      dom_act_time_t now_tick,
                                      dom_governance_audit_log* audit);

u32 dom_governance_legitimacy_apply_slice(legitimacy_registry* registry,
                                          const dom_governance_legitimacy_event* events,
                                          u32 event_count,
                                          u32 start_index,
                                          u32 max_count,
                                          dom_act_time_t now_tick,
                                          dom_governance_audit_log* audit);

u32 dom_governance_authority_enforce_slice(const dom_governance_authority_action* actions,
                                           u32 action_count,
                                           u32 start_index,
                                           u32 max_count,
                                           dom_act_time_t now_tick,
                                           dom_governance_audit_log* audit);

u32 dom_governance_law_lifecycle_slice(dom_governance_law_registry* registry,
                                       const dom_governance_law_lifecycle_event* events,
                                       u32 event_count,
                                       u32 start_index,
                                       u32 max_count,
                                       dom_act_time_t now_tick,
                                       dom_governance_audit_log* audit);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_RULES_GOVERNANCE_LEGITIMACY_TASKS_H */
