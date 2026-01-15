/*
FILE: source/domino/core/dom_time_events.c
MODULE: Domino
RESPONSIBILITY: Deterministic time event queue (engine-side scheduling only).
*/
#include "domino/core/dom_time_events.h"

static int dom_time_event_less(const dom_time_event *a, const dom_time_event *b) {
    if (a->trigger_time < b->trigger_time) {
        return 1;
    }
    if (a->trigger_time > b->trigger_time) {
        return 0;
    }
    if (a->order_key < b->order_key) {
        return 1;
    }
    if (a->order_key > b->order_key) {
        return 0;
    }
    return (a->event_id < b->event_id) ? 1 : 0;
}

static void dom_time_event_swap(dom_time_event *a, dom_time_event *b) {
    dom_time_event tmp = *a;
    *a = *b;
    *b = tmp;
}

static void dom_time_heapify_up(dom_time_event_queue *q, u32 idx) {
    while (idx > 0u) {
        u32 parent = (idx - 1u) / 2u;
        if (!dom_time_event_less(&q->items[idx], &q->items[parent])) {
            break;
        }
        dom_time_event_swap(&q->items[idx], &q->items[parent]);
        idx = parent;
    }
}

static void dom_time_heapify_down(dom_time_event_queue *q, u32 idx) {
    u32 count = q->count;
    while (1) {
        u32 left = (idx * 2u) + 1u;
        u32 right = left + 1u;
        u32 smallest = idx;

        if (left < count && dom_time_event_less(&q->items[left], &q->items[smallest])) {
            smallest = left;
        }
        if (right < count && dom_time_event_less(&q->items[right], &q->items[smallest])) {
            smallest = right;
        }
        if (smallest == idx) {
            break;
        }
        dom_time_event_swap(&q->items[idx], &q->items[smallest]);
        idx = smallest;
    }
}

int dom_time_event_queue_init(dom_time_event_queue *q, dom_time_event *storage, u32 capacity) {
    if (!q || !storage || capacity == 0u) {
        return DOM_TIME_INVALID;
    }
    q->items = storage;
    q->capacity = capacity;
    q->count = 0u;
    return DOM_TIME_OK;
}

int dom_time_event_queue_size(const dom_time_event_queue *q, u32 *out_count) {
    if (!q || !out_count) {
        return DOM_TIME_INVALID;
    }
    *out_count = q->count;
    return DOM_TIME_OK;
}

int dom_time_event_schedule(dom_time_event_queue *q, const dom_time_event *ev) {
    if (!q || !ev) {
        return DOM_TIME_INVALID;
    }
    if (q->count >= q->capacity) {
        return DOM_TIME_FULL;
    }
    q->items[q->count] = *ev;
    dom_time_heapify_up(q, q->count);
    q->count += 1u;
    return DOM_TIME_OK;
}

int dom_time_event_cancel(dom_time_event_queue *q, dom_time_event_id event_id) {
    u32 i;
    if (!q) {
        return DOM_TIME_INVALID;
    }
    for (i = 0u; i < q->count; ++i) {
        if (q->items[i].event_id == event_id) {
            q->count -= 1u;
            if (i != q->count) {
                q->items[i] = q->items[q->count];
                if (i > 0u && dom_time_event_less(&q->items[i], &q->items[(i - 1u) / 2u])) {
                    dom_time_heapify_up(q, i);
                } else {
                    dom_time_heapify_down(q, i);
                }
            }
            return DOM_TIME_OK;
        }
    }
    return DOM_TIME_NOT_FOUND;
}

int dom_time_event_peek(const dom_time_event_queue *q, dom_time_event *out_ev) {
    if (!q || !out_ev) {
        return DOM_TIME_INVALID;
    }
    if (q->count == 0u) {
        return DOM_TIME_EMPTY;
    }
    *out_ev = q->items[0u];
    return DOM_TIME_OK;
}

int dom_time_event_pop(dom_time_event_queue *q, dom_time_event *out_ev) {
    if (!q || !out_ev) {
        return DOM_TIME_INVALID;
    }
    if (q->count == 0u) {
        return DOM_TIME_EMPTY;
    }
    *out_ev = q->items[0u];
    q->count -= 1u;
    if (q->count > 0u) {
        q->items[0u] = q->items[q->count];
        dom_time_heapify_down(q, 0u);
    }
    return DOM_TIME_OK;
}

int dom_time_event_next_time(const dom_time_event_queue *q, dom_act_time_t *out_time) {
    if (!q || !out_time) {
        return DOM_TIME_INVALID;
    }
    if (q->count == 0u) {
        return DOM_TIME_EMPTY;
    }
    *out_time = q->items[0u].trigger_time;
    return DOM_TIME_OK;
}

int dom_time_process_until(dom_time_event_queue *q, dom_act_time_t target_act, dom_time_event_cb cb, void *user) {
    dom_time_event ev;
    int rc;
    if (!q || !cb) {
        return DOM_TIME_INVALID;
    }
    while (q->count > 0u) {
        rc = dom_time_event_peek(q, &ev);
        if (rc != DOM_TIME_OK) {
            return rc;
        }
        if (ev.trigger_time > target_act) {
            break;
        }
        rc = dom_time_event_pop(q, &ev);
        if (rc != DOM_TIME_OK) {
            return rc;
        }
        rc = cb(user, &ev);
        if (rc != DOM_TIME_OK) {
            return rc;
        }
    }
    return DOM_TIME_OK;
}

int dom_time_event_id_init(dom_time_event_id_gen *gen, dom_time_event_id start_id) {
    if (!gen) {
        return DOM_TIME_INVALID;
    }
    gen->next_id = (start_id == 0u) ? 1u : start_id;
    return DOM_TIME_OK;
}

int dom_time_event_id_next(dom_time_event_id_gen *gen, dom_time_event_id *out_id) {
    if (!gen || !out_id) {
        return DOM_TIME_INVALID;
    }
    if (gen->next_id == 0u) {
        return DOM_TIME_OVERFLOW;
    }
    *out_id = gen->next_id;
    gen->next_id += 1u;
    if (gen->next_id == 0u) {
        return DOM_TIME_OVERFLOW;
    }
    return DOM_TIME_OK;
}
