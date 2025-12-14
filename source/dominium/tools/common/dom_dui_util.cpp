#include "dom_dui_util.h"

extern "C" {
#include "domino/core/fixed.h"
}

namespace dom {
namespace tools {
namespace {

static int point_in_rect(const dui_rect *r, int px, int py) {
    int x0, y0, w, h;
    if (!r) return 0;
    x0 = d_q16_16_to_int(r->x);
    y0 = d_q16_16_to_int(r->y);
    w = d_q16_16_to_int(r->w);
    h = d_q16_16_to_int(r->h);
    return (px >= x0 && py >= y0 && px < (x0 + w) && py < (y0 + h));
}

static void add_child_end_raw(dui_widget *parent, dui_widget *child) {
    if (!parent || !child) {
        return;
    }
    if (!parent->first_child) {
        parent->first_child = child;
        child->parent = parent;
        child->next_sibling = (dui_widget *)0;
        return;
    }
    dui_widget *cur = parent->first_child;
    while (cur->next_sibling) {
        cur = cur->next_sibling;
    }
    cur->next_sibling = child;
    child->parent = parent;
    child->next_sibling = (dui_widget *)0;
}

} // namespace

void dui_clear_children(dui_context &ctx, dui_widget *parent) {
    if (!parent) {
        return;
    }
    while (parent->first_child) {
        dui_widget *child = parent->first_child;
        parent->first_child = child->next_sibling;
        dui_widget_destroy(&ctx, child);
    }
}

dui_widget *dui_add_child_end(dui_context &ctx,
                              dui_widget *parent,
                              dui_widget_kind kind) {
    dui_widget *w = dui_widget_create(&ctx, kind);
    if (!w || !parent) {
        return (dui_widget *)0;
    }
    add_child_end_raw(parent, w);
    return w;
}

int dui_try_click(dui_context &ctx, int x, int y) {
    dui_widget *root = ctx.root;
    dui_widget *stack[64];
    int top = -1;

    if (!root) {
        return 0;
    }

    stack[++top] = root;
    while (top >= 0) {
        dui_widget *w = stack[top--];
        dui_widget *child;

        if ((w->flags & DUI_WIDGET_VISIBLE) && w->kind == DUI_WIDGET_BUTTON) {
            if (point_in_rect(&w->final_rect, x, y)) {
                if (w->on_click) {
                    w->on_click(w);
                    return 1;
                }
            }
        }

        child = w->first_child;
        while (child) {
            if (top < 63) {
                stack[++top] = child;
            }
            child = child->next_sibling;
        }
    }
    return 0;
}

} // namespace tools
} // namespace dom

