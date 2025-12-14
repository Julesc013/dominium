#include "dom_world_editor_controller.h"

#include "dominium/tools/common/dom_tool_app.h"
#include "dominium/tools/common/dom_tool_cli.h"

#include <cstdio>

static void print_usage(void) {
    std::printf("Usage: dominium-world-editor [--home=<path>] [--load=<path>] [--demo]\n");
}

int main(int argc, char **argv) {
    dom::tools::DomToolCliConfig cfg;
    std::string err;
    if (!dom::tools::parse_tool_cli(argc, argv, cfg, err)) {
        print_usage();
        return 1;
    }
    if (cfg.home.empty()) {
        cfg.home = ".";
    }

    dom::tools::DomWorldEditorController controller;
    if (cfg.demo && cfg.load.empty()) {
        cfg.load = controller.demo_path(cfg.home);
    }

    dom::tools::DomToolApp app(controller);
    if (!app.init(cfg.sys_backend, cfg.gfx_backend, cfg.home, cfg.load)) {
        return 1;
    }
    return app.run();
}

