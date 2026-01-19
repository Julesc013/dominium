/*
FILE: game/core/life/birth_event.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Game / life
RESPONSIBILITY: Implements birth event append-only storage.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Append-only ordering is deterministic.
*/
#include "dominium/life/birth_event.h"

#include <string.h>

void life_birth_event_list_init(life_birth_event_list* list,
                                life_birth_event* storage,
                                u32 capacity,
                                u64 start_id)
{
    if (!list) {
        return;
    }
    list->events = storage;
    list->count = 0u;
    list->capacity = capacity;
    list->next_id = start_id ? start_id : 1u;
    if (storage && capacity > 0u) {
        memset(storage, 0, sizeof(life_birth_event) * (size_t)capacity);
    }
}

int life_birth_event_append(life_birth_event_list* list,
                            const life_birth_event* event,
                            u64* out_id)
{
    life_birth_event* slot;
    if (!list || !event || !list->events) {
        return -1;
    }
    if (list->count >= list->capacity) {
        return -2;
    }
    slot = &list->events[list->count++];
    *slot = *event;
    slot->birth_event_id = list->next_id++;
    if (out_id) {
        *out_id = slot->birth_event_id;
    }
    return 0;
}

const life_birth_event* life_birth_event_find(const life_birth_event_list* list,
                                              u64 birth_event_id)
{
    u32 i;
    if (!list || !list->events) {
        return 0;
    }
    for (i = 0u; i < list->count; ++i) {
        if (list->events[i].birth_event_id == birth_event_id) {
            return &list->events[i];
        }
    }
    return 0;
}
