/*
FILE: source/domino/sim/sched/dg_work_item.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / sim/sched/dg_work_item
RESPONSIBILITY: Implements `dg_work_item`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include <string.h>

#include "sim/sched/dg_work_item.h"

void dg_work_item_clear(dg_work_item *it) {
    if (!it) {
        return;
    }
    dg_order_key_clear(&it->key);
    it->work_type_id = 0u;
    it->cost_units = 0u;
    it->enqueue_tick = 0u;
    it->payload_ptr = (const unsigned char *)0;
    it->payload_len = 0u;
    memset(it->payload_inline, 0, sizeof(it->payload_inline));
    it->payload_inline_len = 0u;
}

void dg_work_item_set_payload_ref(dg_work_item *it, const unsigned char *ptr, u32 len) {
    if (!it) {
        return;
    }
    it->payload_inline_len = 0u;
    it->payload_ptr = ptr;
    it->payload_len = len;
}

int dg_work_item_set_payload_inline(dg_work_item *it, const unsigned char *ptr, u32 len) {
    if (!it) {
        return -1;
    }
    if (len > DG_WORK_ITEM_INLINE_CAP) {
        return -2;
    }
    if (len != 0u && !ptr) {
        return -3;
    }
    if (len != 0u) {
        memcpy(it->payload_inline, ptr, (size_t)len);
    }
    if (len < DG_WORK_ITEM_INLINE_CAP) {
        memset(it->payload_inline + len, 0, (size_t)(DG_WORK_ITEM_INLINE_CAP - len));
    }
    it->payload_inline_len = len;
    it->payload_ptr = (const unsigned char *)0;
    it->payload_len = 0u;
    return 0;
}

