/*
FILE: source/dominium/launcher/dom_launcher_actions.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / launcher/dom_launcher_actions
RESPONSIBILITY: Implements `dom_launcher_actions`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
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
