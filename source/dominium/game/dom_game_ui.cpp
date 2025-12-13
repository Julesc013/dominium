#include "dom_game_ui.h"

#include <cstring>
extern "C" {
#include "domino/core/fixed.h"
}
#include "dom_game_ui_debug.h"

namespace dom {

namespace {

static dui_widget *g_status_label = (dui_widget *)0;
static dui_widget *g_start_button = (dui_widget *)0;
static dui_widget *g_place_button = (dui_widget *)0;
static dui_widget *g_instance_label = (dui_widget *)0;
static dui_widget *g_remaining_label = (dui_widget *)0;
static dui_widget *g_inventory_label = (dui_widget *)0;
static DomGameApp *g_ui_app = (DomGameApp *)0;

static void clear_children(dui_context &ctx) {
    g_status_label = (dui_widget *)0;
    g_start_button = (dui_widget *)0;
    g_place_button = (dui_widget *)0;
    g_instance_label = (dui_widget *)0;
    g_remaining_label = (dui_widget *)0;
    g_inventory_label = (dui_widget *)0;
    dom_game_ui_debug_reset();
    if (!ctx.root) {
        return;
    }
    while (ctx.root->first_child) {
        dui_widget *child = ctx.root->first_child;
        ctx.root->first_child = child->next_sibling;
        dui_widget_destroy(&ctx, child);
    }
}

static dui_widget *add_child(dui_context &ctx, dui_widget *parent, dui_widget_kind kind) {
    dui_widget *w = dui_widget_create(&ctx, kind);
    if (!w || !parent) {
        return (dui_widget *)0;
    }
    dui_widget_add_child(parent, w);
    return w;
}

static void set_text(dui_widget *w, const char *text) {
    if (!w) return;
    w->text = text;
}

static int point_in_rect(const dui_rect *r, int px, int py) {
    int x0, y0, w, h;
    if (!r) return 0;
    x0 = d_q16_16_to_int(r->x);
    y0 = d_q16_16_to_int(r->y);
    w = d_q16_16_to_int(r->w);
    h = d_q16_16_to_int(r->h);
    return (px >= x0 && py >= y0 && px < (x0 + w) && py < (y0 + h));
}

static void on_click_start(dui_widget *self) {
    DomGameApp *app = self ? (DomGameApp *)self->user_data : (DomGameApp *)0;
    if (app) {
        app->request_state_change(GAME_STATE_LOADING);
    }
}

static void on_click_place(dui_widget *self) {
    DomGameApp *app = self ? (DomGameApp *)self->user_data : (DomGameApp *)0;
    if (app) {
        app->spawn_demo_blueprint();
    }
}

static int traverse_try_click(dui_widget *root, int x, int y) {
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

} // namespace

void dom_game_ui_set_app(DomGameApp *app) {
    g_ui_app = app;
}

void dom_game_ui_build_root(dui_context &ctx, GameMode mode) {
    (void)mode;

    if (!ctx.root) {
        dui_init_context(&ctx);
    }
    clear_children(ctx);
    dom_game_ui_build_main_menu(ctx);
}

void dom_game_ui_build_main_menu(dui_context &ctx) {
    dui_widget *root = ctx.root;
    dui_widget *panel;
    dui_widget *label;

    if (!root) {
        return;
    }

    clear_children(ctx);

    panel = add_child(ctx, root, DUI_WIDGET_PANEL);
    if (!panel) {
        return;
    }

    label = add_child(ctx, panel, DUI_WIDGET_LABEL);
    set_text(label, "Dominium Demo");

    g_start_button = add_child(ctx, panel, DUI_WIDGET_BUTTON);
    if (g_start_button) {
        set_text(g_start_button, "Start Demo");
        g_start_button->on_click = on_click_start;
        g_start_button->user_data = (void *)g_ui_app;
    }
}

void dom_game_ui_build_in_game(dui_context &ctx) {
    dui_widget *root = ctx.root;
    dui_widget *bar;
    dui_widget *label_top;

    if (!root) {
        return;
    }

    clear_children(ctx);

    bar = add_child(ctx, root, DUI_WIDGET_PANEL);
    if (!bar) {
        return;
    }
    bar->layout_rect.h = d_q16_16_from_int(48);

    label_top = add_child(ctx, bar, DUI_WIDGET_LABEL);
    set_text(label_top, "Demo HUD");

    g_instance_label = add_child(ctx, bar, DUI_WIDGET_LABEL);
    set_text(g_instance_label, "Instance: - / Seed: -");

    g_remaining_label = add_child(ctx, bar, DUI_WIDGET_LABEL);
    set_text(g_remaining_label, "Remaining v0: (n/a)");

    g_inventory_label = add_child(ctx, bar, DUI_WIDGET_LABEL);
    set_text(g_inventory_label, "Inventory: (empty)");

    g_place_button = add_child(ctx, bar, DUI_WIDGET_BUTTON);
    if (g_place_button) {
        set_text(g_place_button, "Place Extractor Here");
        g_place_button->on_click = on_click_place;
        g_place_button->user_data = (void *)g_ui_app;
    }
}

void dom_game_ui_set_status(dui_context &ctx, const char *text) {
    (void)ctx;
    if (g_status_label) {
        g_status_label->text = text;
    }
}

dui_widget *dom_game_ui_get_start_button(void) { return g_start_button; }
dui_widget *dom_game_ui_get_place_button(void) { return g_place_button; }
dui_widget *dom_game_ui_get_instance_label(void) { return g_instance_label; }
dui_widget *dom_game_ui_get_remaining_label(void) { return g_remaining_label; }
dui_widget *dom_game_ui_get_inventory_label(void) { return g_inventory_label; }

int dom_game_ui_try_click(dui_context &ctx, int x, int y) {
    return traverse_try_click(ctx.root, x, y);
}

} // namespace dom
