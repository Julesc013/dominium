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

