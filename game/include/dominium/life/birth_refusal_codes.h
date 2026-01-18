/*
FILE: include/dominium/life/birth_refusal_codes.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / life
RESPONSIBILITY: Defines refusal codes for LIFE3 birth pipeline.
ALLOWED DEPENDENCIES: `game/include/**`, `engine/include/**` public headers, and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; product-layer runtime code.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Refusal codes are stable and deterministic.
*/
#ifndef DOMINIUM_LIFE_BIRTH_REFUSAL_CODES_H
#define DOMINIUM_LIFE_BIRTH_REFUSAL_CODES_H

#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum life_birth_refusal_code {
    LIFE_BIRTH_REFUSAL_NONE = 0,
    LIFE_BIRTH_REFUSAL_INELIGIBLE_PARENTS,
    LIFE_BIRTH_REFUSAL_INSUFFICIENT_RESOURCES,
    LIFE_BIRTH_REFUSAL_INSUFFICIENT_AUTHORITY,
    LIFE_BIRTH_REFUSAL_GESTATION_ALREADY_ACTIVE,
    LIFE_BIRTH_REFUSAL_POLICY_DISALLOWS_BIRTH
} life_birth_refusal_code;

const char* life_birth_refusal_to_string(life_birth_refusal_code code);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_LIFE_BIRTH_REFUSAL_CODES_H */
