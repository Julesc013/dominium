/*
FILE: source/dominium/launcher/entry.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / launcher/entry
RESPONSIBILITY: Implements `entry`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "domino/app/startup.h"
#include "dominium/app/product_entry.hpp"
#include "dominium/launcher/launcher_app.hpp"

extern "C" {

int dom_launcher_run_cli(const d_app_params* p) {
    LauncherApp app;
    if (!p) {
        return 1;
    }
    return app.run(p->argc, p->argv);
}

int dom_launcher_run_tui(const d_app_params* p) {
    LauncherApp app;
    (void)p;
    return app.run_tui();
}

int dom_launcher_run_gui(const d_app_params* p) {
    LauncherApp app;
    (void)p;
    return app.run_gui();
}

int dom_game_run_cli(const d_app_params* p) {
    (void)p;
    return D_APP_ERR_NO_INTERFACE;
}

int dom_game_run_tui(const d_app_params* p) {
    (void)p;
    return D_APP_ERR_TUI_UNSUPPORTED;
}

int dom_game_run_gui(const d_app_params* p) {
    (void)p;
    return D_APP_ERR_GUI_UNSUPPORTED;
}

int dom_game_run_headless(const d_app_params* p) {
    (void)p;
    return D_APP_ERR_HEADLESS_ERROR;
}

int dom_setup_run_cli(const d_app_params* p) {
    (void)p;
    return D_APP_ERR_NO_INTERFACE;
}

int dom_setup_run_tui(const d_app_params* p) {
    (void)p;
    return D_APP_ERR_TUI_UNSUPPORTED;
}

int dom_setup_run_gui(const d_app_params* p) {
    (void)p;
    return D_APP_ERR_GUI_UNSUPPORTED;
}

int dom_tools_run_cli(const d_app_params* p) {
    (void)p;
    return D_APP_ERR_NO_INTERFACE;
}

int dom_tools_run_tui(const d_app_params* p) {
    (void)p;
    return D_APP_ERR_TUI_UNSUPPORTED;
}

int dom_tools_run_gui(const d_app_params* p) {
    (void)p;
    return D_APP_ERR_GUI_UNSUPPORTED;
}

} /* extern "C" */
