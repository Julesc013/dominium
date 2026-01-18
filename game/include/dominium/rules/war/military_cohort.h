/*
FILE: include/dominium/rules/war/military_cohort.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / war rules
RESPONSIBILITY: Defines military cohort assignments and deterministic registries.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Cohort ordering and updates are deterministic.
*/
#ifndef DOMINIUM_RULES_WAR_MILITARY_COHORT_H
#define DOMINIUM_RULES_WAR_MILITARY_COHORT_H

#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum military_role {
    MILITARY_ROLE_INFANTRY = 0,
    MILITARY_ROLE_CREW = 1,
    MILITARY_ROLE_SECURITY = 2,
    MILITARY_ROLE_SUPPORT = 3
} military_role;

typedef struct military_cohort {
    u64 cohort_id;
    u64 assigned_force_id;
    u32 count;
    u32 role;
    u64 casualty_tracking_ref;
} military_cohort;

typedef struct military_cohort_registry {
    military_cohort* cohorts;
    u32 count;
    u32 capacity;
} military_cohort_registry;

void military_cohort_registry_init(military_cohort_registry* reg,
                                   military_cohort* storage,
                                   u32 capacity);
military_cohort* military_cohort_find(military_cohort_registry* reg,
                                      u64 cohort_id);
int military_cohort_register(military_cohort_registry* reg,
                             u64 cohort_id,
                             u64 assigned_force_id,
                             u32 count,
                             u32 role,
                             u64 casualty_tracking_ref);
int military_cohort_adjust_count(military_cohort_registry* reg,
                                 u64 cohort_id,
                                 i32 delta,
                                 u32* out_count);
int military_cohort_release(military_cohort_registry* reg,
                            u64 cohort_id);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_RULES_WAR_MILITARY_COHORT_H */
