/*
FILE: source/dominium/launcher/core/include/launcher_launch_attempt.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / launcher/core (foundation) / launch_attempt
RESPONSIBILITY: Failure tracking, auto-recovery suggestion, and post-launch bookkeeping (audit + last-known-good) for launcher instances.
ALLOWED DEPENDENCIES: C++98 standard headers and launcher core prelaunch/history/instance ops and artifact ops; services facade.
FORBIDDEN DEPENDENCIES: OS headers, renderer/UI headers, and any Plan 8 contract changes.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes/false; detailed reasons emitted to audit and optionally returned in out_error.
DETERMINISM: Decisions are deterministic given explicit inputs and injected services (FS/time); no filesystem enumeration ordering.
*/
#ifndef DOMINIUM_LAUNCHER_CORE_LAUNCHER_LAUNCH_ATTEMPT_H
#define DOMINIUM_LAUNCHER_CORE_LAUNCHER_LAUNCH_ATTEMPT_H

#include <string>

extern "C" {
#include "launcher_core_api.h"
}

#include "launcher_instance_launch_history.h"
#include "launcher_prelaunch.h"

namespace dom {
namespace launcher_core {

struct LauncherAuditLog; /* forward-declared; see launcher_audit.h */

struct LauncherRecoverySuggestion {
    u32 threshold;
    u32 consecutive_failures;
    u32 suggest_safe_mode; /* 0/1 */
    u32 suggest_rollback;  /* 0/1 */
    u32 auto_entered_safe_mode; /* 0/1 */

    LauncherRecoverySuggestion();
};

/* Prepare a launch attempt:
 * - Loads per-instance history and applies auto safe-mode fallback after threshold.
 * - Builds a prelaunch plan (config resolution + validation).
 * - Emits audit records for recovery state, safe mode selection, resolved config, and validation results.
 *
 * Returns false only on fatal errors (missing services, cannot load manifest/config/history).
 * Validation failures are represented in `out_plan.validation` and still return true.
 */
bool launcher_launch_prepare_attempt(const launcher_services_api_v1* services,
                                    const LauncherProfile* profile_constraints, /* optional; may be NULL */
                                    const std::string& instance_id,
                                    const std::string& state_root_override,
                                    const LauncherLaunchOverrides& requested_overrides,
                                    LauncherPrelaunchPlan& out_plan,
                                    LauncherRecoverySuggestion& out_recovery,
                                    LauncherAuditLog* audit,
                                    std::string* out_error);

/* Finalize a launch attempt:
 * - Appends a record to `<instance_root>/logs/launch_history.tlv`
 * - On successful non-safe-mode launch, updates last-known-good via verify (creates/updates known_good.tlv + snapshot).
 * - Safe mode never writes back unless `confirm_safe_mode_writeback=1`.
 */
bool launcher_launch_finalize_attempt(const launcher_services_api_v1* services,
                                     const LauncherPrelaunchPlan& plan,
                                     u32 outcome, /* LauncherLaunchOutcome */
                                     i32 exit_code,
                                     const std::string& detail,
                                     u32 confirm_safe_mode_writeback,
                                     LauncherAuditLog* audit,
                                     std::string* out_error);

} /* namespace launcher_core */
} /* namespace dom */

#endif /* DOMINIUM_LAUNCHER_CORE_LAUNCHER_LAUNCH_ATTEMPT_H */

