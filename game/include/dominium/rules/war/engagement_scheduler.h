/*
FILE: include/dominium/rules/war/engagement_scheduler.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / war rules
RESPONSIBILITY: Defines engagement due scheduling and resolution hooks.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Scheduling and resolution ordering are deterministic.
*/
#ifndef DOMINIUM_RULES_WAR_ENGAGEMENT_SCHEDULER_H
#define DOMINIUM_RULES_WAR_ENGAGEMENT_SCHEDULER_H

#include "domino/sim/dg_due_sched.h"
#include "dominium/rules/war/engagement_resolution.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct engagement_scheduler engagement_scheduler;

typedef struct engagement_due_user {
    engagement_scheduler* scheduler;
    engagement* engagement;
} engagement_due_user;

typedef struct engagement_scheduler {
    dg_due_scheduler due;
    dom_time_event* due_events;
    dg_due_entry* due_entries;
    engagement_due_user* due_users;
    engagement_registry* engagements;
    engagement_outcome_list* outcomes;
    engagement_resolution_context* resolution;
    u32 processed_last;
    u32 processed_total;
} engagement_scheduler;

int engagement_scheduler_init(engagement_scheduler* sched,
                              dom_time_event* event_storage,
                              u32 event_capacity,
                              dg_due_entry* entry_storage,
                              engagement_due_user* user_storage,
                              u32 entry_capacity,
                              dom_act_time_t start_tick,
                              engagement_registry* engagements,
                              engagement_outcome_list* outcomes,
                              engagement_resolution_context* resolution);
int engagement_scheduler_register(engagement_scheduler* sched,
                                  engagement* engagement);
int engagement_scheduler_advance(engagement_scheduler* sched,
                                 dom_act_time_t target_tick);
dom_act_time_t engagement_scheduler_next_due(const engagement_scheduler* sched);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_RULES_WAR_ENGAGEMENT_SCHEDULER_H */
