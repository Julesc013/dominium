/*
FILE: game/rules/city/city_services_stub.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Game / city rules
RESPONSIBILITY: Implements minimal city services hooks (water, waste, power).
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Service checks are deterministic.
NOTE: PERMANENT STUB — explicit refusal until CIV1 services are implemented.
*/
#include "dominium/rules/city/city_services_stub.h"

int city_services_available(const city_service_state* state)
{
    civ1_refusal_code refusal = CIV1_REFUSAL_NONE;
    (void)city_services_available_ex(state, &refusal);
    return 0;
}

int city_services_available_ex(const city_service_state* state,
                               civ1_refusal_code* out_refusal)
{
    (void)state;
    if (out_refusal) {
        *out_refusal = CIV1_REFUSAL_NOT_IMPLEMENTED;
    }
    return 0;
}
