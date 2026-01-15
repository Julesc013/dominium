/*
FILE: source/dominium/tools/mod_builder/main_mod_builder.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / tools/mod_builder/main_mod_builder
RESPONSIBILITY: Implements `main_mod_builder`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "dom_mod_builder_controller.h"

#include "dominium/tools/common/dom_tool_app.h"
#include "dominium/tools/common/dom_tool_cli.h"

#include <cstdio>

static void print_usage(void) {
    std::printf("Usage: dominium-mod-builder [--home=<path>] [--load=<path>] [--demo]\n");
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

    dom::tools::DomModBuilderController controller;
    if (cfg.demo && cfg.load.empty()) {
        cfg.load = controller.demo_path(cfg.home);
    }

    dom::tools::DomToolApp app(controller);
    if (!app.init(cfg.sys_backend, cfg.gfx_backend, cfg.home, cfg.load)) {
        return 1;
    }
    return app.run();
}

