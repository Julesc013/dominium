/*
FILE: include/domino/scale/macro_event_queue.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / scale
RESPONSIBILITY: Public deterministic macro event queue contract on d_world.
ALLOWED DEPENDENCIES: include/domino/** plus C89/C++98 standard headers.
FORBIDDEN DEPENDENCIES: source/** private headers; keep contracts freestanding.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: Queue ordering is deterministic across platforms.
*/
#ifndef DOMINO_SCALE_MACRO_EVENT_QUEUE_H
#define DOMINO_SCALE_MACRO_EVENT_QUEUE_H

#include "domino/core/dom_time_core.h"
#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

struct d_world;
typedef struct d_world d_world;

typedef struct dom_macro_event_entry {
    u64 event_id;
    u64 domain_id;
    u64 capsule_id;
    dom_act_time_t event_time;
    u64 order_key;
    u64 sequence;
    u32 event_kind;
    u32 flags;
    u32 payload0;
    u32 payload1;
} dom_macro_event_entry;

int dom_macro_event_queue_schedule(d_world* world,
                                   const dom_macro_event_entry* entry);

int dom_macro_event_queue_peek_next(const d_world* world,
                                    dom_macro_event_entry* out_entry);

int dom_macro_event_queue_pop_next(d_world* world,
                                   dom_act_time_t up_to_time,
                                   dom_macro_event_entry* out_entry);

int dom_macro_event_queue_remove_domain(d_world* world, u64 domain_id);

u32 dom_macro_event_queue_count(const d_world* world);

int dom_macro_event_queue_get_by_index(const d_world* world,
                                       u32 index,
                                       dom_macro_event_entry* out_entry);

void dom_macro_event_queue_clear(d_world* world);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINO_SCALE_MACRO_EVENT_QUEUE_H */
