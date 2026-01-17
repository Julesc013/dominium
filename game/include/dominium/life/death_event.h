/*
FILE: include/dominium/life/death_event.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / life
RESPONSIBILITY: Defines death event records and append-only storage.
ALLOWED DEPENDENCIES: `game/include/**`, `engine/include/**` public headers, and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; product-layer runtime code.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Append-only ordering must be deterministic.
*/
#ifndef DOMINIUM_LIFE_DEATH_EVENT_H
#define DOMINIUM_LIFE_DEATH_EVENT_H

#include "domino/core/dom_time_core.h"
#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum life_death_cause_code {
    LIFE_DEATH_CAUSE_NATURAL = 1,
    LIFE_DEATH_CAUSE_ACCIDENT = 2,
    LIFE_DEATH_CAUSE_VIOLENCE = 3,
    LIFE_DEATH_CAUSE_EXECUTION = 4,
    LIFE_DEATH_CAUSE_UNKNOWN = 5,
    LIFE_DEATH_CAUSE_MISSING_DECLARED = 6
} life_death_cause_code;

typedef struct life_death_event {
    u64 death_event_id;
    u64 body_id;
    u64 person_id;
    u32 cause_code;
    dom_act_time_t act_time_of_death;
    u64 location_ref;
    u64 provenance_ref;
    u64 estate_id;
} life_death_event;

typedef struct life_death_event_list {
    life_death_event* events;
    u32 count;
    u32 capacity;
    u64 next_id;
} life_death_event_list;

void life_death_event_list_init(life_death_event_list* list,
                                life_death_event* storage,
                                u32 capacity,
                                u64 start_id);
int life_death_event_append(life_death_event_list* list,
                            const life_death_event* event,
                            u64* out_id);
const life_death_event* life_death_event_find(const life_death_event_list* list,
                                              u64 death_event_id);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_LIFE_DEATH_EVENT_H */
