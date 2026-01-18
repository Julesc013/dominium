/*
FILE: include/dominium/rules/population/population_scheduler.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / population rules
RESPONSIBILITY: Defines due scheduler for cohort and migration events.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Due processing order is deterministic.
*/
#ifndef DOMINIUM_RULES_POPULATION_SCHEDULER_H
#define DOMINIUM_RULES_POPULATION_SCHEDULER_H

#include "domino/sim/dg_due_sched.h"
#include "dominium/rules/population/cohort_types.h"
#include "dominium/rules/population/migration_model.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum population_due_kind {
    POP_DUE_COHORT = 0,
    POP_DUE_MIGRATION = 1
} population_due_kind;

typedef struct population_scheduler population_scheduler;

typedef struct population_due_user {
    population_scheduler* scheduler;
    population_due_kind kind;
    population_cohort_state* cohort;
    population_migration_flow* flow;
} population_due_user;

typedef struct population_cohort_due_hook {
    dom_act_time_t (*process)(void* user,
                              population_cohort_state* cohort,
                              dom_act_time_t due_tick);
    void* user;
} population_cohort_due_hook;

typedef struct population_migration_hook {
    int (*apply)(void* user, population_migration_flow* flow);
    void* user;
} population_migration_hook;

typedef struct population_scheduler {
    dg_due_scheduler due;
    dom_time_event* due_events;
    dg_due_entry* due_entries;
    population_due_user* due_users;
    population_cohort_registry* cohorts;
    population_migration_registry* migrations;
    population_cohort_due_hook cohort_hook;
    population_migration_hook migration_hook;
    dom_act_time_t start_tick;
    u32 processed_last;
    u32 processed_total;
} population_scheduler;

int population_scheduler_init(population_scheduler* sched,
                              dom_time_event* event_storage,
                              u32 event_capacity,
                              dg_due_entry* entry_storage,
                              population_due_user* user_storage,
                              u32 entry_capacity,
                              dom_act_time_t start_tick,
                              population_cohort_registry* cohorts,
                              population_migration_registry* migrations);
void population_scheduler_set_cohort_hook(population_scheduler* sched,
                                          const population_cohort_due_hook* hook);
void population_scheduler_set_migration_hook(population_scheduler* sched,
                                             const population_migration_hook* hook);
int population_scheduler_register_cohort(population_scheduler* sched,
                                         population_cohort_state* cohort);
int population_scheduler_register_migration(population_scheduler* sched,
                                            population_migration_flow* flow);
int population_scheduler_advance(population_scheduler* sched,
                                 dom_act_time_t target_tick);
dom_act_time_t population_scheduler_next_due(const population_scheduler* sched);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_RULES_POPULATION_SCHEDULER_H */
