#include "dom_launcher_ui.h"

#include <vector>
#include <string>

namespace dom {
namespace {

struct SelectPayload {
    DomLauncherApp *app;
    int index;
};

struct ModePayload {
    DomLauncherApp *app;
    const char *mode;
};

static SelectPayload g_select_payloads[128];
static int g_select_payload_count = 0;

static ModePayload g_mode_payloads[8];
static int g_mode_payload_count = 0;

static std::vector<std::string> g_label_storage;

static SelectPayload* make_select_payload(DomLauncherApp *app, int index) {
    if (g_select_payload_count >= (int)(sizeof(g_select_payloads) / sizeof(g_select_payloads[0]))) {
        return (SelectPayload *)0;
    }
    g_select_payloads[g_select_payload_count].app = app;
    g_select_payloads[g_select_payload_count].index = index;
    return &g_select_payloads[g_select_payload_count++];
}

static ModePayload* make_mode_payload(DomLauncherApp *app, const char *mode) {
    if (g_mode_payload_count >= (int)(sizeof(g_mode_payloads) / sizeof(g_mode_payloads[0]))) {
        return (ModePayload *)0;
    }
    g_mode_payloads[g_mode_payload_count].app = app;
    g_mode_payloads[g_mode_payload_count].mode = mode;
    return &g_mode_payloads[g_mode_payload_count++];
}

static void on_instance_clicked(dui_widget *self) {
    SelectPayload *p;
    if (!self) return;
    p = (SelectPayload *)self->user_data;
    if (p && p->app) {
        p->app->set_selected_instance(p->index);
    }
}

static void on_product_clicked(dui_widget *self) {
    SelectPayload *p;
    if (!self) return;
    p = (SelectPayload *)self->user_data;
    if (p && p->app) {
        p->app->set_selected_product(p->index);
    }
}

static void on_mode_clicked(dui_widget *self) {
    ModePayload *p;
    if (!self) return;
    p = (ModePayload *)self->user_data;
    if (p && p->app && p->mode) {
        p->app->set_selected_mode(p->mode);
    }
}

static void on_launch_clicked(dui_widget *self) {
    DomLauncherApp *app;
    if (!self) return;
    app = (DomLauncherApp *)self->user_data;
    if (!app) return;

    std::string product;
    std::string instance;

    if (app->selected_product_index() >= 0 &&
        app->selected_product_index() < (int)app->products().size()) {
        product = app->products()[(size_t)app->selected_product_index()].product;
    }
    if (app->selected_instance_index() >= 0 &&
        app->selected_instance_index() < (int)app->instances().size()) {
        instance = app->instances()[(size_t)app->selected_instance_index()].id;
    }
    if (!product.empty()) {
        (void)app->launch_product(product, instance, app->selected_mode());
    }
}

static dui_widget* make_label(dui_context &ctx, const std::string &text) {
    dui_widget *label = dui_widget_create(&ctx, DUI_WIDGET_LABEL);
    if (!label) {
        return (dui_widget *)0;
    }
    g_label_storage.push_back(text);
    label->text = g_label_storage.back().c_str();
    return label;
}

static dui_widget* make_button(dui_context &ctx, const std::string &text,
                               void (*on_click)(dui_widget *self),
                               void *userdata) {
    dui_widget *btn = dui_widget_create(&ctx, DUI_WIDGET_BUTTON);
    if (!btn) {
        return (dui_widget *)0;
    }
    g_label_storage.push_back(text);
    btn->text = g_label_storage.back().c_str();
    btn->on_click = on_click;
    btn->user_data = userdata;
    return btn;
}

} // namespace

void dom_launcher_ui_build_root(dui_context &ctx, DomLauncherApp &app) {
    dui_widget *root = ctx.root;
    size_t i;

    g_select_payload_count = 0;
    g_mode_payload_count = 0;
    g_label_storage.clear();
    g_label_storage.reserve(app.instances().size() + app.products().size() + 12u);

    if (!root) {
        return;
    }

    /* Instances panel */
    dui_widget *inst_panel = dui_widget_create(&ctx, DUI_WIDGET_PANEL);
    dui_widget_add_child(root, inst_panel);
    dui_widget_add_child(inst_panel, make_label(ctx, "Instances"));
    for (i = 0u; i < app.instances().size(); ++i) {
        SelectPayload *payload = make_select_payload(&app, (int)i);
        dui_widget *btn = make_button(ctx, app.instances()[i].id, on_instance_clicked, payload);
        dui_widget_add_child(inst_panel, btn);
    }

    /* Products panel */
    dui_widget *prod_panel = dui_widget_create(&ctx, DUI_WIDGET_PANEL);
    dui_widget_add_child(root, prod_panel);
    dui_widget_add_child(prod_panel, make_label(ctx, "Products"));
    for (i = 0u; i < app.products().size(); ++i) {
        const ProductEntry &p = app.products()[i];
        std::string text = p.product + " (" + p.version + ")";
        SelectPayload *payload = make_select_payload(&app, (int)i);
        dui_widget *btn = make_button(ctx, text, on_product_clicked, payload);
        dui_widget_add_child(prod_panel, btn);
    }

    /* Mode selector */
    dui_widget *mode_panel = dui_widget_create(&ctx, DUI_WIDGET_PANEL);
    dui_widget_add_child(root, mode_panel);
    dui_widget_add_child(mode_panel, make_label(ctx, "Mode"));
    {
        ModePayload *pgui = make_mode_payload(&app, "gui");
        ModePayload *ptui = make_mode_payload(&app, "tui");
        ModePayload *pheadless = make_mode_payload(&app, "headless");
        dui_widget_add_child(mode_panel, make_button(ctx, "GUI", on_mode_clicked, pgui));
        dui_widget_add_child(mode_panel, make_button(ctx, "TUI", on_mode_clicked, ptui));
        dui_widget_add_child(mode_panel, make_button(ctx, "Headless", on_mode_clicked, pheadless));
    }

    /* Launch */
    dui_widget *actions = dui_widget_create(&ctx, DUI_WIDGET_PANEL);
    dui_widget_add_child(root, actions);
    dui_widget_add_child(actions, make_button(ctx, "Launch", on_launch_clicked, &app));
}

} // namespace dom
