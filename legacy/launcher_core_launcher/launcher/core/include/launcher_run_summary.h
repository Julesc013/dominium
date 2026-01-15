/*
FILE: source/dominium/launcher/core/include/launcher_run_summary.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / launcher/core (foundation) / run_summary
RESPONSIBILITY: Deterministic per-run summary snapshot (TLV) for diagnostics and UI edges.
ALLOWED DEPENDENCIES: C++98 standard headers and launcher core TLV helpers; no OS/UI headers.
FORBIDDEN DEPENDENCIES: Platform APIs, renderer/UI headers, and any Plan 8 contract changes.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes/false; no exceptions required.
DETERMINISM: Canonical encoding; stable field ordering; skip-unknown semantics.
*/
#ifndef DOMINIUM_LAUNCHER_CORE_LAUNCHER_RUN_SUMMARY_H
#define DOMINIUM_LAUNCHER_CORE_LAUNCHER_RUN_SUMMARY_H

#include <string>
#include <vector>

extern "C" {
#include "domino/core/types.h"
}

#include "dominium/core_err.h"

namespace dom {
namespace launcher_core {

enum { LAUNCHER_RUN_SUMMARY_TLV_VERSION = 1u };

enum LauncherRunSummaryTlvTag {
    LAUNCHER_RUN_SUMMARY_TLV_TAG_RUN_ID = 2u,
    LAUNCHER_RUN_SUMMARY_TLV_TAG_INSTANCE_ID = 3u,
    LAUNCHER_RUN_SUMMARY_TLV_TAG_OUTCOME = 4u,      /* LauncherLaunchOutcome */
    LAUNCHER_RUN_SUMMARY_TLV_TAG_EXIT_CODE = 5u,
    LAUNCHER_RUN_SUMMARY_TLV_TAG_TERM_TYPE = 6u,
    LAUNCHER_RUN_SUMMARY_TLV_TAG_REFUSAL_CODE = 7u,
    LAUNCHER_RUN_SUMMARY_TLV_TAG_ERR_DOMAIN = 8u,
    LAUNCHER_RUN_SUMMARY_TLV_TAG_ERR_CODE = 9u,
    LAUNCHER_RUN_SUMMARY_TLV_TAG_ERR_FLAGS = 10u,
    LAUNCHER_RUN_SUMMARY_TLV_TAG_ERR_MSG_ID = 11u
};

struct LauncherRunSummary {
    u32 schema_version;
    u64 run_id;
    std::string instance_id;
    u32 outcome; /* see launcher_instance_launch_history.h */
    i32 exit_code;
    u32 termination_type;
    u32 refusal_code;
    err_t err;

    LauncherRunSummary();
};

bool launcher_run_summary_to_tlv_bytes(const LauncherRunSummary& s,
                                       std::vector<unsigned char>& out_bytes);
bool launcher_run_summary_from_tlv_bytes(const unsigned char* data,
                                         size_t size,
                                         LauncherRunSummary& out_s);

std::string launcher_run_summary_to_text(const LauncherRunSummary& s);

} /* namespace launcher_core */
} /* namespace dom */

#endif /* DOMINIUM_LAUNCHER_CORE_LAUNCHER_RUN_SUMMARY_H */
