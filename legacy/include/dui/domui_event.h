/*
FILE: include/dui/domui_event.h
MODULE: DUI
LAYER / SUBSYSTEM: DUI API / domui_event
RESPONSIBILITY: Defines the unified DOM UI event ABI for action dispatch.
ALLOWED DEPENDENCIES: C89/C++98 standard headers only.
FORBIDDEN DEPENDENCIES: UI backends, launcher.
THREADING MODEL: Caller-managed; no internal synchronization.
ERROR MODEL: None; POD structs only.
DETERMINISM: Data-only; values are provided by deterministic event sources.
*/
#ifndef DOMUI_EVENT_H_INCLUDED
#define DOMUI_EVENT_H_INCLUDED

#ifdef __cplusplus
extern "C" {
#endif

typedef unsigned int domui_u32;
typedef domui_u32 domui_widget_id;
typedef domui_u32 domui_action_id;

typedef struct domui_vec2i {
    int x;
    int y;
} domui_vec2i;

typedef struct domui_recti {
    int x;
    int y;
    int w;
    int h;
} domui_recti;

typedef enum domui_event_type_e {
    DOMUI_EVENT_CLICK = 0,
    DOMUI_EVENT_CHANGE,
    DOMUI_EVENT_SUBMIT,
    DOMUI_EVENT_TAB_CHANGE,

    DOMUI_EVENT_KEYDOWN,
    DOMUI_EVENT_KEYUP,
    DOMUI_EVENT_TEXT_INPUT,

    DOMUI_EVENT_MOUSE_DOWN,
    DOMUI_EVENT_MOUSE_UP,
    DOMUI_EVENT_MOUSE_MOVE,
    DOMUI_EVENT_SCROLL,

    DOMUI_EVENT_FOCUS_GAIN,
    DOMUI_EVENT_FOCUS_LOST,

    DOMUI_EVENT_CUSTOM
} domui_event_type;

/* Modifier bitmask. */
#define DOMUI_MOD_SHIFT ((domui_u32)1u << 0u)
#define DOMUI_MOD_CTRL  ((domui_u32)1u << 1u)
#define DOMUI_MOD_ALT   ((domui_u32)1u << 2u)
#define DOMUI_MOD_META  ((domui_u32)1u << 3u)

typedef enum domui_value_type_e {
    DOMUI_VALUE_NONE = 0,
    DOMUI_VALUE_I32,
    DOMUI_VALUE_U32,
    DOMUI_VALUE_BOOL,
    DOMUI_VALUE_STR,
    DOMUI_VALUE_VEC2I,
    DOMUI_VALUE_RECTI
} domui_value_type;

typedef struct domui_strref {
    const char* ptr;
    domui_u32 len;
} domui_strref;

typedef struct domui_value {
    domui_value_type type;
    union {
        int v_i32;
        domui_u32 v_u32;
        int v_bool;
        domui_strref v_str;
        domui_vec2i v_vec2i;
        domui_recti v_recti;
    } u;
} domui_value;

typedef struct domui_event {
    domui_action_id action_id;
    domui_widget_id widget_id;
    domui_event_type type;
    domui_u32 modifiers;
    domui_value a;
    domui_value b;
    void* backend_ext;
} domui_event;

typedef void (*domui_action_fn)(void* user_ctx, const domui_event* e);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMUI_EVENT_H_INCLUDED */
