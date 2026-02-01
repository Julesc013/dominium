/*
FILE: source/domino/tui/tui.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / tui/tui
RESPONSIBILITY: Implements `tui`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/specs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/specs/SPEC_*.md` without cross-layer coupling.
*/
#include "domino/tui/tui.h"
#include "domino/system/dsys.h"

#include <stdlib.h>
#include <string.h>

#define D_TUI_MAX_CHILDREN 16
#define D_TUI_TEXT_MAX     128
#define D_TUI_MAX_WIDGETS  128

typedef struct d_tui_widget_list {
    const char* const* items;
    int                count;
    int                selected;
} d_tui_widget_list;

struct d_tui_widget {
    d_tui_widget_type type;
    d_tui_layout      layout;
    char              text[D_TUI_TEXT_MAX];
    struct d_tui_widget* children[D_TUI_MAX_CHILDREN];
    int               child_count;
    int               x, y, w, h;
    d_tui_activate_fn on_activate;
    void*             user;
    d_tui_widget_list list;
};

struct d_tui_context {
    d_tui_widget* root;
    d_tui_widget* widgets[D_TUI_MAX_WIDGETS];
    int           widget_count;
    d_tui_widget* focus[D_TUI_MAX_WIDGETS];
    int           focus_count;
    int           focus_index;
};

static void d_tui_copy_text(char* dst, size_t cap, const char* src) {
    size_t len;
    if (!dst || cap == 0) {
        return;
    }
    if (!src) {
        dst[0] = '\0';
        return;
    }
    len = strlen(src);
    if (len >= cap) {
        len = cap - 1u;
    }
    memcpy(dst, src, len);
    dst[len] = '\0';
}

static d_tui_widget* d_tui_alloc_widget(d_tui_context* ctx, d_tui_widget_type type) {
    d_tui_widget* w;
    if (!ctx || ctx->widget_count >= D_TUI_MAX_WIDGETS) {
        return NULL;
    }
    w = (d_tui_widget*)malloc(sizeof(d_tui_widget));
    if (!w) {
        return NULL;
    }
    memset(w, 0, sizeof(*w));
    w->type = type;
    w->layout = D_TUI_LAYOUT_VERTICAL;
    w->text[0] = '\0';
    ctx->widgets[ctx->widget_count++] = w;
    return w;
}

d_tui_context* d_tui_create(void) {
    d_tui_context* ctx = (d_tui_context*)malloc(sizeof(d_tui_context));
    if (!ctx) {
        return NULL;
    }
    memset(ctx, 0, sizeof(*ctx));
    ctx->focus_index = 0;
    return ctx;
}

void d_tui_destroy(d_tui_context* ctx) {
    int i;
    if (!ctx) return;
    for (i = 0; i < ctx->widget_count; ++i) {
        free(ctx->widgets[i]);
    }
    free(ctx);
}

void d_tui_set_root(d_tui_context* ctx, d_tui_widget* root) {
    if (!ctx) return;
    ctx->root = root;
}

d_tui_widget* d_tui_panel(d_tui_context* ctx, d_tui_layout layout) {
    d_tui_widget* w = d_tui_alloc_widget(ctx, D_TUI_WIDGET_PANEL);
    if (w) {
        w->layout = layout;
    }
    return w;
}

d_tui_widget* d_tui_label(d_tui_context* ctx, const char* text) {
    d_tui_widget* w = d_tui_alloc_widget(ctx, D_TUI_WIDGET_LABEL);
    if (w) {
        d_tui_copy_text(w->text, sizeof(w->text), text);
    }
    return w;
}

d_tui_widget* d_tui_button(d_tui_context* ctx, const char* text,
                           d_tui_activate_fn on_activate, void* user) {
    d_tui_widget* w = d_tui_alloc_widget(ctx, D_TUI_WIDGET_BUTTON);
    if (w) {
        d_tui_copy_text(w->text, sizeof(w->text), text);
        w->on_activate = on_activate;
        w->user = user;
    }
    return w;
}

d_tui_widget* d_tui_list(d_tui_context* ctx, const char* const* items, int item_count) {
    d_tui_widget* w = d_tui_alloc_widget(ctx, D_TUI_WIDGET_LIST);
    if (w) {
        w->list.items = items;
        w->list.count = item_count;
        w->list.selected = 0;
    }
    return w;
}

int d_tui_widget_add(d_tui_widget* parent, d_tui_widget* child) {
    if (!parent || !child) return 0;
    if (parent->child_count >= D_TUI_MAX_CHILDREN) return 0;
    parent->children[parent->child_count++] = child;
    return 1;
}

void d_tui_widget_set_text(d_tui_widget* w, const char* text) {
    if (!w) return;
    d_tui_copy_text(w->text, sizeof(w->text), text);
}

void d_tui_list_set_selection(d_tui_widget* w, int index) {
    if (!w || w->type != D_TUI_WIDGET_LIST) return;
    if (index < 0) index = 0;
    if (index >= w->list.count) index = w->list.count - 1;
    w->list.selected = index;
}

int d_tui_list_get_selection(const d_tui_widget* w) {
    if (!w || w->type != D_TUI_WIDGET_LIST) return -1;
    return w->list.selected;
}

static void d_tui_collect_focus(d_tui_context* ctx, d_tui_widget* w) {
    int i;
    if (!ctx || !w) return;
    if (w->type == D_TUI_WIDGET_BUTTON || w->type == D_TUI_WIDGET_LIST) {
        if (ctx->focus_count < D_TUI_MAX_WIDGETS) {
            ctx->focus[ctx->focus_count++] = w;
        }
    }
    for (i = 0; i < w->child_count; ++i) {
        d_tui_collect_focus(ctx, w->children[i]);
    }
}

static void d_tui_rebuild_focus(d_tui_context* ctx) {
    int old_index = ctx->focus_index;
    ctx->focus_count = 0;
    ctx->focus_index = 0;
    d_tui_collect_focus(ctx, ctx->root);
    if (old_index < ctx->focus_count) {
        ctx->focus_index = old_index;
    } else if (ctx->focus_count > 0) {
        ctx->focus_index = ctx->focus_count - 1;
    }
}

static void d_tui_layout_widget(d_tui_widget* w, int x, int y, int w_px, int h_px) {
    int i;
    if (!w) return;
    w->x = x;
    w->y = y;
    w->w = w_px;
    w->h = h_px;
    if (w->type == D_TUI_WIDGET_PANEL && w->child_count > 0) {
        if (w->layout == D_TUI_LAYOUT_VERTICAL) {
            int slot_h = h_px / w->child_count;
            int extra = h_px - slot_h * w->child_count;
            int cy = y;
            for (i = 0; i < w->child_count; ++i) {
                int ch = slot_h + ((i == w->child_count - 1) ? extra : 0);
                d_tui_layout_widget(w->children[i], x, cy, w_px, ch);
                cy += ch;
            }
        } else {
            int slot_w = w_px / w->child_count;
            int extra = w_px - slot_w * w->child_count;
            int cx = x;
            for (i = 0; i < w->child_count; ++i) {
                int cw = slot_w + ((i == w->child_count - 1) ? extra : 0);
                d_tui_layout_widget(w->children[i], cx, y, cw, h_px);
                cx += cw;
            }
        }
    }
}

static void d_tui_render_label(const d_tui_widget* w, int focused) {
    int row;
    int col;
    char buf[D_TUI_TEXT_MAX];
    int len;
    if (!w) return;
    row = w->y;
    col = w->x;
    d_tui_copy_text(buf, sizeof(buf), w->text);
    len = (int)strlen(buf);
    if (len > w->w) {
        buf[w->w] = '\0';
    }
    if (focused) {
        dsys_terminal_draw_text(row, col, ">");
        dsys_terminal_draw_text(row, col + 1, buf);
    } else {
        dsys_terminal_draw_text(row, col, buf);
    }
}

static void d_tui_render_button(const d_tui_widget* w, int focused) {
    char buf[D_TUI_TEXT_MAX];
    char line[D_TUI_TEXT_MAX + 4];
    (void)focused;
    d_tui_copy_text(buf, sizeof(buf), w->text);
    line[0] = '[';
    line[1] = '\0';
    strncat(line, buf, sizeof(line) - strlen(line) - 1);
    strncat(line, "]", sizeof(line) - strlen(line) - 1);
    if (focused) {
        dsys_terminal_draw_text(w->y, w->x, ">");
        dsys_terminal_draw_text(w->y, w->x + 1, line);
    } else {
        dsys_terminal_draw_text(w->y, w->x, line);
    }
}

static void d_tui_render_list(const d_tui_widget* w, int focused) {
    int i;
    int rows = w->h;
    int start = 0;
    if (w->list.selected >= rows) {
        start = w->list.selected - rows + 1;
    }
    for (i = 0; i < rows && (start + i) < w->list.count; ++i) {
        const char* item = w->list.items[start + i];
        char line[D_TUI_TEXT_MAX];
        d_tui_copy_text(line, sizeof(line), item ? item : "");
        line[w->w - 2 > 0 ? w->w - 2 : 0] = '\0';
        if (focused && (start + i) == w->list.selected) {
            dsys_terminal_draw_text(w->y + i, w->x, ">");
            dsys_terminal_draw_text(w->y + i, w->x + 1, line);
        } else {
            dsys_terminal_draw_text(w->y + i, w->x, " ");
            dsys_terminal_draw_text(w->y + i, w->x + 1, line);
        }
    }
}

static void d_tui_render_widget(const d_tui_context* ctx, const d_tui_widget* w) {
    int i;
    int focused = 0;
    if (!w) return;
    if (ctx && ctx->focus_count > 0 && ctx->focus_index < ctx->focus_count) {
        focused = (ctx->focus[ctx->focus_index] == w) ? 1 : 0;
    }
    switch (w->type) {
    case D_TUI_WIDGET_LABEL:
        d_tui_render_label(w, focused);
        break;
    case D_TUI_WIDGET_BUTTON:
        d_tui_render_button(w, focused);
        break;
    case D_TUI_WIDGET_LIST:
        d_tui_render_list(w, focused);
        break;
    default:
        break;
    }
    for (i = 0; i < w->child_count; ++i) {
        d_tui_render_widget(ctx, w->children[i]);
    }
}

void d_tui_render(d_tui_context* ctx) {
    int rows = 24;
    int cols = 80;
    if (!ctx || !ctx->root) return;
    dsys_terminal_get_size(&rows, &cols);
    if (rows < 1) rows = 24;
    if (cols < 1) cols = 80;
    d_tui_rebuild_focus(ctx);
    d_tui_layout_widget(ctx->root, 0, 0, cols, rows);
    dsys_terminal_clear();
    d_tui_render_widget(ctx, ctx->root);
}

static void d_tui_focus_next(d_tui_context* ctx) {
    if (!ctx || ctx->focus_count == 0) return;
    ctx->focus_index = (ctx->focus_index + 1) % ctx->focus_count;
}

static void d_tui_focus_prev(d_tui_context* ctx) {
    if (!ctx || ctx->focus_count == 0) return;
    ctx->focus_index -= 1;
    if (ctx->focus_index < 0) {
        ctx->focus_index = ctx->focus_count - 1;
    }
}

void d_tui_handle_key(d_tui_context* ctx, int keycode) {
    d_tui_widget* focused;
    if (!ctx || ctx->focus_count == 0) return;
    focused = ctx->focus[ctx->focus_index];
    if (keycode == D_TUI_KEY_UP) {
        if (focused && focused->type == D_TUI_WIDGET_LIST) {
            d_tui_list_set_selection(focused, focused->list.selected - 1);
        } else {
            d_tui_focus_prev(ctx);
        }
    } else if (keycode == D_TUI_KEY_DOWN) {
        if (focused && focused->type == D_TUI_WIDGET_LIST) {
            d_tui_list_set_selection(focused, focused->list.selected + 1);
        } else {
            d_tui_focus_next(ctx);
        }
    } else if (keycode == D_TUI_KEY_LEFT) {
        d_tui_focus_prev(ctx);
    } else if (keycode == D_TUI_KEY_RIGHT) {
        d_tui_focus_next(ctx);
    } else if (keycode == D_TUI_KEY_ENTER) {
        if (focused && focused->on_activate) {
            focused->on_activate(focused, focused->user);
        }
    }
}
