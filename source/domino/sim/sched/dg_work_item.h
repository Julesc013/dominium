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

