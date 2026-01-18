/*
FILE: include/dominium/rules/city/city_services_stub.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / city rules
RESPONSIBILITY: Defines minimal city services hooks (water, waste, power).
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Service checks are deterministic.
*/
#ifndef DOMINIUM_RULES_CITY_SERVICES_STUB_H
#define DOMINIUM_RULES_CITY_SERVICES_STUB_H

#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct city_service_state {
    u32 water_ok;
    u32 power_ok;
    u32 waste_ok;
} city_service_state;

int city_services_available(const city_service_state* state);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_RULES_CITY_SERVICES_STUB_H */
