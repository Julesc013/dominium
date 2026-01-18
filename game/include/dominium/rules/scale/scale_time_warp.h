/*
FILE: include/dominium/rules/scale/scale_time_warp.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / scale
RESPONSIBILITY: Defines deterministic scale-aware time warp policies.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Warp resolution is deterministic and integer-based.
*/
#ifndef DOMINIUM_RULES_SCALE_TIME_WARP_H
#define DOMINIUM_RULES_SCALE_TIME_WARP_H

#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct scale_time_warp_policy {
    u64 policy_id;
    u64 domain_id;
    u32 min_warp;
    u32 max_warp;
    u32 interest_cap;
} scale_time_warp_policy;

typedef struct scale_time_warp_registry {
    scale_time_warp_policy* policies;
    u32 count;
    u32 capacity;
} scale_time_warp_registry;

void scale_time_warp_registry_init(scale_time_warp_registry* reg,
                                   scale_time_warp_policy* storage,
                                   u32 capacity);
int scale_time_warp_register(scale_time_warp_registry* reg,
                             u64 policy_id,
                             u64 domain_id,
                             u32 min_warp,
                             u32 max_warp,
                             u32 interest_cap);
scale_time_warp_policy* scale_time_warp_find(scale_time_warp_registry* reg,
                                             u64 policy_id);
scale_time_warp_policy* scale_time_warp_find_domain(scale_time_warp_registry* reg,
                                                    u64 domain_id);
u32 scale_time_warp_resolve(const scale_time_warp_policy* policy,
                            u32 requested_warp,
                            int has_interest);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_RULES_SCALE_TIME_WARP_H */
