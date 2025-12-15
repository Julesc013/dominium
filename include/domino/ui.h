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

typedef enum dom_ui_backend {
    DOM_UI_BACKEND_CLI    = 1 << 0,
    DOM_UI_BACKEND_TUI    = 1 << 1,
    DOM_UI_BACKEND_NATIVE = 1 << 2,
    DOM_UI_BACKEND_GFX    = 1 << 3
} dom_ui_backend;

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

typedef enum dom_ui_event_type {
    DOM_UI_EVENT_NONE = 0,
    DOM_UI_EVENT_CLICK,
    DOM_UI_EVENT_CHANGE,
    DOM_UI_EVENT_ACTIVATE,
    DOM_UI_EVENT_CLOSE
} dom_ui_event_type;

typedef struct dom_ui_app    dom_ui_app;
typedef struct dom_ui_window dom_ui_window;
typedef struct dom_ui_widget dom_ui_widget;

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

dom_ui_app*    dom_ui_app_create(const dom_ui_desc* desc);
void           dom_ui_app_destroy(dom_ui_app* app);
dom_ui_window* dom_ui_window_create(dom_ui_app* app, const char* title, int32_t w, int32_t h);
void           dom_ui_window_destroy(dom_ui_window* win);
dom_ui_widget* dom_ui_widget_create(dom_ui_window* win, dom_ui_widget_kind kind, dom_ui_widget* parent);
void           dom_ui_widget_set_bounds(dom_ui_widget* w, int32_t x, int32_t y, int32_t width, int32_t height);
void           dom_ui_label_set_text(dom_ui_widget* w, const char* utf8);
void           dom_ui_button_set_text(dom_ui_widget* w, const char* utf8);
void           dom_ui_widget_set_callback(dom_ui_widget* w, dom_ui_event_cb cb, void* user);
bool           dom_ui_app_pump(dom_ui_app* app);
void*          dom_ui_canvas_get_native_handle(dom_ui_widget* canvas);
void           dom_ui_canvas_get_client_rect(dom_ui_widget* canvas, int32_t* x, int32_t* y, int32_t* w, int32_t* h);

/*------------------------------------------------------------
 * Legacy Domino Native UI skeleton - minimal, C89-friendly
 *------------------------------------------------------------*/
typedef struct domino_ui_app    domino_ui_app;
typedef struct domino_ui_window domino_ui_window;
typedef struct domino_ui_widget domino_ui_widget;

typedef struct domino_ui_app_desc {
    const char* app_id;   /* e.g. "dominium.launcher" */
    const char* app_name; /* "Dominium Launcher" */
} domino_ui_app_desc;

int  domino_ui_app_create(domino_sys_context* sys,
                          const domino_ui_app_desc* desc,
                          domino_ui_app** out_app);
int  domino_ui_app_run(domino_ui_app* app);
void domino_ui_app_quit(domino_ui_app* app);
void domino_ui_app_destroy(domino_ui_app* app);

typedef struct domino_ui_window_desc {
    const char* title;
    int width;
    int height;
    int resizable;
} domino_ui_window_desc;

domino_ui_window* domino_ui_window_create(domino_ui_app* app,
                                          const domino_ui_window_desc* desc);
void domino_ui_window_show(domino_ui_window* win);
void domino_ui_window_close(domino_ui_window* win);

typedef enum {
    DOMINO_UI_WIDGET_LABEL,
    DOMINO_UI_WIDGET_BUTTON,
    DOMINO_UI_WIDGET_LIST,
    DOMINO_UI_WIDGET_TEXTBOX
} domino_ui_widget_kind;

domino_ui_widget* domino_ui_widget_create(domino_ui_window* parent,
                                          domino_ui_widget_kind kind);

#ifdef __cplusplus
}
#endif

#endif /* DOMINO_UI_H_INCLUDED */
