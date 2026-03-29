/*
FILE: source/dominium/launcher/core/src/task/launcher_task.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / launcher/core (foundation) / task
RESPONSIBILITY: Implements deterministic task reducers (pure).
*/

#include "launcher_task.h"

namespace dom {
namespace launcher_core {

LauncherTask::LauncherTask()
    : task_id(0ull),
      kind((u32)LAUNCHER_TASK_INSTALL),
      state((u32)LAUNCHER_TASK_PENDING),
      target(),
      progress_permille(0u),
      result_code(0),
      reason() {
}

LauncherTaskAction::LauncherTaskAction()
    : kind((u32)LAUNCHER_TASK_ACT_START),
      progress_permille(0u),
      result_code(0),
      reason() {
}

static LauncherTask apply_progress(const LauncherTask& cur, u32 permille) {
    LauncherTask next = cur;
    if (permille > 1000u) {
        permille = 1000u;
    }
    next.progress_permille = permille;
    return next;
}

LauncherTask launcher_task_reduce(const LauncherTask& cur, const LauncherTaskAction& act) {
    LauncherTask next = cur;

    switch (act.kind) {
    case LAUNCHER_TASK_ACT_START:
        if (cur.state == (u32)LAUNCHER_TASK_PENDING) {
            next.state = (u32)LAUNCHER_TASK_RUNNING;
            next.reason = act.reason;
        }
        break;
    case LAUNCHER_TASK_ACT_PROGRESS:
        if (cur.state == (u32)LAUNCHER_TASK_RUNNING) {
            next = apply_progress(cur, act.progress_permille);
        }
        break;
    case LAUNCHER_TASK_ACT_SUCCEED:
        if (cur.state == (u32)LAUNCHER_TASK_RUNNING) {
            next.state = (u32)LAUNCHER_TASK_SUCCEEDED;
            next.progress_permille = 1000u;
            next.result_code = 0;
            next.reason = act.reason;
        }
        break;
    case LAUNCHER_TASK_ACT_FAIL:
        if (cur.state == (u32)LAUNCHER_TASK_RUNNING) {
            next.state = (u32)LAUNCHER_TASK_FAILED;
            next.result_code = act.result_code;
            next.reason = act.reason;
        }
        break;
    case LAUNCHER_TASK_ACT_CANCEL:
        if (cur.state == (u32)LAUNCHER_TASK_PENDING || cur.state == (u32)LAUNCHER_TASK_RUNNING) {
            next.state = (u32)LAUNCHER_TASK_CANCELED;
            next.reason = act.reason;
        }
        break;
    default:
        break;
    }

    return next;
}

} /* namespace launcher_core */
} /* namespace dom */

