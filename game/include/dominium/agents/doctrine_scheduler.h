/*
FILE: include/dominium/agents/doctrine_scheduler.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / agents
RESPONSIBILITY: Defines deterministic doctrine update scheduling.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Doctrine update ordering is stable and ACT-driven.
*/
#ifndef DOMINIUM_AGENTS_DOCTRINE_SCHEDULER_H
#define DOMINIUM_AGENTS_DOCTRINE_SCHEDULER_H

#include "domino/sim/dg_due_sched.h"
#include "dominium/agents/doctrine.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum doctrine_event_type {
    DOCTRINE_EVENT_APPLY = 0,
    DOCTRINE_EVENT_CLEAR = 1
} doctrine_event_type;

typedef struct doctrine_event {
    u64 event_id;
    u64 doctrine_id;
    dom_act_time_t trigger_act;
    doctrine_event_type type;
    agent_doctrine doctrine;
    u64 provenance_ref;
} doctrine_event;

typedef struct doctrine_due_user {
    struct doctrine_scheduler* scheduler;
    doctrine_event* event;
} doctrine_due_user;

typedef struct doctrine_scheduler {
    dg_due_scheduler due;
    dom_time_event* due_events;
    dg_due_entry* due_entries;
    doctrine_due_user* due_users;
    doctrine_event* events;
    u32 event_capacity;
    u32 event_count;
    u64 next_event_id;
    agent_doctrine_registry* doctrines;
    u32 processed_last;
    u32 processed_total;
} doctrine_scheduler;

int doctrine_scheduler_init(doctrine_scheduler* sched,
                            dom_time_event* event_storage,
                            u32 event_capacity,
                            dg_due_entry* entry_storage,
                            doctrine_due_user* user_storage,
                            u32 entry_capacity,
                            dom_act_time_t start_tick,
                            doctrine_event* events,
                            u32 events_capacity,
                            agent_doctrine_registry* doctrines,
                            u64 start_event_id);
int doctrine_schedule_apply(doctrine_scheduler* sched,
                            const agent_doctrine* doctrine,
                            dom_act_time_t trigger_act);
int doctrine_schedule_clear(doctrine_scheduler* sched,
                            u64 doctrine_id,
                            dom_act_time_t trigger_act);
int doctrine_scheduler_advance(doctrine_scheduler* sched,
                               dom_act_time_t target_tick);
dom_act_time_t doctrine_scheduler_next_due(const doctrine_scheduler* sched);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_AGENTS_DOCTRINE_SCHEDULER_H */
