/*
FILE: source/dominium/launcher/core/launcher_main.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / launcher/core/launcher_main
RESPONSIBILITY: Implements `launcher_main`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "dom_launcher/launcher_context.h"
#include "dom_launcher/launcher_state.h"
#include "dom_launcher/launcher_discovery.h"
#include "dom_launcher/launcher_ui_cli.h"
#include "dom_launcher/launcher_ui_gui.h"
#include "dom_launcher/launcher_ui_tui.h"
#include "dom_shared/logging.h"
#include <cstring>

int main(int argc, char** argv)
{
    (void)argc;
    (void)argv;

    using namespace dom_launcher;
    using namespace dom_shared;

    bool force_cli = false;
    bool force_tui = false;
    for (int i = 1; i < argc; ++i) {
        if (std::strcmp(argv[i], "--cli") == 0) force_cli = true;
        if (std::strcmp(argv[i], "--tui") == 0) force_tui = true;
    }

    LauncherContext ctx = init_launcher_context();
    log_set_min_level(LOG_INFO);
    log_info("Dominium launcher starting. Install root: %s", ctx.self_install.root_path.c_str());

    state_initialize();
    LauncherState& state = get_state();

    std::vector<dom_shared::InstallInfo> discovered = discover_installs(state);
    merge_discovered_installs(state, discovered);
    state_save();

    log_info("Discovered %d installs.", (int)state.installs.size());
    for (size_t i = 0; i < state.installs.size(); ++i) {
        const dom_shared::InstallInfo& ii = state.installs[i];
        log_info("  [%d] %s (%s %s) at %s",
                 (int)i,
                 ii.install_id.c_str(),
                 ii.install_type.c_str(),
                 ii.version.c_str(),
                 ii.root_path.c_str());
    }

    // Mode selection:
    // - If --cli: go straight to CLI.
    // - If --tui: try TUI, fall back to CLI on failure.
    // - Default/--gui: try GUI, fall back to CLI on failure.
    if (force_cli) {
        return launcher_run_cli(argc, argv);
    }

    if (force_tui) {
        int tui_rc = launcher_run_tui(argc, argv);
        if (tui_rc == 0) return 0;
        return launcher_run_cli(argc, argv);
    }

    // Default or explicitly forced GUI
    int gui_rc = launcher_run_gui(argc, argv);
    if (gui_rc == 0) return 0;
    return launcher_run_cli(argc, argv);
}
