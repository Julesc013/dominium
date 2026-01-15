/*
FILE: source/dominium/tools/replay_viewer/main_replay_viewer.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / tools/replay_viewer/main_replay_viewer
RESPONSIBILITY: Implements `main_replay_viewer`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "dom_replay_viewer_controller.h"

#include "dominium/tools/common/dom_tool_app.h"
#include "dominium/tools/common/dom_tool_cli.h"

#include <cstdio>

static void print_usage(void) {
    std::printf("Usage: dominium-replay-viewer [--home=<path>] [--load=<path>]\n");
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

    dom::tools::DomReplayViewerController controller;
    dom::tools::DomToolApp app(controller);
    if (!app.init(cfg.sys_backend, cfg.gfx_backend, cfg.home, cfg.load)) {
        return 1;
    }
    return app.run();
}

