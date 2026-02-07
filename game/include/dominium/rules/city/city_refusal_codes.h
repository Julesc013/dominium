/*
FILE: include/dominium/rules/city/city_refusal_codes.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / city rules
RESPONSIBILITY: Defines refusal codes for CIV1 city/infrastructure/logistics.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Refusal codes are stable and deterministic.
*/
#ifndef DOMINIUM_RULES_CITY_REFUSAL_CODES_H
#define DOMINIUM_RULES_CITY_REFUSAL_CODES_H

#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum civ1_refusal_code {
    CIV1_REFUSAL_NONE = 0,
    CIV1_REFUSAL_INSUFFICIENT_INPUTS,
    CIV1_REFUSAL_CAPACITY_UNAVAILABLE,
    CIV1_REFUSAL_MAINTENANCE_TOO_LOW,
    CIV1_REFUSAL_OWNER_NOT_AUTHORIZED,
    CIV1_REFUSAL_CITY_NOT_FOUND,
    CIV1_REFUSAL_NOT_IMPLEMENTED
} civ1_refusal_code;

const char* civ1_refusal_to_string(civ1_refusal_code code);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_RULES_CITY_REFUSAL_CODES_H */
