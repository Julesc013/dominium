/*
FILE: include/dominium/rules/survival/survival_production_actions.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / survival rules
RESPONSIBILITY: Defines deterministic production actions for CIV0a.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Action ordering is deterministic.
*/
#ifndef DOMINIUM_RULES_SURVIVAL_PRODUCTION_ACTIONS_H
#define DOMINIUM_RULES_SURVIVAL_PRODUCTION_ACTIONS_H

#include "domino/sim/dg_due_sched.h"
#include "dominium/rules/survival/cohort_model.h"
#include "dominium/rules/survival/needs_model.h"
#include "dominium/rules/survival/shelter_proxy.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum survival_production_action_type {
    SURVIVAL_ACTION_GATHER_FOOD = 1,
    SURVIVAL_ACTION_COLLECT_WATER = 2,
    SURVIVAL_ACTION_BUILD_SHELTER = 3
} survival_production_action_type;

typedef enum survival_production_action_status {
    SURVIVAL_ACTION_PENDING = 1,
    SURVIVAL_ACTION_COMPLETED = 2,
    SURVIVAL_ACTION_REFUSED = 3
} survival_production_action_status;

typedef enum survival_production_refusal_code {
    SURVIVAL_REFUSAL_NONE = 0,
    SURVIVAL_REFUSAL_COHORT_NOT_FOUND,
    SURVIVAL_REFUSAL_ACTION_ALREADY_PENDING,
    SURVIVAL_REFUSAL_INSUFFICIENT_TOOLS,
    SURVIVAL_REFUSAL_INSUFFICIENT_LABOR
} survival_production_refusal_code;

typedef struct survival_production_action {
    u64 action_id;
    u64 cohort_id;
    u32 type;
    u32 status;
    dom_act_time_t start_tick;
    dom_act_time_t end_tick;
    u32 output_food;
    u32 output_water;
    u32 output_shelter;
    u64 provenance_ref;
    u32 refusal_code;
} survival_production_action;

typedef struct survival_production_action_input {
    u64 cohort_id;
    u32 type;
    dom_act_time_t start_tick;
    dom_time_delta_t duration_ticks;
    u32 output_food;
    u32 output_water;
    u32 output_shelter;
    u64 provenance_ref;
} survival_production_action_input;

typedef struct survival_production_action_registry {
    survival_production_action* actions;
    u32 count;
    u32 capacity;
    u64 next_id;
} survival_production_action_registry;

typedef struct survival_production_scheduler {
    dg_due_scheduler due;
    dom_time_event* due_events;
    dg_due_entry* due_entries;
    struct survival_production_due_user* due_users;
    survival_cohort_registry* cohorts;
    survival_needs_registry* needs;
    survival_production_action_registry* actions;
} survival_production_scheduler;

typedef struct survival_production_due_user {
    survival_production_scheduler* scheduler;
    survival_production_action* action;
} survival_production_due_user;

void survival_production_action_registry_init(survival_production_action_registry* reg,
                                              survival_production_action* storage,
                                              u32 capacity,
                                              u64 start_id);
survival_production_action* survival_production_action_find(
    survival_production_action_registry* reg,
    u64 action_id);

int survival_production_scheduler_init(survival_production_scheduler* sched,
                                       dom_time_event* event_storage,
                                       u32 event_capacity,
                                       dg_due_entry* entry_storage,
                                       survival_production_due_user* user_storage,
                                       u32 entry_capacity,
                                       dom_act_time_t start_tick,
                                       survival_cohort_registry* cohorts,
                                       survival_needs_registry* needs,
                                       survival_production_action_registry* actions);

int survival_production_schedule_action(survival_production_scheduler* sched,
                                        const survival_production_action_input* input,
                                        survival_production_refusal_code* out_refusal,
                                        u64* out_action_id);
int survival_production_advance(survival_production_scheduler* sched,
                                dom_act_time_t target_tick);
dom_act_time_t survival_production_next_due(const survival_production_scheduler* sched);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_RULES_SURVIVAL_PRODUCTION_ACTIONS_H */
