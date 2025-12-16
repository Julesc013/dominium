/*
FILE: include/domino/input.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / input
RESPONSIBILITY: Defines the public contract for `input` (types/constants/function signatures); does NOT provide implementation.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/SPEC_ABI_TEMPLATES.md` where ABI stability matters.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOMINO_INPUT_H_INCLUDED
#define DOMINO_INPUT_H_INCLUDED

#include "domino/baseline.h"
#include "domino/sys.h"

#ifdef __cplusplus
extern "C" {
#endif

#define DOM_INPUT_MAX_KEYS              256
#define DOM_INPUT_MAX_MOUSE_BUTTONS     8
#define DOM_INPUT_MAX_GAMEPADS          4
#define DOM_INPUT_MAX_GAMEPAD_BUTTONS   16
#define DOM_INPUT_MAX_GAMEPAD_AXES      8

/* dom_input_state: Public type used by `input`. */
typedef struct dom_input_state {
    bool    keys[DOM_INPUT_MAX_KEYS];
    bool    mouse_buttons[DOM_INPUT_MAX_MOUSE_BUTTONS];
    int32_t mouse_x;
    int32_t mouse_y;
    int32_t mouse_dx;
    int32_t mouse_dy;
    int32_t mouse_wheel_x;
    int32_t mouse_wheel_y;
    bool    gamepad_buttons[DOM_INPUT_MAX_GAMEPADS][DOM_INPUT_MAX_GAMEPAD_BUTTONS];
    float   gamepad_axes[DOM_INPUT_MAX_GAMEPADS][DOM_INPUT_MAX_GAMEPAD_AXES];
} dom_input_state;

/* Purpose: Reset input.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 */
void dom_input_reset(dom_input_state* st);
/* Purpose: Consume event.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 */
void dom_input_consume_event(dom_input_state* st, const dsys_event* ev);
/* Purpose: Axis input.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/CONTRACTS.md#Return Values / Errors`.
 */
float dom_input_axis(const char* name);
/* Purpose: Action input.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: `true` on success; `false` on failure.
 */
bool  dom_input_action(const char* name);

#ifdef __cplusplus
}
#endif

#endif /* DOMINO_INPUT_H_INCLUDED */
