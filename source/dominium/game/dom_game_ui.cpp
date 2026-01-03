/*
FILE: source/dominium/game/dom_game_ui.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/dom_game_ui
RESPONSIBILITY: Implements `dom_game_ui`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
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
static dui_widget *g_exit_button = (dui_widget *)0;
static dui_widget *g_place_button = (dui_widget *)0;
static dui_widget *g_place_refiner_button = (dui_widget *)0;
static dui_widget *g_place_assembler_button = (dui_widget *)0;
static dui_widget *g_place_sink_button = (dui_widget *)0;
static dui_widget *g_place_spline_button = (dui_widget *)0;
static dui_widget *g_cancel_tool_button = (dui_widget *)0;
static dui_widget *g_instance_label = (dui_widget *)0;
static dui_widget *g_remaining_label = (dui_widget *)0;
static dui_widget *g_inventory_label = (dui_widget *)0;
static dui_widget *g_loading_status_label = (dui_widget *)0;
static DomGameApp *g_ui_app = (DomGameApp *)0;

static void clear_children(dui_context &ctx) {
    g_status_label = (dui_widget *)0;
    g_start_button = (dui_widget *)0;
    g_exit_button = (dui_widget *)0;
    g_place_button = (dui_widget *)0;
    g_place_refiner_button = (dui_widget *)0;
    g_place_assembler_button = (dui_widget *)0;
    g_place_sink_button = (dui_widget *)0;
    g_place_spline_button = (dui_widget *)0;
    g_cancel_tool_button = (dui_widget *)0;
    g_instance_label = (dui_widget *)0;
    g_remaining_label = (dui_widget *)0;
    g_inventory_label = (dui_widget *)0;
    g_loading_status_label = (dui_widget *)0;
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
        app->request_phase_action(DOM_GAME_PHASE_ACTION_START_HOST);
    }
}

static void on_click_exit(dui_widget *self) {
    DomGameApp *app = self ? (DomGameApp *)self->user_data : (DomGameApp *)0;
    if (app) {
        app->request_phase_action(DOM_GAME_PHASE_ACTION_QUIT_APP);
    }
}

static void on_click_place(dui_widget *self) {
    DomGameApp *app = self ? (DomGameApp *)self->user_data : (DomGameApp *)0;
    if (app) {
        app->build_tool_select_extractor();
    }
}

static void on_click_place_refiner(dui_widget *self) {
    DomGameApp *app = self ? (DomGameApp *)self->user_data : (DomGameApp *)0;
    if (app) {
        app->build_tool_select_refiner();
    }
}

static void on_click_place_assembler(dui_widget *self) {
    DomGameApp *app = self ? (DomGameApp *)self->user_data : (DomGameApp *)0;
    if (app) {
        app->build_tool_select_assembler();
    }
}

static void on_click_place_sink(dui_widget *self) {
    DomGameApp *app = self ? (DomGameApp *)self->user_data : (DomGameApp *)0;
    if (app) {
        app->build_tool_select_bin();
    }
}

static void on_click_place_spline(dui_widget *self) {
    DomGameApp *app = self ? (DomGameApp *)self->user_data : (DomGameApp *)0;
    if (app) {
        app->build_tool_select_spline();
    }
}

static void on_click_cancel_tool(dui_widget *self) {
    DomGameApp *app = self ? (DomGameApp *)self->user_data : (DomGameApp *)0;
    if (app) {
        app->build_tool_cancel();
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
    panel->layout_rect.h = d_q16_16_from_int(200);

    label = add_child(ctx, panel, DUI_WIDGET_LABEL);
    set_text(label, "Dominium");

    label = add_child(ctx, panel, DUI_WIDGET_LABEL);
    set_text(label, "Prototype Build");

    g_start_button = add_child(ctx, panel, DUI_WIDGET_BUTTON);
    if (g_start_button) {
        set_text(g_start_button, "Start Game");
        g_start_button->on_click = on_click_start;
        g_start_button->user_data = (void *)g_ui_app;
    }

    g_exit_button = add_child(ctx, panel, DUI_WIDGET_BUTTON);
    if (g_exit_button) {
        set_text(g_exit_button, "Exit");
        g_exit_button->on_click = on_click_exit;
        g_exit_button->user_data = (void *)g_ui_app;
    }
}

void dom_game_ui_build_loading(dui_context &ctx) {
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
    panel->layout_rect.h = d_q16_16_from_int(160);

    label = add_child(ctx, panel, DUI_WIDGET_LABEL);
    set_text(label, "Dominium");

    label = add_child(ctx, panel, DUI_WIDGET_LABEL);
    set_text(label, "Loading");

    g_loading_status_label = add_child(ctx, panel, DUI_WIDGET_LABEL);
    if (g_loading_status_label) {
        set_text(g_loading_status_label, "Loading... 0%");
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
    bar->layout_rect.h = d_q16_16_from_int(260);

    label_top = add_child(ctx, bar, DUI_WIDGET_LABEL);
    set_text(label_top, "Demo HUD");

    g_instance_label = add_child(ctx, bar, DUI_WIDGET_LABEL);
    set_text(g_instance_label, "Instance: - / Seed: -");

    g_remaining_label = add_child(ctx, bar, DUI_WIDGET_LABEL);
    set_text(g_remaining_label, "Remaining v0: (n/a)");

    g_inventory_label = add_child(ctx, bar, DUI_WIDGET_LABEL);
    set_text(g_inventory_label, "Inventory: (empty)");

    g_status_label = add_child(ctx, bar, DUI_WIDGET_LABEL);
    set_text(g_status_label, "Tool: (none)");

    g_place_button = add_child(ctx, bar, DUI_WIDGET_BUTTON);
    if (g_place_button) {
        set_text(g_place_button, "Tool: Place Demo Extractor");
        g_place_button->on_click = on_click_place;
        g_place_button->user_data = (void *)g_ui_app;
    }

    g_place_refiner_button = add_child(ctx, bar, DUI_WIDGET_BUTTON);
    if (g_place_refiner_button) {
        set_text(g_place_refiner_button, "Tool: Place Demo Refiner");
        g_place_refiner_button->on_click = on_click_place_refiner;
        g_place_refiner_button->user_data = (void *)g_ui_app;
    }

    g_place_assembler_button = add_child(ctx, bar, DUI_WIDGET_BUTTON);
    if (g_place_assembler_button) {
        set_text(g_place_assembler_button, "Tool: Place Demo Assembler");
        g_place_assembler_button->on_click = on_click_place_assembler;
        g_place_assembler_button->user_data = (void *)g_ui_app;
    }

    g_place_sink_button = add_child(ctx, bar, DUI_WIDGET_BUTTON);
    if (g_place_sink_button) {
        set_text(g_place_sink_button, "Tool: Place Demo Bin");
        g_place_sink_button->on_click = on_click_place_sink;
        g_place_sink_button->user_data = (void *)g_ui_app;
    }

    g_place_spline_button = add_child(ctx, bar, DUI_WIDGET_BUTTON);
    if (g_place_spline_button) {
        set_text(g_place_spline_button, "Tool: Draw Demo Item Conveyor");
        g_place_spline_button->on_click = on_click_place_spline;
        g_place_spline_button->user_data = (void *)g_ui_app;
    }

    g_cancel_tool_button = add_child(ctx, bar, DUI_WIDGET_BUTTON);
    if (g_cancel_tool_button) {
        set_text(g_cancel_tool_button, "Tool: Cancel");
        g_cancel_tool_button->on_click = on_click_cancel_tool;
        g_cancel_tool_button->user_data = (void *)g_ui_app;
    }
}

void dom_game_ui_set_status(dui_context &ctx, const char *text) {
    (void)ctx;
    if (g_status_label) {
        g_status_label->text = text;
    }
}

void dom_game_ui_set_loading_status(dui_context &ctx, const char *text) {
    (void)ctx;
    if (g_loading_status_label) {
        g_loading_status_label->text = text;
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
