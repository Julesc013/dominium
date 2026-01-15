#include "dsk/dsk_plan.h"
#include "dsk/dsk_digest.h"

dsk_u64 dsk_plan_payload_digest(const dsk_plan_t *plan) {
    dsk_plan_t tmp;
    dsk_tlv_buffer_t buf;
    dsk_u64 digest;
    dsk_status_t st;

    if (!plan) {
        return 0u;
    }

    tmp = *plan;
    tmp.plan_digest64 = 0u;

    st = dsk_plan_write(&tmp, &buf);
    if (!dsk_error_is_ok(st)) {
        return 0u;
    }
    if (buf.size <= DSK_TLV_HEADER_SIZE) {
        dsk_tlv_buffer_free(&buf);
        return 0u;
    }
    digest = dsk_digest64_bytes(buf.data + DSK_TLV_HEADER_SIZE,
                                buf.size - DSK_TLV_HEADER_SIZE);
    dsk_tlv_buffer_free(&buf);
    return digest;
}
