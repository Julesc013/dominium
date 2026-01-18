/*
FILE: include/dominium/rules/logistics/transport_capacity.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / logistics
RESPONSIBILITY: Defines deterministic transport capacity records.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Capacity updates are deterministic.
*/
#ifndef DOMINIUM_RULES_LOGISTICS_TRANSPORT_CAPACITY_H
#define DOMINIUM_RULES_LOGISTICS_TRANSPORT_CAPACITY_H

#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct transport_capacity {
    u64 capacity_id;
    u32 max_qty;
    u32 available_qty;
} transport_capacity;

typedef struct transport_capacity_registry {
    transport_capacity* capacities;
    u32 count;
    u32 capacity;
} transport_capacity_registry;

void transport_capacity_registry_init(transport_capacity_registry* reg,
                                      transport_capacity* storage,
                                      u32 capacity);
int transport_capacity_register(transport_capacity_registry* reg,
                                u64 capacity_id,
                                u32 max_qty);
transport_capacity* transport_capacity_find(transport_capacity_registry* reg,
                                            u64 capacity_id);
int transport_capacity_reserve(transport_capacity_registry* reg,
                               u64 capacity_id,
                               u32 qty);
int transport_capacity_release(transport_capacity_registry* reg,
                               u64 capacity_id,
                               u32 qty);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_RULES_LOGISTICS_TRANSPORT_CAPACITY_H */
