/*
FILE: include/dominium/rules/governance/enforcement_capacity.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / governance
RESPONSIBILITY: Defines enforcement capacity records and registries.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Capacity ordering is stable and deterministic.
*/
#ifndef DOMINIUM_RULES_GOVERNANCE_ENFORCEMENT_CAPACITY_H
#define DOMINIUM_RULES_GOVERNANCE_ENFORCEMENT_CAPACITY_H

#include "domino/core/dom_time_core.h"
#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct enforcement_capacity {
    u64 capacity_id;
    u32 available_enforcers;
    u32 coverage_area;
    dom_act_time_t response_time;
    u64 cost_ref;
} enforcement_capacity;

typedef struct enforcement_capacity_registry {
    enforcement_capacity* capacities;
    u32 count;
    u32 capacity;
} enforcement_capacity_registry;

void enforcement_capacity_registry_init(enforcement_capacity_registry* reg,
                                        enforcement_capacity* storage,
                                        u32 capacity);
int enforcement_capacity_register(enforcement_capacity_registry* reg,
                                  u64 capacity_id,
                                  u32 enforcers,
                                  u32 coverage_area,
                                  dom_act_time_t response_time,
                                  u64 cost_ref);
enforcement_capacity* enforcement_capacity_find(enforcement_capacity_registry* reg,
                                                u64 capacity_id);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_RULES_GOVERNANCE_ENFORCEMENT_CAPACITY_H */
