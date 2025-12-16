/*
FILE: source/dominium/tools/policy_editor/main_policy_editor.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / tools/policy_editor/main_policy_editor
RESPONSIBILITY: Implements `main_policy_editor`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "dominium/tools/common/dom_tool_app.h"
#include "dominium/tools/common/dom_tool_cli.h"
#include "dominium/tools/common/dom_tool_controller_content.h"

#include <cstdio>

extern "C" {
#include "content/d_content_schema.h"
}

static void print_usage(void) {
    std::printf("Usage: dominium-policy-editor [--home=<path>] [--load=<path>] [--demo]\n");
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
        const u32 focus[] = { D_TLV_SCHEMA_POLICY_RULE_V1 };
        dom::tools::DomContentToolController controller(
            "policy_editor",
            "Policy Editor",
            "Edit rule sets (scope/effect/conditions) without gameplay semantics.",
            &focus[0],
            sizeof(focus) / sizeof(focus[0]),
            "data/tools_demo/policy_demo.tlv"
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
