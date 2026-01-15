/*
FILE: source/dominium/setup/core/src/util/dsu_util_le.c
MODULE: Dominium Setup
PURPOSE: Little-endian read/write helpers for deterministic binary formats.
*/
#include "dsu_util_internal.h"

#include <string.h>

dsu_status_t dsu__blob_put_u8(dsu_blob_t *b, dsu_u8 v) {
    return dsu__blob_append(b, &v, 1u);
}

dsu_status_t dsu__blob_put_u16le(dsu_blob_t *b, dsu_u16 v) {
    dsu_u8 tmp[2];
    tmp[0] = (dsu_u8)(v & 0xFFu);
    tmp[1] = (dsu_u8)((v >> 8) & 0xFFu);
    return dsu__blob_append(b, tmp, 2u);
}

dsu_status_t dsu__blob_put_u32le(dsu_blob_t *b, dsu_u32 v) {
    dsu_u8 tmp[4];
    tmp[0] = (dsu_u8)(v & 0xFFu);
    tmp[1] = (dsu_u8)((v >> 8) & 0xFFu);
    tmp[2] = (dsu_u8)((v >> 16) & 0xFFu);
    tmp[3] = (dsu_u8)((v >> 24) & 0xFFu);
    return dsu__blob_append(b, tmp, 4u);
}

dsu_status_t dsu__blob_put_u64le(dsu_blob_t *b, dsu_u64 v) {
    dsu_u8 tmp[8];
    tmp[0] = (dsu_u8)(v & 0xFFu);
    tmp[1] = (dsu_u8)((v >> 8) & 0xFFu);
    tmp[2] = (dsu_u8)((v >> 16) & 0xFFu);
    tmp[3] = (dsu_u8)((v >> 24) & 0xFFu);
    tmp[4] = (dsu_u8)((v >> 32) & 0xFFu);
    tmp[5] = (dsu_u8)((v >> 40) & 0xFFu);
    tmp[6] = (dsu_u8)((v >> 48) & 0xFFu);
    tmp[7] = (dsu_u8)((v >> 56) & 0xFFu);
    return dsu__blob_append(b, tmp, 8u);
}

dsu_status_t dsu__read_u8(const dsu_u8 *buf, dsu_u32 len, dsu_u32 *io_off, dsu_u8 *out_v) {
    dsu_u32 off;
    if (!buf || !io_off || !out_v) {
        return DSU_STATUS_INVALID_ARGS;
    }
    off = *io_off;
    if (off >= len) {
        return DSU_STATUS_INTEGRITY_ERROR;
    }
    *out_v = buf[off];
    *io_off = off + 1u;
    return DSU_STATUS_SUCCESS;
}

dsu_status_t dsu__read_u16le(const dsu_u8 *buf, dsu_u32 len, dsu_u32 *io_off, dsu_u16 *out_v) {
    dsu_u32 off;
    if (!buf || !io_off || !out_v) {
        return DSU_STATUS_INVALID_ARGS;
    }
    off = *io_off;
    if (len - off < 2u) {
        return DSU_STATUS_INTEGRITY_ERROR;
    }
    *out_v = (dsu_u16)((dsu_u16)buf[off] | ((dsu_u16)buf[off + 1u] << 8));
    *io_off = off + 2u;
    return DSU_STATUS_SUCCESS;
}

dsu_status_t dsu__read_u32le(const dsu_u8 *buf, dsu_u32 len, dsu_u32 *io_off, dsu_u32 *out_v) {
    dsu_u32 off;
    if (!buf || !io_off || !out_v) {
        return DSU_STATUS_INVALID_ARGS;
    }
    off = *io_off;
    if (len - off < 4u) {
        return DSU_STATUS_INTEGRITY_ERROR;
    }
    *out_v = (dsu_u32)buf[off]
           | ((dsu_u32)buf[off + 1u] << 8)
           | ((dsu_u32)buf[off + 2u] << 16)
           | ((dsu_u32)buf[off + 3u] << 24);
    *io_off = off + 4u;
    return DSU_STATUS_SUCCESS;
}

dsu_status_t dsu__read_u64le(const dsu_u8 *buf, dsu_u32 len, dsu_u32 *io_off, dsu_u64 *out_v) {
    dsu_u32 off;
    if (!buf || !io_off || !out_v) {
        return DSU_STATUS_INVALID_ARGS;
    }
    off = *io_off;
    if (len - off < 8u) {
        return DSU_STATUS_INTEGRITY_ERROR;
    }
    *out_v = (dsu_u64)buf[off]
           | ((dsu_u64)buf[off + 1u] << 8)
           | ((dsu_u64)buf[off + 2u] << 16)
           | ((dsu_u64)buf[off + 3u] << 24)
           | ((dsu_u64)buf[off + 4u] << 32)
           | ((dsu_u64)buf[off + 5u] << 40)
           | ((dsu_u64)buf[off + 6u] << 48)
           | ((dsu_u64)buf[off + 7u] << 56);
    *io_off = off + 8u;
    return DSU_STATUS_SUCCESS;
}

dsu_status_t dsu__read_bytes(const dsu_u8 *buf, dsu_u32 len, dsu_u32 *io_off, void *out_bytes, dsu_u32 n) {
    dsu_u32 off;
    if (!buf || !io_off || (!out_bytes && n != 0u)) {
        return DSU_STATUS_INVALID_ARGS;
    }
    off = *io_off;
    if (n == 0u) {
        return DSU_STATUS_SUCCESS;
    }
    if (len - off < n) {
        return DSU_STATUS_INTEGRITY_ERROR;
    }
    memcpy(out_bytes, buf + off, (size_t)n);
    *io_off = off + n;
    return DSU_STATUS_SUCCESS;
}
