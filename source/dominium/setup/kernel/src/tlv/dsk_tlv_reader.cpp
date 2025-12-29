#include "dsk/dsk_tlv.h"

#include <string.h>

static dsk_u16 dsk_read_u16_le(const dsk_u8 *p) {
    return (dsk_u16)p[0] | (dsk_u16)((dsk_u16)p[1] << 8);
}

static dsk_u32 dsk_read_u32_le(const dsk_u8 *p) {
    return (dsk_u32)p[0]
         | ((dsk_u32)p[1] << 8)
         | ((dsk_u32)p[2] << 16)
         | ((dsk_u32)p[3] << 24);
}

static dsk_u64 dsk_read_u64_le(const dsk_u8 *p) {
    dsk_u64 lo = dsk_read_u32_le(p);
    dsk_u64 hi = dsk_read_u32_le(p + 4);
    return lo | (hi << 32);
}

static dsk_status_t dsk_tlv_make_error(dsk_u16 code, dsk_u16 subcode) {
    return dsk_error_make(DSK_DOMAIN_KERNEL, code, subcode, DSK_ERROR_FLAG_USER_ACTIONABLE);
}

static dsk_status_t dsk_tlv_parse_records(const dsk_u8 *payload,
                                          dsk_u32 size,
                                          dsk_tlv_record_t **out_records,
                                          dsk_u32 *out_count) {
    const dsk_u32 max_records = 16384u;
    dsk_u32 count = 0u;
    dsk_u32 cap = 0u;
    dsk_tlv_record_t *records = 0;
    dsk_u32 offset = 0u;

    if (!out_records || !out_count) {
        return dsk_tlv_make_error(DSK_CODE_INVALID_ARGS, DSK_SUBCODE_NONE);
    }
    *out_records = 0;
    *out_count = 0u;
    if (!payload && size != 0u) {
        return dsk_tlv_make_error(DSK_CODE_INVALID_ARGS, DSK_SUBCODE_NONE);
    }

    while (offset < size) {
        dsk_u32 remaining = size - offset;
        dsk_u16 type;
        dsk_u32 length;
        dsk_tlv_record_t rec;

        if (remaining < 6u) {
            delete[] records;
            return dsk_tlv_make_error(DSK_CODE_PARSE_ERROR, DSK_SUBCODE_TLV_TRUNCATED);
        }
        type = dsk_read_u16_le(payload + offset);
        length = dsk_read_u32_le(payload + offset + 2u);
        offset += 6u;
        if (length > size - offset) {
            delete[] records;
            return dsk_tlv_make_error(DSK_CODE_PARSE_ERROR, DSK_SUBCODE_TLV_TRUNCATED);
        }

        if (count == cap) {
            dsk_u32 new_cap = (cap == 0u) ? 16u : (cap * 2u);
            dsk_tlv_record_t *next;
            if (new_cap > max_records) {
                delete[] records;
                return dsk_tlv_make_error(DSK_CODE_PARSE_ERROR, DSK_SUBCODE_TLV_TRUNCATED);
            }
            next = new dsk_tlv_record_t[new_cap];
            if (!next) {
                delete[] records;
                return dsk_tlv_make_error(DSK_CODE_INTERNAL_ERROR, DSK_SUBCODE_NONE);
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
    return dsk_error_make(DSK_DOMAIN_NONE, DSK_CODE_OK, DSK_SUBCODE_NONE, 0u);
}

dsk_status_t dsk_tlv_parse(const dsk_u8 *data,
                           dsk_u32 size,
                           dsk_tlv_view_t *out_view) {
    dsk_tlv_header_t header;
    dsk_u32 crc;
    dsk_u8 header_bytes[DSK_TLV_HEADER_SIZE];
    dsk_u32 header_size;
    dsk_u32 payload_size;
    dsk_status_t st;

    if (!out_view) {
        return dsk_tlv_make_error(DSK_CODE_INVALID_ARGS, DSK_SUBCODE_NONE);
    }
    memset(out_view, 0, sizeof(*out_view));

    if (!data || size < DSK_TLV_HEADER_SIZE) {
        return dsk_tlv_make_error(DSK_CODE_PARSE_ERROR, DSK_SUBCODE_TLV_TRUNCATED);
    }

    memcpy(header.magic, data, 4u);
    header.version = dsk_read_u16_le(data + 4u);
    header.endian = dsk_read_u16_le(data + 6u);
    header.header_size = dsk_read_u32_le(data + 8u);
    header.payload_size = dsk_read_u32_le(data + 12u);
    header.header_crc = dsk_read_u32_le(data + 16u);

    if (memcmp(header.magic, DSK_TLV_MAGIC, 4u) != 0) {
        return dsk_tlv_make_error(DSK_CODE_PARSE_ERROR, DSK_SUBCODE_TLV_BAD_MAGIC);
    }
    if (header.version != DSK_TLV_VERSION) {
        return dsk_tlv_make_error(DSK_CODE_UNSUPPORTED_VERSION, DSK_SUBCODE_NONE);
    }
    if (header.endian != DSK_TLV_ENDIAN_LITTLE) {
        return dsk_tlv_make_error(DSK_CODE_PARSE_ERROR, DSK_SUBCODE_TLV_BAD_ENDIAN);
    }

    header_size = header.header_size;
    payload_size = header.payload_size;
    if (header_size < DSK_TLV_HEADER_SIZE || header_size > size) {
        return dsk_tlv_make_error(DSK_CODE_PARSE_ERROR, DSK_SUBCODE_TLV_BAD_HEADER_SIZE);
    }
    if (header_size + payload_size > size) {
        return dsk_tlv_make_error(DSK_CODE_PARSE_ERROR, DSK_SUBCODE_TLV_BAD_PAYLOAD_SIZE);
    }

    memcpy(header_bytes, data, DSK_TLV_HEADER_SIZE);
    header_bytes[16] = 0u;
    header_bytes[17] = 0u;
    header_bytes[18] = 0u;
    header_bytes[19] = 0u;
    crc = dsk_tlv_crc32(header_bytes, DSK_TLV_HEADER_SIZE);
    if (crc != header.header_crc) {
        return dsk_tlv_make_error(DSK_CODE_PARSE_ERROR, DSK_SUBCODE_TLV_BAD_CRC);
    }

    out_view->header = header;
    out_view->payload = data + header_size;
    out_view->payload_size = payload_size;

    st = dsk_tlv_parse_records(out_view->payload,
                               out_view->payload_size,
                               &out_view->records,
                               &out_view->record_count);
    if (!dsk_error_is_ok(st)) {
        dsk_tlv_view_destroy(out_view);
        return st;
    }
    return dsk_error_make(DSK_DOMAIN_NONE, DSK_CODE_OK, DSK_SUBCODE_NONE, 0u);
}

void dsk_tlv_view_destroy(dsk_tlv_view_t *view) {
    if (!view) {
        return;
    }
    delete[] view->records;
    memset(view, 0, sizeof(*view));
}

dsk_status_t dsk_tlv_parse_stream(const dsk_u8 *payload,
                                  dsk_u32 size,
                                  dsk_tlv_stream_t *out_stream) {
    dsk_status_t st;
    if (!out_stream) {
        return dsk_tlv_make_error(DSK_CODE_INVALID_ARGS, DSK_SUBCODE_NONE);
    }
    memset(out_stream, 0, sizeof(*out_stream));
    st = dsk_tlv_parse_records(payload, size, &out_stream->records, &out_stream->record_count);
    if (!dsk_error_is_ok(st)) {
        dsk_tlv_stream_destroy(out_stream);
        return st;
    }
    out_stream->payload = payload;
    out_stream->payload_size = size;
    return dsk_error_make(DSK_DOMAIN_NONE, DSK_CODE_OK, DSK_SUBCODE_NONE, 0u);
}

void dsk_tlv_stream_destroy(dsk_tlv_stream_t *stream) {
    if (!stream) {
        return;
    }
    delete[] stream->records;
    memset(stream, 0, sizeof(*stream));
}

const dsk_tlv_record_t *dsk_tlv_find_first(const dsk_tlv_record_t *records,
                                           dsk_u32 count,
                                           dsk_u16 type) {
    dsk_u32 i;
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
