/*
FILE: include/dominium/rules/war/resistance_scheduler.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / war rules
RESPONSIBILITY: Defines deterministic scheduling for occupation, resistance, disruption, and pacification.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Scheduler ordering is deterministic.
*/
#ifndef DOMINIUM_RULES_WAR_RESISTANCE_SCHEDULER_H
#define DOMINIUM_RULES_WAR_RESISTANCE_SCHEDULER_H

#include "domino/core/dom_time_core.h"
#include "domino/sim/dg_due_sched.h"
#include "dominium/rules/governance/enforcement_capacity.h"
#include "dominium/rules/governance/legitimacy_model.h"
#include "dominium/rules/infrastructure/store_model.h"
#include "dominium/rules/logistics/transport_capacity.h"
#include "dominium/rules/survival/cohort_model.h"
#include "dominium/rules/survival/needs_model.h"
#include "dominium/rules/war/disruption_effects.h"
#include "dominium/rules/war/occupation_state.h"
#include "dominium/rules/war/pacification_policies.h"
#include "dominium/rules/war/resistance_state.h"
#include "dominium/rules/war/territory_control.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum resistance_due_type {
    RESIST_DUE_OCCUPATION = 0,
    RESIST_DUE_RESISTANCE = 1,
    RESIST_DUE_DISRUPTION = 2,
    RESIST_DUE_POLICY = 3
} resistance_due_type;

typedef struct resistance_scheduler resistance_scheduler;

typedef struct resistance_due_user {
    resistance_scheduler* scheduler;
    u32 type;
    void* target;
    u32 handle;
} resistance_due_user;

struct resistance_scheduler {
    dg_due_scheduler due;
    dom_time_event* due_events;
    dg_due_entry* due_entries;
    resistance_due_user* due_users;
    u32 entry_capacity;

    occupation_registry* occupations;
    resistance_registry* resistances;
    territory_control_registry* territories;
    disruption_event_list* disruptions;
    pacification_policy_registry* policies;
    pacification_policy_event_list* policy_events;

    legitimacy_registry* legitimacy;
    enforcement_capacity_registry* enforcement;
    infra_store_registry* stores;
    transport_capacity_registry* transport;
    survival_cohort_registry* survival_cohorts;
    survival_needs_registry* survival_needs;
    survival_needs_params needs_params;

    u32 processed_last;
    u32 processed_total;
};

int resistance_scheduler_init(resistance_scheduler* sched,
                              dom_time_event* event_storage,
                              u32 event_capacity,
                              dg_due_entry* entry_storage,
                              resistance_due_user* user_storage,
                              u32 entry_capacity,
                              dom_act_time_t start_tick,
                              occupation_registry* occupations,
                              resistance_registry* resistances,
                              territory_control_registry* territories,
                              disruption_event_list* disruptions,
                              pacification_policy_registry* policies,
                              pacification_policy_event_list* policy_events,
                              legitimacy_registry* legitimacy,
                              enforcement_capacity_registry* enforcement,
                              infra_store_registry* stores,
                              transport_capacity_registry* transport,
                              survival_cohort_registry* survival_cohorts,
                              survival_needs_registry* survival_needs,
                              const survival_needs_params* needs_params);

int resistance_scheduler_register_occupation(resistance_scheduler* sched,
                                             occupation_state* state);
int resistance_scheduler_register_resistance(resistance_scheduler* sched,
                                             resistance_state* state);
int resistance_scheduler_register_disruption(resistance_scheduler* sched,
                                             disruption_event* event);
int resistance_scheduler_register_policy(resistance_scheduler* sched,
                                         pacification_policy_event* event);

int resistance_scheduler_advance(resistance_scheduler* sched,
                                 dom_act_time_t target_tick);
dom_act_time_t resistance_scheduler_next_due(const resistance_scheduler* sched);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_RULES_WAR_RESISTANCE_SCHEDULER_H */
