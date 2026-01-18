/*
FILE: include/dominium/life/remains_decay_scheduler.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / life
RESPONSIBILITY: Defines event-driven remains decay scheduling.
ALLOWED DEPENDENCIES: `game/include/**`, `engine/include/**` public headers, and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; product-layer runtime code.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Scheduler ordering is deterministic.
*/
#ifndef DOMINIUM_LIFE_REMAINS_DECAY_SCHEDULER_H
#define DOMINIUM_LIFE_REMAINS_DECAY_SCHEDULER_H

#include "domino/sim/dg_due_sched.h"
#include "dominium/life/remains.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct life_remains_decay_rules {
    dom_time_delta_t fresh_to_decayed;
    dom_time_delta_t decayed_to_skeletal;
    dom_time_delta_t skeletal_to_unknown;
} life_remains_decay_rules;

typedef struct life_remains_decay_scheduler {
    dg_due_scheduler due;
    dom_time_event* due_events;
    dg_due_entry* due_entries;
    struct life_remains_decay_user* due_users;
    life_remains_registry* remains;
    life_remains_decay_rules rules;
} life_remains_decay_scheduler;

typedef struct life_remains_decay_user {
    life_remains_decay_scheduler* scheduler;
    life_remains* remains;
} life_remains_decay_user;

int life_remains_decay_scheduler_init(life_remains_decay_scheduler* sched,
                                      dom_time_event* event_storage,
                                      u32 event_capacity,
                                      dg_due_entry* entry_storage,
                                      life_remains_decay_user* user_storage,
                                      u32 entry_capacity,
                                      dom_act_time_t start_tick,
                                      life_remains_registry* remains,
                                      const life_remains_decay_rules* rules);
int life_remains_decay_register(life_remains_decay_scheduler* sched,
                                life_remains* remains);
int life_remains_decay_advance(life_remains_decay_scheduler* sched,
                               dom_act_time_t target_tick);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_LIFE_REMAINS_DECAY_SCHEDULER_H */
