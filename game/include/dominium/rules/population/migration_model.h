/*
FILE: include/dominium/rules/population/migration_model.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / population rules
RESPONSIBILITY: Defines migration flows and deterministic application.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Flow ordering and application are deterministic.
*/
#ifndef DOMINIUM_RULES_POPULATION_MIGRATION_MODEL_H
#define DOMINIUM_RULES_POPULATION_MIGRATION_MODEL_H

#include "domino/core/dom_time_core.h"
#include "domino/core/types.h"
#include "dominium/rules/population/cohort_types.h"
#include "dominium/rules/population/population_refusal_codes.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum population_migration_status {
    POP_MIGRATION_ACTIVE = 0,
    POP_MIGRATION_COMPLETED = 1,
    POP_MIGRATION_CANCELLED = 2
} population_migration_status;

typedef struct population_migration_flow {
    u64 flow_id;
    population_cohort_key src_key;
    population_cohort_key dst_key;
    u64 src_cohort_id;
    u64 dst_cohort_id;
    u32 count_delta;
    dom_act_time_t start_act;
    dom_act_time_t arrival_act;
    u32 cause_code;
    u64 provenance_mix;
    population_migration_status status;
} population_migration_flow;

typedef struct population_migration_registry {
    population_migration_flow* flows;
    u32 count;
    u32 capacity;
    u64 next_flow_id;
} population_migration_registry;

typedef struct population_migration_input {
    u64 flow_id;
    population_cohort_key src_key;
    population_cohort_key dst_key;
    u32 count_delta;
    dom_act_time_t start_act;
    dom_act_time_t arrival_act;
    u32 cause_code;
    u64 provenance_mix;
} population_migration_input;

void population_migration_registry_init(population_migration_registry* reg,
                                        population_migration_flow* storage,
                                        u32 capacity,
                                        u64 start_flow_id);
population_migration_flow* population_migration_find(population_migration_registry* reg,
                                                     u64 flow_id);
int population_migration_schedule(population_migration_registry* reg,
                                  const population_migration_input* input,
                                  population_refusal_code* out_refusal);
int population_migration_apply(population_migration_flow* flow,
                               population_cohort_registry* cohorts,
                               population_refusal_code* out_refusal);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_RULES_POPULATION_MIGRATION_MODEL_H */
