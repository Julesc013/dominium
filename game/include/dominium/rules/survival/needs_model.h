/*
FILE: include/dominium/rules/survival/needs_model.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / survival rules
RESPONSIBILITY: Defines deterministic needs state for cohorts.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Needs updates are deterministic.
*/
#ifndef DOMINIUM_RULES_SURVIVAL_NEEDS_MODEL_H
#define DOMINIUM_RULES_SURVIVAL_NEEDS_MODEL_H

#include "domino/core/dom_time_core.h"
#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct survival_needs_state {
    u32 food_store;
    u32 water_store;
    u32 shelter_level;
    u32 hunger_level;
    u32 thirst_level;
    dom_act_time_t last_consumption_tick;
    dom_act_time_t next_consumption_tick;
    u64 last_production_provenance;
} survival_needs_state;

typedef struct survival_needs_entry {
    u64 cohort_id;
    survival_needs_state state;
} survival_needs_entry;

typedef struct survival_needs_registry {
    survival_needs_entry* entries;
    u32 count;
    u32 capacity;
} survival_needs_registry;

typedef struct survival_needs_params {
    u32 food_per_person;
    u32 water_per_person;
    u32 hunger_max;
    u32 thirst_max;
    u32 shelter_min;
    u32 shelter_max;
    dom_time_delta_t consumption_interval;
} survival_needs_params;

void survival_needs_registry_init(survival_needs_registry* reg,
                                  survival_needs_entry* storage,
                                  u32 capacity);
int survival_needs_register(survival_needs_registry* reg,
                            u64 cohort_id,
                            const survival_needs_state* initial);
survival_needs_state* survival_needs_get(survival_needs_registry* reg,
                                         u64 cohort_id);

void survival_needs_params_default(survival_needs_params* params);
int survival_needs_resources_sufficient(const survival_needs_state* state,
                                        const survival_needs_params* params,
                                        u32 cohort_count);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_RULES_SURVIVAL_NEEDS_MODEL_H */
