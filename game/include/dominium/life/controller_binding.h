/*
FILE: include/dominium/life/controller_binding.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / life
RESPONSIBILITY: Defines deterministic controller->person bindings.
ALLOWED DEPENDENCIES: `game/include/**`, `engine/include/**` public headers, and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; product-layer runtime code.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Binding updates must be deterministic.
*/
#ifndef DOMINIUM_LIFE_CONTROLLER_BINDING_H
#define DOMINIUM_LIFE_CONTROLLER_BINDING_H

#include "dominium/life/life_types.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct life_controller_binding {
    u64 controller_id;
    u64 person_id;
} life_controller_binding;

typedef struct life_controller_binding_set {
    life_controller_binding* bindings;
    u32 count;
    u32 capacity;
} life_controller_binding_set;

/* Purpose: Initialize binding storage. */
void life_controller_bindings_init(life_controller_binding_set* set,
                                   life_controller_binding* storage,
                                   u32 capacity);
/* Purpose: Clear bindings (keep storage). */
void life_controller_bindings_clear(life_controller_binding_set* set);
/* Purpose: Set or update a controller binding. */
int life_controller_bindings_set(life_controller_binding_set* set,
                                 u64 controller_id,
                                 u64 person_id);
/* Purpose: Lookup a binding; returns 1 if found. */
int life_controller_bindings_get(const life_controller_binding_set* set,
                                 u64 controller_id,
                                 u64* out_person_id);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_LIFE_CONTROLLER_BINDING_H */
