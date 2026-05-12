/*
FILE: source/dominium/launcher/core/include/launcher_instance_launch_history.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / launcher/core (foundation) / instance_launch_history
RESPONSIBILITY: Per-instance launch attempt history (failure tracking) + TLV persistence (versioned; skip-unknown; deterministic).
ALLOWED DEPENDENCIES: C++98 standard headers and launcher core instance paths and TLV helpers; services facade types.
FORBIDDEN DEPENDENCIES: OS headers, renderer/UI headers, and any Plan 8 contract changes.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes/false; no exceptions required.
DETERMINISM: Canonical encoding; stable ordering; unknown tags are preserved.
*/
#ifndef DOMINIUM_LAUNCHER_CORE_LAUNCHER_INSTANCE_LAUNCH_HISTORY_H
#define DOMINIUM_LAUNCHER_CORE_LAUNCHER_INSTANCE_LAUNCH_HISTORY_H

#include <string>
#include <vector>

extern "C" {
#include "launcher_core_api.h"
}

#include "launcher_instance.h"     /* LauncherTlvUnknownRecord */
#include "launcher_instance_ops.h" /* LauncherInstancePaths */

namespace dom {
namespace launcher_core {

enum { LAUNCHER_INSTANCE_LAUNCH_HISTORY_TLV_VERSION = 1u };

enum LauncherInstanceLaunchHistoryTlvTag {
    LAUNCHER_INSTANCE_LAUNCH_HISTORY_TLV_TAG_INSTANCE_ID = 2u,
    LAUNCHER_INSTANCE_LAUNCH_HISTORY_TLV_TAG_MAX_ENTRIES = 3u,
    LAUNCHER_INSTANCE_LAUNCH_HISTORY_TLV_TAG_ATTEMPT = 4u
};

enum LauncherInstanceLaunchAttemptTlvTag {
    LAUNCHER_INSTANCE_LAUNCH_ATTEMPT_TLV_TAG_TIMESTAMP_US = 1u,
    LAUNCHER_INSTANCE_LAUNCH_ATTEMPT_TLV_TAG_MANIFEST_HASH64 = 2u,
    LAUNCHER_INSTANCE_LAUNCH_ATTEMPT_TLV_TAG_CONFIG_HASH64 = 3u,
    LAUNCHER_INSTANCE_LAUNCH_ATTEMPT_TLV_TAG_SAFE_MODE = 4u,
    LAUNCHER_INSTANCE_LAUNCH_ATTEMPT_TLV_TAG_OUTCOME = 5u,
    LAUNCHER_INSTANCE_LAUNCH_ATTEMPT_TLV_TAG_EXIT_CODE = 6u,
    LAUNCHER_INSTANCE_LAUNCH_ATTEMPT_TLV_TAG_DETAIL = 7u
};

enum LauncherLaunchOutcome {
    LAUNCHER_LAUNCH_OUTCOME_SUCCESS = 0u,
    LAUNCHER_LAUNCH_OUTCOME_CRASH = 1u,
    LAUNCHER_LAUNCH_OUTCOME_REFUSAL = 2u,
    LAUNCHER_LAUNCH_OUTCOME_MISSING_ARTIFACT = 3u
};

struct LauncherInstanceLaunchAttempt {
    u64 timestamp_us;
    u64 manifest_hash64;
    u64 config_hash64;
    u32 safe_mode; /* 0/1 */
    u32 outcome;   /* LauncherLaunchOutcome */
    i32 exit_code; /* meaningful for crash; otherwise 0 */
    std::string detail;

    std::vector<LauncherTlvUnknownRecord> unknown_fields;

    LauncherInstanceLaunchAttempt();
};

struct LauncherInstanceLaunchHistory {
    u32 schema_version;
    std::string instance_id;
    u32 max_entries;

    std::vector<LauncherInstanceLaunchAttempt> attempts; /* chronological; oldest first */
    std::vector<LauncherTlvUnknownRecord> unknown_fields;

    LauncherInstanceLaunchHistory();
};

LauncherInstanceLaunchHistory launcher_instance_launch_history_make_default(const std::string& instance_id,
                                                                            u32 max_entries);

bool launcher_instance_launch_history_to_tlv_bytes(const LauncherInstanceLaunchHistory& h,
                                                   std::vector<unsigned char>& out_bytes);
bool launcher_instance_launch_history_from_tlv_bytes(const unsigned char* data,
                                                     size_t size,
                                                     LauncherInstanceLaunchHistory& out_h);

/* File helpers:
 * - Path: `<instance_root>/logs/launch_history.tlv`
 * - Missing file => returns an empty history with defaults.
 */
std::string launcher_instance_launch_history_path(const LauncherInstancePaths& paths);

bool launcher_instance_launch_history_load(const launcher_services_api_v1* services,
                                           const LauncherInstancePaths& paths,
                                           LauncherInstanceLaunchHistory& out_h);
bool launcher_instance_launch_history_store(const launcher_services_api_v1* services,
                                            const LauncherInstancePaths& paths,
                                            const LauncherInstanceLaunchHistory& h);

/* Mutator: appends and truncates to `max_entries` deterministically. */
void launcher_instance_launch_history_append(LauncherInstanceLaunchHistory& h,
                                             const LauncherInstanceLaunchAttempt& attempt);

} /* namespace launcher_core */
} /* namespace dom */

#endif /* DOMINIUM_LAUNCHER_CORE_LAUNCHER_INSTANCE_LAUNCH_HISTORY_H */

