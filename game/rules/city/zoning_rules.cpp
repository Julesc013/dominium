/*
FILE: game/rules/city/zoning_rules.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Game / city rules
RESPONSIBILITY: Implements zoning rule stubs for CIV1.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Zoning checks are deterministic.
*/
#include "dominium/rules/city/zoning_rules.h"

int city_zone_allows_building(const city_zone_policy* policy, u64 building_type_id)
{
    u32 i;
    if (!policy) {
        return 1;
    }
    if (policy->allowed_count == 0u) {
        return 1;
    }
    for (i = 0u; i < policy->allowed_count; ++i) {
        if (policy->allowed_type_ids[i] == building_type_id) {
            return 1;
        }
    }
    return 0;
}
