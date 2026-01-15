/*
FILE: include/domino/input/input.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / input/input
RESPONSIBILITY: Defines the public contract for `input` (types/constants/function signatures); does NOT provide implementation.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/SPEC_ABI_TEMPLATES.md` where ABI stability matters.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOMINO_INPUT_INPUT_H
#define DOMINO_INPUT_INPUT_H

#include "domino/core/types.h"
#include "domino/input/ime.h"

#ifdef __cplusplus
extern "C" {
#endif

/* d_input_event_type: Public type used by `input`. */
typedef enum d_input_event_type {
    D_INPUT_KEYDOWN = 0,
    D_INPUT_KEYUP,
    D_INPUT_CHAR,
    D_INPUT_MOUSEMOVE,
    D_INPUT_MOUSEDOWN,
    D_INPUT_MOUSEUP,
    D_INPUT_MOUSEWHEEL,
    D_INPUT_IME_TEXT,
    D_INPUT_IME_COMPOSITION,
    D_INPUT_CONTROLLER
} d_input_event_type;

/* d_input_event: Public type used by `input`. */
typedef struct d_input_event {
    d_input_event_type type;
    i32 param1;
    i32 param2;
    i32 param3;
    i32 param4;
} d_input_event;

/* Purpose: Init input.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 */
void d_input_init(void);
/* Purpose: Shutdown input.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 */
void d_input_shutdown(void);
/* Purpose: Begin frame.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 */
void d_input_begin_frame(void);
/* Purpose: End frame.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 */
void d_input_end_frame(void);

/* Purpose: Poll input.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/CONTRACTS.md#Return Values / Errors`.
 */
u32  d_input_poll(d_input_event* out_event);

/* Retrieve IME payload for events that report an identifier in param1. */
u32  d_input_get_ime_event(u32 id, d_ime_event* out_event);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINO_INPUT_INPUT_H */
