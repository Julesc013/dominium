/*
FILE: source/dominium/setup/core/src/util/dsu_util_filefmt.c
MODULE: Dominium Setup
PURPOSE: Common DSU file header encoding/decoding for dsuplan/dsulog.
*/
#include "dsu_util_internal.h"

#include <string.h>

dsu_u32 dsu__header_checksum32_base(const dsu_u8 header_base[DSU_FILE_HEADER_BASE_SIZE]) {
    dsu_u32 sum = 0u;
    dsu_u32 i;
    if (!header_base) {
        return 0u;
    }
    /* Sum bytes 0..15 (exclude checksum field). */
    for (i = 0u; i < (DSU_FILE_HEADER_BASE_SIZE - 4u); ++i) {
        sum += (dsu_u32)header_base[i];
    }
    return sum;
}

dsu_status_t dsu__file_wrap_payload(const dsu_u8 magic[4],
                                   dsu_u16 format_version,
                                   const dsu_u8 *payload,
                                   dsu_u32 payload_len,
                                   dsu_blob_t *out_file_bytes) {
    dsu_u8 hdr[DSU_FILE_HEADER_BASE_SIZE];
    dsu_u32 checksum;

    if (!magic || !out_file_bytes) {
        return DSU_STATUS_INVALID_ARGS;
    }
    if (!payload && payload_len != 0u) {
        return DSU_STATUS_INVALID_ARGS;
    }

    dsu__blob_init(out_file_bytes);

    /* Base header (20 bytes). */
    hdr[0] = magic[0];
    hdr[1] = magic[1];
    hdr[2] = magic[2];
    hdr[3] = magic[3];
    hdr[4] = (dsu_u8)(format_version & 0xFFu);
    hdr[5] = (dsu_u8)((format_version >> 8) & 0xFFu);
    hdr[6] = (dsu_u8)(DSU_ENDIAN_MARKER_LE & 0xFFu);
    hdr[7] = (dsu_u8)((DSU_ENDIAN_MARKER_LE >> 8) & 0xFFu);
    /* header_size = 20 */
    hdr[8]  = (dsu_u8)(DSU_FILE_HEADER_BASE_SIZE & 0xFFu);
    hdr[9]  = (dsu_u8)((DSU_FILE_HEADER_BASE_SIZE >> 8) & 0xFFu);
    hdr[10] = (dsu_u8)((DSU_FILE_HEADER_BASE_SIZE >> 16) & 0xFFu);
    hdr[11] = (dsu_u8)((DSU_FILE_HEADER_BASE_SIZE >> 24) & 0xFFu);
    /* payload_length */
    hdr[12] = (dsu_u8)(payload_len & 0xFFu);
    hdr[13] = (dsu_u8)((payload_len >> 8) & 0xFFu);
    hdr[14] = (dsu_u8)((payload_len >> 16) & 0xFFu);
    hdr[15] = (dsu_u8)((payload_len >> 24) & 0xFFu);
    /* checksum placeholder (bytes 16..19) */
    hdr[16] = 0u;
    hdr[17] = 0u;
    hdr[18] = 0u;
    hdr[19] = 0u;

    checksum = dsu__header_checksum32_base(hdr);
    hdr[16] = (dsu_u8)(checksum & 0xFFu);
    hdr[17] = (dsu_u8)((checksum >> 8) & 0xFFu);
    hdr[18] = (dsu_u8)((checksum >> 16) & 0xFFu);
    hdr[19] = (dsu_u8)((checksum >> 24) & 0xFFu);

    if (dsu__blob_append(out_file_bytes, hdr, DSU_FILE_HEADER_BASE_SIZE) != DSU_STATUS_SUCCESS) {
        dsu__blob_free(out_file_bytes);
        return DSU_STATUS_IO_ERROR;
    }
    if (payload_len) {
        if (dsu__blob_append(out_file_bytes, payload, payload_len) != DSU_STATUS_SUCCESS) {
            dsu__blob_free(out_file_bytes);
            return DSU_STATUS_IO_ERROR;
        }
    }
    return DSU_STATUS_SUCCESS;
}

dsu_status_t dsu__file_unwrap_payload(const dsu_u8 *file_bytes,
                                     dsu_u32 file_len,
                                     const dsu_u8 expected_magic[4],
                                     dsu_u16 expected_format_version,
                                     const dsu_u8 **out_payload,
                                     dsu_u32 *out_payload_len) {
    dsu_u32 header_size;
    dsu_u32 payload_len;
    dsu_u16 version;
    dsu_u16 endian_marker;
    dsu_u32 checksum_stored;
    dsu_u32 checksum_calc;

    if (!file_bytes || !expected_magic || !out_payload || !out_payload_len) {
        return DSU_STATUS_INVALID_ARGS;
    }
    if (file_len < DSU_FILE_HEADER_BASE_SIZE) {
        return DSU_STATUS_INTEGRITY_ERROR;
    }

    if (memcmp(file_bytes, expected_magic, 4u) != 0) {
        return DSU_STATUS_INTEGRITY_ERROR;
    }

    version = (dsu_u16)((dsu_u16)file_bytes[4] | ((dsu_u16)file_bytes[5] << 8));
    if (version != expected_format_version) {
        return DSU_STATUS_UNSUPPORTED_VERSION;
    }
    endian_marker = (dsu_u16)((dsu_u16)file_bytes[6] | ((dsu_u16)file_bytes[7] << 8));
    if (endian_marker != (dsu_u16)DSU_ENDIAN_MARKER_LE) {
        return DSU_STATUS_UNSUPPORTED_VERSION;
    }

    header_size = (dsu_u32)file_bytes[8]
                | ((dsu_u32)file_bytes[9] << 8)
                | ((dsu_u32)file_bytes[10] << 16)
                | ((dsu_u32)file_bytes[11] << 24);
    if (header_size < DSU_FILE_HEADER_BASE_SIZE) {
        return DSU_STATUS_INTEGRITY_ERROR;
    }
    if (header_size > file_len) {
        return DSU_STATUS_INTEGRITY_ERROR;
    }

    payload_len = (dsu_u32)file_bytes[12]
                | ((dsu_u32)file_bytes[13] << 8)
                | ((dsu_u32)file_bytes[14] << 16)
                | ((dsu_u32)file_bytes[15] << 24);

    checksum_stored = (dsu_u32)file_bytes[16]
                    | ((dsu_u32)file_bytes[17] << 8)
                    | ((dsu_u32)file_bytes[18] << 16)
                    | ((dsu_u32)file_bytes[19] << 24);
    checksum_calc = dsu__header_checksum32_base(file_bytes);
    if (checksum_stored != checksum_calc) {
        return DSU_STATUS_INTEGRITY_ERROR;
    }

    if (file_len - header_size < payload_len) {
        return DSU_STATUS_INTEGRITY_ERROR;
    }

    *out_payload = file_bytes + header_size;
    *out_payload_len = payload_len;
    return DSU_STATUS_SUCCESS;
}

