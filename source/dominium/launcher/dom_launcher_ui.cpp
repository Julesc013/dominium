#include "dom_launcher_ui.h"

#include <cstdio>
#include <cstring>
#include <string>
#include <vector>

namespace dom {

namespace {

static dui_widget *g_panel = (dui_widget *)0;
static dui_widget *g_title = (dui_widget *)0;
static dui_widget *g_summary = (dui_widget *)0;
static dui_widget *g_instance = (dui_widget *)0;
static dui_widget *g_toggle_view = (dui_widget *)0;
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

static char g_buf_repo_mods[128];
static char g_buf_repo_packs[128];

struct LaunchCtx {
    DomLauncherApp *app;
    std::string tool_id;
    std::string load_path;
    std::string label;
    int use_demo;

    LaunchCtx()
        : app((DomLauncherApp *)0),
          tool_id(),
          load_path(),
          label(),
          use_demo(0) {}
};

static std::vector<LaunchCtx *> g_launch_ctxs;
static std::vector<dui_widget *> g_tool_buttons;
static std::vector<dui_widget *> g_mod_buttons;
static std::vector<dui_widget *> g_pack_buttons;
static dui_widget *g_repo_mods_label = (dui_widget *)0;
static dui_widget *g_repo_packs_label = (dui_widget *)0;

static void free_launch_contexts(void) {
    size_t i;
    for (i = 0u; i < g_launch_ctxs.size(); ++i) {
        delete g_launch_ctxs[i];
    }
    g_launch_ctxs.clear();
    g_tool_buttons.clear();
    g_mod_buttons.clear();
    g_pack_buttons.clear();
}

static void clear_children(dui_context &ctx) {
    free_launch_contexts();

    g_panel = (dui_widget *)0;
    g_title = (dui_widget *)0;
    g_summary = (dui_widget *)0;
    g_instance = (dui_widget *)0;
    g_toggle_view = (dui_widget *)0;
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
    g_repo_mods_label = (dui_widget *)0;
    g_repo_packs_label = (dui_widget *)0;

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

static void on_launch_tool(dui_widget *self);

static void set_visible(dui_widget *w, int visible) {
    if (!w) {
        return;
    }
    if (visible) {
        w->flags |= DUI_WIDGET_VISIBLE;
    } else {
        w->flags &= ~DUI_WIDGET_VISIBLE;
    }
}

static std::string repo_tail(const std::string &path, const char *marker) {
    if (!marker) {
        return path;
    }
    const std::string m(marker);
    const size_t pos = path.find(m);
    if (pos == std::string::npos) {
        return path;
    }
    return path.substr(pos + m.size());
}

static dui_widget *add_launch_button(dui_context &ctx,
                                     dui_widget *parent,
                                     DomLauncherApp &app,
                                     const char *label,
                                     const char *tool_id,
                                     const std::string &load_path,
                                     int use_demo,
                                     std::vector<dui_widget *> &out_buttons) {
    dui_widget *w = add_child(ctx, parent, DUI_WIDGET_BUTTON);
    if (!w) {
        return (dui_widget *)0;
    }

    LaunchCtx *lc = new LaunchCtx();
    lc->app = &app;
    lc->tool_id = tool_id ? tool_id : "";
    lc->load_path = load_path;
    lc->label = label ? label : "";
    lc->use_demo = use_demo;
    g_launch_ctxs.push_back(lc);

    w->text = lc->label.c_str();
    w->on_click = on_launch_tool;
    w->user_data = (void *)lc;
    out_buttons.push_back(w);
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

static void on_toggle_view(dui_widget *self) {
    DomLauncherApp *app = self ? (DomLauncherApp *)self->user_data : (DomLauncherApp *)0;
    if (app) {
        app->toggle_tools_view();
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

static void on_launch_tool(dui_widget *self) {
    LaunchCtx *ctx = self ? (LaunchCtx *)self->user_data : (LaunchCtx *)0;
    if (ctx && ctx->app) {
        (void)ctx->app->launch_tool(ctx->tool_id, ctx->load_path, ctx->use_demo != 0);
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
    g_panel->layout_rect.h = d_q16_16_from_int(560);

    g_title = add_child(ctx, g_panel, DUI_WIDGET_LABEL);
    if (g_title) g_title->text = "Dominium Launcher";

    g_toggle_view = add_child(ctx, g_panel, DUI_WIDGET_BUTTON);

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
    if (g_toggle_view) {
        g_toggle_view->text = "Tools";
        g_toggle_view->on_click = on_toggle_view;
        g_toggle_view->user_data = (void *)&app;
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

    /* Tools (shown only in Tools view). */
    (void)add_launch_button(ctx, g_panel, app, "World Editor", "world_editor", std::string(), 1, g_tool_buttons);
    (void)add_launch_button(ctx, g_panel, app, "Blueprint Editor", "blueprint_editor", std::string(), 1, g_tool_buttons);
    (void)add_launch_button(ctx, g_panel, app, "Tech Tree Editor", "tech_editor", std::string(), 1, g_tool_buttons);
    (void)add_launch_button(ctx, g_panel, app, "Policy Editor", "policy_editor", std::string(), 1, g_tool_buttons);
    (void)add_launch_button(ctx, g_panel, app, "Process Editor", "process_editor", std::string(), 1, g_tool_buttons);
    (void)add_launch_button(ctx, g_panel, app, "Transport Editor", "transport_editor", std::string(), 1, g_tool_buttons);
    (void)add_launch_button(ctx, g_panel, app, "Structure Editor", "struct_editor", std::string(), 1, g_tool_buttons);
    (void)add_launch_button(ctx, g_panel, app, "Item Editor", "item_editor", std::string(), 1, g_tool_buttons);
    (void)add_launch_button(ctx, g_panel, app, "Pack Editor", "pack_editor", std::string(), 1, g_tool_buttons);
    (void)add_launch_button(ctx, g_panel, app, "Mod Builder", "mod_builder", std::string(), 1, g_tool_buttons);
    (void)add_launch_button(ctx, g_panel, app, "Save Inspector", "save_inspector",
                            app.home_join("data/tools_demo/world_demo.dwrl"), 0, g_tool_buttons);
    (void)add_launch_button(ctx, g_panel, app, "Replay Viewer", "replay_viewer", std::string(), 0, g_tool_buttons);
    (void)add_launch_button(ctx, g_panel, app, "Net Inspector", "net_inspector", std::string(), 0, g_tool_buttons);

    g_repo_mods_label = add_child(ctx, g_panel, DUI_WIDGET_LABEL);
    if (g_repo_mods_label) {
        g_repo_mods_label->text = g_buf_repo_mods;
    }
    {
        size_t i;
        const std::vector<std::string> &mods = app.repo_mod_manifests();
        for (i = 0u; i < mods.size() && i < 6u; ++i) {
            const std::string label = std::string("Mod: ") + repo_tail(mods[i], "repo/mods/");
            (void)add_launch_button(ctx, g_panel, app, label.c_str(), "mod_builder", mods[i], 0, g_mod_buttons);
        }
    }

    g_repo_packs_label = add_child(ctx, g_panel, DUI_WIDGET_LABEL);
    if (g_repo_packs_label) {
        g_repo_packs_label->text = g_buf_repo_packs;
    }
    {
        size_t i;
        const std::vector<std::string> &packs = app.repo_pack_manifests();
        for (i = 0u; i < packs.size() && i < 6u; ++i) {
            const std::string label = std::string("Pack: ") + repo_tail(packs[i], "repo/packs/");
            (void)add_launch_button(ctx, g_panel, app, label.c_str(), "pack_editor", packs[i], 0, g_pack_buttons);
        }
    }
}

void dom_launcher_ui_update(dui_context &ctx, DomLauncherApp &app) {
    const int inst_idx = app.selected_instance_index();
    const unsigned inst_count = (unsigned)app.instances().size();
    const int tools_view = app.showing_tools() ? 1 : 0;

    (void)ctx;
    std::snprintf(g_buf_summary, sizeof(g_buf_summary), "Products: %u  Instances: %u  Mods: %u  Packs: %u",
                  (unsigned)app.products().size(),
                  (unsigned)app.instances().size(),
                  (unsigned)app.repo_mod_manifests().size(),
                  (unsigned)app.repo_pack_manifests().size());
    if (g_summary) g_summary->text = g_buf_summary;

    if (g_toggle_view) {
        g_toggle_view->text = tools_view ? "Back to Game" : "Tools";
    }

    std::snprintf(g_buf_repo_mods, sizeof(g_buf_repo_mods),
                  "Repo Mods: %u", (unsigned)app.repo_mod_manifests().size());
    std::snprintf(g_buf_repo_packs, sizeof(g_buf_repo_packs),
                  "Repo Packs: %u", (unsigned)app.repo_pack_manifests().size());

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

    /* Page visibility. */
    set_visible(g_instance, !tools_view);
    set_visible(g_prev_instance, !tools_view);
    set_visible(g_next_instance, !tools_view);
    set_visible(g_mode_button, !tools_view);
    set_visible(g_connect, !tools_view);
    set_visible(g_connect_edit_button, !tools_view);
    set_visible(g_port, !tools_view);
    set_visible(g_port_dec, !tools_view);
    set_visible(g_port_inc, !tools_view);
    set_visible(g_listen, !tools_view);
    set_visible(g_dedicated, !tools_view);
    set_visible(g_connect_button, !tools_view);

    set_visible(g_repo_mods_label, tools_view);
    set_visible(g_repo_packs_label, tools_view);
    if (g_repo_mods_label) g_repo_mods_label->text = g_buf_repo_mods;
    if (g_repo_packs_label) g_repo_packs_label->text = g_buf_repo_packs;

    {
        size_t i;
        for (i = 0u; i < g_tool_buttons.size(); ++i) {
            set_visible(g_tool_buttons[i], tools_view);
        }
        for (i = 0u; i < g_mod_buttons.size(); ++i) {
            set_visible(g_mod_buttons[i], tools_view);
        }
        for (i = 0u; i < g_pack_buttons.size(); ++i) {
            set_visible(g_pack_buttons[i], tools_view);
        }
    }
}

int dom_launcher_ui_try_click(dui_context &ctx, int x, int y) {
    return traverse_try_click(ctx.root, x, y);
}

} // namespace dom
