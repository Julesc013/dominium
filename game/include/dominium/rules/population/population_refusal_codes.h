/*
FILE: include/dominium/rules/population/population_refusal_codes.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / population rules
RESPONSIBILITY: Defines refusal codes for population/household/migration.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Refusal codes are stable and deterministic.
*/
#ifndef DOMINIUM_RULES_POPULATION_REFUSAL_CODES_H
#define DOMINIUM_RULES_POPULATION_REFUSAL_CODES_H

#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum population_refusal_code {
    POP_REFUSAL_NONE = 0,
    POP_REFUSAL_MIGRATION_INSUFFICIENT_RESOURCES,
    POP_REFUSAL_MIGRATION_INSUFFICIENT_AUTHORITY,
    POP_REFUSAL_HOUSEHOLD_TOO_LARGE,
    POP_REFUSAL_COHORT_NOT_FOUND,
    POP_REFUSAL_INVALID_BUCKET_DISTRIBUTION
} population_refusal_code;

const char* population_refusal_to_string(population_refusal_code code);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_RULES_POPULATION_REFUSAL_CODES_H */
