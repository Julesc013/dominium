/*
FILE: game/rules/needs_constraints.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Game rules / life needs
RESPONSIBILITY: Implements minimal resource constraint checks for birth.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Resource checks must be deterministic.
*/
#include "dominium/rules/needs_constraints.h"

int life_needs_constraints_ok(const life_need_snapshot* needs)
{
    if (!needs) {
        return 0;
    }
    if (!needs->has_food) {
        return 0;
    }
    if (!needs->has_shelter) {
        return 0;
    }
    return 1;
}
