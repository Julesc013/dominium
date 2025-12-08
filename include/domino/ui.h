#ifndef DOMINO_UI_H_INCLUDED
#define DOMINO_UI_H_INCLUDED

/* Domino Native UI skeleton - minimal, C89-friendly */

#include "domino/sys.h"

#ifdef __cplusplus
extern "C" {
#endif

/*------------------------------------------------------------
 * New Domino UI ABI (dom_ui_*)
 *------------------------------------------------------------*/
typedef struct dsys_context     dsys_context;
typedef struct dom_view_registry dom_view_registry;
typedef struct dom_ui_context   dom_ui_context;
typedef struct dom_ui_window    dom_ui_window;

typedef struct dom_ui_desc {
    uint32_t           struct_size;
    uint32_t           struct_version;
    dsys_context*      sys;
    dom_view_registry* views;
    const char*        app_id;
    const char*        app_name;
} dom_ui_desc;

int  dom_ui_create(const dom_ui_desc* desc, dom_ui_context** out_ctx);
void dom_ui_destroy(dom_ui_context* ctx);
int  dom_ui_run(dom_ui_context* ctx);
int  dom_ui_open_window(dom_ui_context* ctx, dom_ui_window** out_window);
int  dom_ui_close_window(dom_ui_window* win);

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
