/*
FILE: include/dominium/rules/governance/policy_scheduler.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / governance
RESPONSIBILITY: Defines event-driven policy scheduler and hooks.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Policy scheduling is deterministic.
*/
#ifndef DOMINIUM_RULES_GOVERNANCE_POLICY_SCHEDULER_H
#define DOMINIUM_RULES_GOVERNANCE_POLICY_SCHEDULER_H

#include "domino/sim/dg_due_sched.h"
#include "dominium/rules/governance/enforcement_capacity.h"
#include "dominium/rules/governance/jurisdiction_model.h"
#include "dominium/rules/governance/legitimacy_model.h"
#include "dominium/rules/governance/policy_model.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct policy_event_hook {
    int (*apply)(void* user,
                 const jurisdiction_record* jurisdiction,
                 const policy_record* policy,
                 dom_act_time_t act_time);
    void* user;
} policy_event_hook;

typedef struct policy_due_user {
    struct policy_scheduler* scheduler;
    policy_record* policy;
} policy_due_user;

typedef struct policy_scheduler {
    dg_due_scheduler due;
    dom_time_event* due_events;
    dg_due_entry* due_entries;
    policy_due_user* due_users;
    policy_registry* policies;
    jurisdiction_registry* jurisdictions;
    legitimacy_registry* legitimacies;
    enforcement_capacity_registry* enforcement;
    policy_event_hook hook;
    u32 processed_last;
    u32 processed_total;
} policy_scheduler;

int policy_scheduler_init(policy_scheduler* sched,
                          dom_time_event* event_storage,
                          u32 event_capacity,
                          dg_due_entry* entry_storage,
                          policy_due_user* user_storage,
                          u32 entry_capacity,
                          dom_act_time_t start_tick,
                          policy_registry* policies,
                          jurisdiction_registry* jurisdictions,
                          legitimacy_registry* legitimacies,
                          enforcement_capacity_registry* enforcement);
void policy_scheduler_set_hook(policy_scheduler* sched, const policy_event_hook* hook);
int policy_scheduler_register(policy_scheduler* sched,
                              policy_record* policy);
int policy_scheduler_advance(policy_scheduler* sched,
                             dom_act_time_t target_tick);
dom_act_time_t policy_scheduler_next_due(const policy_scheduler* sched);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_RULES_GOVERNANCE_POLICY_SCHEDULER_H */
