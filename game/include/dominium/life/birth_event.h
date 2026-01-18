/*
FILE: include/dominium/life/birth_event.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / life
RESPONSIBILITY: Defines birth event records and append-only storage.
ALLOWED DEPENDENCIES: `game/include/**`, `engine/include/**` public headers, and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; product-layer runtime code.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Append-only ordering must be deterministic.
*/
#ifndef DOMINIUM_LIFE_BIRTH_EVENT_H
#define DOMINIUM_LIFE_BIRTH_EVENT_H

#include "domino/core/dom_time_core.h"
#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct life_birth_event {
    u64 birth_event_id;
    u64 child_person_id;
    u64 parent_ids[2];
    u32 parent_count;
    dom_act_time_t act_time_of_birth;
    u64 location_ref;
    u64 provenance_ref;
} life_birth_event;

typedef struct life_birth_event_list {
    life_birth_event* events;
    u32 count;
    u32 capacity;
    u64 next_id;
} life_birth_event_list;

void life_birth_event_list_init(life_birth_event_list* list,
                                life_birth_event* storage,
                                u32 capacity,
                                u64 start_id);
int life_birth_event_append(life_birth_event_list* list,
                            const life_birth_event* event,
                            u64* out_id);
const life_birth_event* life_birth_event_find(const life_birth_event_list* list,
                                              u64 birth_event_id);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_LIFE_BIRTH_EVENT_H */
