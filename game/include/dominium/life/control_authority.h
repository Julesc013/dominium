/*
FILE: include/dominium/life/control_authority.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / life
RESPONSIBILITY: Defines control authority records and evaluation for LIFE continuation.
ALLOWED DEPENDENCIES: `game/include/**`, `engine/include/**` public headers, and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; product-layer runtime code.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Deterministic evaluation order required.
*/
#ifndef DOMINIUM_LIFE_CONTROL_AUTHORITY_H
#define DOMINIUM_LIFE_CONTROL_AUTHORITY_H

#include "dominium/life/life_types.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct life_authority_record {
    u64 controller_id;
    u64 target_person_id;
    u32 source;
} life_authority_record;

typedef struct life_authority_set {
    const life_authority_record* records;
    u32 count;
} life_authority_set;

/* Purpose: Determine whether a controller can control a person. */
int life_authority_can_control(const life_authority_set* set,
                               u64 controller_id,
                               u64 target_person_id,
                               life_authority_source* out_source);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_LIFE_CONTROL_AUTHORITY_H */
