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
