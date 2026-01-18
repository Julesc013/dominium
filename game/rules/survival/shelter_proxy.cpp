/*
FILE: game/rules/survival/shelter_proxy.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Game / survival rules
RESPONSIBILITY: Implements minimal shelter proxy helpers.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Shelter adjustments are deterministic.
*/
#include "dominium/rules/survival/shelter_proxy.h"

u32 survival_shelter_clamp(u32 level, u32 max_level)
{
    if (level > max_level) {
        return max_level;
    }
    return level;
}

u32 survival_shelter_apply(u32 current_level, u32 delta, u32 max_level)
{
    u32 next = current_level + delta;
    if (next < current_level) {
        next = max_level;
    }
    return survival_shelter_clamp(next, max_level);
}
