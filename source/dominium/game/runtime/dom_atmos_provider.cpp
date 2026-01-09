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

} // namespace

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
