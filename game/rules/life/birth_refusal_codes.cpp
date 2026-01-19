/*
FILE: game/core/life/birth_refusal_codes.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Game / life
RESPONSIBILITY: Provides string names for birth refusal codes.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: String mapping is stable.
*/
#include "dominium/life/birth_refusal_codes.h"

const char* life_birth_refusal_to_string(life_birth_refusal_code code)
{
    switch (code) {
        case LIFE_BIRTH_REFUSAL_NONE: return "none";
        case LIFE_BIRTH_REFUSAL_INELIGIBLE_PARENTS: return "ineligible_parents";
        case LIFE_BIRTH_REFUSAL_INSUFFICIENT_RESOURCES: return "insufficient_resources";
        case LIFE_BIRTH_REFUSAL_INSUFFICIENT_AUTHORITY: return "insufficient_authority";
        case LIFE_BIRTH_REFUSAL_GESTATION_ALREADY_ACTIVE: return "gestation_already_active";
        case LIFE_BIRTH_REFUSAL_POLICY_DISALLOWS_BIRTH: return "policy_disallows_birth";
        default: return "unknown";
    }
}
