/*
FILE: include/domino/core/det_order.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / core/det_order
RESPONSIBILITY: Deterministic ordering utilities (stable sort + heap).
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: OS-specific headers; non-deterministic containers.
*/
#ifndef DOMINO_CORE_DET_ORDER_H
#define DOMINO_CORE_DET_ORDER_H

#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

enum {
    DOM_DET_OK = 0,
    DOM_DET_INVALID = -1,
    DOM_DET_FULL = -2,
    DOM_DET_EMPTY = -3
};

/* dom_det_order_item
 * Purpose: Canonical ordering item with explicit tie-break keys.
 * Ordering: primary, then secondary, then payload.
 */
typedef struct dom_det_order_item {
    u64 primary;
    u64 secondary;
    u64 payload;
} dom_det_order_item;

/* dom_det_order_item_cmp
 * Purpose: Total-order comparator for dom_det_order_item.
 * Returns: -1/0/1 like strcmp.
 */
int dom_det_order_item_cmp(const dom_det_order_item *a, const dom_det_order_item *b);

/* dom_det_order_sort
 * Purpose: Stable in-place sort for deterministic ordering.
 * Notes: Uses insertion sort (stable, deterministic).
 */
void dom_det_order_sort(dom_det_order_item *items, u32 count);

/* dom_det_heap
 * Purpose: Deterministic min-heap with stable secondary key.
 */
typedef struct dom_det_heap {
    dom_det_order_item *items;
    u32 count;
    u32 capacity;
} dom_det_heap;

int dom_det_heap_init(dom_det_heap *h, dom_det_order_item *storage, u32 capacity);
int dom_det_heap_size(const dom_det_heap *h, u32 *out_count);
int dom_det_heap_push(dom_det_heap *h, const dom_det_order_item *item);
int dom_det_heap_peek(const dom_det_heap *h, dom_det_order_item *out_item);
int dom_det_heap_pop(dom_det_heap *h, dom_det_order_item *out_item);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINO_CORE_DET_ORDER_H */
