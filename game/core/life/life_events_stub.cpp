/*
FILE: game/core/life/life_events_stub.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Game / life
RESPONSIBILITY: Implements continuation command stubs for lockstep/server-auth parity.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Command application is deterministic.
*/
#include "dominium/life/life_events_stub.h"

int life_cmd_continuation_apply(life_controller_binding_set* bindings,
                                const life_cmd_continuation_select* cmd)
{
    if (!bindings || !cmd) {
        return -1;
    }
    if (cmd->action == LIFE_CONT_ACTION_PENDING) {
        return 0;
    }
    if (cmd->action == LIFE_CONT_ACTION_TRANSFER) {
        return life_controller_bindings_set(bindings, cmd->controller_id, cmd->target_person_id);
    }
    if (cmd->action == LIFE_CONT_ACTION_SPECTATOR ||
        cmd->action == LIFE_CONT_ACTION_NONE) {
        return life_controller_bindings_set(bindings, cmd->controller_id, 0u);
    }
    return -2;
}
