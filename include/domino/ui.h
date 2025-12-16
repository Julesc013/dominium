/*
FILE: include/domino/ui.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / ui
RESPONSIBILITY: Defines the public contract for `ui` (types/constants/function signatures); does NOT provide implementation.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/SPEC_ABI_TEMPLATES.md` where ABI stability matters.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOMINO_UI_H_INCLUDED
#define DOMINO_UI_H_INCLUDED

/* Domino Native UI skeleton - minimal, C89-friendly */

#include "domino/sys.h"
#include "domino/baseline.h"

#ifdef __cplusplus
extern "C" {
#endif

/*------------------------------------------------------------
 * Unified Domino UI (dom_ui_*) - in-memory stub tree
 *------------------------------------------------------------*/
typedef enum dom_ui_mode {
    DOM_UI_MODE_NONE = 0,
    DOM_UI_MODE_CLI,
    DOM_UI_MODE_TUI,
    DOM_UI_MODE_GUI
} dom_ui_mode;

/* dom_ui_backend: Public type used by `ui`. */
typedef enum dom_ui_backend {
    DOM_UI_BACKEND_CLI    = 1 << 0,
    DOM_UI_BACKEND_TUI    = 1 << 1,
    DOM_UI_BACKEND_NATIVE = 1 << 2,
    DOM_UI_BACKEND_GFX    = 1 << 3
} dom_ui_backend;

/* dom_ui_widget_kind: Public type used by `ui`. */
typedef enum dom_ui_widget_kind {
    DOM_UI_WIDGET_ROOT = 0,
    DOM_UI_WIDGET_PANEL,
    DOM_UI_WIDGET_LABEL,
    DOM_UI_WIDGET_BUTTON,
    DOM_UI_WIDGET_LIST,
    DOM_UI_WIDGET_TREE,
    DOM_UI_WIDGET_TABS,
    DOM_UI_WIDGET_SPLIT,
    DOM_UI_WIDGET_CANVAS
} dom_ui_widget_kind;

/* dom_ui_event_type: Public type used by `ui`. */
typedef enum dom_ui_event_type {
    DOM_UI_EVENT_NONE = 0,
    DOM_UI_EVENT_CLICK,
    DOM_UI_EVENT_CHANGE,
    DOM_UI_EVENT_ACTIVATE,
    DOM_UI_EVENT_CLOSE
} dom_ui_event_type;

/* dom_ui_app: Public type used by `ui`. */
typedef struct dom_ui_app    dom_ui_app;
/* dom_ui_window: Public type used by `ui`. */
typedef struct dom_ui_window dom_ui_window;
/* dom_ui_widget: Public type used by `ui`. */
typedef struct dom_ui_widget dom_ui_widget;

/* dom_ui_desc: Public type used by `ui`. */
typedef struct dom_ui_desc {
    dom_ui_mode    mode;
    uint32_t       backend_mask;
    dsys_context*  sys;
    const char*    app_id;
    const char*    app_name;
} dom_ui_desc;

typedef void (*dom_ui_event_cb)(dom_ui_widget* widget,
                                dom_ui_event_type type,
                                void* user);

/* Purpose: Create ui app.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: Non-NULL on success; NULL on failure or when not found.
 */
dom_ui_app*    dom_ui_app_create(const dom_ui_desc* desc);
/* Purpose: Destroy ui app.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 */
void           dom_ui_app_destroy(dom_ui_app* app);
/* Purpose: Create ui window.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: Non-NULL on success; NULL on failure or when not found.
 */
dom_ui_window* dom_ui_window_create(dom_ui_app* app, const char* title, int32_t w, int32_t h);
/* Purpose: Destroy ui window.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 */
void           dom_ui_window_destroy(dom_ui_window* win);
/* Purpose: Create ui widget.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: Non-NULL on success; NULL on failure or when not found.
 */
dom_ui_widget* dom_ui_widget_create(dom_ui_window* win, dom_ui_widget_kind kind, dom_ui_widget* parent);
/* Purpose: Widget set bounds.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 */
void           dom_ui_widget_set_bounds(dom_ui_widget* w, int32_t x, int32_t y, int32_t width, int32_t height);
/* Purpose: Label set text.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 */
void           dom_ui_label_set_text(dom_ui_widget* w, const char* utf8);
/* Purpose: Button set text.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 */
void           dom_ui_button_set_text(dom_ui_widget* w, const char* utf8);
/* Purpose: Widget set callback.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 */
void           dom_ui_widget_set_callback(dom_ui_widget* w, dom_ui_event_cb cb, void* user);
/* Purpose: App pump.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: `true` on success; `false` on failure.
 */
bool           dom_ui_app_pump(dom_ui_app* app);
/* Purpose: Canvas get native handle.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 */
void*          dom_ui_canvas_get_native_handle(dom_ui_widget* canvas);
/* Purpose: Canvas get client rect.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 */
void           dom_ui_canvas_get_client_rect(dom_ui_widget* canvas, int32_t* x, int32_t* y, int32_t* w, int32_t* h);

/*------------------------------------------------------------
 * Legacy Domino Native UI skeleton - minimal, C89-friendly
 *------------------------------------------------------------*/
typedef struct domino_ui_app    domino_ui_app;
/* domino_ui_window: Public type used by `ui`. */
typedef struct domino_ui_window domino_ui_window;
/* domino_ui_widget: Public type used by `ui`. */
typedef struct domino_ui_widget domino_ui_widget;

/* domino_ui_app_desc: Public type used by `ui`. */
typedef struct domino_ui_app_desc {
    const char* app_id;   /* e.g. "dominium.launcher" */
    const char* app_name; /* "Dominium Launcher" */
} domino_ui_app_desc;

/* Purpose: Create ui app.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/CONTRACTS.md#Return Values / Errors`.
 */
int  domino_ui_app_create(domino_sys_context* sys,
                          const domino_ui_app_desc* desc,
                          domino_ui_app** out_app);
/* Purpose: App run.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/CONTRACTS.md#Return Values / Errors`.
 */
int  domino_ui_app_run(domino_ui_app* app);
/* Purpose: App quit.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 */
void domino_ui_app_quit(domino_ui_app* app);
/* Purpose: Destroy ui app.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 */
void domino_ui_app_destroy(domino_ui_app* app);

/* domino_ui_window_desc: Public type used by `ui`. */
typedef struct domino_ui_window_desc {
    const char* title;
    int width;
    int height;
    int resizable;
} domino_ui_window_desc;

/* Purpose: Create ui window.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: Non-NULL on success; NULL on failure or when not found.
 */
domino_ui_window* domino_ui_window_create(domino_ui_app* app,
                                          const domino_ui_window_desc* desc);
/* Purpose: Window show.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 */
void domino_ui_window_show(domino_ui_window* win);
/* Purpose: Close ui window.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 */
void domino_ui_window_close(domino_ui_window* win);

/* domino_ui_widget_kind: Public type used by `ui`. */
typedef enum {
    DOMINO_UI_WIDGET_LABEL,
    DOMINO_UI_WIDGET_BUTTON,
    DOMINO_UI_WIDGET_LIST,
    DOMINO_UI_WIDGET_TEXTBOX
} domino_ui_widget_kind;

/* Purpose: Create ui widget.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: Non-NULL on success; NULL on failure or when not found.
 */
domino_ui_widget* domino_ui_widget_create(domino_ui_window* parent,
                                          domino_ui_widget_kind kind);

#ifdef __cplusplus
}
#endif

#endif /* DOMINO_UI_H_INCLUDED */
