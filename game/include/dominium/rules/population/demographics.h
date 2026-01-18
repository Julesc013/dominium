/*
FILE: include/dominium/rules/population/demographics.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / population rules
RESPONSIBILITY: Defines deterministic cohort bucket operations.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Bucket updates are deterministic and ordered.
*/
#ifndef DOMINIUM_RULES_POPULATION_DEMOGRAPHICS_H
#define DOMINIUM_RULES_POPULATION_DEMOGRAPHICS_H

#include "dominium/rules/population/cohort_types.h"
#include "dominium/rules/population/population_refusal_codes.h"

#ifdef __cplusplus
extern "C" {
#endif

int population_demographics_init(population_cohort_state* cohort);
int population_demographics_validate(const population_cohort_state* cohort,
                                     population_refusal_code* out_refusal);
int population_demographics_apply_delta(population_cohort_state* cohort,
                                        i32 delta,
                                        u64 provenance_mix,
                                        population_refusal_code* out_refusal);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_RULES_POPULATION_DEMOGRAPHICS_H */
