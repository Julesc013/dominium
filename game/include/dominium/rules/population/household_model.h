/*
FILE: include/dominium/rules/population/household_model.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / population rules
RESPONSIBILITY: Defines bounded household membership and deterministic ordering.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Member ordering is deterministic.
*/
#ifndef DOMINIUM_RULES_POPULATION_HOUSEHOLD_MODEL_H
#define DOMINIUM_RULES_POPULATION_HOUSEHOLD_MODEL_H

#include "domino/core/dom_time_core.h"
#include "domino/core/types.h"
#include "dominium/rules/population/population_refusal_codes.h"

#ifdef __cplusplus
extern "C" {
#endif

#define POPULATION_HOUSEHOLD_MAX_MEMBERS 32u

typedef struct population_household {
    u64 household_id;
    u64 residence_ref;
    u64 resource_pool_ref;
    u64 members[POPULATION_HOUSEHOLD_MAX_MEMBERS];
    u32 member_count;
    dom_act_time_t next_due_tick;
} population_household;

typedef struct population_household_registry {
    population_household* households;
    u32 count;
    u32 capacity;
} population_household_registry;

void population_household_registry_init(population_household_registry* reg,
                                        population_household* storage,
                                        u32 capacity);
int population_household_register(population_household_registry* reg,
                                  u64 household_id,
                                  u64 residence_ref,
                                  u64 resource_pool_ref);
population_household* population_household_find(population_household_registry* reg,
                                                u64 household_id);
int population_household_add_member(population_household_registry* reg,
                                    u64 household_id,
                                    u64 person_id,
                                    population_refusal_code* out_refusal);
int population_household_remove_member(population_household_registry* reg,
                                       u64 household_id,
                                       u64 person_id);
int population_household_has_member(const population_household* household,
                                    u64 person_id);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_RULES_POPULATION_HOUSEHOLD_MODEL_H */
