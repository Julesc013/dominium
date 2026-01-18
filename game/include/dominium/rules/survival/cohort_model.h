/*
FILE: include/dominium/rules/survival/cohort_model.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / survival rules
RESPONSIBILITY: Defines cohort records and deterministic registries.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Cohort ordering is stable and deterministic.
*/
#ifndef DOMINIUM_RULES_SURVIVAL_COHORT_MODEL_H
#define DOMINIUM_RULES_SURVIVAL_COHORT_MODEL_H

#include "domino/core/dom_time_core.h"
#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct survival_cohort {
    u64 cohort_id;
    u32 count;
    u64 location_ref;
    u32 age_bucket;
    u32 health_bucket;
    dom_act_time_t next_due_tick;
    u64 active_action_id;
} survival_cohort;

typedef struct survival_cohort_registry {
    survival_cohort* cohorts;
    u32 count;
    u32 capacity;
} survival_cohort_registry;

void survival_cohort_registry_init(survival_cohort_registry* reg,
                                   survival_cohort* storage,
                                   u32 capacity);
int survival_cohort_register(survival_cohort_registry* reg,
                             u64 cohort_id,
                             u32 count,
                             u64 location_ref);
survival_cohort* survival_cohort_find(survival_cohort_registry* reg, u64 cohort_id);
int survival_cohort_adjust_count(survival_cohort_registry* reg,
                                 u64 cohort_id,
                                 i32 delta,
                                 u32* out_count);
int survival_cohort_set_next_due(survival_cohort_registry* reg,
                                 u64 cohort_id,
                                 dom_act_time_t next_due_tick);
int survival_cohort_set_active_action(survival_cohort_registry* reg,
                                      u64 cohort_id,
                                      u64 action_id);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_RULES_SURVIVAL_COHORT_MODEL_H */
