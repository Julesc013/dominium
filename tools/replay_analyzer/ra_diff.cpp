/*
FILE: source/dominium/tools/replay_analyzer/ra_diff.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / tools/replay_analyzer
RESPONSIBILITY: Implements desync parsing and comparison helpers.
*/
#include "ra_diff.h"

#include <fstream>
#include <vector>

#include "dominium/core_tlv.h"

namespace dom {
namespace tools {
namespace {

enum {
    RA_DESYNC_TLV_VERSION = 1u,
    RA_DESYNC_TAG_TICK = 2u,
    RA_DESYNC_TAG_EXPECTED_HASH = 3u,
    RA_DESYNC_TAG_ACTUAL_HASH = 4u
};

static bool read_file_bytes(const std::string &path, std::vector<unsigned char> &out) {
    std::ifstream in(path.c_str(), std::ios::binary);
    if (!in) {
        return false;
    }
    in.seekg(0, std::ios::end);
    std::streamoff size = in.tellg();
    in.seekg(0, std::ios::beg);
    if (size <= 0) {
        out.clear();
        return false;
    }
    out.resize((size_t)size);
    in.read(reinterpret_cast<char *>(&out[0]), size);
    return in.good() || in.eof();
}

} // namespace

bool ra_load_desync(const std::string &path,
                    RaDesyncInfo &out,
                    std::string *err) {
    std::vector<unsigned char> bytes;
    core_tlv::TlvRecord rec;
    u32 version = 0u;
    bool have_version = false;
    RaDesyncInfo info;

    info.tick = 0ull;
    info.expected_hash64 = 0ull;
    info.actual_hash64 = 0ull;
    info.has_expected = false;
    info.has_actual = false;

    if (!read_file_bytes(path, bytes)) {
        if (err) *err = "desync_read_failed";
        return false;
    }
    core_tlv::TlvReader r(bytes.empty() ? (const unsigned char *)0 : &bytes[0], bytes.size());
    while (r.next(rec)) {
        switch (rec.tag) {
        case core_tlv::CORE_TLV_TAG_SCHEMA_VERSION:
            if (core_tlv::tlv_read_u32_le(rec.payload, rec.len, version)) {
                have_version = true;
            }
            break;
        case RA_DESYNC_TAG_TICK: {
            u64 v = 0ull;
            if (core_tlv::tlv_read_u64_le(rec.payload, rec.len, v)) {
                info.tick = v;
            }
            break;
        }
        case RA_DESYNC_TAG_EXPECTED_HASH: {
            u64 v = 0ull;
            if (core_tlv::tlv_read_u64_le(rec.payload, rec.len, v)) {
                info.expected_hash64 = v;
                info.has_expected = true;
            }
            break;
        }
        case RA_DESYNC_TAG_ACTUAL_HASH: {
            u64 v = 0ull;
            if (core_tlv::tlv_read_u64_le(rec.payload, rec.len, v)) {
                info.actual_hash64 = v;
                info.has_actual = true;
            }
            break;
        }
        default:
            break;
        }
    }

    if (!have_version || version != RA_DESYNC_TLV_VERSION) {
        if (err) *err = "desync_version_invalid";
        return false;
    }

    out = info;
    return true;
}

bool ra_compare_desync(const RaReplaySummary &summary,
                       const RaDesyncInfo &desync,
                       u64 &out_tick,
                       u64 &out_hash,
                       std::string *err) {
    size_t i;
    if (summary.ticks.empty()) {
        if (err) *err = "desync_requires_tick_hashes";
        return false;
    }
    for (i = 0u; i < summary.ticks.size(); ++i) {
        if (summary.ticks[i].tick == desync.tick) {
            out_tick = desync.tick;
            out_hash = summary.ticks[i].hash64;
            return true;
        }
    }
    if (err) *err = "desync_tick_not_found";
    return false;
}

} // namespace tools
} // namespace dom
