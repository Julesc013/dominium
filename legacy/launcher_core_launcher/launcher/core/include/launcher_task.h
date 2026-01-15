/*
FILE: source/dominium/launcher/core/include/launcher_task.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / launcher/core (foundation) / task
RESPONSIBILITY: Task model + deterministic state transitions (pure reducers; no side effects).
ALLOWED DEPENDENCIES: C++98 standard headers and `include/domino/**` base types only.
FORBIDDEN DEPENDENCIES: Platform APIs, renderer/UI headers, and any Plan 8 contract changes.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: N/A (state transitions expressed via enums and explicit results).
DETERMINISM: Reducers are side-effect free and depend only on explicit inputs.
*/
#ifndef DOMINIUM_LAUNCHER_CORE_LAUNCHER_TASK_H
#define DOMINIUM_LAUNCHER_CORE_LAUNCHER_TASK_H

#include <string>

extern "C" {
#include "domino/core/types.h"
}

#include "launcher_artifact.h"

namespace dom {
namespace launcher_core {

enum LauncherTaskKind {
    LAUNCHER_TASK_INSTALL = 1,
    LAUNCHER_TASK_VERIFY  = 2,
    LAUNCHER_TASK_LAUNCH  = 3
};

enum LauncherTaskState {
    LAUNCHER_TASK_PENDING = 0,
    LAUNCHER_TASK_RUNNING = 1,
    LAUNCHER_TASK_SUCCEEDED = 2,
    LAUNCHER_TASK_FAILED = 3,
    LAUNCHER_TASK_CANCELED = 4
};

struct LauncherTask {
    u64 task_id;
    u32 kind;
    u32 state;

    LauncherArtifactRef target;

    u32 progress_permille; /* 0..1000 */
    i32 result_code;       /* 0 success; negative failure; domain-specific */
    std::string reason;

    LauncherTask();
};

enum LauncherTaskActionKind {
    LAUNCHER_TASK_ACT_START = 1,
    LAUNCHER_TASK_ACT_PROGRESS = 2,
    LAUNCHER_TASK_ACT_SUCCEED = 3,
    LAUNCHER_TASK_ACT_FAIL = 4,
    LAUNCHER_TASK_ACT_CANCEL = 5
};

struct LauncherTaskAction {
    u32 kind;
    u32 progress_permille;
    i32 result_code;
    std::string reason;

    LauncherTaskAction();
};

LauncherTask launcher_task_reduce(const LauncherTask& cur, const LauncherTaskAction& act);

} /* namespace launcher_core */
} /* namespace dom */

#endif /* DOMINIUM_LAUNCHER_CORE_LAUNCHER_TASK_H */

