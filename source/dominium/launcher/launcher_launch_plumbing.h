/*
FILE: source/dominium/launcher/launcher_launch_plumbing.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / launcher / launch_plumbing
RESPONSIBILITY: Launcher-side handshake generation, run-log persistence, deterministic validation, and process spawn plumbing.
ALLOWED DEPENDENCIES: `include/dominium/**`, `include/domino/**`, launcher core headers, and C++98 standard headers.
FORBIDDEN DEPENDENCIES: OS headers, UI headers, and any Plan 8 contract changes.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes/false; no exceptions required.
DETERMINISM: Canonical TLV; deterministic ordering for cleanup and listing.
*/
#ifndef DOMINIUM_LAUNCHER_LAUNCH_PLUMBING_H
#define DOMINIUM_LAUNCHER_LAUNCH_PLUMBING_H

#include <string>
#include <vector>

extern "C" {
#include "domino/profile.h"
}

#include "core/include/launcher_prelaunch.h"

namespace dom {

struct LaunchTarget {
    u32 is_tool; /* 0=game, 1=tool */
    std::string tool_id;

    LaunchTarget();
};

bool launcher_parse_launch_target(const std::string& text,
                                  LaunchTarget& out_target,
                                  std::string& out_error);

std::string launcher_launch_target_to_string(const LaunchTarget& t);

struct LaunchRunResult {
    u32 ok; /* 0/1 */
    u64 run_id;
    std::string run_dir;
    std::string handshake_path;
    std::string launch_config_path;
    std::string audit_path;
    std::string selection_summary_path;
    std::string run_summary_path;
    std::string caps_path;
    std::string exit_status_path;

    u32 refused; /* 0/1 */
    u32 refusal_code;
    std::string refusal_detail;

    u32 spawned; /* 0/1 */
    u32 waited;  /* 0/1 */
    i32 child_exit_code;

    std::string error;

    LaunchRunResult();
};

/* Executes a launch attempt (game or tool executable) with per-attempt run logs:
 * - Writes handshake and per-run audit TLV into `instances/<id>/logs/runs/<run_id>/`
 * - Appends `--handshake=<path>` to argv and spawns the child
 * - Cleanup: keeps last `keep_last_runs` run directories (best-effort)
 */
bool launcher_execute_launch_attempt(const std::string& state_root,
                                     const std::string& instance_id,
                                     const LaunchTarget& target,
                                     const dom_profile* profile,
                                     const std::string& executable_path,
                                     const std::vector<std::string>& child_args,
                                     u32 wait_for_exit,
                                     u32 keep_last_runs,
                                     const dom::launcher_core::LauncherLaunchOverrides& overrides,
                                     LaunchRunResult& out_result);

/* Lists run directory ids under `instances/<id>/logs/runs/` (sorted lexicographic). */
bool launcher_list_instance_runs(const std::string& state_root,
                                 const std::string& instance_id,
                                 std::vector<std::string>& out_run_ids,
                                 std::string& out_error);

} /* namespace dom */

#endif /* DOMINIUM_LAUNCHER_LAUNCH_PLUMBING_H */
