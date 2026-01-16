/*
FILE: source/domino/core/det_order.c
MODULE: Domino
RESPONSIBILITY: Deterministic ordering utilities (stable sort + heap).
*/
#include "domino/core/det_order.h"

static int dom_det_u64_cmp(u64 a, u64 b) {
    if (a < b) return -1;
    if (a > b) return 1;
    return 0;
}

int dom_det_order_item_cmp(const dom_det_order_item *a, const dom_det_order_item *b) {
    int c;
    if (!a && !b) return 0;
    if (!a) return -1;
    if (!b) return 1;
    c = dom_det_u64_cmp(a->primary, b->primary);
    if (c) return c;
    c = dom_det_u64_cmp(a->secondary, b->secondary);
    if (c) return c;
    return dom_det_u64_cmp(a->payload, b->payload);
}

void dom_det_order_sort(dom_det_order_item *items, u32 count) {
    u32 i;
    if (!items || count <= 1u) {
        return;
    }
    for (i = 1u; i < count; ++i) {
        dom_det_order_item key = items[i];
        u32 j = i;
        while (j > 0u && dom_det_order_item_cmp(&items[j - 1u], &key) > 0) {
            items[j] = items[j - 1u];
            --j;
        }
        items[j] = key;
    }
}

static void dom_det_heap_swap(dom_det_order_item *a, dom_det_order_item *b) {
    dom_det_order_item tmp = *a;
    *a = *b;
    *b = tmp;
}

static void dom_det_heapify_up(dom_det_heap *h, u32 idx) {
    while (idx > 0u) {
        u32 parent = (idx - 1u) / 2u;
        if (dom_det_order_item_cmp(&h->items[idx], &h->items[parent]) >= 0) {
            break;
        }
        dom_det_heap_swap(&h->items[idx], &h->items[parent]);
        idx = parent;
    }
}

static void dom_det_heapify_down(dom_det_heap *h, u32 idx) {
    u32 count = h->count;
    while (1) {
        u32 left = (idx * 2u) + 1u;
        u32 right = left + 1u;
        u32 smallest = idx;

        if (left < count && dom_det_order_item_cmp(&h->items[left], &h->items[smallest]) < 0) {
            smallest = left;
        }
        if (right < count && dom_det_order_item_cmp(&h->items[right], &h->items[smallest]) < 0) {
            smallest = right;
        }
        if (smallest == idx) {
            break;
        }
        dom_det_heap_swap(&h->items[idx], &h->items[smallest]);
        idx = smallest;
    }
}

int dom_det_heap_init(dom_det_heap *h, dom_det_order_item *storage, u32 capacity) {
    if (!h || !storage || capacity == 0u) {
        return DOM_DET_INVALID;
    }
    h->items = storage;
    h->capacity = capacity;
    h->count = 0u;
    return DOM_DET_OK;
}

int dom_det_heap_size(const dom_det_heap *h, u32 *out_count) {
    if (!h || !out_count) {
        return DOM_DET_INVALID;
    }
    *out_count = h->count;
    return DOM_DET_OK;
}

int dom_det_heap_push(dom_det_heap *h, const dom_det_order_item *item) {
    if (!h || !item) {
        return DOM_DET_INVALID;
    }
    if (h->count >= h->capacity) {
        return DOM_DET_FULL;
    }
    h->items[h->count] = *item;
    dom_det_heapify_up(h, h->count);
    h->count += 1u;
    return DOM_DET_OK;
}

int dom_det_heap_peek(const dom_det_heap *h, dom_det_order_item *out_item) {
    if (!h || !out_item) {
        return DOM_DET_INVALID;
    }
    if (h->count == 0u) {
        return DOM_DET_EMPTY;
    }
    *out_item = h->items[0u];
    return DOM_DET_OK;
}

int dom_det_heap_pop(dom_det_heap *h, dom_det_order_item *out_item) {
    if (!h || !out_item) {
        return DOM_DET_INVALID;
    }
    if (h->count == 0u) {
        return DOM_DET_EMPTY;
    }
    *out_item = h->items[0u];
    h->count -= 1u;
    if (h->count > 0u) {
        h->items[0u] = h->items[h->count];
        dom_det_heapify_down(h, 0u);
    }
    return DOM_DET_OK;
}
