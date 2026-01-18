/*
FILE: include/dominium/rules/war/readiness_state.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / war rules
RESPONSIBILITY: Defines readiness state and deterministic scheduling.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Readiness updates and scheduling are deterministic.
*/
#ifndef DOMINIUM_RULES_WAR_READINESS_STATE_H
#define DOMINIUM_RULES_WAR_READINESS_STATE_H

#include "domino/core/dom_time_core.h"
#include "domino/core/types.h"
#include "domino/sim/dg_due_sched.h"
#include "dominium/rules/infrastructure/store_model.h"

#ifdef __cplusplus
extern "C" {
#endif

#define READINESS_SCALE 1000u

typedef struct readiness_state {
    u64 readiness_id;
    u32 readiness_level;
    u32 degradation_rate;
    u32 recovery_rate;
    dom_act_time_t last_update_act;
    dom_act_time_t next_due_tick;
} readiness_state;

typedef struct readiness_registry {
    readiness_state* states;
    u32 count;
    u32 capacity;
} readiness_registry;

void readiness_registry_init(readiness_registry* reg,
                             readiness_state* storage,
                             u32 capacity);
int readiness_register(readiness_registry* reg,
                       u64 readiness_id,
                       u32 readiness_level,
                       u32 degradation_rate,
                       u32 recovery_rate);
readiness_state* readiness_find(readiness_registry* reg,
                                u64 readiness_id);
int readiness_apply_delta(readiness_state* state,
                          i32 delta,
                          dom_act_time_t update_act);

typedef enum readiness_event_type {
    READINESS_EVENT_DELTA = 0,
    READINESS_EVENT_SUPPLY_CHECK = 1
} readiness_event_type;

typedef struct readiness_event {
    u64 event_id;
    u64 readiness_id;
    i32 delta;
    dom_act_time_t trigger_act;
    readiness_event_type type;
    u64 supply_store_ref;
    u64 supply_asset_id;
    u32 supply_qty;
    u64 provenance_ref;
} readiness_event;

typedef struct readiness_due_user {
    struct readiness_scheduler* scheduler;
    readiness_event* event;
} readiness_due_user;

typedef struct readiness_scheduler {
    dg_due_scheduler due;
    dom_time_event* due_events;
    dg_due_entry* due_entries;
    readiness_due_user* due_users;
    readiness_event* events;
    u32 event_capacity;
    u32 event_count;
    u64 next_event_id;
    readiness_registry* registry;
    infra_store_registry* stores;
    u32 processed_last;
    u32 processed_total;
} readiness_scheduler;

int readiness_scheduler_init(readiness_scheduler* sched,
                             dom_time_event* event_storage,
                             u32 event_capacity,
                             dg_due_entry* entry_storage,
                             readiness_due_user* user_storage,
                             u32 entry_capacity,
                             dom_act_time_t start_tick,
                             readiness_event* events,
                             u32 events_capacity,
                             readiness_registry* registry,
                             infra_store_registry* stores,
                             u64 start_event_id);
int readiness_schedule_event(readiness_scheduler* sched,
                             u64 readiness_id,
                             i32 delta,
                             dom_act_time_t trigger_act);
int readiness_schedule_supply_check(readiness_scheduler* sched,
                                    u64 readiness_id,
                                    dom_act_time_t trigger_act,
                                    u64 supply_store_ref,
                                    u64 supply_asset_id,
                                    u32 supply_qty,
                                    i32 shortage_delta);
int readiness_scheduler_advance(readiness_scheduler* sched,
                                dom_act_time_t target_tick);
dom_act_time_t readiness_scheduler_next_due(const readiness_scheduler* sched);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_RULES_WAR_READINESS_STATE_H */
