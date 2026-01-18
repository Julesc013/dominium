/*
FILE: game/rules/population/population_refusal_codes.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Game / population rules
RESPONSIBILITY: Implements refusal code string conversion.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Refusal codes are stable and deterministic.
*/
#include "dominium/rules/population/population_refusal_codes.h"

const char* population_refusal_to_string(population_refusal_code code)
{
    switch (code) {
        case POP_REFUSAL_NONE: return "none";
        case POP_REFUSAL_MIGRATION_INSUFFICIENT_RESOURCES: return "migration_insufficient_resources";
        case POP_REFUSAL_MIGRATION_INSUFFICIENT_AUTHORITY: return "migration_insufficient_authority";
        case POP_REFUSAL_HOUSEHOLD_TOO_LARGE: return "household_too_large";
        case POP_REFUSAL_COHORT_NOT_FOUND: return "cohort_not_found";
        case POP_REFUSAL_INVALID_BUCKET_DISTRIBUTION: return "invalid_bucket_distribution";
        default: return "unknown";
    }
}
