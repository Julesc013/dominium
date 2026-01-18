/*
FILE: include/dominium/rules/logistics/routing_stub.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / logistics
RESPONSIBILITY: Defines deterministic routing/cost stubs for CIV1.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Routing estimates are deterministic.
*/
#ifndef DOMINIUM_RULES_LOGISTICS_ROUTING_STUB_H
#define DOMINIUM_RULES_LOGISTICS_ROUTING_STUB_H

#include "domino/core/dom_time_core.h"
#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct logistics_route_params {
    u32 distance_units;
    u32 weight_class;
    u32 base_speed;
    u32 base_cost;
} logistics_route_params;

int logistics_route_estimate(const logistics_route_params* params,
                             dom_act_time_t* out_duration,
                             u32* out_cost);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_RULES_LOGISTICS_ROUTING_STUB_H */
