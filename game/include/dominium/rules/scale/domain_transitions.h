/*
FILE: include/dominium/rules/scale/domain_transitions.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / scale
RESPONSIBILITY: Defines deterministic domain transitions and scheduler.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Transition ordering and processing are deterministic.
*/
#ifndef DOMINIUM_RULES_SCALE_DOMAIN_TRANSITIONS_H
#define DOMINIUM_RULES_SCALE_DOMAIN_TRANSITIONS_H

#include "domino/core/dom_time_core.h"
#include "domino/sim/dg_due_sched.h"
#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum scale_transition_status {
    SCALE_TRANSITION_PENDING = 0,
    SCALE_TRANSITION_ARRIVED = 1,
    SCALE_TRANSITION_BLOCKED = 2
} scale_transition_status;

typedef struct scale_domain_transition {
    u64 transition_id;
    u64 src_domain_id;
    u64 dst_domain_id;
    dom_act_time_t departure_act;
    dom_act_time_t arrival_act;
    u32 resource_cost;
    u64 provenance_ref;
    dom_act_time_t next_due_tick;
    scale_transition_status status;
} scale_domain_transition;

typedef struct scale_transition_registry {
    scale_domain_transition* transitions;
    u32 count;
    u32 capacity;
} scale_transition_registry;

void scale_transition_registry_init(scale_transition_registry* reg,
                                    scale_domain_transition* storage,
                                    u32 capacity);
int scale_transition_register(scale_transition_registry* reg,
                              u64 transition_id,
                              u64 src_domain_id,
                              u64 dst_domain_id,
                              dom_act_time_t departure_act,
                              dom_act_time_t arrival_act,
                              u32 resource_cost,
                              u64 provenance_ref);
scale_domain_transition* scale_transition_find(scale_transition_registry* reg,
                                               u64 transition_id);

typedef struct scale_transition_hook {
    int (*on_arrival)(void* user, const scale_domain_transition* transition);
    void* user;
} scale_transition_hook;

typedef struct scale_transition_due_user {
    struct scale_transition_scheduler* scheduler;
    scale_domain_transition* transition;
} scale_transition_due_user;

typedef struct scale_transition_scheduler {
    dg_due_scheduler due;
    dom_time_event* due_events;
    dg_due_entry* due_entries;
    scale_transition_due_user* due_users;
    scale_transition_registry* registry;
    scale_transition_hook hook;
    u32 processed_last;
    u32 processed_total;
} scale_transition_scheduler;

int scale_transition_scheduler_init(scale_transition_scheduler* sched,
                                    dom_time_event* event_storage,
                                    u32 event_capacity,
                                    dg_due_entry* entry_storage,
                                    scale_transition_due_user* user_storage,
                                    u32 entry_capacity,
                                    dom_act_time_t start_tick,
                                    scale_transition_registry* registry);
void scale_transition_set_hook(scale_transition_scheduler* sched,
                               const scale_transition_hook* hook);
int scale_transition_scheduler_register(scale_transition_scheduler* sched,
                                        scale_domain_transition* transition);
int scale_transition_scheduler_advance(scale_transition_scheduler* sched,
                                       dom_act_time_t target_tick);
dom_act_time_t scale_transition_scheduler_next_due(const scale_transition_scheduler* sched);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_RULES_SCALE_DOMAIN_TRANSITIONS_H */
