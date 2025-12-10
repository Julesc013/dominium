#ifndef DOMINO_UI_EVENTS_H_INCLUDED
#define DOMINO_UI_EVENTS_H_INCLUDED

#include <stdint.h>
#include "domino/sys.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum ui_event_type {
    UI_EVT_NONE = 0,
    UI_EVT_MOUSE,
    UI_EVT_KEY,
    UI_EVT_TEXT,
    UI_EVT_FOCUS,
    UI_EVT_SCROLL,
    UI_EVT_TIMER
} ui_event_type;

typedef struct ui_key {
    int code;
    int mods;
    int pressed;
} ui_key;

typedef struct ui_mouse {
    int x;
    int y;
    int dx;
    int dy;
    int button;
    int pressed;
    int wheel;
} ui_mouse;

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
