#include "dsk/dsk_tlv.h"

#include <string.h>
#include <vector>

struct dsk_tlv_builder_t {
    std::vector<dsk_u8> payload;
};

static void dsk_write_u16_le(dsk_u8 *p, dsk_u16 v) {
    p[0] = (dsk_u8)(v & 0xFFu);
    p[1] = (dsk_u8)((v >> 8) & 0xFFu);
}

static void dsk_write_u32_le(dsk_u8 *p, dsk_u32 v) {
    p[0] = (dsk_u8)(v & 0xFFu);
    p[1] = (dsk_u8)((v >> 8) & 0xFFu);
    p[2] = (dsk_u8)((v >> 16) & 0xFFu);
    p[3] = (dsk_u8)((v >> 24) & 0xFFu);
}

static void dsk_write_u64_le(dsk_u8 *p, dsk_u64 v) {
    dsk_write_u32_le(p, (dsk_u32)(v & 0xFFFFFFFFu));
    dsk_write_u32_le(p + 4u, (dsk_u32)((v >> 32) & 0xFFFFFFFFu));
}

dsk_tlv_builder_t *dsk_tlv_builder_create(void) {
    return new dsk_tlv_builder_t();
}

void dsk_tlv_builder_destroy(dsk_tlv_builder_t *builder) {
    delete builder;
}

static dsk_status_t dsk_tlv_builder_add_raw(dsk_tlv_builder_t *builder,
                                            dsk_u16 type,
                                            const dsk_u8 *payload,
                                            dsk_u32 length) {
    dsk_u8 header[6];
    if (!builder) {
        return dsk_error_make(DSK_DOMAIN_KERNEL, DSK_CODE_INVALID_ARGS, DSK_SUBCODE_NONE, 0u);
    }
    dsk_write_u16_le(header, type);
    dsk_write_u32_le(header + 2u, length);
    builder->payload.insert(builder->payload.end(), header, header + 6u);
    if (length && payload) {
        builder->payload.insert(builder->payload.end(), payload, payload + length);
    }
    return dsk_error_make(DSK_DOMAIN_NONE, DSK_CODE_OK, DSK_SUBCODE_NONE, 0u);
}

dsk_status_t dsk_tlv_builder_add_bytes(dsk_tlv_builder_t *builder,
                                       dsk_u16 type,
                                       const dsk_u8 *payload,
                                       dsk_u32 length) {
    if (length != 0u && !payload) {
        return dsk_error_make(DSK_DOMAIN_KERNEL, DSK_CODE_INVALID_ARGS, DSK_SUBCODE_NONE, 0u);
    }
    return dsk_tlv_builder_add_raw(builder, type, payload, length);
}

dsk_status_t dsk_tlv_builder_add_string(dsk_tlv_builder_t *builder,
                                        dsk_u16 type,
                                        const char *value) {
    dsk_u32 len;
    if (!value) {
        return dsk_error_make(DSK_DOMAIN_KERNEL, DSK_CODE_INVALID_ARGS, DSK_SUBCODE_NONE, 0u);
    }
    len = (dsk_u32)strlen(value);
    return dsk_tlv_builder_add_raw(builder, type, (const dsk_u8 *)value, len);
}

dsk_status_t dsk_tlv_builder_add_u16(dsk_tlv_builder_t *builder,
                                     dsk_u16 type,
                                     dsk_u16 value) {
    dsk_u8 tmp[2];
    dsk_write_u16_le(tmp, value);
    return dsk_tlv_builder_add_raw(builder, type, tmp, 2u);
}

dsk_status_t dsk_tlv_builder_add_u32(dsk_tlv_builder_t *builder,
                                     dsk_u16 type,
                                     dsk_u32 value) {
    dsk_u8 tmp[4];
    dsk_write_u32_le(tmp, value);
    return dsk_tlv_builder_add_raw(builder, type, tmp, 4u);
}

dsk_status_t dsk_tlv_builder_add_u64(dsk_tlv_builder_t *builder,
                                     dsk_u16 type,
                                     dsk_u64 value) {
    dsk_u8 tmp[8];
    dsk_write_u64_le(tmp, value);
    return dsk_tlv_builder_add_raw(builder, type, tmp, 8u);
}

dsk_status_t dsk_tlv_builder_add_container(dsk_tlv_builder_t *builder,
                                           dsk_u16 type,
                                           const dsk_u8 *payload,
                                           dsk_u32 length) {
    return dsk_tlv_builder_add_raw(builder, type, payload, length);
}

static dsk_status_t dsk_tlv_builder_emit(const dsk_tlv_builder_t *builder,
                                         dsk_tlv_buffer_t *out_buf,
                                         int with_header) {
    dsk_u32 payload_size;
    dsk_u32 total_size;
    dsk_u8 header[DSK_TLV_HEADER_SIZE];
    dsk_u32 crc;
    dsk_u8 *buf;

    if (!builder || !out_buf) {
        return dsk_error_make(DSK_DOMAIN_KERNEL, DSK_CODE_INVALID_ARGS, DSK_SUBCODE_NONE, 0u);
    }
    out_buf->data = 0;
    out_buf->size = 0u;

    payload_size = (dsk_u32)builder->payload.size();
    total_size = with_header ? (DSK_TLV_HEADER_SIZE + payload_size) : payload_size;

    buf = new dsk_u8[total_size ? total_size : 1u];
    if (!buf) {
        return dsk_error_make(DSK_DOMAIN_KERNEL, DSK_CODE_INTERNAL_ERROR, DSK_SUBCODE_NONE, 0u);
    }

    if (with_header) {
        memcpy(header, DSK_TLV_MAGIC, 4u);
        dsk_write_u16_le(header + 4u, (dsk_u16)DSK_TLV_VERSION);
        dsk_write_u16_le(header + 6u, (dsk_u16)DSK_TLV_ENDIAN_LITTLE);
        dsk_write_u32_le(header + 8u, (dsk_u32)DSK_TLV_HEADER_SIZE);
        dsk_write_u32_le(header + 12u, payload_size);
        dsk_write_u32_le(header + 16u, 0u);
        crc = dsk_tlv_crc32(header, DSK_TLV_HEADER_SIZE);
        dsk_write_u32_le(header + 16u, crc);

        memcpy(buf, header, DSK_TLV_HEADER_SIZE);
        if (payload_size != 0u) {
            memcpy(buf + DSK_TLV_HEADER_SIZE, &builder->payload[0], payload_size);
        }
    } else if (payload_size != 0u) {
        memcpy(buf, &builder->payload[0], payload_size);
    }

    out_buf->data = buf;
    out_buf->size = total_size;
    return dsk_error_make(DSK_DOMAIN_NONE, DSK_CODE_OK, DSK_SUBCODE_NONE, 0u);
}

dsk_status_t dsk_tlv_builder_finalize(const dsk_tlv_builder_t *builder,
                                      dsk_tlv_buffer_t *out_buf) {
    return dsk_tlv_builder_emit(builder, out_buf, 1);
}

dsk_status_t dsk_tlv_builder_finalize_payload(const dsk_tlv_builder_t *builder,
                                              dsk_tlv_buffer_t *out_buf) {
    return dsk_tlv_builder_emit(builder, out_buf, 0);
}

void dsk_tlv_buffer_free(dsk_tlv_buffer_t *buf) {
    if (!buf) {
        return;
    }
    delete[] buf->data;
    buf->data = 0;
    buf->size = 0u;
}
