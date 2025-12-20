/*
FILE: source/dominium/setup/core/src/util/dsu_util_tlv.c
MODULE: Dominium Setup
PURPOSE: TLV read/write helpers (u16 type, u32 length, payload bytes).
*/
#include "dsu_util_internal.h"

dsu_status_t dsu__tlv_read_header(const dsu_u8 *buf,
                                 dsu_u32 len,
                                 dsu_u32 *io_off,
                                 dsu_u16 *out_type,
                                 dsu_u32 *out_payload_len) {
    dsu_status_t st;
    dsu_u32 off;
    dsu_u16 type;
    dsu_u32 payload_len;

    if (!buf || !io_off || !out_type || !out_payload_len) {
        return DSU_STATUS_INVALID_ARGS;
    }

    off = *io_off;
    st = dsu__read_u16le(buf, len, &off, &type);
    if (st != DSU_STATUS_SUCCESS) {
        return st;
    }
    st = dsu__read_u32le(buf, len, &off, &payload_len);
    if (st != DSU_STATUS_SUCCESS) {
        return st;
    }
    if (payload_len > (len - off)) {
        return DSU_STATUS_INTEGRITY_ERROR;
    }

    *io_off = off;
    *out_type = type;
    *out_payload_len = payload_len;
    return DSU_STATUS_SUCCESS;
}

dsu_status_t dsu__tlv_skip_value(dsu_u32 len, dsu_u32 *io_off, dsu_u32 payload_len) {
    dsu_u32 off;
    if (!io_off) {
        return DSU_STATUS_INVALID_ARGS;
    }
    off = *io_off;
    if (payload_len > (len - off)) {
        return DSU_STATUS_INTEGRITY_ERROR;
    }
    *io_off = off + payload_len;
    return DSU_STATUS_SUCCESS;
}

dsu_status_t dsu__blob_put_tlv(dsu_blob_t *b, dsu_u16 type, const void *payload, dsu_u32 payload_len) {
    dsu_status_t st;
    if (!b) {
        return DSU_STATUS_INVALID_ARGS;
    }
    if (!payload && payload_len != 0u) {
        return DSU_STATUS_INVALID_ARGS;
    }
    st = dsu__blob_put_u16le(b, type);
    if (st != DSU_STATUS_SUCCESS) {
        return st;
    }
    st = dsu__blob_put_u32le(b, payload_len);
    if (st != DSU_STATUS_SUCCESS) {
        return st;
    }
    return dsu__blob_append(b, payload, payload_len);
}

