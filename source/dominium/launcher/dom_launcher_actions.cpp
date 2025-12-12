#include "dom_launcher_actions.h"

#include <cstdio>

#include "dom_launcher_catalog.h"

namespace dom {

bool launcher_action_list_instances(const std::vector<InstanceInfo> &instances) {
    launcher_print_instances(instances);
    return true;
}

bool launcher_action_list_products(const std::vector<ProductEntry> &products) {
    launcher_print_products(products);
    return true;
}

bool launcher_action_launch(DomLauncherApp &app,
                            const LauncherConfig &cfg) {
    std::string inst_id = cfg.instance_id;
    std::string mode = cfg.product_mode.empty() ? app.selected_mode() : cfg.product_mode;
    std::string product = cfg.product;

    if (product.empty() && app.selected_product_index() >= 0 &&
        app.selected_product_index() < (int)app.products().size()) {
        product = app.products()[(size_t)app.selected_product_index()].product;
    }
    if (inst_id.empty() && app.selected_instance_index() >= 0 &&
        app.selected_instance_index() < (int)app.instances().size()) {
        inst_id = app.instances()[(size_t)app.selected_instance_index()].id;
    }

    if (product.empty()) {
        std::printf("Launcher: no product specified for launch.\n");
        return false;
    }
    return app.launch_product(product, inst_id, mode);
}

} // namespace dom
