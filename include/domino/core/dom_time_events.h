/*
FILE: include/domino/core/dom_time_events.h
MODULE: Domino
RESPONSIBILITY: Deterministic time event queue (engine-side scheduling only).
NOTES: Pure C90 header; no gameplay logic, no event interpretation.
*/
#ifndef DOMINO_CORE_DOM_TIME_EVENTS_H
#define DOMINO_CORE_DOM_TIME_EVENTS_H

#include "domino/core/dom_time_core.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dom_time_event {
    dom_time_event_id event_id;
    dom_act_time_t trigger_time;
    u64 order_key;
    u64 payload_id;
} dom_time_event;

typedef struct dom_time_event_queue {
    dom_time_event *items;
    u32 capacity;
    u32 count;
} dom_time_event_queue;

typedef struct dom_time_event_id_gen {
    dom_time_event_id next_id;
} dom_time_event_id_gen;

typedef int (*dom_time_event_cb)(void *user, const dom_time_event *ev);

int dom_time_event_queue_init(dom_time_event_queue *q, dom_time_event *storage, u32 capacity);
int dom_time_event_queue_size(const dom_time_event_queue *q, u32 *out_count);

int dom_time_event_schedule(dom_time_event_queue *q, const dom_time_event *ev);
int dom_time_event_cancel(dom_time_event_queue *q, dom_time_event_id event_id);

int dom_time_event_peek(const dom_time_event_queue *q, dom_time_event *out_ev);
int dom_time_event_pop(dom_time_event_queue *q, dom_time_event *out_ev);

int dom_time_event_id_init(dom_time_event_id_gen *gen, dom_time_event_id start_id);
int dom_time_event_id_next(dom_time_event_id_gen *gen, dom_time_event_id *out_id);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINO_CORE_DOM_TIME_EVENTS_H */
