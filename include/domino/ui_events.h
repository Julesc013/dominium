/*
FILE: include/domino/ui_events.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / ui_events
RESPONSIBILITY: Defines the public contract for `ui_events` (types/constants/function signatures); does NOT provide implementation.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/SPEC_ABI_TEMPLATES.md` where ABI stability matters.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOMINO_UI_EVENTS_H_INCLUDED
#define DOMINO_UI_EVENTS_H_INCLUDED

#include "domino/baseline.h"
#include "domino/sys.h"

#ifdef __cplusplus
extern "C" {
#endif

/* ui_event_type: Public type used by `ui_events`. */
typedef enum ui_event_type {
    UI_EVT_NONE = 0,
    UI_EVT_MOUSE,
    UI_EVT_KEY,
    UI_EVT_TEXT,
    UI_EVT_FOCUS,
    UI_EVT_SCROLL,
    UI_EVT_TIMER
} ui_event_type;

/* ui_key: Public type used by `ui_events`. */
typedef struct ui_key {
    int code;
    int mods;
    int pressed;
} ui_key;

/* ui_mouse: Public type used by `ui_events`. */
typedef struct ui_mouse {
    int x;
    int y;
    int dx;
    int dy;
    int button;
    int pressed;
    int wheel;
} ui_mouse;

/* data: Public type used by `ui_events`. */
typedef struct ui_event {
    ui_event_type type;
    union {
        ui_key   key;
        ui_mouse mouse;
        char     text[8];
    } data;
} ui_event;

#ifdef __cplusplus
}
#endif

#endif /* DOMINO_UI_EVENTS_H_INCLUDED */
