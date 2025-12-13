#include "dom_launcher_ui.h"

#include <vector>
#include <string>
#include <cstdio>

namespace dom {

void dom_launcher_ui_build_root(dui_context &ctx, DomLauncherApp &app) {
    dui_widget *root = ctx.root;
    dui_widget *title;
    dui_widget *summary;
    static std::vector<std::string> labels;

    labels.clear();
    labels.reserve(2u);

    if (!root) {
        return;
    }

    title = dui_widget_create(&ctx, DUI_WIDGET_LABEL);
    if (title) {
        labels.push_back("Dominium Launcher");
        title->text = labels.back().c_str();
        dui_widget_add_child(root, title);
    }

    summary = dui_widget_create(&ctx, DUI_WIDGET_LABEL);
    if (summary) {
        char buf[128];
        std::snprintf(buf, sizeof(buf), "Products: %u  Instances: %u",
                      (unsigned)app.products().size(),
                      (unsigned)app.instances().size());
        labels.push_back(buf);
        summary->text = labels.back().c_str();
        dui_widget_add_child(root, summary);
    }
}

} // namespace dom
