/*
FILE: include/dominium/rules/population/cohort_types.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / population rules
RESPONSIBILITY: Defines cohort keys, cohort state, and deterministic registries.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Cohort IDs and ordering are deterministic.
*/
#ifndef DOMINIUM_RULES_POPULATION_COHORT_TYPES_H
#define DOMINIUM_RULES_POPULATION_COHORT_TYPES_H

#include "domino/core/dom_time_core.h"
#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

#define POPULATION_AGE_BUCKETS 8u
#define POPULATION_SEX_BUCKETS 3u
#define POPULATION_HEALTH_BUCKETS 4u
#define POPULATION_SEX_UNKNOWN_INDEX 2u
#define POPULATION_HEALTH_DEFAULT_INDEX 0u

typedef struct population_cohort_key {
    u64 body_id;
    u64 region_id;
    u64 org_id;
} population_cohort_key;

u64 population_cohort_id_from_key(const population_cohort_key* key);

typedef struct population_cohort_state {
    u64 cohort_id;
    population_cohort_key key;
    u32 count;
    u32 age_buckets[POPULATION_AGE_BUCKETS];
    u32 sex_buckets[POPULATION_SEX_BUCKETS];
    u32 health_buckets[POPULATION_HEALTH_BUCKETS];
    u64 needs_state_ref;
    dom_act_time_t next_due_tick;
    u64 provenance_summary_hash;
} population_cohort_state;

typedef struct population_cohort_registry {
    population_cohort_state* cohorts;
    u32 count;
    u32 capacity;
} population_cohort_registry;

void population_cohort_registry_init(population_cohort_registry* reg,
                                     population_cohort_state* storage,
                                     u32 capacity);
int population_cohort_register(population_cohort_registry* reg,
                               const population_cohort_key* key,
                               u32 count,
                               u64 needs_state_ref);
population_cohort_state* population_cohort_find(population_cohort_registry* reg,
                                                u64 cohort_id);
population_cohort_state* population_cohort_find_by_key(population_cohort_registry* reg,
                                                       const population_cohort_key* key);
int population_cohort_adjust_count(population_cohort_registry* reg,
                                   u64 cohort_id,
                                   i32 delta,
                                   u32* out_count);
int population_cohort_set_next_due(population_cohort_registry* reg,
                                   u64 cohort_id,
                                   dom_act_time_t next_due_tick);
int population_cohort_set_provenance(population_cohort_registry* reg,
                                     u64 cohort_id,
                                     u64 provenance_hash);
int population_cohort_mix_provenance(population_cohort_registry* reg,
                                     u64 cohort_id,
                                     u64 provenance_mix);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_RULES_POPULATION_COHORT_TYPES_H */
