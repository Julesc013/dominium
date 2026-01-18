/*
FILE: include/dominium/rules/governance/legitimacy_model.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / governance
RESPONSIBILITY: Defines legitimacy state and deterministic event scheduling.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Legitimacy updates are deterministic.
*/
#ifndef DOMINIUM_RULES_GOVERNANCE_LEGITIMACY_MODEL_H
#define DOMINIUM_RULES_GOVERNANCE_LEGITIMACY_MODEL_H

#include "domino/core/dom_time_core.h"
#include "domino/core/types.h"
#include "domino/sim/dg_due_sched.h"

#ifdef __cplusplus
extern "C" {
#endif

#define LEGITIMACY_SCALE 1000u

typedef struct legitimacy_state {
    u64 legitimacy_id;
    u32 value;
    u32 max_value;
    u32 stable_threshold;
    u32 contested_threshold;
    u32 failed_threshold;
    dom_act_time_t next_due_tick;
} legitimacy_state;

typedef struct legitimacy_registry {
    legitimacy_state* states;
    u32 count;
    u32 capacity;
} legitimacy_registry;

void legitimacy_registry_init(legitimacy_registry* reg,
                              legitimacy_state* storage,
                              u32 capacity);
int legitimacy_register(legitimacy_registry* reg,
                        u64 legitimacy_id,
                        u32 start_value,
                        u32 max_value,
                        u32 stable_threshold,
                        u32 contested_threshold,
                        u32 failed_threshold);
legitimacy_state* legitimacy_find(legitimacy_registry* reg, u64 legitimacy_id);
int legitimacy_apply_delta(legitimacy_state* state, i32 delta);
int legitimacy_is_failed(const legitimacy_state* state);

typedef struct legitimacy_event {
    u64 event_id;
    u64 legitimacy_id;
    i32 delta;
    dom_act_time_t trigger_act;
} legitimacy_event;

typedef struct legitimacy_due_user {
    struct legitimacy_scheduler* scheduler;
    legitimacy_event* event;
} legitimacy_due_user;

typedef struct legitimacy_scheduler {
    dg_due_scheduler due;
    dom_time_event* due_events;
    dg_due_entry* due_entries;
    legitimacy_due_user* due_users;
    legitimacy_event* events;
    u32 event_capacity;
    u32 event_count;
    u64 next_event_id;
    legitimacy_registry* registry;
    u32 processed_last;
    u32 processed_total;
} legitimacy_scheduler;

int legitimacy_scheduler_init(legitimacy_scheduler* sched,
                              dom_time_event* event_storage,
                              u32 event_capacity,
                              dg_due_entry* entry_storage,
                              legitimacy_due_user* user_storage,
                              u32 entry_capacity,
                              dom_act_time_t start_tick,
                              legitimacy_event* events,
                              u32 events_capacity,
                              legitimacy_registry* registry,
                              u64 start_event_id);
int legitimacy_schedule_event(legitimacy_scheduler* sched,
                              u64 legitimacy_id,
                              i32 delta,
                              dom_act_time_t trigger_act);
int legitimacy_scheduler_advance(legitimacy_scheduler* sched,
                                 dom_act_time_t target_tick);
dom_act_time_t legitimacy_scheduler_next_due(const legitimacy_scheduler* sched);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_RULES_GOVERNANCE_LEGITIMACY_MODEL_H */
