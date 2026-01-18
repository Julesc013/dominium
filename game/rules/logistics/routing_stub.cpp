/*
FILE: game/rules/logistics/routing_stub.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Game / logistics
RESPONSIBILITY: Implements deterministic routing/cost stubs for CIV1.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Routing estimates are deterministic.
*/
#include "dominium/rules/logistics/routing_stub.h"

int logistics_route_estimate(const logistics_route_params* params,
                             dom_act_time_t* out_duration,
                             u32* out_cost)
{
    u32 speed;
    u32 duration;
    u32 cost;
    if (!params) {
        return -1;
    }
    speed = (params->base_speed == 0u) ? 1u : params->base_speed;
    duration = params->distance_units / speed;
    if (duration == 0u) {
        duration = 1u;
    }
    cost = params->distance_units * (params->weight_class + 1u);
    cost = cost * (params->base_cost == 0u ? 1u : params->base_cost);
    if (out_duration) {
        *out_duration = (dom_act_time_t)duration;
    }
    if (out_cost) {
        *out_cost = cost;
    }
    return 0;
}
