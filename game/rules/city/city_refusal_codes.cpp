/*
FILE: game/rules/city/city_refusal_codes.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Game / city rules
RESPONSIBILITY: Implements refusal code string conversion.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Refusal codes are stable and deterministic.
*/
#include "dominium/rules/city/city_refusal_codes.h"

const char* civ1_refusal_to_string(civ1_refusal_code code)
{
    switch (code) {
        case CIV1_REFUSAL_NONE: return "none";
        case CIV1_REFUSAL_INSUFFICIENT_INPUTS: return "insufficient_inputs";
        case CIV1_REFUSAL_CAPACITY_UNAVAILABLE: return "capacity_unavailable";
        case CIV1_REFUSAL_MAINTENANCE_TOO_LOW: return "maintenance_too_low";
        case CIV1_REFUSAL_OWNER_NOT_AUTHORIZED: return "owner_not_authorized";
        case CIV1_REFUSAL_CITY_NOT_FOUND: return "city_not_found";
        case CIV1_REFUSAL_NOT_IMPLEMENTED: return "not_implemented";
        default: return "unknown";
    }
}
