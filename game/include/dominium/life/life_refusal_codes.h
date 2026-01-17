/*
FILE: include/dominium/life/life_refusal_codes.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / life
RESPONSIBILITY: Defines refusal codes for LIFE2 death/estate pipeline.
ALLOWED DEPENDENCIES: `game/include/**`, `engine/include/**` public headers, and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; product-layer runtime code.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Refusal codes are stable and deterministic.
*/
#ifndef DOMINIUM_LIFE_REFUSAL_CODES_H
#define DOMINIUM_LIFE_REFUSAL_CODES_H

#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum life_death_refusal_code {
    LIFE_DEATH_REFUSAL_NONE = 0,
    LIFE_DEATH_REFUSAL_BODY_NOT_ALIVE,
    LIFE_DEATH_REFUSAL_PERSON_MISSING,
    LIFE_DEATH_REFUSAL_LEDGER_ACCOUNT_MISSING,
    LIFE_DEATH_REFUSAL_ESTATE_ALREADY_EXISTS,
    LIFE_DEATH_REFUSAL_NO_EXECUTOR_AUTHORITY,
    LIFE_DEATH_REFUSAL_SCHEDULE_INVALID
} life_death_refusal_code;

const char* life_death_refusal_to_string(life_death_refusal_code code);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_LIFE_REFUSAL_CODES_H */
