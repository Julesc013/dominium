/*
FILE: source/dominium/launcher/core/src/audit/launcher_audit.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / launcher/core (foundation) / audit
RESPONSIBILITY: Implements audit model + TLV persistence (selected-and-why, skip-unknown, versioned root).
*/

#include "launcher_audit.h"

#include <sstream>

#include "launcher_tlv.h"

namespace dom {
namespace launcher_core {

namespace {
enum {
    TAG_RUN_ID = 2u,
    TAG_TIMESTAMP_US = 3u,
    TAG_INPUT = 4u,
    TAG_SELECTED_PROFILE = 5u,
    TAG_SELECTED_BACKEND = 6u,
    TAG_REASON = 7u,
    TAG_VERSION_STRING = 9u,
    TAG_BUILD_ID = 10u,
    TAG_GIT_HASH = 11u,
    TAG_MANIFEST_HASH64 = 12u,
    TAG_EXIT_RESULT = 13u
};

enum {
    TAG_B_SUBSYS_ID = 1u,
    TAG_B_SUBSYS_NAME = 2u,
    TAG_B_BACKEND_NAME = 3u,
    TAG_B_DET_GRADE = 4u,
    TAG_B_PERF_CLASS = 5u,
    TAG_B_PRIORITY = 6u,
    TAG_B_OVERRIDE = 7u
};
}

LauncherAuditBackend::LauncherAuditBackend()
    : subsystem_id(0u),
      subsystem_name(),
      backend_name(),
      determinism_grade(0u),
      perf_class(0u),
      priority(0u),
      chosen_by_override(0u) {
}

LauncherAuditLog::LauncherAuditLog()
    : schema_version(LAUNCHER_AUDIT_TLV_VERSION),
      run_id(0ull),
      timestamp_us(0ull),
      inputs(),
      selected_profile_id(),
      selected_backends(),
      reasons(),
      version_string(),
      build_id(),
      git_hash(),
      manifest_hash64(0ull),
      exit_result(0) {
}

bool launcher_audit_to_tlv_bytes(const LauncherAuditLog& audit,
                                 std::vector<unsigned char>& out_bytes) {
    TlvWriter w;
    size_t i;

    w.add_u32(LAUNCHER_TLV_TAG_SCHEMA_VERSION, LAUNCHER_AUDIT_TLV_VERSION);
    w.add_u64(TAG_RUN_ID, audit.run_id);
    w.add_u64(TAG_TIMESTAMP_US, audit.timestamp_us);
    w.add_string(TAG_SELECTED_PROFILE, audit.selected_profile_id);
    w.add_string(TAG_VERSION_STRING, audit.version_string);
    w.add_string(TAG_BUILD_ID, audit.build_id);
    w.add_string(TAG_GIT_HASH, audit.git_hash);
    w.add_u64(TAG_MANIFEST_HASH64, audit.manifest_hash64);
    w.add_i32(TAG_EXIT_RESULT, audit.exit_result);

    for (i = 0u; i < audit.inputs.size(); ++i) {
        w.add_string(TAG_INPUT, audit.inputs[i]);
    }
    for (i = 0u; i < audit.reasons.size(); ++i) {
        w.add_string(TAG_REASON, audit.reasons[i]);
    }
    for (i = 0u; i < audit.selected_backends.size(); ++i) {
        TlvWriter entry;
        const LauncherAuditBackend& b = audit.selected_backends[i];
        entry.add_u32(TAG_B_SUBSYS_ID, b.subsystem_id);
        entry.add_string(TAG_B_SUBSYS_NAME, b.subsystem_name);
        entry.add_string(TAG_B_BACKEND_NAME, b.backend_name);
        entry.add_u32(TAG_B_DET_GRADE, b.determinism_grade);
        entry.add_u32(TAG_B_PERF_CLASS, b.perf_class);
        entry.add_u32(TAG_B_PRIORITY, b.priority);
        entry.add_u32(TAG_B_OVERRIDE, b.chosen_by_override);
        w.add_container(TAG_SELECTED_BACKEND, entry.bytes());
    }

    out_bytes = w.bytes();
    return true;
}

bool launcher_audit_from_tlv_bytes(const unsigned char* data,
                                   size_t size,
                                   LauncherAuditLog& out_audit) {
    TlvReader r(data, size);
    TlvRecord rec;
    u32 version = 0u;

    out_audit = LauncherAuditLog();
    if (!tlv_read_schema_version_or_default(data, size, version, LAUNCHER_AUDIT_TLV_VERSION)) {
        return false;
    }
    out_audit.schema_version = version;
    if (version != LAUNCHER_AUDIT_TLV_VERSION) {
        return launcher_audit_migrate_tlv(version, LAUNCHER_AUDIT_TLV_VERSION, data, size, out_audit);
    }

    while (r.next(rec)) {
        switch (rec.tag) {
        case LAUNCHER_TLV_TAG_SCHEMA_VERSION:
            break;
        case TAG_RUN_ID: {
            u64 v;
            if (tlv_read_u64_le(rec.payload, rec.len, v)) {
                out_audit.run_id = v;
            }
            break;
        }
        case TAG_TIMESTAMP_US: {
            u64 v;
            if (tlv_read_u64_le(rec.payload, rec.len, v)) {
                out_audit.timestamp_us = v;
            }
            break;
        }
        case TAG_INPUT:
            out_audit.inputs.push_back(tlv_read_string(rec.payload, rec.len));
            break;
        case TAG_SELECTED_PROFILE:
            out_audit.selected_profile_id = tlv_read_string(rec.payload, rec.len);
            break;
        case TAG_REASON:
            out_audit.reasons.push_back(tlv_read_string(rec.payload, rec.len));
            break;
        case TAG_VERSION_STRING:
            out_audit.version_string = tlv_read_string(rec.payload, rec.len);
            break;
        case TAG_BUILD_ID:
            out_audit.build_id = tlv_read_string(rec.payload, rec.len);
            break;
        case TAG_GIT_HASH:
            out_audit.git_hash = tlv_read_string(rec.payload, rec.len);
            break;
        case TAG_MANIFEST_HASH64: {
            u64 v;
            if (tlv_read_u64_le(rec.payload, rec.len, v)) {
                out_audit.manifest_hash64 = v;
            }
            break;
        }
        case TAG_EXIT_RESULT: {
            i32 v;
            if (tlv_read_i32_le(rec.payload, rec.len, v)) {
                out_audit.exit_result = v;
            }
            break;
        }
        case TAG_SELECTED_BACKEND: {
            LauncherAuditBackend b;
            TlvReader er(rec.payload, (size_t)rec.len);
            TlvRecord e;
            while (er.next(e)) {
                if (e.tag == TAG_B_SUBSYS_ID) {
                    u32 v;
                    if (tlv_read_u32_le(e.payload, e.len, v)) {
                        b.subsystem_id = v;
                    }
                } else if (e.tag == TAG_B_SUBSYS_NAME) {
                    b.subsystem_name = tlv_read_string(e.payload, e.len);
                } else if (e.tag == TAG_B_BACKEND_NAME) {
                    b.backend_name = tlv_read_string(e.payload, e.len);
                } else if (e.tag == TAG_B_DET_GRADE) {
                    u32 v;
                    if (tlv_read_u32_le(e.payload, e.len, v)) {
                        b.determinism_grade = v;
                    }
                } else if (e.tag == TAG_B_PERF_CLASS) {
                    u32 v;
                    if (tlv_read_u32_le(e.payload, e.len, v)) {
                        b.perf_class = v;
                    }
                } else if (e.tag == TAG_B_PRIORITY) {
                    u32 v;
                    if (tlv_read_u32_le(e.payload, e.len, v)) {
                        b.priority = v;
                    }
                } else if (e.tag == TAG_B_OVERRIDE) {
                    u32 v;
                    if (tlv_read_u32_le(e.payload, e.len, v)) {
                        b.chosen_by_override = v;
                    }
                } else {
                    /* skip unknown */
                }
            }
            out_audit.selected_backends.push_back(b);
            break;
        }
        default:
            /* skip unknown */
            break;
        }
    }

    return true;
}

bool launcher_audit_migrate_tlv(u32 /*from_version*/,
                                u32 /*to_version*/,
                                const unsigned char* /*data*/,
                                size_t /*size*/,
                                LauncherAuditLog& /*out_audit*/) {
    /* Defined but not implemented in foundation. */
    return false;
}

std::string launcher_audit_to_text(const LauncherAuditLog& audit) {
    std::ostringstream oss;
    size_t i;
    oss << "Launcher Audit\n";
    oss << "run_id=" << audit.run_id << "\n";
    oss << "timestamp_us=" << audit.timestamp_us << "\n";
    oss << "profile=" << audit.selected_profile_id << "\n";
    oss << "exit=" << audit.exit_result << "\n";
    if (!audit.version_string.empty()) {
        oss << "version=" << audit.version_string << "\n";
    }
    if (!audit.build_id.empty()) {
        oss << "build_id=" << audit.build_id << "\n";
    }
    if (!audit.git_hash.empty()) {
        oss << "git_hash=" << audit.git_hash << "\n";
    }
    if (audit.manifest_hash64 != 0ull) {
        oss << "manifest_hash64=" << audit.manifest_hash64 << "\n";
    }
    oss << "inputs=" << audit.inputs.size() << "\n";
    for (i = 0u; i < audit.inputs.size(); ++i) {
        oss << "  argv[" << i << "]=" << audit.inputs[i] << "\n";
    }
    oss << "selected_backends=" << audit.selected_backends.size() << "\n";
    for (i = 0u; i < audit.selected_backends.size(); ++i) {
        const LauncherAuditBackend& b = audit.selected_backends[i];
        oss << "  subsys=" << b.subsystem_id << " backend=" << b.backend_name << " why_override=" << b.chosen_by_override << "\n";
    }
    oss << "reasons=" << audit.reasons.size() << "\n";
    for (i = 0u; i < audit.reasons.size(); ++i) {
        oss << "  why=" << audit.reasons[i] << "\n";
    }
    return oss.str();
}

} /* namespace launcher_core */
} /* namespace dom */
