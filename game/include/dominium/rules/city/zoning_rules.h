/*
FILE: include/dominium/rules/city/zoning_rules.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / city rules
RESPONSIBILITY: Defines zoning rule stubs for CIV1.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Zoning checks are deterministic.
*/
#ifndef DOMINIUM_RULES_CITY_ZONING_RULES_H
#define DOMINIUM_RULES_CITY_ZONING_RULES_H

#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

#define CITY_MAX_ZONE_TYPES 16u

typedef struct city_zone_policy {
    u64 zone_id;
    u64 allowed_type_ids[CITY_MAX_ZONE_TYPES];
    u32 allowed_count;
} city_zone_policy;

int city_zone_allows_building(const city_zone_policy* policy, u64 building_type_id);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_RULES_CITY_ZONING_RULES_H */
