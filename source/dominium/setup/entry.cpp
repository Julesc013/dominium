#include "domino/app/startup.h"
#include "dominium/app/product_entry.hpp"

extern "C" {

int dom_setup_run_cli(const d_app_params* p) {
    extern "C" int dom_setup_entry_cli(int argc, char** argv);
    if (!p) {
        return 1;
    }
    return dom_setup_entry_cli(p->argc, p->argv);
}

int dom_setup_run_tui(const d_app_params* p) {
    extern "C" int dom_setup_run_tui_impl(void);
    (void)p;
    return dom_setup_run_tui_impl();
}

int dom_setup_run_gui(const d_app_params* p) {
    extern "C" int dom_setup_run_gui_impl(void);
    (void)p;
    return dom_setup_run_gui_impl();
}

int dom_launcher_run_cli(const d_app_params* p) {
    (void)p;
    return D_APP_ERR_NO_INTERFACE;
}

int dom_launcher_run_tui(const d_app_params* p) {
    (void)p;
    return D_APP_ERR_TUI_UNSUPPORTED;
}

int dom_launcher_run_gui(const d_app_params* p) {
    (void)p;
    return D_APP_ERR_GUI_UNSUPPORTED;
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
