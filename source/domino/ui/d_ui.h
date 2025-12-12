/* Minimal Domino UI toolkit (C89). */
#ifndef D_UI_H
#define D_UI_H

#include "domino/core/types.h"
#include "domino/core/d_tlv.h"
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
    dui_widget_kind kind;

    struct dui_widget *parent;
    struct dui_widget *first_child;
    struct dui_widget *next_sibling;

    dui_rect        layout_rect;    /* desired rect before layout */
    dui_rect        final_rect;     /* computed by layout pass */

    u32             flags;          /* VISIBLE, DISABLED, FOCUSABLE, etc. */

    const char     *text;           /* label text for LABEL/BUTTON, etc. */
    d_tlv_blob      style;          /* per-widget style info */

    void           *user_data;      /* opaque for application */

    /* For now, input handlers can be simple function pointers. */
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
