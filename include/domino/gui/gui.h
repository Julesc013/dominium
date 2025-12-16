/*
FILE: include/domino/gui/gui.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / gui/gui
RESPONSIBILITY: Defines the public contract for `gui` (types/constants/function signatures); does NOT provide implementation.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/SPEC_ABI_TEMPLATES.md` where ABI stability matters.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOMINO_GUI_GUI_H_INCLUDED
#define DOMINO_GUI_GUI_H_INCLUDED

#include "domino/core/types.h"
#include "domino/render/gui_prim.h"
#include "domino/gui/style.h"
#include "domino/render/pipeline.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum dgui_widget_type {
    DGUI_WIDGET_PANEL = 0,
    DGUI_WIDGET_LABEL,
    DGUI_WIDGET_BUTTON,
    DGUI_WIDGET_SLIDER,
    DGUI_WIDGET_CHECKBOX,
    DGUI_WIDGET_LIST
} dgui_widget_type;

typedef enum dgui_layout {
    DGUI_LAYOUT_VERTICAL = 0,
    DGUI_LAYOUT_HORIZONTAL
} dgui_layout;

typedef struct dgui_widget dgui_widget;
typedef struct dgui_context dgui_context;
typedef struct dgui_widget d_gui_widget;
typedef struct dgui_context d_gui_context;
typedef struct d_gui_window d_gui_window;

typedef struct d_gui_window_desc {
    const char* title;
    i32 x;
    i32 y;
    i32 width;
    i32 height;
    int resizable;
} d_gui_window_desc;

typedef void (*dgui_activate_fn)(dgui_widget* self, void* user);

dgui_context* dgui_create(void);
void          dgui_destroy(dgui_context* ctx);

void          dgui_set_root(dgui_context* ctx, dgui_widget* root);
void          dgui_set_style(dgui_context* ctx, const dgui_style* style);

dgui_widget*  dgui_panel(dgui_context* ctx, dgui_layout layout);
dgui_widget*  dgui_label(dgui_context* ctx, const char* text);
dgui_widget*  dgui_button(dgui_context* ctx, const char* text, dgui_activate_fn cb, void* user);
dgui_widget*  dgui_list(dgui_context* ctx, const char* const* items, int count);

int           dgui_widget_add(dgui_widget* parent, dgui_widget* child);

void          dgui_render(dgui_context* ctx, struct dcvs_t* canvas);
void          dgui_handle_key(dgui_context* ctx, int keycode);

/*------------------------------------------------------------
 * Multi-window GUI host
 *------------------------------------------------------------*/
d_gui_window* d_gui_window_create(const d_gui_window_desc* desc);
void          d_gui_window_destroy(d_gui_window* win);
int           d_gui_window_should_close(d_gui_window* win);
void          d_gui_window_frame(d_gui_window* win, float delta_time);
void          d_gui_window_set_root(d_gui_window* win, d_gui_widget* root);
d_gui_context* d_gui_window_get_gui(d_gui_window* win);

d_gui_window* d_gui_window_get_first(void);
d_gui_window* d_gui_window_get_next(d_gui_window* current);
void          d_gui_tick_all_windows(float delta_time);
int           d_gui_any_window_alive(void);

/* Optional: provide a shared pipeline for newly created windows. */
void          d_gui_set_shared_pipeline(struct d_gfx_pipeline* pipe);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINO_GUI_GUI_H_INCLUDED */
