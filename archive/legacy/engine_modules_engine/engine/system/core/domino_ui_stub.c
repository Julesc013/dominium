/*
FILE: source/domino/system/core/domino_ui_stub.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / system/core/domino_ui_stub
RESPONSIBILITY: Implements `domino_ui_stub`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "domino/ui.h"

#include <stdlib.h>

struct domino_ui_app {
    domino_sys_context* sys;
};

struct domino_ui_window {
    int placeholder;
};

struct domino_ui_widget {
    int placeholder;
};

int domino_ui_app_create(domino_sys_context* sys,
                         const domino_ui_app_desc* desc,
                         domino_ui_app** out_app)
{
    domino_ui_app* app;
    (void)desc;
    if (!out_app) return -1;
    app = (domino_ui_app*)malloc(sizeof(domino_ui_app));
    if (!app) return -1;
    app->sys = sys;
    *out_app = app;
    return -1; /* unsupported for now */
}

int domino_ui_app_run(domino_ui_app* app)
{
    (void)app;
    return -1;
}

void domino_ui_app_quit(domino_ui_app* app)
{
    (void)app;
}

void domino_ui_app_destroy(domino_ui_app* app)
{
    if (app) {
        free(app);
    }
}

domino_ui_window* domino_ui_window_create(domino_ui_app* app,
                                          const domino_ui_window_desc* desc)
{
    domino_ui_window* win;
    (void)app; (void)desc;
    win = (domino_ui_window*)malloc(sizeof(domino_ui_window));
    if (!win) return NULL;
    win->placeholder = 0;
    return win;
}

void domino_ui_window_show(domino_ui_window* win)
{
    (void)win;
}

void domino_ui_window_close(domino_ui_window* win)
{
    (void)win;
}

domino_ui_widget* domino_ui_widget_create(domino_ui_window* parent,
                                          domino_ui_widget_kind kind)
{
    domino_ui_widget* w;
    (void)parent; (void)kind;
    w = (domino_ui_widget*)malloc(sizeof(domino_ui_widget));
    if (!w) return NULL;
    w->placeholder = 0;
    return w;
}
