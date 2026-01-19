/*
FILE: game/core/life/controller_binding.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Game / life
RESPONSIBILITY: Implements deterministic controller bindings.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Binding order is stable and deterministic.
*/
#include "dominium/life/controller_binding.h"

#include <string.h>

void life_controller_bindings_init(life_controller_binding_set* set,
                                   life_controller_binding* storage,
                                   u32 capacity)
{
    if (!set) {
        return;
    }
    set->bindings = storage;
    set->count = 0u;
    set->capacity = capacity;
    if (storage && capacity > 0u) {
        memset(storage, 0, sizeof(life_controller_binding) * (size_t)capacity);
    }
}

void life_controller_bindings_clear(life_controller_binding_set* set)
{
    if (!set) {
        return;
    }
    set->count = 0u;
}

static u32 life_binding_find_index(const life_controller_binding_set* set,
                                   u64 controller_id,
                                   int* out_found)
{
    u32 i;
    if (out_found) {
        *out_found = 0;
    }
    if (!set || !set->bindings) {
        return 0u;
    }
    for (i = 0u; i < set->count; ++i) {
        if (set->bindings[i].controller_id == controller_id) {
            if (out_found) {
                *out_found = 1;
            }
            return i;
        }
        if (set->bindings[i].controller_id > controller_id) {
            break;
        }
    }
    return i;
}

int life_controller_bindings_set(life_controller_binding_set* set,
                                 u64 controller_id,
                                 u64 person_id)
{
    int found = 0;
    u32 index;
    u32 i;

    if (!set || !set->bindings) {
        return -1;
    }
    index = life_binding_find_index(set, controller_id, &found);
    if (found) {
        set->bindings[index].person_id = person_id;
        return 0;
    }
    if (set->count >= set->capacity) {
        return -2;
    }
    for (i = set->count; i > index; --i) {
        set->bindings[i] = set->bindings[i - 1u];
    }
    set->bindings[index].controller_id = controller_id;
    set->bindings[index].person_id = person_id;
    set->count += 1u;
    return 0;
}

int life_controller_bindings_get(const life_controller_binding_set* set,
                                 u64 controller_id,
                                 u64* out_person_id)
{
    int found = 0;
    u32 index;
    if (!set || !set->bindings) {
        return 0;
    }
    index = life_binding_find_index(set, controller_id, &found);
    if (!found) {
        return 0;
    }
    if (out_person_id) {
        *out_person_id = set->bindings[index].person_id;
    }
    return 1;
}
