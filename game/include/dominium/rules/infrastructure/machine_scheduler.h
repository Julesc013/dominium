/*
FILE: include/dominium/rules/infrastructure/machine_scheduler.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / infrastructure
RESPONSIBILITY: Defines event-driven machine scheduler for production.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Scheduling and processing are deterministic.
*/
#ifndef DOMINIUM_RULES_INFRA_MACHINE_SCHEDULER_H
#define DOMINIUM_RULES_INFRA_MACHINE_SCHEDULER_H

#include "domino/sim/dg_due_sched.h"
#include "dominium/rules/city/city_refusal_codes.h"
#include "dominium/rules/infrastructure/building_machine.h"
#include "dominium/rules/infrastructure/production_chain.h"
#include "dominium/rules/infrastructure/store_model.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct machine_scheduler_params {
    u32 retry_interval;
    u32 cooldown_interval;
    u32 maintenance_degrade;
    u32 maintenance_min_operational;
} machine_scheduler_params;

void machine_scheduler_params_default(machine_scheduler_params* params);

typedef struct machine_due_user {
    struct machine_scheduler* scheduler;
    building_machine* machine;
} machine_due_user;

typedef struct machine_scheduler {
    dg_due_scheduler due;
    dom_time_event* due_events;
    dg_due_entry* due_entries;
    machine_due_user* due_users;
    building_machine_registry* machines;
    const production_recipe_registry* recipes;
    infra_store_registry* stores;
    machine_scheduler_params params;
    u32 processed_last;
    u32 processed_total;
} machine_scheduler;

int machine_scheduler_init(machine_scheduler* sched,
                           dom_time_event* event_storage,
                           u32 event_capacity,
                           dg_due_entry* entry_storage,
                           machine_due_user* user_storage,
                           u32 entry_capacity,
                           dom_act_time_t start_tick,
                           building_machine_registry* machines,
                           const production_recipe_registry* recipes,
                           infra_store_registry* stores,
                           const machine_scheduler_params* params);
int machine_scheduler_register(machine_scheduler* sched,
                               building_machine* machine);
int machine_scheduler_advance(machine_scheduler* sched,
                              dom_act_time_t target_tick,
                              civ1_refusal_code* out_refusal);
dom_act_time_t machine_scheduler_next_due(const machine_scheduler* sched);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_RULES_INFRA_MACHINE_SCHEDULER_H */
