/*
FILE: include/dominium/rules/war/occupation_state.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / war rules
RESPONSIBILITY: Defines deterministic occupation state records and maintenance hooks.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Occupation updates are deterministic and event-driven.
*/
#ifndef DOMINIUM_RULES_WAR_OCCUPATION_STATE_H
#define DOMINIUM_RULES_WAR_OCCUPATION_STATE_H

#include "domino/core/dom_time_core.h"
#include "domino/core/types.h"
#include "dominium/rules/governance/enforcement_capacity.h"
#include "dominium/rules/governance/legitimacy_model.h"
#include "dominium/rules/infrastructure/store_model.h"
#include "dominium/rules/war/territory_control.h"

#ifdef __cplusplus
extern "C" {
#endif

#define OCCUPATION_MAX_FORCES 8u
#define OCCUPATION_MAX_SUPPLY_REFS 4u

typedef enum occupation_status {
    OCCUPATION_STATUS_ACTIVE = 0,
    OCCUPATION_STATUS_FAILED = 1,
    OCCUPATION_STATUS_ENDED = 2
} occupation_status;

typedef enum occupation_refusal_code {
    OCCUPATION_REFUSAL_NONE = 0,
    OCCUPATION_REFUSAL_INSUFFICIENT_ENFORCEMENT = 1,
    OCCUPATION_REFUSAL_INSUFFICIENT_SUPPLY = 2,
    OCCUPATION_REFUSAL_POLICY_NOT_ALLOWED = 3,
    OCCUPATION_REFUSAL_TERRITORY_NOT_CONTROLLED = 4,
    OCCUPATION_REFUSAL_UNKNOWN_TERRITORY = 5
} occupation_refusal_code;

const char* occupation_refusal_to_string(occupation_refusal_code code);

typedef struct occupation_state {
    u64 occupation_id;
    u64 territory_id;
    u64 occupier_org_id;
    u64 occupying_force_refs[OCCUPATION_MAX_FORCES];
    u32 occupying_force_count;
    u64 supply_refs[OCCUPATION_MAX_SUPPLY_REFS];
    u32 supply_ref_count;
    u64 legitimacy_id;
    u64 enforcement_capacity_id;
    u32 enforcement_min;
    u32 coercion_level;
    u64 supply_asset_id;
    u32 supply_qty;
    u32 control_gain;
    u32 control_loss;
    u32 legitimacy_min;
    i32 legitimacy_decay;
    dom_act_time_t start_act;
    dom_act_time_t next_due_tick;
    u32 maintenance_interval;
    u32 status;
    u64 provenance_ref;
} occupation_state;

typedef struct occupation_registry {
    occupation_state* states;
    u32 count;
    u32 capacity;
    u64 next_id;
} occupation_registry;

typedef struct occupation_update_context {
    territory_control_registry* territory;
    legitimacy_registry* legitimacy;
    enforcement_capacity_registry* enforcement;
    infra_store_registry* stores;
    dom_act_time_t now_act;
} occupation_update_context;

void occupation_registry_init(occupation_registry* reg,
                              occupation_state* storage,
                              u32 capacity,
                              u64 start_id);
occupation_state* occupation_find(occupation_registry* reg,
                                  u64 occupation_id);
occupation_state* occupation_find_by_territory(occupation_registry* reg,
                                               u64 territory_id);
int occupation_register(occupation_registry* reg,
                        const occupation_state* input,
                        u64* out_id);
int occupation_set_next_due(occupation_registry* reg,
                            u64 occupation_id,
                            dom_act_time_t next_due_tick);

int occupation_apply_maintenance(occupation_state* state,
                                 occupation_update_context* ctx,
                                 occupation_refusal_code* out_refusal);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_RULES_WAR_OCCUPATION_STATE_H */
