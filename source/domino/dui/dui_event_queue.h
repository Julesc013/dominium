/*
FILE: source/domino/dui/dui_event_queue.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / dui/event_queue
RESPONSIBILITY: Internal fixed-capacity event queue for DUI backends (no allocations).
ALLOWED DEPENDENCIES: `include/dui/**`, `include/domino/**`, and C89/C++98 standard headers.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**`.
THREADING MODEL: No internal synchronization; one thread drives UI.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Presentation-only; event ordering is stable for a given backend input stream.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal).
EXTENSION POINTS: Increase capacity if needed (must remain bounded).
*/
#ifndef DOMINO_DUI_EVENT_QUEUE_H
#define DOMINO_DUI_EVENT_QUEUE_H

#include "dui/dui_api_v1.h"

#ifdef __cplusplus
extern "C" {
#endif

#define DUI_EVENT_QUEUE_CAP 64u

typedef struct dui_event_queue {
    u32 head;
    u32 tail;
    u32 count;
    dui_event_v1 ev[DUI_EVENT_QUEUE_CAP];
} dui_event_queue;

void dui_event_queue_init(dui_event_queue* q);
int  dui_event_queue_push(dui_event_queue* q, const dui_event_v1* ev);
int  dui_event_queue_pop(dui_event_queue* q, dui_event_v1* out_ev);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINO_DUI_EVENT_QUEUE_H */

