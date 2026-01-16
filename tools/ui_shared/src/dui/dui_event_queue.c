/*
FILE: source/domino/dui/dui_event_queue.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / dui/event_queue
RESPONSIBILITY: Implements internal fixed-capacity event queue for DUI backends.
ALLOWED DEPENDENCIES: `include/dui/**`, `include/domino/**`, and C89/C++98 standard headers.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**`.
THREADING MODEL: No internal synchronization; one thread drives UI.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Presentation-only; stable FIFO ordering.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal).
EXTENSION POINTS: N/A.
*/
#include "dui_event_queue.h"

void dui_event_queue_init(dui_event_queue* q)
{
    if (!q) {
        return;
    }
    q->head = 0u;
    q->tail = 0u;
    q->count = 0u;
}

int dui_event_queue_push(dui_event_queue* q, const dui_event_v1* ev)
{
    if (!q || !ev) {
        return -1;
    }
    if (q->count >= (u32)DUI_EVENT_QUEUE_CAP) {
        return -2;
    }
    q->ev[q->tail] = *ev;
    q->tail = (q->tail + 1u) % (u32)DUI_EVENT_QUEUE_CAP;
    q->count += 1u;
    return 0;
}

int dui_event_queue_pop(dui_event_queue* q, dui_event_v1* out_ev)
{
    if (!q || !out_ev) {
        return -1;
    }
    if (q->count == 0u) {
        return 0;
    }
    *out_ev = q->ev[q->head];
    q->head = (q->head + 1u) % (u32)DUI_EVENT_QUEUE_CAP;
    q->count -= 1u;
    return 1;
}

