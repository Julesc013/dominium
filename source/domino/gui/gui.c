#include "domino/gui/gui.h"
#include "domino/canvas.h"
#include <stdlib.h>
#include <string.h>

#define DGUI_MAX_CHILDREN 16
#define DGUI_TEXT_MAX 128
#define DGUI_MAX_WIDGETS 128

struct dgui_widget {
    dgui_widget_type type;
    dgui_layout layout;
    char text[DGUI_TEXT_MAX];
    dgui_widget* children[DGUI_MAX_CHILDREN];
    int child_count;
    int x, y, w, h;
    dgui_activate_fn on_activate;
    void* user;
};

struct dgui_context {
    dgui_widget* root;
    dgui_widget* focus[DGUI_MAX_WIDGETS];
    int focus_count;
    int focus_index;
    const dgui_style* style;
};

static void dgui_copy(char* dst, size_t cap, const char* src) {
    size_t len;
    if (!dst || cap == 0) return;
    if (!src) {
        dst[0] = '\0';
        return;
    }
    len = strlen(src);
    if (len >= cap) len = cap - 1u;
    memcpy(dst, src, len);
    dst[len] = '\0';
}

static dgui_widget* dgui_alloc_widget(dgui_widget_type type) {
    dgui_widget* w = (dgui_widget*)malloc(sizeof(dgui_widget));
    if (!w) return NULL;
    memset(w, 0, sizeof(*w));
    w->type = type;
    w->layout = DGUI_LAYOUT_VERTICAL;
    return w;
}

dgui_context* dgui_create(void) {
    dgui_context* ctx = (dgui_context*)malloc(sizeof(dgui_context));
    if (!ctx) return NULL;
    memset(ctx, 0, sizeof(*ctx));
    ctx->style = dgui_style_default();
    return ctx;
}

void dgui_destroy(dgui_context* ctx) {
    int i;
    if (!ctx) return;
    for (i = 0; i < ctx->focus_count; ++i) {
        free(ctx->focus[i]);
    }
    if (ctx->root) free(ctx->root);
    free(ctx);
}

void dgui_set_root(dgui_context* ctx, dgui_widget* root) {
    if (!ctx) return;
    ctx->root = root;
}

void dgui_set_style(dgui_context* ctx, const dgui_style* style) {
    if (!ctx) return;
    ctx->style = style ? style : dgui_style_default();
}

dgui_widget* dgui_panel(dgui_context* ctx, dgui_layout layout) {
    dgui_widget* w = dgui_alloc_widget(DGUI_WIDGET_PANEL);
    if (w) w->layout = layout;
    return w;
}

dgui_widget* dgui_label(dgui_context* ctx, const char* text) {
    dgui_widget* w = dgui_alloc_widget(DGUI_WIDGET_LABEL);
    if (w) dgui_copy(w->text, sizeof(w->text), text);
    return w;
}

dgui_widget* dgui_button(dgui_context* ctx, const char* text, dgui_activate_fn cb, void* user) {
    dgui_widget* w = dgui_alloc_widget(DGUI_WIDGET_BUTTON);
    if (w) {
        dgui_copy(w->text, sizeof(w->text), text);
        w->on_activate = cb;
        w->user = user;
    }
    return w;
}

dgui_widget* dgui_list(dgui_context* ctx, const char* const* items, int count) {
    (void)items;
    (void)count;
    return dgui_alloc_widget(DGUI_WIDGET_LIST);
}

int dgui_widget_add(dgui_widget* parent, dgui_widget* child) {
    if (!parent || !child) return 0;
    if (parent->child_count >= DGUI_MAX_CHILDREN) return 0;
    parent->children[parent->child_count++] = child;
    return 1;
}

static void dgui_collect_focus(dgui_context* ctx, dgui_widget* w) {
    int i;
    if (!ctx || !w) return;
    if (w->type == DGUI_WIDGET_BUTTON) {
        if (ctx->focus_count < DGUI_MAX_WIDGETS) {
            ctx->focus[ctx->focus_count++] = w;
        }
    }
    for (i = 0; i < w->child_count; ++i) {
        dgui_collect_focus(ctx, w->children[i]);
    }
}

static void dgui_layout(dgui_widget* w, int x, int y, int w_px, int h_px) {
    int i;
    if (!w) return;
    w->x = x; w->y = y; w->w = w_px; w->h = h_px;
    if (w->type == DGUI_WIDGET_PANEL && w->child_count > 0) {
        if (w->layout == DGUI_LAYOUT_VERTICAL) {
            int slot = h_px / w->child_count;
            int extra = h_px - slot * w->child_count;
            int cy = y;
            for (i = 0; i < w->child_count; ++i) {
                int ch = slot + ((i == w->child_count - 1) ? extra : 0);
                dgui_layout(w->children[i], x, cy, w_px, ch);
                cy += ch;
            }
        } else {
            int slot = w_px / w->child_count;
            int extra = w_px - slot * w->child_count;
            int cx = x;
            for (i = 0; i < w->child_count; ++i) {
                int cw = slot + ((i == w->child_count - 1) ? extra : 0);
                dgui_layout(w->children[i], cx, y, cw, h_px);
                cx += cw;
            }
        }
    }
}

static void dgui_render_widget(const dgui_context* ctx, dgui_widget* w, struct dcvs_t* canvas) {
    int i;
    if (!w) return;
    if (w->type == DGUI_WIDGET_PANEL) {
        dgui_rect_prim rp;
        rp.rect.x = w->x; rp.rect.y = w->y; rp.rect.w = w->w; rp.rect.h = w->h;
        rp.fill = ctx->style->panel;
        rp.stroke = ctx->style->panel;
        rp.stroke_width = 0;
        rp.corner_radius = 0;
        dgui_draw_rect(canvas, &rp);
    } else if (w->type == DGUI_WIDGET_LABEL) {
        dgui_text_prim tp;
        tp.x = w->x + ctx->style->padding;
        tp.y = w->y + ctx->style->padding + 1;
        tp.color = ctx->style->text;
        tp.text = w->text;
        dgui_draw_text(canvas, &tp);
    } else if (w->type == DGUI_WIDGET_BUTTON) {
        dgui_rect_prim rp;
        dgui_text_prim tp;
        rp.rect.x = w->x + ctx->style->padding;
        rp.rect.y = w->y + ctx->style->padding;
        rp.rect.w = w->w - ctx->style->padding * 2;
        rp.rect.h = w->h - ctx->style->padding * 2;
        rp.fill = ctx->style->accent;
        rp.stroke = ctx->style->panel;
        rp.stroke_width = 0;
        rp.corner_radius = 2;
        dgui_draw_rect(canvas, &rp);
        tp.x = rp.rect.x + 1;
        tp.y = rp.rect.y + 1;
        tp.color = ctx->style->text;
        tp.text = w->text;
        dgui_draw_text(canvas, &tp);
    }
    for (i = 0; i < w->child_count; ++i) {
        dgui_render_widget(ctx, w->children[i], canvas);
    }
}

void dgui_render(dgui_context* ctx, struct dcvs_t* canvas) {
    if (!ctx || !ctx->root || !canvas) return;
    ctx->focus_count = 0;
    ctx->focus_index = 0;
    dgui_collect_focus(ctx, ctx->root);
    dgui_layout(ctx->root, 0, 0, 640, 360);
    dgui_render_widget(ctx, ctx->root, canvas);
}

void dgui_handle_key(dgui_context* ctx, int keycode) {
    dgui_widget* focused;
    if (!ctx || ctx->focus_count == 0) return;
    focused = ctx->focus[ctx->focus_index];
    if (keycode == 1002 /* down */) {
        ctx->focus_index = (ctx->focus_index + 1) % ctx->focus_count;
    } else if (keycode == 1001 /* up */) {
        ctx->focus_index -= 1;
        if (ctx->focus_index < 0) ctx->focus_index = ctx->focus_count - 1;
    } else if (keycode == 10 && focused && focused->on_activate) {
        focused->on_activate(focused, focused->user);
    }
}
