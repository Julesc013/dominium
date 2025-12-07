#ifndef DOMINO_UI_H
#define DOMINO_UI_H

/* Domino Native UI skeleton - minimal, C89-friendly */

#include "domino/sys.h"

#ifdef __cplusplus
extern "C" {
#endif

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

#endif /* DOMINO_UI_H */
