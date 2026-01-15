/*
FILE: include/domino/state/state.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / state/state
RESPONSIBILITY: Defines the public contract for `state` (types/constants/function signatures); does NOT provide implementation.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/SPEC_ABI_TEMPLATES.md` where ABI stability matters.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOMINO_STATE_STATE_H
#define DOMINO_STATE_STATE_H

#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

/* d_state: Public type used by `state`. */
typedef struct d_state {
    void (*on_enter)(void* userdata);
    void (*on_update)(void* userdata);
    void (*on_exit)(void* userdata);
} d_state;

/* d_state_machine: Public type used by `state`. */
typedef struct d_state_machine {
    u32      current;
    d_state* states;
    u32      count;
    void*    userdata;
} d_state_machine;

/* Purpose: Init state machine.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 */
void d_state_machine_init(d_state_machine* sm,
                          d_state* states,
                          u32 count,
                          void* userdata);
/* Purpose: Machine update.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 */
void d_state_machine_update(d_state_machine* sm);
/* Purpose: Set state machine.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 */
void d_state_machine_set(d_state_machine* sm, u32 index);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINO_STATE_STATE_H */
