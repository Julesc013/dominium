/*
FILE: source/dominium/common/core_tlv_framed_reader.cpp
MODULE: Dominium
PURPOSE: Framed TLV reader helpers (header + u16 tag, CRC32).
*/

#include "dominium/core_tlv.h"

#include <string.h>

static u16 core_tlv_read_u16_le(const unsigned char* p) {
    return (u16)p[0] | (u16)((u16)p[1] << 8);
}

static u32 core_tlv_read_u32_le(const unsigned char* p) {
    return (u32)p[0]
         | ((u32)p[1] << 8)
         | ((u32)p[2] << 16)
         | ((u32)p[3] << 24);
}

static err_t core_tlv_err_invalid_args(void) {
    return err_make((u16)ERRD_COMMON,
                    (u16)ERRC_COMMON_INVALID_ARGS,
                    (u32)ERRF_FATAL,
                    (u32)ERRMSG_COMMON_INVALID_ARGS);
}

static err_t core_tlv_err_internal(u16 subcode) {
    err_t err = err_make((u16)ERRD_COMMON,
                         (u16)ERRC_COMMON_INTERNAL,
                         (u32)ERRF_FATAL,
                         (u32)ERRMSG_COMMON_INTERNAL);
    if (subcode != 0u) {
        err_add_detail_u32(&err, (u32)ERR_DETAIL_KEY_SUBCODE, subcode);
    }
    return err;
}

static err_t core_tlv_err_parse(u16 subcode) {
    err_t err = err_make((u16)ERRD_TLV,
                         (u16)ERRC_TLV_PARSE_FAILED,
                         (u32)ERRF_USER_ACTIONABLE,
                         (u32)ERRMSG_TLV_PARSE_FAILED);
    if (subcode != 0u) {
        err_add_detail_u32(&err, (u32)ERR_DETAIL_KEY_SUBCODE, subcode);
    }
    return err;
}

static err_t core_tlv_err_schema(u16 subcode) {
    err_t err = err_make((u16)ERRD_TLV,
                         (u16)ERRC_TLV_SCHEMA_VERSION,
                         (u32)(ERRF_POLICY_REFUSAL | ERRF_NOT_SUPPORTED),
                         (u32)ERRMSG_TLV_SCHEMA_VERSION);
    if (subcode != 0u) {
        err_add_detail_u32(&err, (u32)ERR_DETAIL_KEY_SUBCODE, subcode);
    }
    return err;
}

static err_t core_tlv_err_integrity(u16 subcode) {
    err_t err = err_make((u16)ERRD_TLV,
                         (u16)ERRC_TLV_INTEGRITY,
                         (u32)ERRF_INTEGRITY,
                         (u32)ERRMSG_TLV_INTEGRITY);
    if (subcode != 0u) {
        err_add_detail_u32(&err, (u32)ERR_DETAIL_KEY_SUBCODE, subcode);
    }
    return err;
}

static err_t core_tlv_parse_records(const unsigned char* payload,
                                    u32 size,
                                    core_tlv_framed_record_t** out_records,
                                    u32* out_count) {
    const u32 max_records = 16384u;
    u32 count = 0u;
    u32 cap = 0u;
    core_tlv_framed_record_t* records = 0;
    u32 offset = 0u;

    if (!out_records || !out_count) {
        return core_tlv_err_invalid_args();
    }
    *out_records = 0;
    *out_count = 0u;
    if (!payload && size != 0u) {
        return core_tlv_err_invalid_args();
    }

    while (offset < size) {
        u32 remaining = size - offset;
        u16 type;
        u32 length;
        core_tlv_framed_record_t rec;

        if (remaining < 6u) {
            delete[] records;
            return core_tlv_err_parse((u16)CORE_TLV_SUBCODE_TLV_TRUNCATED);
        }
        type = core_tlv_read_u16_le(payload + offset);
        length = core_tlv_read_u32_le(payload + offset + 2u);
        offset += 6u;
        if (length > size - offset) {
            delete[] records;
            return core_tlv_err_parse((u16)CORE_TLV_SUBCODE_TLV_TRUNCATED);
        }

        if (count == cap) {
            u32 new_cap = (cap == 0u) ? 16u : (cap * 2u);
            core_tlv_framed_record_t* next;
            if (new_cap > max_records) {
                delete[] records;
                return core_tlv_err_parse((u16)CORE_TLV_SUBCODE_TLV_TRUNCATED);
            }
            next = new core_tlv_framed_record_t[new_cap];
            if (!next) {
                delete[] records;
                return core_tlv_err_internal(0u);
            }
            if (records && count) {
                memcpy(next, records, (size_t)count * sizeof(*records));
            }
            delete[] records;
            records = next;
            cap = new_cap;
        }

        rec.type = type;
        rec.payload = payload + offset;
        rec.length = length;
        records[count++] = rec;
        offset += length;
    }

    *out_records = records;
    *out_count = count;
    return err_ok();
}

err_t core_tlv_framed_parse(const unsigned char* data,
                            u32 size,
                            core_tlv_framed_view_t* out_view) {
    core_tlv_framed_header_t header;
    u32 crc;
    unsigned char header_bytes[CORE_TLV_FRAMED_HEADER_SIZE];
    u32 header_size;
    u32 payload_size;
    err_t st;

    if (!out_view) {
        return core_tlv_err_invalid_args();
    }
    memset(out_view, 0, sizeof(*out_view));

    if (!data || size < CORE_TLV_FRAMED_HEADER_SIZE) {
        return core_tlv_err_parse((u16)CORE_TLV_SUBCODE_TLV_TRUNCATED);
    }

    memcpy(header.magic, data, 4u);
    header.version = core_tlv_read_u16_le(data + 4u);
    header.endian = core_tlv_read_u16_le(data + 6u);
    header.header_size = core_tlv_read_u32_le(data + 8u);
    header.payload_size = core_tlv_read_u32_le(data + 12u);
    header.header_crc = core_tlv_read_u32_le(data + 16u);

    if (memcmp(header.magic, CORE_TLV_FRAMED_MAGIC, 4u) != 0) {
        return core_tlv_err_parse((u16)CORE_TLV_SUBCODE_TLV_BAD_MAGIC);
    }
    if (header.version != CORE_TLV_FRAMED_VERSION) {
        return core_tlv_err_schema(0u);
    }
    if (header.endian != CORE_TLV_FRAMED_ENDIAN_LITTLE) {
        return core_tlv_err_parse((u16)CORE_TLV_SUBCODE_TLV_BAD_ENDIAN);
    }

    header_size = header.header_size;
    payload_size = header.payload_size;
    if (header_size < CORE_TLV_FRAMED_HEADER_SIZE || header_size > size) {
        return core_tlv_err_parse((u16)CORE_TLV_SUBCODE_TLV_BAD_HEADER_SIZE);
    }
    if (payload_size > CORE_TLV_FRAMED_MAX_PAYLOAD) {
        return core_tlv_err_parse((u16)CORE_TLV_SUBCODE_TLV_BAD_PAYLOAD_SIZE);
    }
    if (header_size + payload_size > size) {
        return core_tlv_err_parse((u16)CORE_TLV_SUBCODE_TLV_BAD_PAYLOAD_SIZE);
    }

    memcpy(header_bytes, data, CORE_TLV_FRAMED_HEADER_SIZE);
    header_bytes[16] = 0u;
    header_bytes[17] = 0u;
    header_bytes[18] = 0u;
    header_bytes[19] = 0u;
    crc = core_tlv_crc32(header_bytes, CORE_TLV_FRAMED_HEADER_SIZE);
    if (crc != header.header_crc) {
        return core_tlv_err_integrity((u16)CORE_TLV_SUBCODE_TLV_BAD_CRC);
    }

    out_view->header = header;
    out_view->payload = data + header_size;
    out_view->payload_size = payload_size;

    st = core_tlv_parse_records(out_view->payload,
                                out_view->payload_size,
                                &out_view->records,
                                &out_view->record_count);
    if (!err_is_ok(&st)) {
        core_tlv_framed_view_destroy(out_view);
        return st;
    }
    return err_ok();
}

void core_tlv_framed_view_destroy(core_tlv_framed_view_t* view) {
    if (!view) {
        return;
    }
    delete[] view->records;
    memset(view, 0, sizeof(*view));
}

err_t core_tlv_framed_parse_stream(const unsigned char* payload,
                                   u32 size,
                                   core_tlv_framed_stream_t* out_stream) {
    err_t st;
    if (!out_stream) {
        return core_tlv_err_invalid_args();
    }
    memset(out_stream, 0, sizeof(*out_stream));
    st = core_tlv_parse_records(payload, size, &out_stream->records, &out_stream->record_count);
    if (!err_is_ok(&st)) {
        core_tlv_framed_stream_destroy(out_stream);
        return st;
    }
    out_stream->payload = payload;
    out_stream->payload_size = size;
    return err_ok();
}

void core_tlv_framed_stream_destroy(core_tlv_framed_stream_t* stream) {
    if (!stream) {
        return;
    }
    delete[] stream->records;
    memset(stream, 0, sizeof(*stream));
}

const core_tlv_framed_record_t* core_tlv_framed_find_first(const core_tlv_framed_record_t* records,
                                                           u32 count,
                                                           u16 type) {
    u32 i;
    if (!records) {
        return 0;
    }
    for (i = 0u; i < count; ++i) {
        if (records[i].type == type) {
            return &records[i];
        }
    }
    return 0;
}
