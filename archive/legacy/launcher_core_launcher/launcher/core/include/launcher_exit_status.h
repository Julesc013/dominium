/*
FILE: source/dominium/launcher/core/include/launcher_exit_status.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / launcher/core (ecosystem) / exit_status
RESPONSIBILITY: Per-run exit_status.tlv schema + deterministic encode/decode helpers (versioned root; skip-unknown).
ALLOWED DEPENDENCIES: C++98 standard headers and launcher core TLV helpers only.
FORBIDDEN DEPENDENCIES: OS headers, renderer/UI headers, and any Plan 8 contract changes.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes/false; no exceptions required.
DETERMINISM: Canonical encoding with explicit ordering; integers are little-endian; skip-unknown supported.
*/
#ifndef DOMINIUM_LAUNCHER_CORE_LAUNCHER_EXIT_STATUS_H
#define DOMINIUM_LAUNCHER_CORE_LAUNCHER_EXIT_STATUS_H

#include <string>
#include <vector>

extern "C" {
#include "domino/core/types.h"
}

namespace dom {
namespace launcher_core {

/* TLV schema version for exit_status.tlv root. */
enum { LAUNCHER_EXIT_STATUS_TLV_VERSION = 1u };

enum LauncherTerminationType {
    LAUNCHER_TERM_NORMAL = 0u,
    LAUNCHER_TERM_CRASH = 1u,
    LAUNCHER_TERM_REFUSED = 2u,
    LAUNCHER_TERM_UNKNOWN = 3u
};

struct LauncherExitStatus {
    u32 schema_version;

    u64 run_id;
    i32 exit_code;
    u32 termination_type; /* LauncherTerminationType */

    u64 timestamp_start_us;
    u64 timestamp_end_us;

    u32 stdout_capture_supported; /* 0/1 */
    u32 stderr_capture_supported; /* 0/1 */

    LauncherExitStatus();
};

bool launcher_exit_status_to_tlv_bytes(const LauncherExitStatus& st,
                                       std::vector<unsigned char>& out_bytes);
bool launcher_exit_status_from_tlv_bytes(const unsigned char* data,
                                         size_t size,
                                         LauncherExitStatus& out_st);

} /* namespace launcher_core */
} /* namespace dom */

#endif /* DOMINIUM_LAUNCHER_CORE_LAUNCHER_EXIT_STATUS_H */

