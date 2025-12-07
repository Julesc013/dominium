#ifndef DOMINIUM_DOM_PLAT_UI_H
#define DOMINIUM_DOM_PLAT_UI_H

/* Native UI abstraction (NATIVE_UI mode). Most fields are placeholders. */

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#define DOM_UI_API_VERSION 1u

struct dom_sys_vtable; /* fwd */

typedef struct dom_ui_app    dom_ui_app;
typedef struct dom_ui_window dom_ui_window;
typedef struct dom_ui_widget dom_ui_widget;

enum dom_ui_widget_type {
    DOM_UI_WIDGET_VBOX = 0,
    DOM_UI_WIDGET_HBOX,
    DOM_UI_WIDGET_SPLIT,
    DOM_UI_WIDGET_TABS,
    DOM_UI_WIDGET_LIST,
    DOM_UI_WIDGET_TREE,
    DOM_UI_WIDGET_BUTTON,
    DOM_UI_WIDGET_LABEL,
    DOM_UI_WIDGET_TEXT_ENTRY,
    DOM_UI_WIDGET_CHECKBOX,
    DOM_UI_WIDGET_PROGRESS
};

struct dom_ui_window_desc {
    const char* title;
    int width;
    int height;
};

struct dom_ui_widget_desc {
    const char* text;
};

struct dom_ui_layout {
    int placeholder;
};

struct dom_ui_vtable {
    uint32_t api_version;

    dom_ui_app*    (*app_create)(int argc, char** argv);
    int            (*app_run)(dom_ui_app*);
    void           (*app_quit)(dom_ui_app*);

    dom_ui_window* (*window_create)(dom_ui_app*, const struct dom_ui_window_desc*);
    void           (*window_show)(dom_ui_window*);

    dom_ui_widget* (*widget_create)(dom_ui_window*, enum dom_ui_widget_type,
                                    const struct dom_ui_widget_desc*);

    void           (*layout_apply)(dom_ui_window*, const struct dom_ui_layout*);
};

const struct dom_ui_vtable* dom_plat_ui_probe(const struct dom_sys_vtable* sys);

#ifdef __cplusplus
}
#endif

#endif /* DOMINIUM_DOM_PLAT_UI_H */
