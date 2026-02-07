/*
FILE: include/dominium/life/life_events_stub.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / life
RESPONSIBILITY: Defines lockstep/server-auth continuation command stubs.
ALLOWED DEPENDENCIES: `game/include/**`, `engine/include/**` public headers, and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; product-layer runtime code.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Commands must be deterministic and replay-safe.
*/
#ifndef DOMINIUM_LIFE_EVENTS_STUB_H
#define DOMINIUM_LIFE_EVENTS_STUB_H

#include "dominium/life/controller_binding.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct life_cmd_continuation_select {
    u64 controller_id;
    u32 policy_id;
    u64 target_person_id;
    u32 action;
} life_cmd_continuation_select;

/* Purpose: Apply a continuation selection command to bindings. */
int life_cmd_continuation_apply(life_controller_binding_set* bindings,
                                const life_cmd_continuation_select* cmd);
int life_cmd_continuation_apply_ex(life_controller_binding_set* bindings,
                                   const life_cmd_continuation_select* cmd,
                                   life_refusal_code* out_refusal);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_LIFE_EVENTS_STUB_H */
