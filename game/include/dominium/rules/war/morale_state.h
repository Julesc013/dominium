/*
FILE: include/dominium/rules/war/morale_state.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / war rules
RESPONSIBILITY: Defines morale state and deterministic scheduling.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Morale updates and scheduling are deterministic.
*/
#ifndef DOMINIUM_RULES_WAR_MORALE_STATE_H
#define DOMINIUM_RULES_WAR_MORALE_STATE_H

#include "domino/core/dom_time_core.h"
#include "domino/core/types.h"
#include "domino/sim/dg_due_sched.h"
#include "dominium/rules/governance/legitimacy_model.h"

#ifdef __cplusplus
extern "C" {
#endif

#define MORALE_SCALE 1000u

typedef struct morale_modifiers {
    i32 supply;
    i32 victories;
    i32 losses;
    i32 legitimacy;
} morale_modifiers;

typedef struct morale_state {
    u64 morale_id;
    u32 morale_level;
    morale_modifiers modifiers;
    dom_act_time_t next_due_tick;
} morale_state;

typedef struct morale_registry {
    morale_state* states;
    u32 count;
    u32 capacity;
} morale_registry;

void morale_registry_init(morale_registry* reg,
                          morale_state* storage,
                          u32 capacity);
int morale_register(morale_registry* reg,
                    u64 morale_id,
                    u32 morale_level,
                    const morale_modifiers* modifiers);
morale_state* morale_find(morale_registry* reg,
                          u64 morale_id);
int morale_apply_delta(morale_state* state,
                       i32 delta);
int morale_set_modifiers(morale_state* state,
                         const morale_modifiers* modifiers);

typedef enum morale_event_type {
    MORALE_EVENT_DELTA = 0,
    MORALE_EVENT_LEGITIMACY_CHECK = 1
} morale_event_type;

typedef struct morale_event {
    u64 event_id;
    u64 morale_id;
    i32 delta;
    dom_act_time_t trigger_act;
    morale_event_type type;
    u64 legitimacy_id;
    u32 legitimacy_min;
    u64 provenance_ref;
} morale_event;

typedef struct morale_due_user {
    struct morale_scheduler* scheduler;
    morale_event* event;
} morale_due_user;

typedef struct morale_scheduler {
    dg_due_scheduler due;
    dom_time_event* due_events;
    dg_due_entry* due_entries;
    morale_due_user* due_users;
    morale_event* events;
    u32 event_capacity;
    u32 event_count;
    u64 next_event_id;
    morale_registry* registry;
    legitimacy_registry* legitimacy;
    u32 processed_last;
    u32 processed_total;
} morale_scheduler;

int morale_scheduler_init(morale_scheduler* sched,
                          dom_time_event* event_storage,
                          u32 event_capacity,
                          dg_due_entry* entry_storage,
                          morale_due_user* user_storage,
                          u32 entry_capacity,
                          dom_act_time_t start_tick,
                          morale_event* events,
                          u32 events_capacity,
                          morale_registry* registry,
                          legitimacy_registry* legitimacy,
                          u64 start_event_id);
int morale_schedule_event(morale_scheduler* sched,
                          u64 morale_id,
                          i32 delta,
                          dom_act_time_t trigger_act);
int morale_schedule_legitimacy_check(morale_scheduler* sched,
                                     u64 morale_id,
                                     dom_act_time_t trigger_act,
                                     u64 legitimacy_id,
                                     u32 legitimacy_min,
                                     i32 delta_if_below);
int morale_scheduler_advance(morale_scheduler* sched,
                             dom_act_time_t target_tick);
dom_act_time_t morale_scheduler_next_due(const morale_scheduler* sched);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_RULES_WAR_MORALE_STATE_H */
