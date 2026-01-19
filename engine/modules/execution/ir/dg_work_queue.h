/*
FILE: source/domino/execution/ir/dg_work_queue.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / execution/ir/dg_work_queue
RESPONSIBILITY: Defines internal contract for `dg_work_queue`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
/* Deterministic bounded work queues (C89).
 *
 * Queue ordering is always the canonical ascending order of dg_order_key.
 * No unordered containers or pointer-order behavior is permitted.
 */
#ifndef DG_WORK_QUEUE_H
#define DG_WORK_QUEUE_H

#include "execution/ir/dg_work_item.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dg_work_queue {
    dg_work_item *items;
    u32           count;
    u32           capacity;
    d_bool        owns_storage;
    u32           probe_refused; /* enqueue refusals due to capacity */
} dg_work_queue;

void dg_work_queue_init(dg_work_queue *q);
void dg_work_queue_free(dg_work_queue *q);

/* Allocate internal bounded storage for items. */
int dg_work_queue_reserve(dg_work_queue *q, u32 capacity);

/* Use caller-provided bounded storage (does not allocate). */
int dg_work_queue_use_storage(dg_work_queue *q, dg_work_item *storage, u32 capacity);

void dg_work_queue_clear(dg_work_queue *q);

u32 dg_work_queue_count(const dg_work_queue *q);
u32 dg_work_queue_capacity(const dg_work_queue *q);
u32 dg_work_queue_probe_refused(const dg_work_queue *q);

/* Deterministic: inserts by canonical dg_order_key order (ascending). */
int dg_work_queue_push(dg_work_queue *q, const dg_work_item *it);

/* Read-only accessors. */
const dg_work_item *dg_work_queue_peek_next(const dg_work_queue *q);
const dg_work_item *dg_work_queue_at(const dg_work_queue *q, u32 index);

/* Pops the next item; returns D_TRUE if one was popped. */
d_bool dg_work_queue_pop_next(dg_work_queue *q, dg_work_item *out);

/* Merge items from src into dst in deterministic order.
 * Items successfully moved are removed from src. If dst fills, remaining src
 * items stay in src and dst->probe_refused is incremented for each refused.
 */
int dg_work_queue_merge(dg_work_queue *dst, dg_work_queue *src);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DG_WORK_QUEUE_H */
