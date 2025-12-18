/*
FILE: source/dominium/launcher/core/src/launch/launcher_exit_status.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / launcher/core (ecosystem) / exit_status
RESPONSIBILITY: Implements exit_status.tlv schema encode/decode (versioned root; skip-unknown).
*/

#include "launcher_exit_status.h"

#include "launcher_tlv.h"

namespace dom {
namespace launcher_core {

namespace {
enum {
    TAG_RUN_ID = 2u,
    TAG_EXIT_CODE = 3u,
    TAG_TERMINATION_TYPE = 4u,
    TAG_TIMESTAMP_START_US = 5u,
    TAG_TIMESTAMP_END_US = 6u,
    TAG_STDOUT_CAPTURE_SUPPORTED = 7u,
    TAG_STDERR_CAPTURE_SUPPORTED = 8u
};
}

LauncherExitStatus::LauncherExitStatus()
    : schema_version(LAUNCHER_EXIT_STATUS_TLV_VERSION),
      run_id(0ull),
      exit_code(0),
      termination_type((u32)LAUNCHER_TERM_UNKNOWN),
      timestamp_start_us(0ull),
      timestamp_end_us(0ull),
      stdout_capture_supported(0u),
      stderr_capture_supported(0u) {
}

bool launcher_exit_status_to_tlv_bytes(const LauncherExitStatus& st,
                                       std::vector<unsigned char>& out_bytes) {
    TlvWriter w;

    w.add_u32(LAUNCHER_TLV_TAG_SCHEMA_VERSION, LAUNCHER_EXIT_STATUS_TLV_VERSION);
    w.add_u64(TAG_RUN_ID, st.run_id);
    w.add_i32(TAG_EXIT_CODE, st.exit_code);
    w.add_u32(TAG_TERMINATION_TYPE, st.termination_type);
    w.add_u64(TAG_TIMESTAMP_START_US, st.timestamp_start_us);
    w.add_u64(TAG_TIMESTAMP_END_US, st.timestamp_end_us);
    w.add_u32(TAG_STDOUT_CAPTURE_SUPPORTED, st.stdout_capture_supported ? 1u : 0u);
    w.add_u32(TAG_STDERR_CAPTURE_SUPPORTED, st.stderr_capture_supported ? 1u : 0u);

    out_bytes = w.bytes();
    return true;
}

bool launcher_exit_status_from_tlv_bytes(const unsigned char* data,
                                         size_t size,
                                         LauncherExitStatus& out_st) {
    TlvReader r(data, size);
    TlvRecord rec;
    u32 version = 0u;

    out_st = LauncherExitStatus();
    if (!tlv_read_schema_version_or_default(data, size, version, LAUNCHER_EXIT_STATUS_TLV_VERSION)) {
        return false;
    }
    if (version != LAUNCHER_EXIT_STATUS_TLV_VERSION) {
        return false;
    }

    while (r.next(rec)) {
        switch (rec.tag) {
        case LAUNCHER_TLV_TAG_SCHEMA_VERSION:
            break;
        case TAG_RUN_ID: {
            u64 v;
            if (tlv_read_u64_le(rec.payload, rec.len, v)) out_st.run_id = v;
            break;
        }
        case TAG_EXIT_CODE: {
            i32 v;
            if (tlv_read_i32_le(rec.payload, rec.len, v)) out_st.exit_code = v;
            break;
        }
        case TAG_TERMINATION_TYPE: {
            u32 v;
            if (tlv_read_u32_le(rec.payload, rec.len, v)) out_st.termination_type = v;
            break;
        }
        case TAG_TIMESTAMP_START_US: {
            u64 v;
            if (tlv_read_u64_le(rec.payload, rec.len, v)) out_st.timestamp_start_us = v;
            break;
        }
        case TAG_TIMESTAMP_END_US: {
            u64 v;
            if (tlv_read_u64_le(rec.payload, rec.len, v)) out_st.timestamp_end_us = v;
            break;
        }
        case TAG_STDOUT_CAPTURE_SUPPORTED: {
            u32 v;
            if (tlv_read_u32_le(rec.payload, rec.len, v)) out_st.stdout_capture_supported = v ? 1u : 0u;
            break;
        }
        case TAG_STDERR_CAPTURE_SUPPORTED: {
            u32 v;
            if (tlv_read_u32_le(rec.payload, rec.len, v)) out_st.stderr_capture_supported = v ? 1u : 0u;
            break;
        }
        default:
            /* skip unknown */
            break;
        }
    }

    return true;
}

} /* namespace launcher_core */
} /* namespace dom */

