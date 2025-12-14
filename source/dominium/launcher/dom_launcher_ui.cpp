#include "dom_launcher_ui.h"

#include <cstdio>
#include <cstring>

namespace dom {

namespace {

static dui_widget *g_panel = (dui_widget *)0;
static dui_widget *g_title = (dui_widget *)0;
static dui_widget *g_summary = (dui_widget *)0;
static dui_widget *g_instance = (dui_widget *)0;
static dui_widget *g_mode_button = (dui_widget *)0;
static dui_widget *g_connect = (dui_widget *)0;
static dui_widget *g_connect_edit_button = (dui_widget *)0;
static dui_widget *g_port = (dui_widget *)0;
static dui_widget *g_port_dec = (dui_widget *)0;
static dui_widget *g_port_inc = (dui_widget *)0;
static dui_widget *g_prev_instance = (dui_widget *)0;
static dui_widget *g_next_instance = (dui_widget *)0;
static dui_widget *g_listen = (dui_widget *)0;
static dui_widget *g_dedicated = (dui_widget *)0;
static dui_widget *g_connect_button = (dui_widget *)0;
static dui_widget *g_status = (dui_widget *)0;

static char g_buf_summary[128];
static char g_buf_instance[256];
static char g_buf_mode[64];
static char g_buf_connect[256];
static char g_buf_connect_edit[64];
static char g_buf_port[64];
static char g_buf_status[256];

static void clear_children(dui_context &ctx) {
    g_panel = (dui_widget *)0;
    g_title = (dui_widget *)0;
    g_summary = (dui_widget *)0;
    g_instance = (dui_widget *)0;
    g_mode_button = (dui_widget *)0;
    g_connect = (dui_widget *)0;
    g_connect_edit_button = (dui_widget *)0;
    g_port = (dui_widget *)0;
    g_port_dec = (dui_widget *)0;
    g_port_inc = (dui_widget *)0;
    g_prev_instance = (dui_widget *)0;
    g_next_instance = (dui_widget *)0;
    g_listen = (dui_widget *)0;
    g_dedicated = (dui_widget *)0;
    g_connect_button = (dui_widget *)0;
    g_status = (dui_widget *)0;

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

static int point_in_rect(const dui_rect *r, int px, int py) {
    int x0, y0, w, h;
    if (!r) return 0;
    x0 = d_q16_16_to_int(r->x);
    y0 = d_q16_16_to_int(r->y);
    w = d_q16_16_to_int(r->w);
    h = d_q16_16_to_int(r->h);
    return (px >= x0 && py >= y0 && px < (x0 + w) && py < (y0 + h));
}

static void on_prev_instance(dui_widget *self) {
    DomLauncherApp *app = self ? (DomLauncherApp *)self->user_data : (DomLauncherApp *)0;
    if (app) {
        app->select_prev_instance();
    }
}

static void on_next_instance(dui_widget *self) {
    DomLauncherApp *app = self ? (DomLauncherApp *)self->user_data : (DomLauncherApp *)0;
    if (app) {
        app->select_next_instance();
    }
}

static void on_cycle_mode(dui_widget *self) {
    DomLauncherApp *app = self ? (DomLauncherApp *)self->user_data : (DomLauncherApp *)0;
    if (app) {
        app->cycle_selected_mode();
    }
}

static void on_edit_connect(dui_widget *self) {
    DomLauncherApp *app = self ? (DomLauncherApp *)self->user_data : (DomLauncherApp *)0;
    if (app) {
        app->toggle_connect_host_edit();
    }
}

static void on_port_dec(dui_widget *self) {
    DomLauncherApp *app = self ? (DomLauncherApp *)self->user_data : (DomLauncherApp *)0;
    if (app) {
        app->adjust_net_port(-1);
    }
}

static void on_port_inc(dui_widget *self) {
    DomLauncherApp *app = self ? (DomLauncherApp *)self->user_data : (DomLauncherApp *)0;
    if (app) {
        app->adjust_net_port(+1);
    }
}

static void on_listen(dui_widget *self) {
    DomLauncherApp *app = self ? (DomLauncherApp *)self->user_data : (DomLauncherApp *)0;
    if (app) {
        (void)app->launch_game_listen();
    }
}

static void on_dedicated(dui_widget *self) {
    DomLauncherApp *app = self ? (DomLauncherApp *)self->user_data : (DomLauncherApp *)0;
    if (app) {
        (void)app->launch_game_dedicated();
    }
}

static void on_connect(dui_widget *self) {
    DomLauncherApp *app = self ? (DomLauncherApp *)self->user_data : (DomLauncherApp *)0;
    if (app) {
        (void)app->launch_game_connect();
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

void dom_launcher_ui_build_root(dui_context &ctx, DomLauncherApp &app) {
    dui_widget *root = ctx.root;
    if (!root) {
        dui_init_context(&ctx);
        root = ctx.root;
    }
    if (!root) {
        return;
    }

    clear_children(ctx);

    g_panel = add_child(ctx, root, DUI_WIDGET_PANEL);
    if (!g_panel) {
        return;
    }
    g_panel->layout_rect.h = d_q16_16_from_int(440);

    g_title = add_child(ctx, g_panel, DUI_WIDGET_LABEL);
    if (g_title) g_title->text = "Dominium Launcher";

    g_summary = add_child(ctx, g_panel, DUI_WIDGET_LABEL);
    g_status = add_child(ctx, g_panel, DUI_WIDGET_LABEL);

    g_instance = add_child(ctx, g_panel, DUI_WIDGET_LABEL);
    g_prev_instance = add_child(ctx, g_panel, DUI_WIDGET_BUTTON);
    g_next_instance = add_child(ctx, g_panel, DUI_WIDGET_BUTTON);

    g_mode_button = add_child(ctx, g_panel, DUI_WIDGET_BUTTON);

    g_connect = add_child(ctx, g_panel, DUI_WIDGET_LABEL);
    g_connect_edit_button = add_child(ctx, g_panel, DUI_WIDGET_BUTTON);

    g_port = add_child(ctx, g_panel, DUI_WIDGET_LABEL);
    g_port_dec = add_child(ctx, g_panel, DUI_WIDGET_BUTTON);
    g_port_inc = add_child(ctx, g_panel, DUI_WIDGET_BUTTON);

    g_listen = add_child(ctx, g_panel, DUI_WIDGET_BUTTON);
    g_dedicated = add_child(ctx, g_panel, DUI_WIDGET_BUTTON);
    g_connect_button = add_child(ctx, g_panel, DUI_WIDGET_BUTTON);

    if (g_prev_instance) {
        g_prev_instance->text = "Prev Instance";
        g_prev_instance->on_click = on_prev_instance;
        g_prev_instance->user_data = (void *)&app;
    }
    if (g_next_instance) {
        g_next_instance->text = "Next Instance";
        g_next_instance->on_click = on_next_instance;
        g_next_instance->user_data = (void *)&app;
    }
    if (g_mode_button) {
        g_mode_button->on_click = on_cycle_mode;
        g_mode_button->user_data = (void *)&app;
    }
    if (g_connect_edit_button) {
        g_connect_edit_button->on_click = on_edit_connect;
        g_connect_edit_button->user_data = (void *)&app;
    }
    if (g_port_dec) {
        g_port_dec->text = "Port -";
        g_port_dec->on_click = on_port_dec;
        g_port_dec->user_data = (void *)&app;
    }
    if (g_port_inc) {
        g_port_inc->text = "Port +";
        g_port_inc->on_click = on_port_inc;
        g_port_inc->user_data = (void *)&app;
    }
    if (g_listen) {
        g_listen->text = "Start Local Host";
        g_listen->on_click = on_listen;
        g_listen->user_data = (void *)&app;
    }
    if (g_dedicated) {
        g_dedicated->text = "Start Dedicated Host";
        g_dedicated->on_click = on_dedicated;
        g_dedicated->user_data = (void *)&app;
    }
    if (g_connect_button) {
        g_connect_button->text = "Connect To Host";
        g_connect_button->on_click = on_connect;
        g_connect_button->user_data = (void *)&app;
    }
}

void dom_launcher_ui_update(dui_context &ctx, DomLauncherApp &app) {
    const int inst_idx = app.selected_instance_index();
    const unsigned inst_count = (unsigned)app.instances().size();

    (void)ctx;
    std::snprintf(g_buf_summary, sizeof(g_buf_summary), "Products: %u  Instances: %u",
                  (unsigned)app.products().size(),
                  (unsigned)app.instances().size());
    if (g_summary) g_summary->text = g_buf_summary;

    if (inst_idx >= 0 && inst_idx < (int)app.instances().size()) {
        const InstanceInfo &inst = app.instances()[(size_t)inst_idx];
        std::snprintf(g_buf_instance, sizeof(g_buf_instance),
                      "Instance: %s (%d/%u)", inst.id.c_str(), inst_idx + 1, inst_count);
    } else {
        std::snprintf(g_buf_instance, sizeof(g_buf_instance),
                      "Instance: (none)");
    }
    if (g_instance) g_instance->text = g_buf_instance;

    std::snprintf(g_buf_mode, sizeof(g_buf_mode),
                  "Mode: %s", app.selected_mode().c_str());
    if (g_mode_button) g_mode_button->text = g_buf_mode;

    std::snprintf(g_buf_connect, sizeof(g_buf_connect),
                  "Connect host: %s%s",
                  app.connect_host().c_str(),
                  app.editing_connect_host() ? " (editing)" : "");
    if (g_connect) g_connect->text = g_buf_connect;

    std::snprintf(g_buf_connect_edit, sizeof(g_buf_connect_edit),
                  "%s Connect Host",
                  app.editing_connect_host() ? "Finish" : "Edit");
    if (g_connect_edit_button) g_connect_edit_button->text = g_buf_connect_edit;

    std::snprintf(g_buf_port, sizeof(g_buf_port),
                  "Port: %u", (unsigned)app.net_port());
    if (g_port) g_port->text = g_buf_port;

    std::snprintf(g_buf_status, sizeof(g_buf_status),
                  "Status: %s", app.status_text().empty() ? "(none)" : app.status_text().c_str());
    if (g_status) g_status->text = g_buf_status;
}

int dom_launcher_ui_try_click(dui_context &ctx, int x, int y) {
    return traverse_try_click(ctx.root, x, y);
}

} // namespace dom
