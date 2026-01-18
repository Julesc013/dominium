/*
FILE: include/dominium/rules/war/pacification_policies.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / war rules
RESPONSIBILITY: Defines deterministic pacification policies and scheduled effects.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Pacification policy application is deterministic.
*/
#ifndef DOMINIUM_RULES_WAR_PACIFICATION_POLICIES_H
#define DOMINIUM_RULES_WAR_PACIFICATION_POLICIES_H

#include "domino/core/dom_time_core.h"
#include "domino/core/types.h"
#include "dominium/rules/governance/legitimacy_model.h"
#include "dominium/rules/infrastructure/store_model.h"
#include "dominium/rules/war/occupation_state.h"
#include "dominium/rules/war/resistance_state.h"
#include "dominium/rules/war/territory_control.h"

#ifdef __cplusplus
extern "C" {
#endif

#define PACIFICATION_MAX_COSTS 4u

typedef struct pacification_policy {
    u64 policy_id;
    u32 allowed;
    u64 cost_asset_ids[PACIFICATION_MAX_COSTS];
    u32 cost_qtys[PACIFICATION_MAX_COSTS];
    u32 cost_count;
    i32 legitimacy_delta;
    i32 resistance_pressure_delta;
    i32 coercion_delta;
    u32 coercion_floor;
    u64 provenance_ref;
} pacification_policy;

typedef struct pacification_policy_registry {
    pacification_policy* policies;
    u32 count;
    u32 capacity;
    u64 next_id;
} pacification_policy_registry;

typedef enum pacification_event_status {
    PACIFICATION_EVENT_SCHEDULED = 0,
    PACIFICATION_EVENT_APPLIED = 1
} pacification_event_status;

typedef struct pacification_policy_event {
    u64 event_id;
    u64 policy_id;
    u64 occupation_id;
    u64 resistance_id;
    u64 territory_id;
    u64 supply_store_ref;
    dom_act_time_t scheduled_act;
    u32 status;
    u64 provenance_ref;
} pacification_policy_event;

typedef struct pacification_policy_event_list {
    pacification_policy_event* events;
    u32 count;
    u32 capacity;
    u64 next_id;
} pacification_policy_event_list;

typedef struct pacification_apply_context {
    pacification_policy_registry* policies;
    infra_store_registry* stores;
    legitimacy_registry* legitimacy;
    territory_control_registry* territory;
    occupation_registry* occupations;
    resistance_registry* resistances;
} pacification_apply_context;

void pacification_policy_registry_init(pacification_policy_registry* reg,
                                       pacification_policy* storage,
                                       u32 capacity,
                                       u64 start_id);
pacification_policy* pacification_policy_find(pacification_policy_registry* reg,
                                              u64 policy_id);
int pacification_policy_register(pacification_policy_registry* reg,
                                 const pacification_policy* input,
                                 u64* out_id);

void pacification_policy_event_list_init(pacification_policy_event_list* list,
                                         pacification_policy_event* storage,
                                         u32 capacity,
                                         u64 start_id);
pacification_policy_event* pacification_policy_event_find(pacification_policy_event_list* list,
                                                          u64 event_id);
int pacification_policy_event_schedule(pacification_policy_event_list* list,
                                       const pacification_policy_event* input,
                                       u64* out_id);

int pacification_policy_apply(pacification_policy_event* event,
                              pacification_apply_context* ctx,
                              occupation_refusal_code* out_refusal);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_RULES_WAR_PACIFICATION_POLICIES_H */
