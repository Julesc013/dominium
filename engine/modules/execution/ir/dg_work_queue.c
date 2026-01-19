/*
FILE: source/domino/execution/ir/dg_work_queue.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / execution/ir/dg_work_queue
RESPONSIBILITY: Implements `dg_work_queue`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include <stdlib.h>
#include <string.h>

#include "execution/ir/dg_work_queue.h"

#include "core/det_invariants.h"

static d_bool dg_work_queue_is_sorted(const dg_work_queue *q) {
    u32 i;
    if (!q || !q->items || q->count < 2u) {
        return D_TRUE;
    }
    for (i = 1u; i < q->count; ++i) {
        if (dg_order_key_cmp(&q->items[i - 1u].key, &q->items[i].key) > 0) {
            return D_FALSE;
        }
    }
    return D_TRUE;
}

void dg_work_queue_init(dg_work_queue *q) {
    if (!q) {
        return;
    }
    q->items = (dg_work_item *)0;
    q->count = 0u;
    q->capacity = 0u;
    q->owns_storage = D_FALSE;
    q->probe_refused = 0u;
}

void dg_work_queue_free(dg_work_queue *q) {
    if (!q) {
        return;
    }
    if (q->owns_storage && q->items) {
        free(q->items);
    }
    dg_work_queue_init(q);
}

int dg_work_queue_reserve(dg_work_queue *q, u32 capacity) {
    dg_work_item *items;
    if (!q) {
        return -1;
    }
    dg_work_queue_free(q);
    if (capacity == 0u) {
        return 0;
    }
    items = (dg_work_item *)malloc(sizeof(dg_work_item) * (size_t)capacity);
    if (!items) {
        return -2;
    }
    memset(items, 0, sizeof(dg_work_item) * (size_t)capacity);
    q->items = items;
    q->capacity = capacity;
    q->count = 0u;
    q->owns_storage = D_TRUE;
    q->probe_refused = 0u;
    return 0;
}

int dg_work_queue_use_storage(dg_work_queue *q, dg_work_item *storage, u32 capacity) {
    if (!q) {
        return -1;
    }
    dg_work_queue_free(q);
    if (capacity != 0u && !storage) {
        return -2;
    }
    q->items = storage;
    q->capacity = capacity;
    q->count = 0u;
    q->owns_storage = D_FALSE;
    q->probe_refused = 0u;
    return 0;
}

void dg_work_queue_clear(dg_work_queue *q) {
    if (!q) {
        return;
    }
    q->count = 0u;
}

u32 dg_work_queue_count(const dg_work_queue *q) {
    return q ? q->count : 0u;
}

u32 dg_work_queue_capacity(const dg_work_queue *q) {
    return q ? q->capacity : 0u;
}

u32 dg_work_queue_probe_refused(const dg_work_queue *q) {
    return q ? q->probe_refused : 0u;
}

static u32 dg_work_queue_upper_bound(const dg_work_queue *q, const dg_order_key *key) {
    u32 lo = 0u;
    u32 hi;
    u32 mid;

    if (!q || !key) {
        return 0u;
    }
    hi = q->count;
    while (lo < hi) {
        int cmp;
        mid = lo + ((hi - lo) / 2u);
        cmp = dg_order_key_cmp(&q->items[mid].key, key);
        if (cmp <= 0) {
            lo = mid + 1u;
        } else {
            hi = mid;
        }
    }
    return lo;
}

int dg_work_queue_push(dg_work_queue *q, const dg_work_item *it) {
    u32 idx;
    if (!q || !it) {
        return -1;
    }
    if (!q->items || q->capacity == 0u) {
        q->probe_refused += 1u;
        return -2;
    }
    if (q->count >= q->capacity) {
        q->probe_refused += 1u;
        return -3;
    }

    idx = dg_work_queue_upper_bound(q, &it->key);
    if (idx < q->count) {
        memmove(&q->items[idx + 1u], &q->items[idx],
                sizeof(dg_work_item) * (size_t)(q->count - idx));
    }
    q->items[idx] = *it;
    q->count += 1u;
#ifndef NDEBUG
    DG_DET_GUARD_SORTED(dg_work_queue_is_sorted(q) == D_TRUE);
#endif
    return 0;
}

const dg_work_item *dg_work_queue_peek_next(const dg_work_queue *q) {
    if (!q || q->count == 0u || !q->items) {
        return (const dg_work_item *)0;
    }
    return &q->items[0];
}

const dg_work_item *dg_work_queue_at(const dg_work_queue *q, u32 index) {
    if (!q || !q->items || index >= q->count) {
        return (const dg_work_item *)0;
    }
    return &q->items[index];
}

d_bool dg_work_queue_pop_next(dg_work_queue *q, dg_work_item *out) {
    if (!q || !q->items || q->count == 0u) {
        return D_FALSE;
    }
#ifndef NDEBUG
    DG_DET_GUARD_SORTED(dg_work_queue_is_sorted(q) == D_TRUE);
#endif
    if (out) {
        *out = q->items[0];
    }
    if (q->count > 1u) {
        memmove(&q->items[0], &q->items[1], sizeof(dg_work_item) * (size_t)(q->count - 1u));
    }
    q->count -= 1u;
    return D_TRUE;
}

int dg_work_queue_merge(dg_work_queue *dst, dg_work_queue *src) {
    dg_work_item it;
    if (!dst || !src) {
        return -1;
    }
#ifndef NDEBUG
    DG_DET_GUARD_SORTED(dg_work_queue_is_sorted(dst) == D_TRUE);
    DG_DET_GUARD_SORTED(dg_work_queue_is_sorted(src) == D_TRUE);
#endif
    /* Deterministic: consume src in its canonical order. */
    while (src->count != 0u) {
        const dg_work_item *next = dg_work_queue_peek_next(src);
        if (!next) {
            break;
        }
        it = *next;
        if (dg_work_queue_push(dst, &it) != 0) {
            /* dst full; refuse remaining items, but do not drop src contents. */
            if (src->count > 1u) {
                dst->probe_refused += (src->count - 1u);
            }
            return 1;
        }
        (void)dg_work_queue_pop_next(src, (dg_work_item *)0);
    }
#ifndef NDEBUG
    DG_DET_GUARD_SORTED(dg_work_queue_is_sorted(dst) == D_TRUE);
    DG_DET_GUARD_SORTED(dg_work_queue_is_sorted(src) == D_TRUE);
#endif
    return 0;
}
