/*
FILE: source/dominium/common/core_tlv_framed_writer.cpp
MODULE: Dominium
PURPOSE: Framed TLV writer helpers (header + u16 tag, CRC32).
*/

#include "dominium/core_tlv.h"

#include <string.h>
#include <vector>

struct core_tlv_framed_builder_t {
    std::vector<unsigned char> payload;
};

static void core_tlv_write_u16_le(unsigned char* p, u16 v) {
    p[0] = (unsigned char)(v & 0xFFu);
    p[1] = (unsigned char)((v >> 8) & 0xFFu);
}

static void core_tlv_write_u32_le(unsigned char* p, u32 v) {
    p[0] = (unsigned char)(v & 0xFFu);
    p[1] = (unsigned char)((v >> 8) & 0xFFu);
    p[2] = (unsigned char)((v >> 16) & 0xFFu);
    p[3] = (unsigned char)((v >> 24) & 0xFFu);
}

static void core_tlv_write_u64_le(unsigned char* p, u64 v) {
    core_tlv_write_u32_le(p, (u32)(v & 0xFFFFFFFFu));
    core_tlv_write_u32_le(p + 4u, (u32)((v >> 32) & 0xFFFFFFFFu));
}

static err_t core_tlv_err_invalid_args(void) {
    return err_make((u16)ERRD_COMMON,
                    (u16)ERRC_COMMON_INVALID_ARGS,
                    (u32)ERRF_FATAL,
                    (u32)ERRMSG_COMMON_INVALID_ARGS);
}

static err_t core_tlv_err_internal(void) {
    return err_make((u16)ERRD_COMMON,
                    (u16)ERRC_COMMON_INTERNAL,
                    (u32)ERRF_FATAL,
                    (u32)ERRMSG_COMMON_INTERNAL);
}

core_tlv_framed_builder_t* core_tlv_framed_builder_create(void) {
    return new core_tlv_framed_builder_t();
}

void core_tlv_framed_builder_destroy(core_tlv_framed_builder_t* builder) {
    delete builder;
}

static err_t core_tlv_framed_builder_add_raw(core_tlv_framed_builder_t* builder,
                                             u16 type,
                                             const unsigned char* payload,
                                             u32 length) {
    unsigned char header[6];
    if (!builder) {
        return core_tlv_err_invalid_args();
    }
    core_tlv_write_u16_le(header, type);
    core_tlv_write_u32_le(header + 2u, length);
    builder->payload.insert(builder->payload.end(), header, header + 6u);
    if (length && payload) {
        builder->payload.insert(builder->payload.end(), payload, payload + length);
    }
    return err_ok();
}

err_t core_tlv_framed_builder_add_bytes(core_tlv_framed_builder_t* builder,
                                        u16 type,
                                        const unsigned char* payload,
                                        u32 length) {
    if (length != 0u && !payload) {
        return core_tlv_err_invalid_args();
    }
    return core_tlv_framed_builder_add_raw(builder, type, payload, length);
}

err_t core_tlv_framed_builder_add_string(core_tlv_framed_builder_t* builder,
                                         u16 type,
                                         const char* value) {
    u32 len;
    if (!value) {
        return core_tlv_err_invalid_args();
    }
    len = (u32)strlen(value);
    return core_tlv_framed_builder_add_raw(builder, type, (const unsigned char*)value, len);
}

err_t core_tlv_framed_builder_add_u16(core_tlv_framed_builder_t* builder,
                                      u16 type,
                                      u16 value) {
    unsigned char tmp[2];
    core_tlv_write_u16_le(tmp, value);
    return core_tlv_framed_builder_add_raw(builder, type, tmp, 2u);
}

err_t core_tlv_framed_builder_add_u32(core_tlv_framed_builder_t* builder,
                                      u16 type,
                                      u32 value) {
    unsigned char tmp[4];
    core_tlv_write_u32_le(tmp, value);
    return core_tlv_framed_builder_add_raw(builder, type, tmp, 4u);
}

err_t core_tlv_framed_builder_add_u64(core_tlv_framed_builder_t* builder,
                                      u16 type,
                                      u64 value) {
    unsigned char tmp[8];
    core_tlv_write_u64_le(tmp, value);
    return core_tlv_framed_builder_add_raw(builder, type, tmp, 8u);
}

err_t core_tlv_framed_builder_add_container(core_tlv_framed_builder_t* builder,
                                            u16 type,
                                            const unsigned char* payload,
                                            u32 length) {
    return core_tlv_framed_builder_add_raw(builder, type, payload, length);
}

static err_t core_tlv_framed_builder_emit(const core_tlv_framed_builder_t* builder,
                                          core_tlv_framed_buffer_t* out_buf,
                                          int with_header) {
    u32 payload_size;
    u32 total_size;
    unsigned char header[CORE_TLV_FRAMED_HEADER_SIZE];
    u32 crc;
    unsigned char* buf;

    if (!builder || !out_buf) {
        return core_tlv_err_invalid_args();
    }
    out_buf->data = 0;
    out_buf->size = 0u;

    payload_size = (u32)builder->payload.size();
    total_size = with_header ? (CORE_TLV_FRAMED_HEADER_SIZE + payload_size) : payload_size;

    buf = new unsigned char[total_size ? total_size : 1u];
    if (!buf) {
        return core_tlv_err_internal();
    }

    if (with_header) {
        memcpy(header, CORE_TLV_FRAMED_MAGIC, 4u);
        core_tlv_write_u16_le(header + 4u, (u16)CORE_TLV_FRAMED_VERSION);
        core_tlv_write_u16_le(header + 6u, (u16)CORE_TLV_FRAMED_ENDIAN_LITTLE);
        core_tlv_write_u32_le(header + 8u, (u32)CORE_TLV_FRAMED_HEADER_SIZE);
        core_tlv_write_u32_le(header + 12u, payload_size);
        core_tlv_write_u32_le(header + 16u, 0u);
        crc = core_tlv_crc32(header, CORE_TLV_FRAMED_HEADER_SIZE);
        core_tlv_write_u32_le(header + 16u, crc);

        memcpy(buf, header, CORE_TLV_FRAMED_HEADER_SIZE);
        if (payload_size != 0u) {
            memcpy(buf + CORE_TLV_FRAMED_HEADER_SIZE, &builder->payload[0], payload_size);
        }
    } else if (payload_size != 0u) {
        memcpy(buf, &builder->payload[0], payload_size);
    }

    out_buf->data = buf;
    out_buf->size = total_size;
    return err_ok();
}

err_t core_tlv_framed_builder_finalize(const core_tlv_framed_builder_t* builder,
                                       core_tlv_framed_buffer_t* out_buf) {
    return core_tlv_framed_builder_emit(builder, out_buf, 1);
}

err_t core_tlv_framed_builder_finalize_payload(const core_tlv_framed_builder_t* builder,
                                               core_tlv_framed_buffer_t* out_buf) {
    return core_tlv_framed_builder_emit(builder, out_buf, 0);
}

void core_tlv_framed_buffer_free(core_tlv_framed_buffer_t* buf) {
    if (!buf) {
        return;
    }
    delete[] buf->data;
    buf->data = 0;
    buf->size = 0u;
}
