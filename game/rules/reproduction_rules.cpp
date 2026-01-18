/*
FILE: game/rules/reproduction_rules.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Game rules / life reproduction
RESPONSIBILITY: Implements reproduction eligibility rules (bounded).
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Eligibility evaluation must be deterministic.
*/
#include "dominium/rules/reproduction_rules.h"

int life_reproduction_rules_validate(const life_reproduction_rules* rules,
                                     const u64* parent_ids,
                                     u32 parent_count)
{
    u32 i;
    if (!rules || !parent_ids) {
        return 0;
    }
    if (parent_count < rules->min_parents || parent_count > rules->max_parents) {
        return 0;
    }
    for (i = 0u; i < parent_count; ++i) {
        if (parent_ids[i] == 0u && !rules->allow_unknown_parents) {
            return 0;
        }
    }
    return 1;
}
