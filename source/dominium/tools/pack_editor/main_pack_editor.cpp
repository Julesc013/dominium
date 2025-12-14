#include "dominium/tools/common/dom_tool_app.h"
#include "dominium/tools/common/dom_tool_cli.h"
#include "dominium/tools/common/dom_tool_controller_content.h"

#include <cstdio>

extern "C" {
#include "content/d_content_schema.h"
}

static void print_usage(void) {
    std::printf("Usage: dominium-pack-editor [--home=<path>] [--load=<path>] [--demo]\n");
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
        /* Pack editor focuses on the pack container schema, but can open raw content streams too. */
        const u32 focus[] = {
            D_TLV_SCHEMA_MATERIAL_V1,
            D_TLV_SCHEMA_ITEM_V1,
            D_TLV_SCHEMA_CONTAINER_V1,
            D_TLV_SCHEMA_PROCESS_V1,
            D_TLV_SCHEMA_DEPOSIT_V1,
            D_TLV_SCHEMA_STRUCTURE_V1,
            D_TLV_SCHEMA_VEHICLE_V1,
            D_TLV_SCHEMA_SPLINE_V1,
            D_TLV_SCHEMA_JOB_TEMPLATE_V1,
            D_TLV_SCHEMA_BUILDING_V1,
            D_TLV_SCHEMA_BLUEPRINT_V1,
            D_TLV_SCHEMA_RESEARCH_V1,
            D_TLV_SCHEMA_RESEARCH_POINT_SOURCE_V1,
            D_TLV_SCHEMA_POLICY_RULE_V1
        };

        dom::tools::DomContentToolController controller(
            "pack_editor",
            "Pack Editor",
            "Edit pack metadata and assets (vector/raster/audio).",
            &focus[0],
            sizeof(focus) / sizeof(focus[0]),
            "data/tools_demo/pack_demo.tlv"
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
