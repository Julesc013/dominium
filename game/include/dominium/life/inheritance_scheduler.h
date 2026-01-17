/*
FILE: include/dominium/life/inheritance_scheduler.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / life
RESPONSIBILITY: Defines inheritance scheduling over ACT using due-event scheduler.
ALLOWED DEPENDENCIES: `game/include/**`, `engine/include/**` public headers, and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; product-layer runtime code.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Scheduler ordering must be deterministic and stable.
*/
#ifndef DOMINIUM_LIFE_INHERITANCE_SCHEDULER_H
#define DOMINIUM_LIFE_INHERITANCE_SCHEDULER_H

#include "domino/sim/dg_due_sched.h"
#include "dominium/life/estate.h"
#include "dominium/life/life_refusal_codes.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct life_inheritance_action {
    u64 action_id;
    u64 estate_id;
    dom_act_time_t trigger_act;
    u32 policy_id;
    u64 target_person_id;
    life_death_refusal_code refusal_code;
} life_inheritance_action;

typedef struct life_inheritance_action_list {
    life_inheritance_action* actions;
    u32 count;
    u32 capacity;
    u64 next_id;
} life_inheritance_action_list;

typedef struct life_inheritance_scheduler {
    dg_due_scheduler due;
    dom_time_event* due_events;
    dg_due_entry* due_entries;
    struct life_inheritance_due_user* due_users;
    life_inheritance_action_list* action_list;
    life_estate_registry* estates;
    dom_act_time_t claim_period_ticks;
} life_inheritance_scheduler;

typedef struct life_inheritance_due_user {
    life_inheritance_scheduler* scheduler;
    life_estate* estate;
} life_inheritance_due_user;

void life_inheritance_action_list_init(life_inheritance_action_list* list,
                                       life_inheritance_action* storage,
                                       u32 capacity,
                                       u64 start_id);
int life_inheritance_action_append(life_inheritance_action_list* list,
                                   const life_inheritance_action* action,
                                   u64* out_id);

int life_inheritance_scheduler_init(life_inheritance_scheduler* sched,
                                    dom_time_event* event_storage,
                                    u32 event_capacity,
                                    dg_due_entry* entry_storage,
                                    life_inheritance_due_user* user_storage,
                                    u32 entry_capacity,
                                    dom_act_time_t start_tick,
                                    dom_act_time_t claim_period_ticks,
                                    life_estate_registry* estates,
                                    life_inheritance_action_list* actions);
int life_inheritance_scheduler_register_estate(life_inheritance_scheduler* sched,
                                               life_estate* estate);
int life_inheritance_scheduler_advance(life_inheritance_scheduler* sched,
                                       dom_act_time_t target_tick);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_LIFE_INHERITANCE_SCHEDULER_H */
