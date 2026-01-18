/*
FILE: include/dominium/rules/scale/scale_interest_binding.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / scale
RESPONSIBILITY: Defines deterministic interest bindings across scale domains.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Interest ordering and checks are deterministic.
*/
#ifndef DOMINIUM_RULES_SCALE_INTEREST_BINDING_H
#define DOMINIUM_RULES_SCALE_INTEREST_BINDING_H

#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct scale_interest_binding {
    u64 binding_id;
    u64 domain_id;
    u64 object_id;
    u32 strength;
    u32 pinned;
} scale_interest_binding;

typedef struct scale_interest_registry {
    scale_interest_binding* bindings;
    u32 count;
    u32 capacity;
} scale_interest_registry;

void scale_interest_registry_init(scale_interest_registry* reg,
                                  scale_interest_binding* storage,
                                  u32 capacity);
int scale_interest_register(scale_interest_registry* reg,
                            u64 binding_id,
                            u64 domain_id,
                            u64 object_id,
                            u32 strength,
                            u32 pinned);
scale_interest_binding* scale_interest_find(scale_interest_registry* reg,
                                            u64 binding_id);
int scale_interest_set_strength(scale_interest_registry* reg,
                                u64 binding_id,
                                u32 strength);
int scale_interest_set_pinned(scale_interest_registry* reg,
                              u64 binding_id,
                              u32 pinned);
int scale_interest_domain_active(const scale_interest_registry* reg,
                                 u64 domain_id,
                                 u32 threshold);
int scale_interest_should_refine(const scale_interest_registry* reg,
                                 u64 domain_id,
                                 u32 threshold);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_RULES_SCALE_INTEREST_BINDING_H */
