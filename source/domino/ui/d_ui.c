#include <stdlib.h>
#include <string.h>

#include "d_ui.h"
#include "domino/core/fixed.h"

static dui_widget_id g_next_widget_id = 1u;

static void dui_reset_widget(dui_widget *w, dui_widget_kind kind) {
    if (!w) {
        return;
    }
    memset(w, 0, sizeof(*w));
    w->id = g_next_widget_id++;
    w->kind = kind;
    w->flags = DUI_WIDGET_VISIBLE;
    w->style.ptr = (unsigned char *)0;
    w->style.len = 0u;
}

static void dui_free_tree(dui_widget *w) {
    dui_widget *child;
    if (!w) {
        return;
    }
    child = w->first_child;
    while (child) {
        dui_widget *next = child->next_sibling;
        dui_free_tree(child);
        child = next;
    }
    free(w);
}

void dui_init_context(dui_context *ctx) {
    if (!ctx) {
        return;
    }
    ctx->root = (dui_widget *)malloc(sizeof(dui_widget));
    if (!ctx->root) {
        return;
    }
    dui_reset_widget(ctx->root, DUI_WIDGET_ROOT);
    ctx->root->parent = (dui_widget *)0;
    ctx->root->text = (const char *)0;
}

void dui_shutdown_context(dui_context *ctx) {
    if (!ctx) {
        return;
    }
    if (ctx->root) {
        dui_free_tree(ctx->root);
        ctx->root = (dui_widget *)0;
    }
}

dui_widget *dui_widget_create(dui_context *ctx, dui_widget_kind kind) {
    dui_widget *w;
    if (!ctx) {
        return (dui_widget *)0;
    }
    w = (dui_widget *)malloc(sizeof(dui_widget));
    if (!w) {
        return (dui_widget *)0;
    }
    dui_reset_widget(w, kind);
    return w;
}

static void dui_detach_from_parent(dui_widget *w) {
    dui_widget *parent;
    if (!w) {
        return;
    }
    parent = w->parent;
    if (!parent) {
        return;
    }
    if (parent->first_child == w) {
        parent->first_child = w->next_sibling;
    } else {
        dui_widget *cur = parent->first_child;
        while (cur) {
            if (cur->next_sibling == w) {
                cur->next_sibling = w->next_sibling;
                break;
            }
            cur = cur->next_sibling;
        }
    }
    w->parent = (dui_widget *)0;
    w->next_sibling = (dui_widget *)0;
}

void dui_widget_destroy(dui_context *ctx, dui_widget *w) {
    if (!ctx || !w) {
        return;
    }
    if (ctx->root == w) {
        return;
    }
    dui_detach_from_parent(w);
    dui_free_tree(w);
}

void dui_widget_add_child(dui_widget *parent, dui_widget *child) {
    if (!parent || !child) {
        return;
    }
    if (child->parent) {
        dui_widget_remove_from_parent(child);
    }
    child->next_sibling = parent->first_child;
    child->parent = parent;
    parent->first_child = child;
}

void dui_widget_remove_from_parent(dui_widget *w) {
    if (!w || !w->parent) {
        return;
    }
    dui_detach_from_parent(w);
}

static q16_16 dui_div_q16(q16_16 num, u32 denom) {
    if (denom == 0u) {
        return 0;
    }
    return d_q16_16_div(num, d_q16_16_from_int((i32)denom));
}

static void dui_layout_node(dui_widget *node, const dui_rect *available) {
    dui_widget *child;
    if (!node || !available) {
        return;
    }

    if (node->kind == DUI_WIDGET_ROOT || node->kind == DUI_WIDGET_PANEL) {
        u32 visible_children = 0u;
        q16_16 cursor_y;
        q16_16 default_h;

        node->final_rect = *available;
        child = node->first_child;
        while (child) {
            if (child->flags & DUI_WIDGET_VISIBLE) {
                visible_children += 1u;
            }
            child = child->next_sibling;
        }

        default_h = dui_div_q16(node->final_rect.h, visible_children ? visible_children : 1u);
        cursor_y = node->final_rect.y;
        child = node->first_child;
        while (child) {
            if (child->flags & DUI_WIDGET_VISIBLE) {
                dui_rect rect;
                rect.x = node->final_rect.x + child->layout_rect.x;
                rect.y = cursor_y + child->layout_rect.y;
                rect.w = child->layout_rect.w ? child->layout_rect.w : node->final_rect.w;
                rect.h = child->layout_rect.h ? child->layout_rect.h : default_h;
                child->final_rect = rect;
                cursor_y = rect.y + rect.h;
                dui_layout_node(child, &rect);
            }
            child = child->next_sibling;
        }
    } else {
        dui_rect rect;
        rect.x = available->x + node->layout_rect.x;
        rect.y = available->y + node->layout_rect.y;
        rect.w = node->layout_rect.w ? node->layout_rect.w : available->w;
        rect.h = node->layout_rect.h ? node->layout_rect.h : available->h;
        node->final_rect = rect;
    }
}

void dui_layout(dui_context *ctx, const dui_rect *root_rect) {
    if (!ctx || !ctx->root) {
        return;
    }
    if (root_rect) {
        ctx->root->layout_rect = *root_rect;
        ctx->root->final_rect = *root_rect;
    }
    dui_layout_node(ctx->root, &ctx->root->final_rect);
}

static int dui_render_rect(dgfx_cmd_buffer *buf, const dui_rect *rect, u32 color) {
    dgfx_sprite_t spr;
    if (!buf || !rect) {
        return -1;
    }
    spr.x = d_q16_16_to_int(rect->x);
    spr.y = d_q16_16_to_int(rect->y);
    spr.w = d_q16_16_to_int(rect->w);
    spr.h = d_q16_16_to_int(rect->h);
    spr.color_rgba = color;
    return dgfx_cmd_emit(buf, (uint16_t)DGFX_CMD_DRAW_SPRITES, &spr, (uint16_t)sizeof(dgfx_sprite_t)) ? 0 : -1;
}

static int dui_render_text(dgfx_cmd_buffer *buf, const dui_rect *rect, const char *text, u32 color) {
    dgfx_text_draw_t td;
    const char *safe_text = text ? text : "";
    if (!buf || !rect) {
        return -1;
    }
    td.x = d_q16_16_to_int(rect->x);
    td.y = d_q16_16_to_int(rect->y);
    td.color_rgba = color;
    td.utf8_text = safe_text;
    return dgfx_cmd_emit(buf, (uint16_t)DGFX_CMD_DRAW_TEXT, &td, (uint16_t)sizeof(dgfx_text_draw_t)) ? 0 : -1;
}

static int dui_render_widget(const dui_widget *w, d_view_frame *frame) {
    const u32 bg_root = 0x202020FFu;
    const u32 bg_panel = 0x2A2A2AFFu;
    const u32 bg_button = 0x3A6EA5FFu;
    const u32 fg_text = 0xFFFFFFFFu;
    int rc;

    if (!w || !frame || !frame->cmd_buffer) {
        return -1;
    }
    if ((w->flags & DUI_WIDGET_VISIBLE) == 0u) {
        return 0;
    }

    switch (w->kind) {
        case DUI_WIDGET_ROOT:
            rc = dui_render_rect(frame->cmd_buffer, &w->final_rect, bg_root);
            if (rc != 0) return rc;
            break;
        case DUI_WIDGET_PANEL:
            rc = dui_render_rect(frame->cmd_buffer, &w->final_rect, bg_panel);
            if (rc != 0) return rc;
            break;
        case DUI_WIDGET_BUTTON:
            rc = dui_render_rect(frame->cmd_buffer, &w->final_rect, bg_button);
            if (rc != 0) return rc;
            rc = dui_render_text(frame->cmd_buffer, &w->final_rect, w->text, fg_text);
            if (rc != 0) return rc;
            break;
        case DUI_WIDGET_LABEL:
            rc = dui_render_text(frame->cmd_buffer, &w->final_rect, w->text, fg_text);
            if (rc != 0) return rc;
            break;
        case DUI_WIDGET_LIST:
            rc = dui_render_rect(frame->cmd_buffer, &w->final_rect, bg_panel);
            if (rc != 0) return rc;
            break;
        default:
            break;
    }
    return 0;
}

void dui_render(dui_context *ctx, d_view_frame *frame) {
    dui_widget *stack[64];
    int top = -1;
    if (!ctx || !ctx->root || !frame) {
        return;
    }

    stack[++top] = ctx->root;
    while (top >= 0) {
        dui_widget *w = stack[top--];
        dui_widget *child;
        if (dui_render_widget(w, frame) != 0) {
            return;
        }
        child = w->first_child;
        while (child) {
            if (top < 63) {
                stack[++top] = child;
            }
            child = child->next_sibling;
        }
    }
}
