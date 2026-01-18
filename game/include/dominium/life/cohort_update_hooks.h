/*
FILE: include/dominium/life/cohort_update_hooks.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / life
RESPONSIBILITY: Defines cohort aggregation hooks for macro fidelity.
ALLOWED DEPENDENCIES: `game/include/**`, `engine/include/**` public headers, and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; product-layer runtime code.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Cohort ordering and counts are deterministic.
*/
#ifndef DOMINIUM_LIFE_COHORT_UPDATE_HOOKS_H
#define DOMINIUM_LIFE_COHORT_UPDATE_HOOKS_H

#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct life_cohort_entry {
    u64 cohort_id;
    u64 population_count;
} life_cohort_entry;

typedef struct life_cohort_registry {
    life_cohort_entry* entries;
    u32 count;
    u32 capacity;
} life_cohort_registry;

void life_cohort_registry_init(life_cohort_registry* reg,
                               life_cohort_entry* storage,
                               u32 capacity);
int life_cohort_add_birth(life_cohort_registry* reg,
                          u64 cohort_id,
                          u64 count);
int life_cohort_get_count(const life_cohort_registry* reg,
                          u64 cohort_id,
                          u64* out_count);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_LIFE_COHORT_UPDATE_HOOKS_H */
