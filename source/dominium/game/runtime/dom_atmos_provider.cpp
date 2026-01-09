/*
FILE: source/dominium/game/runtime/dom_atmos_provider.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/runtime/atmos_provider
RESPONSIBILITY: Atmosphere profile TLV helper for v1 providers.
*/
#include "runtime/dom_atmos_provider.h"

#include <cstring>

#include "dominium/core_tlv.h"

namespace {

static void write_i32_le(unsigned char out[4], i32 v) {
    dom::core_tlv::tlv_write_u32_le(out, (u32)v);
}

static void write_i64_le(unsigned char out[8], i64 v) {
    dom::core_tlv::tlv_write_u64_le(out, (u64)v);
}

static int read_i64_le(const unsigned char *payload, u32 len, i64 *out_v) {
    u64 value = 0;
    if (!payload || !out_v) {
        return 0;
    }
    if (!dom::core_tlv::tlv_read_u64_le(payload, len, value)) {
        return 0;
    }
    *out_v = (i64)value;
    return 1;
}

} // namespace

int dom_atmos_profile_top_altitude(const dom_media_binding *binding,
                                   q48_16 *out_top_altitude_m) {
    if (!binding || !out_top_altitude_m) {
        return DOM_ATMOS_INVALID_ARGUMENT;
    }
    if (!binding->params || binding->params_len == 0u) {
        return DOM_ATMOS_INVALID_DATA;
    }

    dom::core_tlv::TlvReader reader(binding->params, binding->params_len);
    dom::core_tlv::TlvRecord rec;
    u32 schema_version = 0u;
    q48_16 top_alt = 0;
    q48_16 last_segment_alt = 0;
    u32 segment_count = 0u;

    while (reader.next(rec)) {
        if (rec.tag == dom::core_tlv::CORE_TLV_TAG_SCHEMA_VERSION) {
            (void)dom::core_tlv::tlv_read_u32_le(rec.payload, rec.len, schema_version);
        } else if (rec.tag == DOM_ATMOS_TLV_TOP_ALT_M) {
            i64 v = 0;
            if (!read_i64_le(rec.payload, rec.len, &v)) {
                return DOM_ATMOS_INVALID_DATA;
            }
            top_alt = (q48_16)v;
        } else if (rec.tag == DOM_ATMOS_TLV_SEGMENT) {
            i64 v = 0;
            if (rec.len != 20u) {
                return DOM_ATMOS_INVALID_DATA;
            }
            if (!read_i64_le(rec.payload, 8u, &v)) {
                return DOM_ATMOS_INVALID_DATA;
            }
            last_segment_alt = (q48_16)v;
            ++segment_count;
        }
    }

    if (schema_version != DOM_ATMOS_PROFILE_V1 || segment_count < 2u) {
        return DOM_ATMOS_INVALID_DATA;
    }
    if (top_alt <= 0) {
        top_alt = last_segment_alt;
    }
    if (top_alt <= 0) {
        return DOM_ATMOS_INVALID_DATA;
    }
    *out_top_altitude_m = top_alt;
    return DOM_ATMOS_OK;
}

int dom_atmos_profile_build_tlv(const dom_atmos_profile_segment *segments,
                                u32 segment_count,
                                q48_16 top_altitude_m,
                                std::vector<unsigned char> &out_tlv) {
    if (!segments || segment_count < 2u) {
        return DOM_ATMOS_INVALID_ARGUMENT;
    }
    if (segment_count > DOM_ATMOS_PROFILE_MAX_SEGMENTS) {
        return DOM_ATMOS_INVALID_ARGUMENT;
    }
    dom::core_tlv::TlvWriter writer;
    writer.add_u32(dom::core_tlv::CORE_TLV_TAG_SCHEMA_VERSION, DOM_ATMOS_PROFILE_V1);

    {
        unsigned char buf[8];
        write_i64_le(buf, (i64)top_altitude_m);
        writer.add_bytes(DOM_ATMOS_TLV_TOP_ALT_M, buf, 8u);
    }

    for (u32 i = 0u; i < segment_count; ++i) {
        unsigned char seg[20];
        write_i64_le(seg + 0, (i64)segments[i].altitude_m);
        write_i32_le(seg + 8, (i32)segments[i].density_q16);
        write_i32_le(seg + 12, (i32)segments[i].pressure_q16);
        write_i32_le(seg + 16, (i32)segments[i].temperature_q16);
        writer.add_bytes(DOM_ATMOS_TLV_SEGMENT, seg, 20u);
    }

    out_tlv = writer.bytes();
    return DOM_ATMOS_OK;
}
