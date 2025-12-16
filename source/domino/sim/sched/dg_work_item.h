/*
FILE: source/domino/sim/sched/dg_work_item.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / sim/sched/dg_work_item
RESPONSIBILITY: Defines internal contract for `dg_work_item`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
/* Work item abstraction for deterministic deferred scheduling (C89).
 *
 * Work items are immutable scheduling records. They can be deferred across
 * ticks by leaving them in deterministic carryover queues.
 */
#ifndef DG_WORK_ITEM_H
#define DG_WORK_ITEM_H

#include "core/dg_order_key.h"

#ifdef __cplusplus
extern "C" {
#endif

#define DG_WORK_ITEM_INLINE_CAP 16u

typedef struct dg_work_item {
    dg_order_key         key;
    dg_type_id           work_type_id; /* taxonomy for work routing */
    u32                  cost_units;   /* deterministic budget units */
    dg_tick              enqueue_tick;

    /* Payload (optional).
     * If payload_inline_len > 0: use payload_inline bytes.
     * Else: payload_ptr/payload_len is a borrowed reference (e.g., arena).
     */
    const unsigned char *payload_ptr;
    u32                  payload_len;
    unsigned char        payload_inline[DG_WORK_ITEM_INLINE_CAP];
    u32                  payload_inline_len;
} dg_work_item;

void dg_work_item_clear(dg_work_item *it);

/* Set payload as an external reference (not owned). */
void dg_work_item_set_payload_ref(dg_work_item *it, const unsigned char *ptr, u32 len);

/* Copy payload into inline storage; returns 0 on success. */
int dg_work_item_set_payload_inline(dg_work_item *it, const unsigned char *ptr, u32 len);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DG_WORK_ITEM_H */

