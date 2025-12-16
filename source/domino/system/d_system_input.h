/*
FILE: source/domino/system/d_system_input.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / system/d_system_input
RESPONSIBILITY: Implements `d_system_input`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef D_SYSTEM_INPUT_H
#define D_SYSTEM_INPUT_H

#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum d_sys_event_type_e {
    D_SYS_EVENT_NONE = 0,
    D_SYS_EVENT_QUIT,
    D_SYS_EVENT_KEY_DOWN,
    D_SYS_EVENT_KEY_UP,
    D_SYS_EVENT_MOUSE_MOVE,
    D_SYS_EVENT_MOUSE_BUTTON_DOWN,
    D_SYS_EVENT_MOUSE_BUTTON_UP
} d_sys_event_type;

typedef enum d_sys_key_e {
    D_SYS_KEY_UNKNOWN = 0,
    D_SYS_KEY_ESCAPE,
    D_SYS_KEY_ENTER,
    D_SYS_KEY_SPACE,
    D_SYS_KEY_BACKSPACE,
    D_SYS_KEY_0,
    D_SYS_KEY_1,
    D_SYS_KEY_2,
    D_SYS_KEY_3,
    D_SYS_KEY_4,
    D_SYS_KEY_5,
    D_SYS_KEY_6,
    D_SYS_KEY_7,
    D_SYS_KEY_8,
    D_SYS_KEY_9,
    D_SYS_KEY_PERIOD,
    D_SYS_KEY_W,
    D_SYS_KEY_A,
    D_SYS_KEY_S,
    D_SYS_KEY_D,
    D_SYS_KEY_Q,
    D_SYS_KEY_E,
    D_SYS_KEY_UP,
    D_SYS_KEY_DOWN,
    D_SYS_KEY_LEFT,
    D_SYS_KEY_RIGHT
} d_sys_key;

typedef struct d_sys_event_key_s {
    d_sys_key key;
} d_sys_event_key;

typedef struct d_sys_event_mouse_s {
    i32 x;
    i32 y;
    u8  button; /* 1=left,2=right,3=middle */
} d_sys_event_mouse;

typedef struct d_sys_event_s {
    d_sys_event_type type;
    union {
        d_sys_event_key   key;
        d_sys_event_mouse mouse;
    } u;
} d_sys_event;

/* Poll one event per call; returns 1 if event filled, 0 if none, <0 on error. */
int d_system_poll_event(d_sys_event *out_ev);

/* Internal helpers for platform backends. */
int d_system_input_enqueue(const d_sys_event *ev);
int d_system_input_pump_dsys(void);

#ifdef __cplusplus
}
#endif

#endif /* D_SYSTEM_INPUT_H */
