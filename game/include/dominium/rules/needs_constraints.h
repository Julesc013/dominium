/*
FILE: include/dominium/rules/needs_constraints.h
MODULE: Dominium
LAYER / SUBSYSTEM: Game rules / life needs
RESPONSIBILITY: Defines minimal resource constraint checks for birth.
ALLOWED DEPENDENCIES: `game/include/**`, `engine/include/**` public headers, and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; product-layer runtime code.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Resource checks must be deterministic.
*/
#ifndef DOMINIUM_RULES_NEEDS_CONSTRAINTS_H
#define DOMINIUM_RULES_NEEDS_CONSTRAINTS_H

#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct life_need_snapshot {
    u8 has_food;
    u8 has_shelter;
} life_need_snapshot;

int life_needs_constraints_ok(const life_need_snapshot* needs);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_RULES_NEEDS_CONSTRAINTS_H */
