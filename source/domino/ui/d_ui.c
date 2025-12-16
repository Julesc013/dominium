/*
FILE: source/domino/ui/d_ui.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / ui/d_ui
RESPONSIBILITY: Implements `d_ui`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include <stdlib.h>
#include <string.h>

#include "d_ui.h"

static dui_widget_id g_next_widget_id = 1u;

static void dui_reset_widget(dui_widget *w, dui_widget_kind kind)
{
    if (!w) {
        return;
    }
    memset(w, 0, sizeof(*w));
    w->id = g_next_widget_id++;
    w->kind = kind;
    w->flags = DUI_WIDGET_VISIBLE;
}

static void dui_free_tree(dui_widget *w)
{
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

void dui_init_context(dui_context *ctx)
{
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

void dui_shutdown_context(dui_context *ctx)
{
    if (!ctx) {
        return;
    }
    if (ctx->root) {
        dui_free_tree(ctx->root);
        ctx->root = (dui_widget *)0;
    }
}

dui_widget *dui_widget_create(dui_context *ctx, dui_widget_kind kind)
{
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

static void dui_detach_from_parent(dui_widget *w)
{
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

void dui_widget_destroy(dui_context *ctx, dui_widget *w)
{
    if (!ctx || !w) {
        return;
    }
    if (ctx->root == w) {
        return;
    }
    dui_detach_from_parent(w);
    dui_free_tree(w);
}

void dui_widget_add_child(dui_widget *parent, dui_widget *child)
{
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

void dui_widget_remove_from_parent(dui_widget *w)
{
    if (!w || !w->parent) {
        return;
    }
    dui_detach_from_parent(w);
}

static void dui_layout_children(dui_widget *parent, const dui_rect *root_rect)
{
    dui_widget *child;
    q16_16 cursor_y;
    q16_16 margin;
    q16_16 spacing;
    q16_16 default_h;

    if (!parent || !root_rect) {
        return;
    }

    parent->final_rect = *root_rect;
    margin = d_q16_16_from_int(8);
    spacing = d_q16_16_from_int(4);
    cursor_y = root_rect->y + margin;
    child = parent->first_child;
    default_h = d_q16_16_from_int(24);

    while (child) {
        if (child->flags & DUI_WIDGET_VISIBLE) {
            dui_rect rect;
            rect.x = root_rect->x + margin + child->layout_rect.x;
            rect.y = cursor_y + child->layout_rect.y;
            rect.w = root_rect->w - margin - margin;
            rect.h = child->layout_rect.h ? child->layout_rect.h : default_h;
            child->final_rect = rect;
            cursor_y = rect.y + rect.h + spacing;
            if (child->first_child) {
                dui_layout_children(child, &rect);
            }
        }
        child = child->next_sibling;
    }
}

void dui_layout(dui_context *ctx, const dui_rect *root_rect)
{
    if (!ctx || !ctx->root || !root_rect) {
        return;
    }
    ctx->root->layout_rect = *root_rect;
    ctx->root->final_rect = *root_rect;
    dui_layout_children(ctx->root, root_rect);
}

static void dui_emit_rect(d_gfx_cmd_buffer *buf, const dui_rect *rect, d_gfx_color color)
{
    d_gfx_draw_rect_cmd r;
    if (!buf || !rect) {
        return;
    }
    r.x = d_q16_16_to_int(rect->x);
    r.y = d_q16_16_to_int(rect->y);
    r.w = d_q16_16_to_int(rect->w);
    r.h = d_q16_16_to_int(rect->h);
    r.color = color;
    d_gfx_cmd_draw_rect(buf, &r);
}

static void dui_emit_text(d_gfx_cmd_buffer *buf, const dui_rect *rect, const char *text, d_gfx_color color)
{
    d_gfx_draw_text_cmd t;
    if (!buf || !rect) {
        return;
    }
    t.x = d_q16_16_to_int(rect->x);
    t.y = d_q16_16_to_int(rect->y);
    t.text = text ? text : "";
    t.color = color;
    d_gfx_cmd_draw_text(buf, &t);
}

static int dui_render_widget(const dui_widget *w, d_view_frame *frame)
{
    d_gfx_color bg_panel = { 0xffu, 0x2au, 0x2au, 0x2au };
    d_gfx_color bg_button = { 0xffu, 0x3au, 0x6eu, 0xa5u };
    d_gfx_color fg_text = { 0xffu, 0xffu, 0xffu, 0xffu };

    if (!w || !frame || !frame->cmd_buffer) {
        return -1;
    }
    if ((w->flags & DUI_WIDGET_VISIBLE) == 0u) {
        return 0;
    }

    switch (w->kind) {
    case DUI_WIDGET_ROOT:
        break;
    case DUI_WIDGET_PANEL:
        dui_emit_rect(frame->cmd_buffer, &w->final_rect, bg_panel);
        break;
    case DUI_WIDGET_BUTTON:
        dui_emit_rect(frame->cmd_buffer, &w->final_rect, bg_button);
        dui_emit_text(frame->cmd_buffer, &w->final_rect, w->text, fg_text);
        break;
    case DUI_WIDGET_LABEL:
        dui_emit_text(frame->cmd_buffer, &w->final_rect, w->text, fg_text);
        break;
    case DUI_WIDGET_LIST:
        dui_emit_rect(frame->cmd_buffer, &w->final_rect, bg_panel);
        break;
    default:
        break;
    }
    return 0;
}

void dui_render(dui_context *ctx, d_view_frame *frame)
{
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
