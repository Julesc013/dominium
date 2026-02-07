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
NOTE: PERMANENT STUB — explicit refusal until CIV1 routing is implemented.
*/
#include "dominium/rules/logistics/routing_stub.h"

int logistics_route_estimate(const logistics_route_params* params,
                             dom_act_time_t* out_duration,
                             u32* out_cost)
{
    civ1_refusal_code refusal = CIV1_REFUSAL_NONE;
    return logistics_route_estimate_ex(params, out_duration, out_cost, &refusal);
}

int logistics_route_estimate_ex(const logistics_route_params* params,
                                dom_act_time_t* out_duration,
                                u32* out_cost,
                                civ1_refusal_code* out_refusal)
{
    (void)params;
    if (out_duration) {
        *out_duration = (dom_act_time_t)0;
    }
    if (out_cost) {
        *out_cost = 0u;
    }
    if (out_refusal) {
        *out_refusal = CIV1_REFUSAL_NOT_IMPLEMENTED;
    }
    return -1;
}
