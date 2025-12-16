/*
FILE: source/domino/ui/ui.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / ui/ui
RESPONSIBILITY: Implements `ui`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
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
#include <string.h>

struct dom_ui_widget {
    dom_ui_widget_kind kind;
    int32_t            x;
    int32_t            y;
    int32_t            width;
    int32_t            height;
    char*              text;
    dom_ui_event_cb    callback;
    void*              callback_user;
    struct dom_ui_widget* parent;
    struct dom_ui_widget* first_child;
    struct dom_ui_widget* next_sibling;
};

struct dom_ui_window {
    char*            title;
    int32_t          width;
    int32_t          height;
    dom_ui_widget*   root;
    struct dom_ui_window* next;
    struct dom_ui_app*    owner;
};

struct dom_ui_app {
    dom_ui_desc     desc;
    dom_ui_window*  windows;
    bool            quit;
};

static char* dom_ui_dup_string(const char* src)
{
    size_t len;
    char* out;

    if (!src) {
        return NULL;
    }
    len = strlen(src);
    out = (char*)malloc(len + 1u);
    if (!out) {
        return NULL;
    }
    memcpy(out, src, len + 1u);
    return out;
}

static void dom_ui_free_widget(dom_ui_widget* w)
{
    dom_ui_widget* child;
    dom_ui_widget* next;

    if (!w) {
        return;
    }
    child = w->first_child;
    while (child) {
        next = child->next_sibling;
        dom_ui_free_widget(child);
        child = next;
    }
    if (w->text) {
        free(w->text);
    }
    free(w);
}

static void dom_ui_detach_window(dom_ui_app* app, dom_ui_window* win)
{
    dom_ui_window* prev;
    dom_ui_window* cur;

    if (!app || !win) {
        return;
    }
    prev = NULL;
    cur = app->windows;
    while (cur) {
        if (cur == win) {
            if (prev) {
                prev->next = cur->next;
            } else {
                app->windows = cur->next;
            }
            return;
        }
        prev = cur;
        cur = cur->next;
    }
}

dom_ui_app* dom_ui_app_create(const dom_ui_desc* desc)
{
    dom_ui_app* app;
    dom_ui_desc local_desc;

    app = (dom_ui_app*)malloc(sizeof(dom_ui_app));
    if (!app) {
        return NULL;
    }
    memset(app, 0, sizeof(*app));

    memset(&local_desc, 0, sizeof(local_desc));
    if (desc) {
        local_desc = *desc;
    } else {
        local_desc.backend_mask = DOM_UI_BACKEND_CLI | DOM_UI_BACKEND_TUI | DOM_UI_BACKEND_NATIVE | DOM_UI_BACKEND_GFX;
        local_desc.mode = DOM_UI_MODE_NONE;
    }

    app->desc = local_desc;
    app->windows = NULL;
    app->quit = false;
    return app;
}

void dom_ui_app_destroy(dom_ui_app* app)
{
    dom_ui_window* cur;
    dom_ui_window* next;

    if (!app) {
        return;
    }
    cur = app->windows;
    while (cur) {
        next = cur->next;
        if (cur->root) {
            dom_ui_free_widget(cur->root);
        }
        if (cur->title) {
            free(cur->title);
        }
        free(cur);
        cur = next;
    }
    free(app);
}

dom_ui_window* dom_ui_window_create(dom_ui_app* app, const char* title, int32_t w, int32_t h)
{
    dom_ui_window* win;

    win = (dom_ui_window*)malloc(sizeof(dom_ui_window));
    if (!win) {
        return NULL;
    }
    memset(win, 0, sizeof(*win));

    win->title = dom_ui_dup_string(title);
    win->width = w;
    win->height = h;
    win->owner = app;

    win->root = (dom_ui_widget*)malloc(sizeof(dom_ui_widget));
    if (win->root) {
        memset(win->root, 0, sizeof(*win->root));
        win->root->kind = DOM_UI_WIDGET_ROOT;
    }

    if (app) {
        win->next = app->windows;
        app->windows = win;
    }

    return win;
}

void dom_ui_window_destroy(dom_ui_window* win)
{
    if (!win) {
        return;
    }
    if (win->owner) {
        dom_ui_detach_window(win->owner, win);
    }
    if (win->root) {
        dom_ui_free_widget(win->root);
    }
    if (win->title) {
        free(win->title);
    }
    free(win);
}

dom_ui_widget* dom_ui_widget_create(dom_ui_window* win, dom_ui_widget_kind kind, dom_ui_widget* parent)
{
    dom_ui_widget* w;
    dom_ui_widget* attach_to;

    if (!win) {
        return NULL;
    }

    w = (dom_ui_widget*)malloc(sizeof(dom_ui_widget));
    if (!w) {
        return NULL;
    }
    memset(w, 0, sizeof(*w));
    w->kind = kind;

    attach_to = parent;
    if (!attach_to) {
        attach_to = win->root;
    }
    w->parent = attach_to;
    if (attach_to) {
        w->next_sibling = attach_to->first_child;
        attach_to->first_child = w;
    }
    return w;
}

void dom_ui_widget_set_bounds(dom_ui_widget* w, int32_t x, int32_t y, int32_t width, int32_t height)
{
    if (!w) {
        return;
    }
    w->x = x;
    w->y = y;
    w->width = width;
    w->height = height;
}

static void dom_ui_set_text(dom_ui_widget* w, const char* utf8)
{
    if (!w) {
        return;
    }
    if (w->text) {
        free(w->text);
        w->text = NULL;
    }
    if (utf8) {
        w->text = dom_ui_dup_string(utf8);
    }
}

void dom_ui_label_set_text(dom_ui_widget* w, const char* utf8)
{
    dom_ui_set_text(w, utf8);
}

void dom_ui_button_set_text(dom_ui_widget* w, const char* utf8)
{
    dom_ui_set_text(w, utf8);
}

void dom_ui_widget_set_callback(dom_ui_widget* w, dom_ui_event_cb cb, void* user)
{
    if (!w) {
        return;
    }
    w->callback = cb;
    w->callback_user = user;
}

bool dom_ui_app_pump(dom_ui_app* app)
{
    if (!app) {
        return false;
    }
    if (app->quit) {
        return false;
    }
    return true;
}

void* dom_ui_canvas_get_native_handle(dom_ui_widget* canvas)
{
    (void)canvas;
    return NULL;
}

void dom_ui_canvas_get_client_rect(dom_ui_widget* canvas, int32_t* x, int32_t* y, int32_t* w, int32_t* h)
{
    if (x) *x = 0;
    if (y) *y = 0;
    if (w) *w = 0;
    if (h) *h = 0;
    if (!canvas) {
        return;
    }
    if (x) *x = canvas->x;
    if (y) *y = canvas->y;
    if (w) *w = canvas->width;
    if (h) *h = canvas->height;
}
