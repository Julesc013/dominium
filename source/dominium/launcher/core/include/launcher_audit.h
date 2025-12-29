/*
FILE: source/dominium/launcher/core/include/launcher_audit.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / launcher/core (foundation) / audit
RESPONSIBILITY: Deterministic audit record model + TLV persistence schema; "selected-and-why" must be emitted every run.
ALLOWED DEPENDENCIES: C++98 standard headers and `include/domino/**` base types only.
FORBIDDEN DEPENDENCIES: Platform APIs, renderer/UI headers, and any Plan 8 contract changes.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes/false; no exceptions.
DETERMINISM: Content is derived solely from explicit inputs and deterministic selection results; serialization is canonical.
*/
#ifndef DOMINIUM_LAUNCHER_CORE_LAUNCHER_AUDIT_H
#define DOMINIUM_LAUNCHER_CORE_LAUNCHER_AUDIT_H

#include <string>
#include <vector>

extern "C" {
#include "domino/core/types.h"
}

#include "dominium/core_err.h"

namespace dom {
namespace launcher_core {

/* TLV schema version for audit log root. */
enum { LAUNCHER_AUDIT_TLV_VERSION = 1u };

/* Audit Log TLV schema (versioned root; skip-unknown; mandatory per launcher execution).
 *
 * Root TLV records:
 * - `LAUNCHER_TLV_TAG_SCHEMA_VERSION` (u32): must be `LAUNCHER_AUDIT_TLV_VERSION`.
 * - `LAUNCHER_AUDIT_TLV_TAG_RUN_ID` (u64): unique run id for this launcher execution.
 * - `LAUNCHER_AUDIT_TLV_TAG_TIMESTAMP_US` (u64): monotonic timestamp (microseconds).
 * - `LAUNCHER_AUDIT_TLV_TAG_INPUT` (string, repeated): argv / explicit inputs.
 * - `LAUNCHER_AUDIT_TLV_TAG_SELECTED_PROFILE` (string)
 * - `LAUNCHER_AUDIT_TLV_TAG_SELECTED_BACKEND` (container, repeated): selected subsystem backends.
 * - `LAUNCHER_AUDIT_TLV_TAG_REASON` (string, repeated): "why" records (no silent decisions).
 * - `LAUNCHER_AUDIT_TLV_TAG_VERSION_STRING` (string)
 * - `LAUNCHER_AUDIT_TLV_TAG_BUILD_ID` (string)
 * - `LAUNCHER_AUDIT_TLV_TAG_GIT_HASH` (string)
 * - `LAUNCHER_AUDIT_TLV_TAG_MANIFEST_HASH64` (u64)
 * - `LAUNCHER_AUDIT_TLV_TAG_EXIT_RESULT` (i32)
 * - `LAUNCHER_AUDIT_TLV_TAG_SELECTION_SUMMARY` (container, optional): embedded `selection_summary.tlv` bytes (see `launcher_selection_summary.h`).
 * - `LAUNCHER_AUDIT_TLV_TAG_ERR_DOMAIN` (u32, optional)
 * - `LAUNCHER_AUDIT_TLV_TAG_ERR_CODE` (u32, optional)
 * - `LAUNCHER_AUDIT_TLV_TAG_ERR_FLAGS` (u32, optional)
 * - `LAUNCHER_AUDIT_TLV_TAG_ERR_MSG_ID` (u32, optional)
 * - `LAUNCHER_AUDIT_TLV_TAG_ERR_DETAIL` (container, repeated, optional)
 * - `LAUNCHER_AUDIT_TLV_TAG_REASON_MSG_ID` (u32, repeated, optional)
 *
 * Selected-backend entry payload (container TLV):
 * - `LAUNCHER_AUDIT_BACKEND_TLV_TAG_SUBSYS_ID` (u32)
 * - `LAUNCHER_AUDIT_BACKEND_TLV_TAG_SUBSYS_NAME` (string)
 * - `LAUNCHER_AUDIT_BACKEND_TLV_TAG_BACKEND_NAME` (string)
 * - `LAUNCHER_AUDIT_BACKEND_TLV_TAG_DET_GRADE` (u32)
 * - `LAUNCHER_AUDIT_BACKEND_TLV_TAG_PERF_CLASS` (u32)
 * - `LAUNCHER_AUDIT_BACKEND_TLV_TAG_PRIORITY` (u32)
 * - `LAUNCHER_AUDIT_BACKEND_TLV_TAG_OVERRIDE` (u32; 0/1)
 */
enum LauncherAuditTlvTag {
    LAUNCHER_AUDIT_TLV_TAG_RUN_ID = 2u,
    LAUNCHER_AUDIT_TLV_TAG_TIMESTAMP_US = 3u,
    LAUNCHER_AUDIT_TLV_TAG_INPUT = 4u,
    LAUNCHER_AUDIT_TLV_TAG_SELECTED_PROFILE = 5u,
    LAUNCHER_AUDIT_TLV_TAG_SELECTED_BACKEND = 6u,
    LAUNCHER_AUDIT_TLV_TAG_REASON = 7u,
    LAUNCHER_AUDIT_TLV_TAG_VERSION_STRING = 9u,
    LAUNCHER_AUDIT_TLV_TAG_BUILD_ID = 10u,
    LAUNCHER_AUDIT_TLV_TAG_GIT_HASH = 11u,
    LAUNCHER_AUDIT_TLV_TAG_MANIFEST_HASH64 = 12u,
    LAUNCHER_AUDIT_TLV_TAG_EXIT_RESULT = 13u,
    LAUNCHER_AUDIT_TLV_TAG_SELECTION_SUMMARY = 14u,
    LAUNCHER_AUDIT_TLV_TAG_ERR_DOMAIN = 20u,
    LAUNCHER_AUDIT_TLV_TAG_ERR_CODE = 21u,
    LAUNCHER_AUDIT_TLV_TAG_ERR_FLAGS = 22u,
    LAUNCHER_AUDIT_TLV_TAG_ERR_MSG_ID = 23u,
    LAUNCHER_AUDIT_TLV_TAG_ERR_DETAIL = 24u,
    LAUNCHER_AUDIT_TLV_TAG_REASON_MSG_ID = 25u
};

enum LauncherAuditBackendTlvTag {
    LAUNCHER_AUDIT_BACKEND_TLV_TAG_SUBSYS_ID = 1u,
    LAUNCHER_AUDIT_BACKEND_TLV_TAG_SUBSYS_NAME = 2u,
    LAUNCHER_AUDIT_BACKEND_TLV_TAG_BACKEND_NAME = 3u,
    LAUNCHER_AUDIT_BACKEND_TLV_TAG_DET_GRADE = 4u,
    LAUNCHER_AUDIT_BACKEND_TLV_TAG_PERF_CLASS = 5u,
    LAUNCHER_AUDIT_BACKEND_TLV_TAG_PRIORITY = 6u,
    LAUNCHER_AUDIT_BACKEND_TLV_TAG_OVERRIDE = 7u
};

enum LauncherAuditErrDetailTlvTag {
    LAUNCHER_AUDIT_ERR_TLV_TAG_KEY = 1u,
    LAUNCHER_AUDIT_ERR_TLV_TAG_TYPE = 2u,
    LAUNCHER_AUDIT_ERR_TLV_TAG_VALUE_U32 = 3u,
    LAUNCHER_AUDIT_ERR_TLV_TAG_VALUE_U64 = 4u
};

struct LauncherAuditBackend {
    u32 subsystem_id;
    std::string subsystem_name;
    std::string backend_name;

    u32 determinism_grade;
    u32 perf_class;
    u32 priority;
    u32 chosen_by_override;

    LauncherAuditBackend();
};

struct LauncherAuditLog {
    u32 schema_version;

    u64 run_id;
    u64 timestamp_us;

    std::vector<std::string> inputs;

    std::string selected_profile_id;
    std::vector<LauncherAuditBackend> selected_backends;

    std::vector<std::string> reasons;
    std::vector<u32> reason_msg_ids;

    std::string version_string; /* launcher version */
    std::string build_id;       /* optional */
    std::string git_hash;       /* optional */
    u64 manifest_hash64;        /* optional (0 when absent) */

    i32 exit_result;
    err_t err;

    u32 has_selection_summary; /* 0/1 */
    std::vector<unsigned char> selection_summary_tlv; /* optional; raw TLV bytes */

    LauncherAuditLog();
};

bool launcher_audit_to_tlv_bytes(const LauncherAuditLog& audit,
                                 std::vector<unsigned char>& out_bytes);
bool launcher_audit_from_tlv_bytes(const unsigned char* data,
                                   size_t size,
                                   LauncherAuditLog& out_audit);

/* Human-readable dump (no UI required). */
std::string launcher_audit_to_text(const LauncherAuditLog& audit);

/* Migration hook (defined but not implemented in foundation).
 * Returns false until a future prompt provides migrations.
 */
bool launcher_audit_migrate_tlv(u32 from_version,
                                u32 to_version,
                                const unsigned char* data,
                                size_t size,
                                LauncherAuditLog& out_audit);

} /* namespace launcher_core */
} /* namespace dom */

#endif /* DOMINIUM_LAUNCHER_CORE_LAUNCHER_AUDIT_H */
