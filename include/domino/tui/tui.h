/*
FILE: include/domino/tui/tui.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / tui/tui
RESPONSIBILITY: Defines the public contract for `tui` (types/constants/function signatures); does NOT provide implementation.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/SPEC_ABI_TEMPLATES.md` where ABI stability matters.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOMINO_TUI_TUI_H_INCLUDED
#define DOMINO_TUI_TUI_H_INCLUDED

/* Domino text UI (C89).
 * Minimal widget tree with deterministic layout and navigation.
 */

#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

enum {
    D_TUI_KEY_NONE  = 0,
    D_TUI_KEY_ENTER = 10,
    D_TUI_KEY_UP    = 1001,
    D_TUI_KEY_DOWN  = 1002,
    D_TUI_KEY_RIGHT = 1003,
    D_TUI_KEY_LEFT  = 1004
};

typedef enum d_tui_widget_type {
    D_TUI_WIDGET_PANEL = 0,
    D_TUI_WIDGET_LABEL,
    D_TUI_WIDGET_BUTTON,
    D_TUI_WIDGET_LIST
} d_tui_widget_type;

typedef enum d_tui_layout {
    D_TUI_LAYOUT_VERTICAL = 0,
    D_TUI_LAYOUT_HORIZONTAL = 1
} d_tui_layout;

typedef struct d_tui_widget d_tui_widget;
typedef struct d_tui_context d_tui_context;

typedef void (*d_tui_activate_fn)(d_tui_widget* self, void* user);

d_tui_context* d_tui_create(void);
void           d_tui_destroy(d_tui_context* ctx);

void           d_tui_set_root(d_tui_context* ctx, d_tui_widget* root);

d_tui_widget*  d_tui_panel(d_tui_context* ctx, d_tui_layout layout);
d_tui_widget*  d_tui_label(d_tui_context* ctx, const char* text);
d_tui_widget*  d_tui_button(d_tui_context* ctx, const char* text,
                            d_tui_activate_fn on_activate, void* user);
d_tui_widget*  d_tui_list(d_tui_context* ctx, const char* const* items, int item_count);

int            d_tui_widget_add(d_tui_widget* parent, d_tui_widget* child);
void           d_tui_widget_set_text(d_tui_widget* w, const char* text);
void           d_tui_list_set_selection(d_tui_widget* w, int index);
int            d_tui_list_get_selection(const d_tui_widget* w);

void           d_tui_render(d_tui_context* ctx);
void           d_tui_handle_key(d_tui_context* ctx, int keycode);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINO_TUI_TUI_H_INCLUDED */
