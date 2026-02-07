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
NOTE: PERMANENT STUB — explicit refusal until LIFE continuation execution is implemented.
*/
#include "dominium/life/life_events_stub.h"

int life_cmd_continuation_apply(life_controller_binding_set* bindings,
                                const life_cmd_continuation_select* cmd)
{
    life_refusal_code refusal = LIFE_REFUSAL_NONE;
    return life_cmd_continuation_apply_ex(bindings, cmd, &refusal);
}

int life_cmd_continuation_apply_ex(life_controller_binding_set* bindings,
                                   const life_cmd_continuation_select* cmd,
                                   life_refusal_code* out_refusal)
{
    (void)bindings;
    (void)cmd;
    if (out_refusal) {
        *out_refusal = LIFE_REFUSAL_NOT_IMPLEMENTED;
    }
    return -1;
}
