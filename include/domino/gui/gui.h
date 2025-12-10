#ifndef DOMINO_GUI_GUI_H_INCLUDED
#define DOMINO_GUI_GUI_H_INCLUDED

#include "domino/render/gui_prim.h"
#include "domino/gui/style.h"

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

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINO_GUI_GUI_H_INCLUDED */
