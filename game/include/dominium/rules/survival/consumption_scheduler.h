/*
FILE: include/dominium/rules/survival/consumption_scheduler.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / survival rules
RESPONSIBILITY: Defines event-driven consumption scheduler for cohorts.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Scheduler ordering is deterministic.
*/
#ifndef DOMINIUM_RULES_SURVIVAL_CONSUMPTION_SCHEDULER_H
#define DOMINIUM_RULES_SURVIVAL_CONSUMPTION_SCHEDULER_H

#include "domino/sim/dg_due_sched.h"
#include "dominium/rules/survival/cohort_model.h"
#include "dominium/rules/survival/needs_model.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum survival_death_cause {
    SURVIVAL_DEATH_CAUSE_STARVATION = 1,
    SURVIVAL_DEATH_CAUSE_DEHYDRATION = 2
} survival_death_cause;

typedef struct survival_death_hook {
    int (*emit)(void* user,
                u64 cohort_id,
                u32 count,
                dom_act_time_t act_time,
                u32 cause_code);
    void* user;
} survival_death_hook;

typedef struct survival_consumption_scheduler {
    dg_due_scheduler due;
    dom_time_event* due_events;
    dg_due_entry* due_entries;
    struct survival_consumption_due_user* due_users;
    survival_cohort_registry* cohorts;
    survival_needs_registry* needs;
    survival_needs_params params;
    survival_death_hook death_hook;
    dom_act_time_t start_tick;
    u32 processed_last;
    u32 processed_total;
} survival_consumption_scheduler;

typedef struct survival_consumption_due_user {
    survival_consumption_scheduler* scheduler;
    survival_cohort* cohort;
} survival_consumption_due_user;

int survival_consumption_scheduler_init(survival_consumption_scheduler* sched,
                                        dom_time_event* event_storage,
                                        u32 event_capacity,
                                        dg_due_entry* entry_storage,
                                        survival_consumption_due_user* user_storage,
                                        u32 entry_capacity,
                                        dom_act_time_t start_tick,
                                        survival_cohort_registry* cohorts,
                                        survival_needs_registry* needs,
                                        const survival_needs_params* params);

void survival_consumption_set_death_hook(survival_consumption_scheduler* sched,
                                         const survival_death_hook* hook);

int survival_consumption_register_cohort(survival_consumption_scheduler* sched,
                                         survival_cohort* cohort);
int survival_consumption_advance(survival_consumption_scheduler* sched,
                                 dom_act_time_t target_tick);
dom_act_time_t survival_consumption_next_due(const survival_consumption_scheduler* sched);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_RULES_SURVIVAL_CONSUMPTION_SCHEDULER_H */
