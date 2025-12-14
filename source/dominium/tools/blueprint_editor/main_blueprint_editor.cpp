#include "dominium/tools/common/dom_tool_app.h"
#include "dominium/tools/common/dom_tool_cli.h"
#include "dominium/tools/common/dom_tool_controller_content.h"

#include <cstdio>

extern "C" {
#include "content/d_content_schema.h"
}

static void print_usage(void) {
    /* Minimal; flags are shared across all tools. */
    std::printf("Usage: dominium-blueprint-editor [--home=<path>] [--load=<path>] [--demo]\n");
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

    {
        const u32 focus[] = { D_TLV_SCHEMA_BLUEPRINT_V1 };
        dom::tools::DomContentToolController controller(
            "blueprint_editor",
            "Blueprint Editor",
            "Assemble reusable factory blueprints (TLV-first).",
            &focus[0],
            sizeof(focus) / sizeof(focus[0]),
            "data/tools_demo/blueprint_demo.tlv"
        );

        if (cfg.demo && cfg.load.empty()) {
            cfg.load = controller.demo_path(cfg.home);
        }

        dom::tools::DomToolApp app(controller);
        if (!app.init(cfg.sys_backend, cfg.gfx_backend, cfg.home, cfg.load)) {
            return 1;
        }
        return app.run();
    }
}
