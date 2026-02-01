/*
FILE: include/dui/dui_api_v1.h
MODULE: DUI
LAYER / SUBSYSTEM: DUI API / facade
RESPONSIBILITY: Defines the DUI facade ABI (`dui_api_v1`) for presentation-only UI (no launcher-core dependencies).
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; launcher core headers; UI toolkit headers in this contract.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes/NULL pointers; no exceptions across ABI boundaries.
DETERMINISM: UI must not influence authoritative simulation; events are explicit inputs; see `docs/specs/SPEC_DUI.md`.
VERSIONING / ABI / DATA FORMAT NOTES: Versioned POD vtable; `DOM_ABI_HEADER`; `query_interface`.
EXTENSION POINTS: `query_interface` + capability bits; schema/state TLV is skip-unknown.
*/
#ifndef DUI_API_V1_H_INCLUDED
#define DUI_API_V1_H_INCLUDED

#include "domino/abi.h"
#include "domino/core/types.h"

#include "dui/dui_schema_tlv.h"
#include "dui/domui_event.h"

#ifdef __cplusplus
extern "C" {
#endif

/* ABI version for the root vtable. */
#define DUI_API_ABI_VERSION 1u

/* Interface IDs for query_interface. */
#define DUI_IID_API_V1        ((dom_iid)0x44554901u) /* 'DUI\x01' */
#define DUI_IID_TEST_API_V1   ((dom_iid)0x44554980u) /* 'DUI\x80' */
#define DUI_IID_NATIVE_API_V1 ((dom_iid)0x44554981u) /* 'DUI\x81' */
#define DUI_IID_ACTION_API_V1 ((dom_iid)0x44554982u) /* 'DUI\x82' */

typedef u64 dui_caps;

/* Core capability bits (widget + feature surface). */
#define DUI_CAP_WINDOW            ((dui_caps)1u << 0u)
#define DUI_CAP_EVENT_PUMP        ((dui_caps)1u << 1u)

#define DUI_CAP_LABEL             ((dui_caps)1u << 8u)
#define DUI_CAP_BUTTON            ((dui_caps)1u << 9u)
#define DUI_CAP_CHECKBOX          ((dui_caps)1u << 10u)
#define DUI_CAP_LIST              ((dui_caps)1u << 11u)
#define DUI_CAP_TEXT_FIELD        ((dui_caps)1u << 12u)
#define DUI_CAP_PROGRESS          ((dui_caps)1u << 13u)

#define DUI_CAP_LAYOUT_ROW        ((dui_caps)1u << 16u)
#define DUI_CAP_LAYOUT_COLUMN     ((dui_caps)1u << 17u)
#define DUI_CAP_LAYOUT_STACK      ((dui_caps)1u << 18u)

#define DUI_CAP_FOCUS             ((dui_caps)1u << 24u)
#define DUI_CAP_KEYBOARD_NAV      ((dui_caps)1u << 25u)

/* Optional feature bits (presentation-only). */
#define DUI_CAP_IME               ((dui_caps)1u << 32u)
#define DUI_CAP_ACCESSIBILITY     ((dui_caps)1u << 33u)
#define DUI_CAP_DPI_AWARE         ((dui_caps)1u << 34u)

typedef struct dui_context dui_context;
typedef struct dui_window  dui_window;

typedef struct dui_widget_v1 {
    DOM_ABI_HEADER;
    u32 id;
    u32 kind; /* dui_node_kind */
} dui_widget_v1;

typedef enum dui_event_type_e {
    DUI_EVENT_NONE = 0,
    DUI_EVENT_QUIT = 1,

    /* Button activated / checkbox toggled / list activated / etc. */
    DUI_EVENT_ACTION = 2,

    /* Value changed (text field, checkbox, list selection). */
    DUI_EVENT_VALUE_CHANGED = 3
} dui_event_type;

typedef struct dui_event_action_v1 {
    u32 widget_id;
    u32 action_id; /* schema ACTN */
    u32 item_id;   /* list item id when applicable; 0 otherwise */
} dui_event_action_v1;

typedef struct dui_event_value_v1 {
    u32 widget_id;
    u32 value_type; /* dui_value_type */
    u32 v_u32;
    i32 v_i32;
    u64 v_u64;
    u32 text_len;
    char text[256]; /* UTF-8, not necessarily NUL-terminated */
    u32 item_id;     /* list item id when applicable; 0 otherwise */
} dui_event_value_v1;

typedef struct dui_event_v1 {
    DOM_ABI_HEADER;
    u32 type; /* dui_event_type */
    u32 reserved0;
    union {
        dui_event_action_v1 action;
        dui_event_value_v1  value;
    } u;
} dui_event_v1;

/* Window creation descriptor. */
typedef struct dui_window_desc_v1 {
    DOM_ABI_HEADER;
    const char* title;
    i32 width;
    i32 height;
    u32 flags; /* DUI_WINDOW_FLAG_* */
    void* parent_hwnd; /* HWND on Win32 when DUI_WINDOW_FLAG_CHILD is set; may be NULL */
} dui_window_desc_v1;

/* Window flags */
#define DUI_WINDOW_FLAG_HEADLESS ((u32)1u << 0u) /* no OS window; offscreen/headless operation when supported */
#define DUI_WINDOW_FLAG_CHILD    ((u32)1u << 1u) /* embed as a child window when supported */

typedef enum dui_result_e {
    DUI_OK = 0,
    DUI_ERR = -1,
    DUI_ERR_NULL = -2,
    DUI_ERR_UNSUPPORTED = -3,
    DUI_ERR_BAD_DESC = -4,
    DUI_ERR_BACKEND_UNAVAILABLE = -5
} dui_result;

/* dui_api_v1: Presentation-only facade. */
typedef struct dui_api_v1 {
    DOM_ABI_HEADER;
    dom_query_interface_fn query_interface;

    /* Backend identity + capabilities. */
    const char* (*backend_name)(void); /* stable ASCII id (e.g. "win32", "dgfx", "null") */
    dui_caps    (*get_caps)(void);

    /* Lifecycle. */
    dui_result (*create_context)(dui_context** out_ctx);
    void       (*destroy_context)(dui_context* ctx);

    dui_result (*create_window)(dui_context* ctx, const dui_window_desc_v1* desc, dui_window** out_win);
    void       (*destroy_window)(dui_window* win);

    /* Schema + state (TLV). */
    dui_result (*set_schema_tlv)(dui_window* win, const void* schema_tlv, u32 schema_len);
    dui_result (*set_state_tlv)(dui_window* win, const void* state_tlv, u32 state_len);

    /* Frame/pump. For native backends, render may be a no-op. */
    dui_result (*render)(dui_window* win);
    dui_result (*pump)(dui_context* ctx);

    /* Event queue. Returns: 1 if filled, 0 if none, <0 on error. */
    int (*poll_event)(dui_context* ctx, dui_event_v1* out_ev);

    /* Request quit (e.g., programmatic close). */
    dui_result (*request_quit)(dui_context* ctx);
} dui_api_v1;

/* Optional test injection surface (IID: DUI_IID_TEST_API_V1).
 * This is intended for smoke tests and headless validation only.
 */
typedef struct dui_test_api_v1 {
    DOM_ABI_HEADER;
    dui_result (*post_event)(dui_context* ctx, const dui_event_v1* ev);
} dui_test_api_v1;

/* Optional native handle surface (IID: DUI_IID_NATIVE_API_V1).
 * Native handles are presentation-only and must not influence deterministic logic.
 */
typedef struct dui_native_api_v1 {
    DOM_ABI_HEADER;
    void* (*get_native_window_handle)(dui_window* win); /* HWND on Win32, etc; may be NULL */
} dui_native_api_v1;

/* Optional action dispatch surface (IID: DUI_IID_ACTION_API_V1).
 * This enables domui_event dispatch directly from the backend.
 */
typedef struct dui_action_api_v1 {
    DOM_ABI_HEADER;
    void (*set_action_dispatch)(dui_context* ctx, domui_action_fn fn, void* user_ctx);
} dui_action_api_v1;

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DUI_API_V1_H_INCLUDED */
