/*
FILE: include/domino/scale/macro_schedule_store.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / scale
RESPONSIBILITY: Public macro schedule storage contract on d_world.
ALLOWED DEPENDENCIES: include/domino/** plus C89/C++98 standard headers.
FORBIDDEN DEPENDENCIES: source/** private headers; keep contracts freestanding.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: Storage order is deterministic by domain_id.
*/
#ifndef DOMINO_SCALE_MACRO_SCHEDULE_STORE_H
#define DOMINO_SCALE_MACRO_SCHEDULE_STORE_H

#include "domino/core/dom_time_core.h"
#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

struct d_world;
typedef struct d_world d_world;

typedef struct dom_macro_schedule_entry {
    u64 domain_id;
    u64 capsule_id;
    dom_act_time_t last_event_time;
    dom_act_time_t next_event_time;
    dom_act_time_t interval_ticks;
    u64 order_key_seed;
    u32 executed_events;
    u32 narrative_events;
    dom_act_time_t compacted_through_time;
    u32 compaction_count;
} dom_macro_schedule_entry;

int dom_macro_schedule_store_set(d_world* world,
                                 const dom_macro_schedule_entry* entry);

int dom_macro_schedule_store_get(const d_world* world,
                                 u64 domain_id,
                                 dom_macro_schedule_entry* out_entry);

int dom_macro_schedule_store_remove(d_world* world, u64 domain_id);

u32 dom_macro_schedule_store_count(const d_world* world);

int dom_macro_schedule_store_get_by_index(const d_world* world,
                                          u32 index,
                                          dom_macro_schedule_entry* out_entry);

void dom_macro_schedule_store_clear(d_world* world);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINO_SCALE_MACRO_SCHEDULE_STORE_H */
