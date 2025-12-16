/*
FILE: source/domino/ui/d_ui.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / ui/d_ui
RESPONSIBILITY: Defines internal contract for `d_ui`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
/* Minimal Domino UI toolkit (C89). */
#ifndef D_UI_H
#define D_UI_H

#include "domino/core/types.h"
#include "domino/core/fixed.h"
#include "view/d_view.h"
#include "domino/gfx.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef u32 dui_widget_id;

typedef enum {
    DUI_WIDGET_ROOT = 0,
    DUI_WIDGET_PANEL,
    DUI_WIDGET_LABEL,
    DUI_WIDGET_BUTTON,
    DUI_WIDGET_LIST
} dui_widget_kind;

#define DUI_WIDGET_VISIBLE   (1u << 0)
#define DUI_WIDGET_DISABLED  (1u << 1)
#define DUI_WIDGET_FOCUSABLE (1u << 2)

typedef struct dui_rect {
    q16_16 x, y, w, h;
} dui_rect;

typedef struct dui_widget {
    dui_widget_id  id;
    dui_widget_kind  kind;

    struct dui_widget *parent;
    struct dui_widget *first_child;
    struct dui_widget *next_sibling;

    dui_rect        layout_rect;
    dui_rect        final_rect;

    u32             flags;

    const char     *text;
    void           *user_data;

    void (*on_click)(struct dui_widget *self);
} dui_widget;

/* UI tree context; one per view or per application. */
typedef struct dui_context {
    dui_widget *root;
} dui_context;

/* Create/destroy context */
void dui_init_context(dui_context *ctx);
void dui_shutdown_context(dui_context *ctx);

/* Create/destroy widgets */
dui_widget *dui_widget_create(dui_context *ctx, dui_widget_kind kind);
void        dui_widget_destroy(dui_context *ctx, dui_widget *w);

/* Hierarchy management */
void dui_widget_add_child(dui_widget *parent, dui_widget *child);
void dui_widget_remove_from_parent(dui_widget *w);

/* Layout and render integration */
void dui_layout(dui_context *ctx, const dui_rect *root_rect);
void dui_render(dui_context *ctx, d_view_frame *frame);

#ifdef __cplusplus
}
#endif

#endif /* D_UI_H */
