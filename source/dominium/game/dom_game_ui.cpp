#include "dom_game_ui.h"

#include <cstring>

extern "C" {
#include "domino/core/fixed.h"
}

namespace dom {

namespace {

static void clear_children(dui_context &ctx) {
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

} // namespace

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
    dui_widget *btn_exit;
    dui_widget *btn_load;
    dui_widget *btn_new;
    dui_widget *title;

    if (!root) {
        return;
    }

    clear_children(ctx);

    panel = add_child(ctx, root, DUI_WIDGET_PANEL);
    if (!panel) {
        return;
    }

    btn_exit = add_child(ctx, panel, DUI_WIDGET_BUTTON);
    btn_load = add_child(ctx, panel, DUI_WIDGET_BUTTON);
    btn_new = add_child(ctx, panel, DUI_WIDGET_BUTTON);
    title = add_child(ctx, panel, DUI_WIDGET_LABEL);

    set_text(title, "Dominium");
    set_text(btn_new, "New Game");
    set_text(btn_load, "Load Game");
    set_text(btn_exit, "Exit");

    /* Default layout: column; buttons inherit panel sizing. */
}

void dom_game_ui_build_in_game_hud(dui_context &ctx) {
    dui_widget *root = ctx.root;
    dui_widget *bar;
    dui_widget *label;

    if (!root) {
        return;
    }

    clear_children(ctx);

    bar = add_child(ctx, root, DUI_WIDGET_PANEL);
    if (!bar) {
        return;
    }
    bar->layout_rect.h = d_q16_16_from_int(48);

    label = add_child(ctx, bar, DUI_WIDGET_LABEL);
    set_text(label, "Running (stub HUD)");
}

} // namespace dom
