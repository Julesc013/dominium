/*
FILE: game/core/life/death_event.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Game / life
RESPONSIBILITY: Implements death event append-only storage.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Append-only ordering is deterministic.
*/
#include "dominium/life/death_event.h"

#include <string.h>

void life_death_event_list_init(life_death_event_list* list,
                                life_death_event* storage,
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
        memset(storage, 0, sizeof(life_death_event) * (size_t)capacity);
    }
}

int life_death_event_append(life_death_event_list* list,
                            const life_death_event* event,
                            u64* out_id)
{
    life_death_event* slot;
    if (!list || !event || !list->events) {
        return -1;
    }
    if (list->count >= list->capacity) {
        return -2;
    }
    slot = &list->events[list->count++];
    *slot = *event;
    slot->death_event_id = list->next_id++;
    if (out_id) {
        *out_id = slot->death_event_id;
    }
    return 0;
}

const life_death_event* life_death_event_find(const life_death_event_list* list,
                                              u64 death_event_id)
{
    u32 i;
    if (!list || !list->events) {
        return 0;
    }
    for (i = 0u; i < list->count; ++i) {
        if (list->events[i].death_event_id == death_event_id) {
            return &list->events[i];
        }
    }
    return 0;
}
