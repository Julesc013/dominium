/*
FILE: source/dominium/launcher/core/src/run/launcher_run_summary.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / launcher/core (foundation) / run_summary
RESPONSIBILITY: Implements run summary TLV persistence and stable text rendering.
*/

#include "launcher_run_summary.h"

#include <sstream>

#include "launcher_tlv.h"

namespace dom {
namespace launcher_core {

LauncherRunSummary::LauncherRunSummary()
    : schema_version(LAUNCHER_RUN_SUMMARY_TLV_VERSION),
      run_id(0ull),
      instance_id(),
      outcome(0u),
      exit_code(0),
      termination_type(0u),
      refusal_code(0u),
      err(err_ok()) {
}

bool launcher_run_summary_to_tlv_bytes(const LauncherRunSummary& s,
                                       std::vector<unsigned char>& out_bytes) {
    TlvWriter w;

    w.add_u32(LAUNCHER_TLV_TAG_SCHEMA_VERSION, LAUNCHER_RUN_SUMMARY_TLV_VERSION);
    w.add_u64(LAUNCHER_RUN_SUMMARY_TLV_TAG_RUN_ID, s.run_id);
    w.add_string(LAUNCHER_RUN_SUMMARY_TLV_TAG_INSTANCE_ID, s.instance_id);
    w.add_u32(LAUNCHER_RUN_SUMMARY_TLV_TAG_OUTCOME, s.outcome);
    w.add_i32(LAUNCHER_RUN_SUMMARY_TLV_TAG_EXIT_CODE, s.exit_code);
    w.add_u32(LAUNCHER_RUN_SUMMARY_TLV_TAG_TERM_TYPE, s.termination_type);
    if (s.refusal_code != 0u) {
        w.add_u32(LAUNCHER_RUN_SUMMARY_TLV_TAG_REFUSAL_CODE, s.refusal_code);
    }
    if (!err_is_ok(&s.err)) {
        w.add_u32(LAUNCHER_RUN_SUMMARY_TLV_TAG_ERR_DOMAIN, (u32)s.err.domain);
        w.add_u32(LAUNCHER_RUN_SUMMARY_TLV_TAG_ERR_CODE, (u32)s.err.code);
        w.add_u32(LAUNCHER_RUN_SUMMARY_TLV_TAG_ERR_FLAGS, (u32)s.err.flags);
        w.add_u32(LAUNCHER_RUN_SUMMARY_TLV_TAG_ERR_MSG_ID, (u32)s.err.msg_id);
    }

    out_bytes = w.bytes();
    return true;
}

bool launcher_run_summary_from_tlv_bytes(const unsigned char* data,
                                         size_t size,
                                         LauncherRunSummary& out_s) {
    TlvReader r(data, size);
    TlvRecord rec;
    u32 version = 0u;

    out_s = LauncherRunSummary();
    if (!tlv_read_schema_version_or_default(data, size, version, LAUNCHER_RUN_SUMMARY_TLV_VERSION)) {
        return false;
    }
    if (version != LAUNCHER_RUN_SUMMARY_TLV_VERSION) {
        return false;
    }

    while (r.next(rec)) {
        switch (rec.tag) {
        case LAUNCHER_TLV_TAG_SCHEMA_VERSION:
            break;
        case LAUNCHER_RUN_SUMMARY_TLV_TAG_RUN_ID: {
            u64 v;
            if (tlv_read_u64_le(rec.payload, rec.len, v)) out_s.run_id = v;
            break;
        }
        case LAUNCHER_RUN_SUMMARY_TLV_TAG_INSTANCE_ID:
            out_s.instance_id = tlv_read_string(rec.payload, rec.len);
            break;
        case LAUNCHER_RUN_SUMMARY_TLV_TAG_OUTCOME: {
            u32 v;
            if (tlv_read_u32_le(rec.payload, rec.len, v)) out_s.outcome = v;
            break;
        }
        case LAUNCHER_RUN_SUMMARY_TLV_TAG_EXIT_CODE: {
            i32 v;
            if (tlv_read_i32_le(rec.payload, rec.len, v)) out_s.exit_code = v;
            break;
        }
        case LAUNCHER_RUN_SUMMARY_TLV_TAG_TERM_TYPE: {
            u32 v;
            if (tlv_read_u32_le(rec.payload, rec.len, v)) out_s.termination_type = v;
            break;
        }
        case LAUNCHER_RUN_SUMMARY_TLV_TAG_REFUSAL_CODE: {
            u32 v;
            if (tlv_read_u32_le(rec.payload, rec.len, v)) out_s.refusal_code = v;
            break;
        }
        case LAUNCHER_RUN_SUMMARY_TLV_TAG_ERR_DOMAIN: {
            u32 v;
            if (tlv_read_u32_le(rec.payload, rec.len, v)) out_s.err.domain = (u16)v;
            break;
        }
        case LAUNCHER_RUN_SUMMARY_TLV_TAG_ERR_CODE: {
            u32 v;
            if (tlv_read_u32_le(rec.payload, rec.len, v)) out_s.err.code = (u16)v;
            break;
        }
        case LAUNCHER_RUN_SUMMARY_TLV_TAG_ERR_FLAGS: {
            u32 v;
            if (tlv_read_u32_le(rec.payload, rec.len, v)) out_s.err.flags = (u32)v;
            break;
        }
        case LAUNCHER_RUN_SUMMARY_TLV_TAG_ERR_MSG_ID: {
            u32 v;
            if (tlv_read_u32_le(rec.payload, rec.len, v)) out_s.err.msg_id = (u32)v;
            break;
        }
        default:
            /* skip unknown */
            break;
        }
    }

    return true;
}

std::string launcher_run_summary_to_text(const LauncherRunSummary& s) {
    std::ostringstream oss;

    oss << "run_summary.schema_version=" << (u32)LAUNCHER_RUN_SUMMARY_TLV_VERSION << "\n";
    oss << "run_summary.run_id=0x" << std::hex << (unsigned long long)s.run_id << std::dec << "\n";
    oss << "run_summary.instance_id=" << s.instance_id << "\n";
    oss << "run_summary.outcome=" << s.outcome << "\n";
    oss << "run_summary.exit_code=" << s.exit_code << "\n";
    oss << "run_summary.termination_type=" << s.termination_type << "\n";
    oss << "run_summary.refusal_code=" << s.refusal_code << "\n";
    oss << "run_summary.err.domain=" << s.err.domain << "\n";
    oss << "run_summary.err.code=" << s.err.code << "\n";
    oss << "run_summary.err.flags=" << s.err.flags << "\n";
    oss << "run_summary.err.msg_id=" << s.err.msg_id << "\n";

    return oss.str();
}

} /* namespace launcher_core */
} /* namespace dom */
